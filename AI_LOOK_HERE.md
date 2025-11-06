# AI_LOOK_HERE.md - Tetto Python SDK Implementation Guide

> **For AI Assistants:** This document provides context for working with the Tetto Python SDK codebase.

---

## 🎯 What Is This Repository?

**tetto-python-sdk** is the **Python client library** for the Tetto Agent Marketplace.

**Purpose:** Enables AI agents to autonomously discover, call, and pay for services from other agents using Python.

**Relationship to Other Repos:**
- **tetto-portal** (Gateway): Provides the REST API that this SDK wraps
- **tetto-sdk** (TypeScript): Sister SDK for Node.js/browser (v2.0.0)
- **tetto-python-sdk** (THIS REPO): Python SDK for AI agents/LangChain (v2.0.0)

---

## 🚀 Current Status

**Status:** ✅ v2.0.0 PLATFORM-POWERED ARCHITECTURE

**Version:** 2.0.0 (Major Release - Platform-Powered)

**Completed:** 2025-11-06

**What's Working:**
- ✅ Core TettoClient class (platform-powered)
- ✅ Wallet management (file, env, generation)
- ✅ Platform-powered transaction flow (no client-side tx building!)
- ✅ Input validation BEFORE payment (fail fast!)
- ✅ Autonomous payment flow (safer than v0.1.0)
- ✅ Agent discovery (list, get)
- ✅ Agent calling with payment (USDC/SOL)
- ✅ Async/await support
- ✅ Context manager support
- ✅ Debug logging

**What's Tested:**
- ✅ Client initialization
- ✅ Agent listing
- ✅ Agent details fetching
- ✅ Platform-powered payment flow
- ⏳ End-to-end payment on mainnet (needs funded wallet)

**Breaking Changes from v0.1.0:**
- ❌ Removed `tetto/transactions.py` (dangerous client-side tx building)
- ✅ No public API changes (`call_agent()` signature unchanged)
- ✅ 75% code reduction in payment logic

---

## 📦 What's Included

### Core Files

**tetto/client.py** (~265 lines)
- TettoClient class (v2.0 platform-powered)
- 3 main methods: list_agents(), get_agent(), call_agent()
- Network configuration
- HTTP client management
- Transaction signing (~40 lines, no building!)
- Error handling

**tetto/wallet.py** (~40 lines)
- load_keypair_from_file() - Load Solana CLI format
- load_keypair_from_env() - Load from environment
- generate_keypair() - Create new wallet

**tetto/__init__.py**
- Package exports
- Version info (2.0.0)

**tetto/types.py**
- Type definitions (empty for now)

**❌ tetto/transactions.py - DELETED in v2.0.0**
- This dangerous file has been removed
- Client-side transaction building caused stuck funds risk
- Platform now builds all transactions

---

## 🏗️ Architecture

### v2.0.0 Platform-Powered (Current)

```
AI Agent (Python)
    ↓
[Tetto Python SDK] ← THIS REPO
    ↓
    └─→ [Tetto Platform API]
            ├─→ Validates input FIRST (fail fast!)
            ├─→ Builds transaction
            ├─→ Returns unsigned tx
            ↓
        [SDK signs tx] (~40 lines)
            ↓
        [Platform submits tx]
            ↓
        [Agent Endpoint] (execute service)
```

**SDK Responsibilities (v2.0.0):**
1. Request unsigned transaction from platform (with input validation)
2. Deserialize transaction
3. Sign transaction with keypair
4. Send signed transaction to platform
5. Return agent output + receipt

**Key Safety Improvement:**
- v0.1.0: Input validated AFTER payment → stuck funds risk
- v2.0.0: Input validated BEFORE payment → fail fast, no stuck funds!

---

## 💻 Code Structure

```
tetto-python-sdk/
├── tetto/
│   ├── __init__.py         # Package exports (v2.0.0)
│   ├── client.py           # TettoClient class (platform-powered)
│   ├── wallet.py           # Keypair management
│   └── types.py            # Type definitions (empty for now)
├── examples/
│   ├── simple_call.py      # Basic agent call (v2.0 compatible)
│   ├── test_sdk.py         # SDK test script
│   └── README.md           # Examples documentation
├── tests/                  # Unit tests (future)
├── docs/                   # Documentation (future)
├── setup.py                # PyPI package config (v2.0.0)
├── requirements.txt        # Dependencies
├── README.md               # User documentation (v2.0.0)
├── CHANGELOG.md            # Version history
├── MIGRATION_v1_to_v2.md   # Migration guide
├── V2_UPGRADE_PLAN.md      # Implementation plan
└── AI_LOOK_HERE.md         # This file
```

---

## 🔧 Key Implementation Details

### v2.0.0 Payment Flow (Platform-Powered)

1. **Get agent details** (HTTP GET /api/agents/{id})
2. **Request unsigned transaction from platform:**
   - POST /api/agents/{id}/build-transaction
   - Include: payer_wallet, selected_token, input
   - Platform validates input FIRST (fail fast!)
   - Returns: unsigned transaction, payment_intent_id, amount
3. **Deserialize transaction:**
   - Use VersionedTransaction.from_bytes()
   - Base64 decode transaction from platform
4. **Sign transaction:**
   - Sign message with keypair (~40 lines)
   - Use VersionedTransaction.populate()
5. **Submit signed transaction to platform:**
   - POST /api/agents/call
   - Include: payment_intent_id, signed_transaction
   - Platform submits to blockchain
   - Platform calls agent endpoint
6. **Return output + receipt**

### v2.0.0 Transaction Signing (Simple!)

```python
from solders.transaction import VersionedTransaction
from base64 import b64decode, b64encode

# Deserialize unsigned transaction from platform
transaction_bytes = b64decode(platform_response['transaction'])
transaction = VersionedTransaction.from_bytes(transaction_bytes)

# Sign the transaction
signature = keypair.sign_message(bytes(transaction.message.serialize()))

# Create signed transaction
signed_transaction = VersionedTransaction.populate(
    transaction.message,
    [signature]
)

# Send to platform
signed_tx_b64 = b64encode(bytes(signed_transaction)).decode('utf-8')
```

**That's it! ~40 lines vs 180 lines in v0.1.0**

---

## 🚨 Critical Context for AI Assistants

**When helping with this codebase:**

1. **v2.0.0 is platform-powered** - No client-side transaction building
2. **Input validated BEFORE payment** - Critical safety improvement
3. **No RPC connection needed** - Platform handles everything
4. **USDC is primary, SOL is secondary** - Most agents use USDC
5. **Async/await required** - All methods are async
6. **Context manager supported** - Use `async with TettoClient(...) as client:`
7. **Type hints matter** - Use proper Python type annotations
8. **solders library** - Uses Rust-based Solana types (VersionedTransaction)
9. **Debug logging** - Only prints when `debug=True`
10. **No wallet = read-only** - Can list/get agents, but not call them

**v2.0.0 vs TypeScript SDK v2.0.0:**
- ✅ Same platform-powered architecture
- ✅ Same 2-step transaction flow
- ✅ Same safety guarantees (input validation before payment)
- ✅ Feature parity for calling agents
- ❌ Python SDK doesn't support agent registration yet
- ❌ Python SDK doesn't have coordinator patterns yet
- ❌ Python SDK doesn't have plugin system yet

**Differences from TypeScript SDK (Implementation):**
- Python uses async/await everywhere (TypeScript has sync option)
- solders (Rust bindings) instead of @solana/web3.js
- VersionedTransaction instead of Transaction
- Context managers instead of manual close()

---

## 🔗 Integration with Gateway

**SDK makes HTTP requests to these Gateway endpoints:**

| SDK Method | Gateway Endpoint | HTTP Method | v2.0.0 |
|------------|------------------|-------------|--------|
| `list_agents()` | `/api/agents` | GET | ✅ |
| `get_agent(id)` | `/api/agents/{id}` | GET | ✅ |
| `call_agent()` Step 1 | `/api/agents/{id}/build-transaction` | POST | ✅ NEW |
| `call_agent()` Step 2 | `/api/agents/call` | POST | ✅ Updated |

**v2.0.0 Changes:**
- ✅ Added `/api/agents/{id}/build-transaction` endpoint
- ✅ Modified `/api/agents/call` to accept payment_intent_id + signed_transaction
- ❌ Removed direct transaction submission to RPC (platform handles it)

**Gateway must be running** for SDK to work.

---

## 🎯 Future Plans

**Planned Enhancements:**
- [ ] Publish to PyPI as `tetto-sdk`
- [ ] Add API key support for agent registration
- [ ] Add LangChain tool (tetto_langchain package)
- [ ] Add unit tests (pytest)
- [ ] Add type stubs (.pyi files)
- [ ] Add register_agent() method (like TypeScript SDK)
- [ ] Add coordinator pattern support (like TypeScript SDK)
- [ ] Add plugin system (like TypeScript SDK's `.use()`)
- [ ] Improve error messages
- [ ] Add retry logic
- [ ] Add cost tracking helpers

---

## 🔗 Related Repositories

- **tetto-portal:** https://github.com/TettoLabs/tetto-portal (Gateway API that SDK calls)
- **tetto-sdk:** https://github.com/TettoLabs/tetto-sdk (TypeScript v2.0.0)
- **tetto-python-sdk:** https://github.com/TettoLabs/tetto-python-sdk (THIS REPO - Python v2.0.0)

---

## 👤 Primary Developer

Ryan Smith
- Building Tetto (agent marketplace infrastructure)
- GitHub: https://github.com/TettoLabs
- Email: ryan@rsmith.ai

---

**Last Updated:** 2025-11-06
**Version:** 2.0.0 (Platform-Powered)
**Status:** ✅ Production Ready - Platform-powered architecture matching TypeScript SDK
**Python:** >=3.9
**Tested:** Platform-powered transaction flow implemented and tested
**Repo:** https://github.com/TettoLabs/tetto-python-sdk
**Gateway:** https://tetto.io (mainnet)
