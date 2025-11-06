# Migration Guide: v0.1.0 → v2.0.0

> **TL;DR:** No code changes required! The public API is unchanged, but you get major safety improvements.

---

## Overview

Tetto Python SDK v2.0.0 brings the **platform-powered architecture** that validates input **BEFORE** payment, eliminating the risk of stuck funds from invalid input.

**Migration Difficulty:** ⭐️ EASY (No code changes needed!)

**Time Required:** 5 minutes (just update dependency)

**Breaking Changes:** Only internal implementation (public API unchanged)

---

## What Changed?

### Architecture: v0.1.0 vs v2.0.0

**v0.1.0 (Old - DANGEROUS):**
```
Your Code → SDK builds transaction client-side (180 lines)
         → SDK sends to Solana RPC
         → Tetto API validates input
         → ❌ If invalid, payment already sent = STUCK FUNDS!
```

**v2.0.0 (New - SAFE):**
```
Your Code → Platform validates input FIRST
         → ✅ If invalid, fails immediately (no payment!)
         → Platform builds transaction
         → SDK signs transaction (~40 lines)
         → Platform submits to blockchain
         → ✅ No stuck funds risk!
```

### Key Improvements

| Feature | v0.1.0 | v2.0.0 |
|---------|--------|--------|
| **Input Validation** | ❌ After payment | ✅ Before payment |
| **Stuck Funds Risk** | ❌ Yes | ✅ No |
| **Transaction Building** | ❌ Client-side (180 lines) | ✅ Platform (40 lines) |
| **RPC Connection** | ❌ Required | ✅ Not needed |
| **Error Messages** | 🟡 After payment sent | ✅ Before payment |
| **Code Complexity** | 🟡 High | ✅ 75% simpler |

---

## Migration Steps

### Step 1: Update Dependency (1 minute)

**From PyPI (when published):**
```bash
pip install --upgrade tetto-python-sdk
```

**From Git:**
```bash
pip install --upgrade git+https://github.com/TettoLabs/tetto-python-sdk.git
```

**Verify version:**
```bash
python -c "import tetto; print(tetto.__version__)"
# Should print: 2.0.0
```

### Step 2: Test Your Code (No Changes Required!)

**Your existing code works unchanged:**

```python
import asyncio
from tetto import TettoClient, load_keypair_from_env

async def main():
    keypair = load_keypair_from_env("SOLANA_PRIVATE_KEY")

    async with TettoClient(
        api_url="https://tetto.io",
        network="mainnet",
        keypair=keypair,
        debug=True
    ) as client:
        # This code works in both v0.1.0 AND v2.0.0!
        result = await client.call_agent(
            agent_id="60fa88a8-5e8e-4884-944f-ac9fe278ff18",
            input_data={"text": "Hello from v2.0!"},
            preferred_token="USDC"
        )

        print(result["output"])
        print(result["tx_signature"])

asyncio.run(main())
```

**That's it!** Your code runs unchanged but now with input validation before payment.

### Step 3: Enjoy the Benefits

**Immediate improvements:**
- ✅ Invalid input rejected BEFORE payment (fail fast!)
- ✅ Better error messages (before funds are sent)
- ✅ No more stuck funds from validation errors
- ✅ Simpler SDK internals (75% code reduction)

---

## What's Different Under the Hood?

### Transaction Flow Changes

**v0.1.0 Flow:**
```python
# Old internal flow (you don't see this, but it happened):
# 1. SDK builds transaction with USDC/SOL instructions
# 2. SDK signs transaction
# 3. SDK sends to Solana RPC
# 4. SDK calls Tetto API with tx_signature
# 5. Tetto validates input
# 6. ❌ If invalid input, payment already sent = stuck funds!
```

**v2.0.0 Flow:**
```python
# New internal flow (you don't see this, but it happens):
# 1. SDK sends input to Tetto for validation
# 2. ✅ Tetto validates input FIRST (fail fast!)
# 3. Tetto builds unsigned transaction
# 4. SDK receives and signs transaction
# 5. SDK sends signed transaction to Tetto
# 6. Tetto submits to blockchain and calls agent
# 7. ✅ No stuck funds possible!
```

### Removed Files

**v0.1.0 had:**
- `tetto/transactions.py` (184 lines of client-side transaction code)

**v2.0.0 removed:**
- ❌ `tetto/transactions.py` (DELETED - dangerous code)

**Why?** This file contained dangerous client-side transaction building that validated input AFTER payment. The platform now handles all transaction building, eliminating stuck funds risk.

**Impact on your code:** ✅ None - this was an internal file

---

## Breaking Changes

### ❌ Removed: `tetto/transactions.py`

**If you imported from this file directly:**
```python
# ❌ This will break in v2.0.0:
from tetto.transactions import build_and_send_payment
```

**Solution:** Use the public API instead:
```python
# ✅ Use the public API (works in all versions):
result = await client.call_agent(agent_id, input_data)
```

**Note:** This file was never documented in the public API, so most users won't be affected.

### ✅ No Changes: Public API

**All public APIs remain unchanged:**
- ✅ `TettoClient.__init__()` - Same signature
- ✅ `client.list_agents()` - Same signature
- ✅ `client.get_agent()` - Same signature
- ✅ `client.call_agent()` - Same signature
- ✅ `load_keypair_from_file()` - Same signature
- ✅ `load_keypair_from_env()` - Same signature
- ✅ `generate_keypair()` - Same signature

---

## Error Handling Changes

### Better Error Messages

**v0.1.0:**
```python
# Invalid input example
try:
    result = await client.call_agent(
        agent_id="...",
        input_data={"wrong_field": "value"}  # Invalid!
    )
except Exception as e:
    # ❌ Error happens AFTER payment sent
    # ❌ Funds already stuck on blockchain
    print(f"Error: {e}")
```

**v2.0.0:**
```python
# Same invalid input
try:
    result = await client.call_agent(
        agent_id="...",
        input_data={"wrong_field": "value"}  # Invalid!
    )
except Exception as e:
    # ✅ Error happens BEFORE payment
    # ✅ No funds sent, nothing stuck!
    # ✅ Better error message from platform validation
    print(f"Error: {e}")  # "Transaction building failed: Invalid input schema"
```

---

## Testing Your Migration

### 1. Test on Devnet First

```python
async with TettoClient(
    api_url="https://tetto.io",
    network="devnet",  # 👈 Test on devnet first!
    keypair=keypair,
    debug=True  # 👈 Enable debug logs
) as client:
    # Test your agent calls with free devnet tokens
    result = await client.call_agent(agent_id, input_data, "SOL")
    print(result)
```

### 2. Verify Version

```python
import tetto
print(f"SDK Version: {tetto.__version__}")
# Should print: 2.0.0
```

### 3. Test Invalid Input (Should Fail Fast!)

```python
# Test that invalid input fails BEFORE payment
try:
    result = await client.call_agent(
        agent_id="60fa88a8-5e8e-4884-944f-ac9fe278ff18",
        input_data={"invalid": "field"}  # Wrong schema!
    )
except Exception as e:
    # ✅ Should fail immediately with clear error
    # ✅ No payment sent!
    print(f"✅ Failed fast: {e}")
```

### 4. Test Valid Call (Should Work!)

```python
# Test valid agent call
result = await client.call_agent(
    agent_id="60fa88a8-5e8e-4884-944f-ac9fe278ff18",
    input_data={"text": "Test migration to v2.0.0"}
)
print(f"✅ Success: {result['output']}")
print(f"✅ Transaction: {result['tx_signature']}")
```

---

## Rollback (If Needed)

**If you encounter issues, you can rollback to v0.1.0:**

```bash
# Rollback to v0.1.0
pip install git+https://github.com/TettoLabs/tetto-python-sdk.git@v0.1.0

# Verify version
python -c "import tetto; print(tetto.__version__)"
# Should print: 0.1.0
```

**Note:** v0.1.0 has the stuck funds risk, so only rollback temporarily while reporting issues.

---

## FAQ

### Q: Do I need to change my code?

**A:** No! The public API is unchanged. Just update the dependency.

### Q: Will my existing code break?

**A:** No. The `call_agent()` signature is identical. Your code will work unchanged.

### Q: What if I was using `tetto.transactions` directly?

**A:** That was never a documented public API. Use `client.call_agent()` instead.

### Q: Is v2.0.0 production-ready?

**A:** Yes! v2.0.0 matches the TypeScript SDK v2.0.0 architecture which has been running in production with 11+ agents on mainnet.

### Q: Can I test without risking funds?

**A:** Yes! Use `network="devnet"` for testing with free tokens before switching to mainnet.

### Q: What if input validation fails?

**A:** In v2.0.0, validation happens BEFORE payment, so you get an error immediately without losing funds. In v0.1.0, you'd lose the payment fees.

### Q: Why is this a major version bump (2.0.0)?

**A:** We're following semantic versioning. Deleting `tetto/transactions.py` is technically a breaking change, even though it was never documented in the public API. Major version bump signals significant architectural change.

### Q: Do I need to update my wallet or keys?

**A:** No. Wallet management is unchanged.

### Q: Will transaction signatures change?

**A:** Transaction structure changes (built by platform instead of SDK), but signatures are still valid Solana transactions viewable on explorers.

---

## Benefits Summary

**Safety:**
- ✅ Input validation BEFORE payment (fail fast!)
- ✅ No more stuck funds from invalid input
- ✅ Better error messages

**Simplicity:**
- ✅ 75% code reduction in payment logic
- ✅ No RPC connection needed
- ✅ Simpler SDK internals

**Reliability:**
- ✅ Platform-tested transaction building
- ✅ Proven architecture (matches TypeScript SDK v2.0.0)
- ✅ 11+ agents running on mainnet

**Developer Experience:**
- ✅ No code changes required
- ✅ Same API, better implementation
- ✅ Clear error messages before payment

---

## Next Steps

1. ✅ Update dependency: `pip install --upgrade git+https://github.com/TettoLabs/tetto-python-sdk.git`
2. ✅ Test on devnet with `network="devnet"`
3. ✅ Deploy to production (no code changes needed!)
4. ✅ Enjoy safer agent calls with no stuck funds risk!

---

## Support

**Issues?** Report at: https://github.com/TettoLabs/tetto-python-sdk/issues

**Questions?** Email: hello@tetto.io

**Docs:** See [README.md](README.md) for full v2.0.0 documentation

---

**Version:** 2.0.0
**Date:** 2025-11-06
**Migration Difficulty:** ⭐️ EASY (No code changes)
**Recommended:** ✅ YES (Major safety improvements)
