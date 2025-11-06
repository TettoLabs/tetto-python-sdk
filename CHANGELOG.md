# Changelog

All notable changes to the Tetto Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Planned for v0.2.0 (Platform-Powered Architecture)

**Breaking Changes:**
- Migration from client-side to platform-powered transactions
- Input validation will occur BEFORE payment (safer!)
- Transaction building moved to platform (75% code reduction)

**New Features:**
- API key authentication for programmatic access
- Agent registration support
- Payment receipt retrieval (`get_receipt()`)
- Simplified transaction code (remove 180-line transactions.py)
- Feature parity with TypeScript SDK v2.0 calling features

**Improvements:**
- Faster transaction processing
- Better error messages with validation before payment
- Reduced SDK bundle size
- Improved reliability through platform handling

**See:** [PYTHON_SDK_APPENDIX.md](https://github.com/TettoLabs/tetto-sdk/blob/main/PYTHON_SDK_APPENDIX.md) for implementation details

---

### Planned for v0.3.0+ (Advanced Features)

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

- **v0.1.0** (2025-10-14) - Initial release, calling-only SDK
- **v0.2.0** (Planned 2025-Q1) - Platform-powered architecture
- **v0.3.0** (Planned 2025-Q2) - Advanced features (coordinators, plugins)

---

## Migration Guides

### v0.1.0 → v0.2.0 (When Released)

**Transaction Building:**
```python
# v0.1.0 (Current) - Client builds transaction
result = await client.call_agent(agent_id, input_data, "USDC")

# v0.2.0 (Future) - Platform builds transaction
# Same API, but platform handles transaction building
result = await client.call_agent(agent_id, input_data, "USDC")
# Input validated FIRST, transaction built by platform
```

**No breaking API changes expected** - the client API will remain the same, but the underlying transaction handling will be improved.

**Key Benefits:**
- Input validation before payment (fail-fast pattern)
- Simpler SDK codebase (remove transactions.py)
- Better error messages
- Faster processing

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
