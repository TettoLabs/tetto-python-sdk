# AI_LOOK_HERE.md - Tetto Python SDK Implementation Guide

> **For AI Assistants:** This document provides context for working with the Tetto Python SDK codebase.

---

## 🎯 What Is This Repository?

**tetto-python-sdk** is the **Python client library** for the Tetto Agent Marketplace.

**Purpose:** Enables AI agents to autonomously discover, call, and pay for services from other agents using Python.

**Relationship to Other Repos:**
- **tetto-portal** (Gateway): Provides the REST API that this SDK wraps
- **tetto-sdk** (TypeScript): Sister SDK for Node.js/browser
- **tetto-python-sdk** (THIS REPO): Python SDK for AI agents/LangChain

---

## 🚀 Current Status

**Status:** ✅ v0.1.0 FOUNDATION COMPLETE

**Version:** 0.1.0 (Initial Release)

**Completed:** 2025-10-14

**What's Working:**
- ✅ Core TettoClient class implemented
- ✅ Wallet management (file, env, generation)
- ✅ Transaction building for USDC and SOL
- ✅ Autonomous payment flow
- ✅ Agent discovery (list, get)
- ✅ Agent calling with payment
- ✅ Async/await support
- ✅ Context manager support
- ✅ Debug logging

**What's Tested:**
- ✅ Client initialization
- ✅ Agent listing
- ✅ Agent details fetching
- ⏳ End-to-end payment (needs funded wallet)

---

## 📦 What's Included

### Core Files

**tetto/client.py** (~210 lines)
- TettoClient class
- 3 main methods: list_agents(), get_agent(), call_agent()
- Network configuration
- HTTP client management
- Error handling

**tetto/wallet.py** (~40 lines)
- load_keypair_from_file() - Load Solana CLI format
- load_keypair_from_env() - Load from environment
- generate_keypair() - Create new wallet

**tetto/transactions.py** (~180 lines)
- build_and_send_payment() - Main payment function
- USDC transfers (SPL Token program)
- SOL transfers (System program)
- Fee calculation (90/10 split)
- ATA derivation
- Transaction confirmation

**tetto/__init__.py**
- Package exports
- Version info

---

## 🏗️ Architecture

```
AI Agent (Python)
    ↓
[Tetto Python SDK] ← THIS REPO
    ↓
    ├─→ [Solana RPC] (build & send payment tx)
    └─→ [Tetto API] (call agent with tx proof)
            ↓
        [Agent Endpoint] (execute service)
```

**SDK Responsibilities:**
1. Build Solana payment transaction
2. Sign with AI agent's keypair
3. Send transaction to blockchain
4. Call Tetto API with transaction proof
5. Return agent output + receipt

---

## 💻 Code Structure

```
tetto-python-sdk/
├── tetto/
│   ├── __init__.py         # Package exports
│   ├── client.py           # TettoClient class
│   ├── wallet.py           # Keypair management
│   ├── transactions.py     # Payment building
│   └── types.py            # Type definitions (empty for now)
├── examples/
│   ├── simple_call.py      # Basic agent call
│   └── test_sdk.py         # SDK test script
├── tests/                  # Unit tests (future)
├── docs/                   # Documentation (future)
├── setup.py                # PyPI package config
├── requirements.txt        # Dependencies
├── README.md               # User documentation
└── AI_LOOK_HERE.md         # This file
```

---

## 🔧 Key Implementation Details

### Payment Flow

1. **Get agent details** (HTTP GET /api/agents/{id})
2. **Build payment transaction:**
   - USDC: SPL Token TransferChecked instructions
   - SOL: System Transfer instructions
3. **Sign with keypair** (autonomous)
4. **Send to Solana** (RPC sendTransaction)
5. **Confirm transaction** (wait for finality)
6. **Call Tetto API** (POST /api/agents/call with tx_signature)
7. **Return output + receipt**

### USDC Implementation

```python
# Derive ATAs (Associated Token Accounts)
payer_ata = get_associated_token_address(payer, usdc_mint)
agent_ata = get_associated_token_address(agent_wallet, usdc_mint)
protocol_ata = get_associated_token_address(protocol_wallet, usdc_mint)

# Build TransferChecked instructions
# Instruction discriminator: 12
# Data: [12, amount (u64), decimals (u8)]
```

### SOL Implementation

```python
# Simple system transfers
transfer(from=payer, to=agent, lamports=amount)
transfer(from=payer, to=protocol, lamports=fee)
```

---

## 🚨 Critical Context for AI Assistants

**When helping with this codebase:**

1. **USDC is primary, SOL is secondary** - Most agents use USDC
2. **Async/await required** - All methods are async
3. **Context manager supported** - Use `async with TettoClient(...) as client:`
4. **Type hints matter** - Use proper Python type annotations
5. **solders library** - Uses Rust-based Solana types (faster than solana-py alone)
6. **Debug logging** - Only prints when `debug=True`
7. **No wallet = read-only** - Can list/get agents, but not call them
8. **ATAs must exist** - USDC requires associated token accounts
9. **Gas fees in SOL** - Even USDC payments need SOL for gas

**Differences from TypeScript SDK:**
- Python uses async/await everywhere
- solders (Rust bindings) instead of @solana/web3.js
- Different transaction building API
- Context managers instead of manual close()

---

## 🔗 Integration with Gateway

**SDK makes HTTP requests to these Gateway endpoints:**

| SDK Method | Gateway Endpoint | HTTP Method |
|------------|------------------|-------------|
| `list_agents()` | `/api/agents` | GET |
| `get_agent(id)` | `/api/agents/{id}` | GET |
| `call_agent()` | `/api/agents/call` | POST |

**Gateway must be running** for SDK to work.

---

## 🎯 Future Plans

**Planned Enhancements:**
- [ ] Publish to PyPI as `tetto-sdk`
- [ ] Add full USDC support (currently SOL only works reliably)
- [ ] Add LangChain tool (tetto_langchain package)
- [ ] Add unit tests (pytest)
- [ ] Add type stubs (.pyi files)
- [ ] Add register_agent() method
- [ ] Add async context manager tests
- [ ] Improve error messages
- [ ] Add retry logic
- [ ] Add cost tracking helpers

---

## 🔗 Related Repositories

- **tetto-portal:** https://github.com/TettoLabs/tetto-portal (Gateway API that SDK calls)
- **tetto-sdk:** https://github.com/TettoLabs/tetto-sdk (TypeScript version)
- **tetto-python-sdk:** https://github.com/TettoLabs/tetto-python-sdk (THIS REPO)

---

## 👤 Primary Developer

Ryan Smith
- Building Tetto (agent marketplace infrastructure)
- GitHub: https://github.com/TettoLabs
- Email: ryan@rsmith.ai

---

**Last Updated:** 2025-10-14
**Version:** 0.1.0 (Initial Release)
**Status:** ✅ Foundation Complete - Core features working
**Python:** >=3.9
**Tested:** Client + wallet + transactions implemented
**Repo:** https://github.com/TettoLabs/tetto-python-sdk
**Gateway:** https://tetto.io (mainnet)
