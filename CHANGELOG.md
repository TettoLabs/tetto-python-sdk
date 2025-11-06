# Changelog

All notable changes to the Tetto Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-11-06

### 🎉 Major Release - Platform-Powered Architecture

This release brings the Python SDK to feature parity with TypeScript SDK v2.0.0, implementing the platform-powered architecture that validates input BEFORE payment, eliminating the risk of stuck funds from invalid input.

### ⚠️ Breaking Changes

**Removed:**
- ❌ `tetto/transactions.py` - Deleted 184 lines of dangerous client-side transaction code
  - This file caused stuck funds risk by validating input AFTER payment
  - Platform now builds all transactions (safer!)

**No API Changes:**
- ✅ Public API remains unchanged (`call_agent()` signature identical)
- ✅ Existing code continues to work with v2.0.0
- ✅ Only internal implementation changed

### 🚀 New Features

**Platform-Powered Transactions:**
- ✅ Input validation BEFORE payment (fail-fast pattern)
- ✅ Platform builds unsigned transactions
- ✅ SDK only signs transactions (~40 lines vs 180 lines)
- ✅ Platform submits transactions to blockchain
- ✅ 75% code reduction in payment logic

**Safety Improvements:**
- ✅ No more stuck funds from invalid input
- ✅ Errors discovered immediately (before payment)
- ✅ Better error messages from platform validation
- ✅ More reliable transaction processing

**Architecture Changes:**
- ✅ 2-step transaction flow:
  1. POST `/api/agents/{id}/build-transaction` (validates input, returns unsigned tx)
  2. SDK signs transaction with `VersionedTransaction`
  3. POST `/api/agents/call` (submit signed tx)
- ✅ No RPC connection needed (platform handles everything)
- ✅ Simpler codebase (easier to maintain)

### 📝 Changed

**Updated Files:**
- `tetto/client.py`: Completely rewrote `call_agent()` method for v2.0 architecture
- `tetto/__init__.py`: Updated version to 2.0.0
- `setup.py`: Updated version to 2.0.0
- `README.md`: Comprehensive v2.0.0 documentation with safety benefits
- `AI_LOOK_HERE.md`: Updated for platform-powered architecture
- `CHANGELOG.md`: Added v2.0.0 release notes (this file)

**New Files:**
- `MIGRATION_v1_to_v2.md`: Migration guide from v0.1.0 to v2.0.0
- `V2_UPGRADE_PLAN.md`: Implementation plan and technical details

### 🔄 Migration from v0.1.0

**Good News:** No code changes required! The public API is unchanged.

```python
# v0.1.0 (Old) - Client builds transaction
result = await client.call_agent(agent_id, input_data, "USDC")

# v2.0.0 (New) - Platform builds transaction (same API!)
result = await client.call_agent(agent_id, input_data, "USDC")
# Now with input validation BEFORE payment!
```

**What Changed Under the Hood:**
- v0.1.0: Client built transaction → validated input → sent to RPC (DANGEROUS!)
- v2.0.0: Platform validates input → builds transaction → SDK signs → Platform submits (SAFE!)

**See:** [MIGRATION_v1_to_v2.md](MIGRATION_v1_to_v2.md) for detailed migration guide

### 🎯 Feature Parity with TypeScript SDK

**Matching TypeScript SDK v2.0.0:**
- ✅ Platform-powered architecture
- ✅ 2-step transaction flow
- ✅ Input validation before payment
- ✅ Same safety guarantees
- ✅ Feature parity for calling agents

**Not Yet Implemented (Python-specific roadmap):**
- ❌ Agent registration (coming in future version)
- ❌ Coordinator patterns (coming in future version)
- ❌ Plugin system (coming in future version)

### 📊 Statistics

**Code Reduction:**
- Deleted: 184 lines (dangerous transaction building code)
- Added: ~40 lines (transaction signing code)
- **Net reduction: 75%** in payment logic complexity

**Safety Improvement:**
- v0.1.0: Input validation AFTER payment → stuck funds risk
- v2.0.0: Input validation BEFORE payment → fail fast, no stuck funds!

### 🔗 Related Changes

**TypeScript SDK:**
- Python SDK v2.0.0 now matches TypeScript SDK v2.0.0 architecture
- Both SDKs use identical platform-powered flow
- Both SDKs have same safety guarantees

**Platform API:**
- New endpoint: POST `/api/agents/{id}/build-transaction`
- Updated endpoint: POST `/api/agents/call` (now accepts payment_intent_id)
- Platform handles all transaction building and submission

### 📚 Documentation

**Updated:**
- README.md: Comprehensive v2.0.0 guide with safety benefits
- AI_LOOK_HERE.md: Platform-powered architecture documentation
- Examples: Updated comments to reflect v2.0 flow

**New:**
- MIGRATION_v1_to_v2.md: Step-by-step migration guide
- V2_UPGRADE_PLAN.md: Technical implementation details

### 🙏 Acknowledgments

This release follows the SDK Maintenance Manifesto principles:
- "Research first, change second"
- "Slow and methodical beats fast and sloppy"
- "Version numbers matter - use semantic versioning"

Special thanks to the TypeScript SDK v2.0.0 for providing the proven architecture patterns.

---

## [0.1.0] - 2025-10-14

### Added

**Core Functionality:**
- Initial release of Python SDK for calling Tetto agents
- `TettoClient` class with async/await support
- Agent discovery methods (`list_agents()`, `get_agent()`)
- Agent calling with autonomous payments (`call_agent()`)
- Support for USDC and SOL payment tokens
- Async context manager support for clean resource management

**Wallet Management:**
- `load_keypair_from_file()` - Load Solana CLI format keypairs
- `load_keypair_from_env()` - Load from environment variables
- `generate_keypair()` - Generate new random keypairs

**Transaction Building:**
- Client-side transaction building for USDC (SPL Token)
- Client-side transaction building for SOL (System Program)
- Automatic 90/10 fee splitting (agent/protocol)
- Associated Token Account (ATA) derivation for USDC
- Transaction confirmation and receipt handling

**Network Support:**
- Mainnet configuration with production endpoints
- Devnet configuration for testing with free tokens
- Custom RPC URL support
- Custom protocol wallet support (for testing)

**Developer Experience:**
- Debug logging mode for troubleshooting
- Comprehensive error handling
- Type hints throughout codebase
- Example scripts (`simple_call.py`, `test_sdk.py`)

**Documentation:**
- Comprehensive README with quickstart guide
- Architecture documentation in AI_LOOK_HERE.md
- Security best practices
- Payment token guide (USDC vs SOL)
- Example usage patterns

### Technical Details

**Architecture:**
- Client-side transaction architecture (v1.0 pattern)
- Direct Solana RPC submission
- Input validation after payment (current limitation)

**Dependencies:**
- Python >=3.9
- solana >=0.34.0
- solders >=0.21.0
- httpx >=0.25.0
- pydantic >=2.0.0

**Known Limitations:**
- No agent registration (use TypeScript SDK or dashboard)
- No API key authentication support
- No platform-powered transactions
- No payment receipt retrieval
- Input validation occurs after payment (pre-v2.0 pattern)

### Notes

This is the initial foundation release. The Python SDK is designed for **calling agents only** - agent building is handled by the TypeScript SDK. Future versions will add platform-powered architecture and additional features.

---

## [Unreleased]

### Planned for Future Versions (v2.1.0+)

**Coordinator Patterns:**
- Multi-agent workflow orchestration
- Context passing between agents
- Identity preservation in sub-calls

**Plugin System:**
- Extensibility through plugins
- Custom functionality injection
- Similar to TypeScript SDK's `.use()` method

**Agent Building:**
- Python utilities for building agents
- Handler creation (similar to `createAgentHandler` in TypeScript)
- Input/output validation helpers
- Revenue tracking utilities

---

## Version History

- **v2.0.0** (2025-11-06) - Platform-powered architecture (CURRENT)
- **v0.1.0** (2025-10-14) - Initial release, calling-only SDK
- **v2.1.0+** (Planned) - Advanced features (coordinators, plugins, agent registration)

---

## Migration Guides

### v0.1.0 → v2.0.0 (Released 2025-11-06)

**Good News:** No code changes required! The public API is unchanged.

**Transaction Building:**
```python
# v0.1.0 (Old) - Client builds transaction
result = await client.call_agent(agent_id, input_data, "USDC")

# v2.0.0 (New) - Platform builds transaction (same API!)
result = await client.call_agent(agent_id, input_data, "USDC")
# Now with input validation BEFORE payment!
```

**What Changed Under the Hood:**
- v0.1.0: Client built transaction → validated input → sent to RPC (DANGEROUS!)
- v2.0.0: Platform validates input → builds transaction → SDK signs → Platform submits (SAFE!)

**Key Benefits:**
- Input validation before payment (fail-fast pattern)
- Simpler SDK codebase (removed transactions.py)
- Better error messages
- Faster processing
- No stuck funds risk

**See:** [MIGRATION_v1_to_v2.md](MIGRATION_v1_to_v2.md) for detailed migration guide

---

## Links

- **Repository:** https://github.com/TettoLabs/tetto-python-sdk
- **TypeScript SDK:** https://github.com/TettoLabs/tetto-sdk
- **Documentation:** [README.md](README.md)
- **Implementation Guide:** [AI_LOOK_HERE.md](AI_LOOK_HERE.md)
- **Marketplace:** https://tetto.io

---

**Maintained by:** Tetto Labs
**License:** MIT
**Python:** >=3.9
