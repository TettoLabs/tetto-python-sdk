# Python SDK v0.1.0 → v2.0.0 Upgrade Plan

**Date:** 2025-11-06
**Following:** SDK Maintenance Manifesto
**Principle:** Research first, change second. Slow and methodical beats fast and sloppy.

---

## ✅ Research Phase Complete

**TypeScript SDK v2.0.0 analyzed:**
- ✅ Read src/index.ts (818 lines) - Main SDK with callAgent implementation
- ✅ Read src/wallet-helpers.ts - Wallet creation patterns
- ✅ Read src/network-helpers.ts - Configuration helpers
- ✅ Read src/types.ts - Type definitions
- ✅ Read examples/calling-agents/node-keypair.ts - Production example

**Key findings documented below.**

---

## 🎯 v2.0.0 Architecture (TypeScript SDK - PROVEN PRODUCTION)

### Flow for `callAgent()`:

```
1. Get agent details (validate agent exists)
   GET /api/agents/{agent_id}

2. Request unsigned transaction from platform
   POST /api/agents/{agent_id}/build-transaction
   Body: {
     payer_wallet: string,
     selected_token?: 'SOL' | 'USDC',
     input: {...},           # ✅ INPUT VALIDATED BEFORE PAYMENT
     calling_agent_id?: string
   }
   Response: {
     ok: boolean,
     transaction: string (base64),  # Unsigned transaction
     payment_intent_id: string,
     amount_base: number,
     token: string,
     expires_at: string,
     input_hash: string,
     error?: string
   }

3. Sign transaction client-side
   Transaction.from(Buffer.from(base64))
   wallet.signTransaction(tx)

4. Submit signed transaction to platform
   POST /api/agents/call
   Body: {
     payment_intent_id: string,
     signed_transaction: string (base64)
   }
   Response: {
     ok: boolean,
     message: string,
     output: {...},
     tx_signature: string,
     receipt_id: string,
     explorer_url: string,
     agent_received: number,
     protocol_fee: number,
     error?: string
   }
```

### Key Differences from v1.0 (Current Python SDK):

| Aspect | v1.0 (DANGEROUS) | v2.0 (SAFE) |
|--------|------------------|-------------|
| **Transaction Building** | Client-side (180 lines) | ✅ Platform builds |
| **Input Validation** | After payment ❌ | ✅ **BEFORE payment** (fail-fast!) |
| **Code Complexity** | 180 lines transactions.py | ✅ ~40 lines |
| **RPC Connection** | Required | ✅ Not needed |
| **Stuck Funds Risk** | Yes ❌ | ✅ **No** (validate first!) |
| **Dependencies** | solana, solders (heavy) | ✅ Lighter |

---

## 📋 Complete File-by-File Change Map

### Files to MODIFY:

**1. tetto/client.py**
- **Line 119-205:** Replace `call_agent()` method completely
  - Remove import of transactions.py
  - Implement 2-step platform flow:
    1. POST `/api/agents/{id}/build-transaction`
    2. Sign transaction
    3. POST `/api/agents/call` with payment_intent_id
  - Update docstring to reflect v2.0 architecture
  - Add debug logging for each step

- **Line 33-66:** Simplify `__init__()`
  - Remove `rpc_url` parameter (not needed in v2.0)
  - Keep `protocol_wallet` (for reference only)
  - Keep `usdc_mint` (for reference only)

**2. tetto/__init__.py**
- **Line 14:** Update `__version__` from "0.1.0" to "2.0.0"
- No other changes needed

**3. setup.py**
- **Line 8:** Update `version` from "0.1.0" to "2.0.0"
- **Line 11:** Update `description` to mention v2.0 features
- **Line 28-33:** Review dependencies:
  - Keep: httpx, pydantic
  - Reduce: solana, solders (still needed for signing, but simpler usage)

### Files to DELETE:

**4. tetto/transactions.py** ❌
- **ENTIRE FILE (184 lines)** - Delete completely
- This is the DANGEROUS client-side transaction building code
- Replaced by platform-powered architecture
- Reason: Input validation after payment = stuck funds risk

### Files to UPDATE (Documentation):

**5. README.md**
- **Line 11-13:** Update from "v0.1.0" to "v2.0.0"
- **Line 11-28:** REMOVE "⚠️ Architecture & Current Limitations" section
- **Line 30-63:** UPDATE "Planned for v0.2.0+" section:
  - Move from "planned" to "✅ IMPLEMENTED in v2.0.0"
  - Features now available:
    - ✅ Input validation BEFORE payment
    - ✅ Platform-powered architecture
    - ✅ 75% code reduction (removed transactions.py)
- **Throughout:** Replace mentions of "v0.1.0" with "v2.0.0"
- **Throughout:** Replace "client-side" with "platform-powered"
- **Line 285-322:** UPDATE "Testing on Devnet" section
  - Emphasize NO RPC connection needed
  - Simpler setup

**6. AI_LOOK_HERE.md**
- **Line 22:** Update "v0.1.0" to "v2.0.0"
- **Line 20-44:** UPDATE "Current Status" section:
  - v2.0.0 PRODUCTION READY
  - Platform-powered architecture
  - Input validation before payment
- **Line 77-95:** UPDATE "Architecture" section:
  - Remove mentions of building transactions client-side
  - Update to platform-powered flow
- **Line 122-155:** UPDATE "Payment Flow":
  - Document new 2-step flow
  - Remove USDC/SOL implementation details (platform handles)

**7. CHANGELOG.md**
- Add new section at top:
  ```
  ## [2.0.0] - 2025-11-06

  ### 🎉 MAJOR RELEASE - Platform-Powered Architecture

  **BREAKING CHANGES:**
  - Removed client-side transaction building (deleted transactions.py)
  - Input validation now occurs BEFORE payment (safer!)
  - RPC URL parameter no longer used (platform handles submission)

  **Added:**
  - Platform-powered agent calling (validate input before payment)
  - 75% code reduction (removed 180 lines of transaction code)
  - Fail-fast pattern (invalid input rejected before funds spent)

  **Removed:**
  - tetto/transactions.py (DANGEROUS client-side building)
  - build_and_send_payment() function
  - Manual ATA derivation code
  - Manual fee calculation code

  **Migration from v0.1.0:**
  - API unchanged - client.call_agent() works the same
  - Internal implementation completely rewritten
  - No code changes needed for users!
  ```

**8. examples/simple_call.py**
- **Line 1-23:** Update header comments:
  - Mention v2.0.0 platform-powered architecture
  - Emphasize input validation before payment
  - Note that NO RPC connection is needed
- **Line 82-85:** Update comments:
  - "Platform validates input BEFORE creating transaction"
  - "If input is invalid, you'll know immediately - no stuck funds!"

**9. examples/test_sdk.py**
- **Throughout:** Update references to v0.1.0 → v2.0.0
- Add note about platform-powered architecture

**10. examples/README.md**
- Update throughout to mention v2.0.0
- Emphasize safer input validation

### Files to CREATE:

**11. MIGRATION_v1_to_v2.md** (NEW)
- Document the upgrade from v0.1.0 to v2.0.0
- Explain breaking changes
- Provide migration path (if any)

---

## 🔧 Detailed Implementation for client.py

### Current `call_agent()` (v1.0 - DANGEROUS):

```python
async def call_agent(self, agent_id, input_data, preferred_token="USDC"):
    # Get agent
    agent = await self.get_agent(agent_id)

    # Build transaction CLIENT-SIDE (DANGEROUS!)
    from .transactions import build_and_send_payment
    tx_signature = await build_and_send_payment(...)  # 180 lines of code

    # THEN call platform (INPUT VALIDATED AFTER PAYMENT ❌)
    response = await self.http_client.post("/api/agents/call", {
        "tx_signature": tx_signature,
        "input": input_data  # Too late! Already paid!
    })
```

### New `call_agent()` (v2.0 - SAFE):

```python
async def call_agent(self, agent_id, input_data, preferred_token="USDC"):
    # Step 1: Get agent
    agent = await self.get_agent(agent_id)

    # Step 2: Request unsigned transaction (VALIDATE INPUT FIRST ✅)
    build_response = await self.http_client.post(
        f"{self.api_url}/api/agents/{agent_id}/build-transaction",
        json={
            "payer_wallet": str(self.keypair.pubkey()),
            "selected_token": preferred_token,
            "input": input_data,  # ✅ Platform validates BEFORE building tx
        }
    )
    build_result = build_response.json()

    if not build_result["ok"]:
        raise Exception(build_result["error"])  # ✅ Fail fast! No payment yet!

    # Step 3: Deserialize and sign transaction
    from solders.transaction import VersionedTransaction
    from base64 import b64decode, b64encode

    tx_bytes = b64decode(build_result["transaction"])
    transaction = VersionedTransaction.from_bytes(tx_bytes)

    # Sign (client-side signing)
    signature = self.keypair.sign_message(bytes(transaction.message))
    signed_tx = VersionedTransaction.populate(transaction.message, [signature])

    # Step 4: Submit signed transaction
    response = await self.http_client.post(
        f"{self.api_url}/api/agents/call",
        json={
            "payment_intent_id": build_result["payment_intent_id"],
            "signed_transaction": b64encode(bytes(signed_tx)).decode(),
        }
    )

    data = response.json()
    if not data["ok"]:
        raise Exception(data["error"])

    return data
```

**Total lines:** ~40 (vs 180 in v1.0)
**Safety:** ✅ Input validated BEFORE payment
**Complexity:** ✅ 75% reduction

---

## 🚨 Critical Safety Improvements

### Why v2.0 is CRITICAL:

**v1.0 Problem (DANGEROUS):**
```
1. Build transaction (costs SOL for gas) ❌
2. Send to Solana (PAYMENT SENT) ❌
3. Call platform with tx proof ❌
4. Platform validates input ❌
5. IF INVALID → FUNDS STUCK! ❌❌❌
```

**v2.0 Solution (SAFE):**
```
1. Send input to platform ✅
2. Platform validates input FIRST ✅
3. IF INVALID → Reject (NO PAYMENT YET) ✅
4. IF VALID → Build unsigned tx ✅
5. Sign tx ✅
6. Platform submits to Solana ✅
7. Call agent ✅
```

**Result:** ✅ ZERO risk of stuck funds from invalid input!

---

## 📊 Impact Assessment

### Code Changes:

| File | Before | After | Change |
|------|--------|-------|--------|
| client.py | 218 lines | ~220 lines | Rewrite call_agent() |
| transactions.py | 184 lines | ❌ DELETED | -184 lines |
| **Total** | 402 lines | 220 lines | **-45% code** |

### Features:

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Input validation | After payment ❌ | ✅ Before payment |
| RPC connection | Required | ✅ Not needed |
| Code complexity | High | ✅ Low |
| Stuck funds risk | Yes ❌ | ✅ No |
| Platform-powered | No | ✅ Yes |

### Breaking Changes:

**For SDK users:**
- ✅ **NO BREAKING CHANGES** to public API
- `client.call_agent(agent_id, input_data, preferred_token)` - SAME
- Internal implementation completely different, but API unchanged

**For SDK developers:**
- ❌ `transactions.py` deleted (if anyone imported it directly)
- ❌ `build_and_send_payment()` no longer exists
- ✅ Much simpler codebase to maintain

---

## ⚠️ Risks and Mitigation

### Risk 1: Platform API not working as expected

**Mitigation:**
- TypeScript SDK v2.0.0 is PROVEN PRODUCTION
- Platform endpoints exist and work
- Follow TypeScript implementation exactly

### Risk 2: Transaction signing differences (Python vs TypeScript)

**Mitigation:**
- Test with devnet first
- Verify signature format matches
- Add comprehensive error handling

### Risk 3: Breaking existing Python SDK users

**Mitigation:**
- Version bump to 2.0.0 signals breaking change (semantic versioning)
- Document migration (though API is same)
- Add note in CHANGELOG

---

## 📝 Implementation Checklist

### Phase 1: Code Changes
- [ ] Update `tetto/client.py` call_agent() method
- [ ] Update `tetto/__init__.py` version to 2.0.0
- [ ] Update `setup.py` version to 2.0.0
- [ ] Delete `tetto/transactions.py`
- [ ] Test implementation

### Phase 2: Documentation Updates
- [ ] Update `README.md` (remove limitations, update version)
- [ ] Update `AI_LOOK_HERE.md` (v2.0 architecture)
- [ ] Update `CHANGELOG.md` (add v2.0.0 release notes)
- [ ] Update `examples/simple_call.py` (comments)
- [ ] Update `examples/test_sdk.py` (version references)
- [ ] Update `examples/README.md` (version references)
- [ ] Create `MIGRATION_v1_to_v2.md`

### Phase 3: Verification
- [ ] All examples compile
- [ ] No forbidden patterns
- [ ] Version consistency (all files show 2.0.0)
- [ ] Documentation accurate
- [ ] Test on devnet (if possible)

### Phase 4: Commit
- [ ] Single logical commit with breaking change marker
- [ ] Comprehensive commit message
- [ ] Push to remote

---

## 🎯 Success Criteria

**Before declaring success:**
1. ✅ All code implements v2.0 platform-powered architecture
2. ✅ transactions.py deleted (dangerous code removed)
3. ✅ All documentation updated to v2.0
4. ✅ Version consistently 2.0.0 throughout
5. ✅ Examples updated and compile
6. ✅ CHANGELOG documents breaking changes
7. ✅ No forbidden patterns
8. ✅ Manifesto compliance verified

---

**Next Step:** Begin Phase 1 - Code Changes

**Principle:** Make changes systematically, one file at a time, testing as we go.
