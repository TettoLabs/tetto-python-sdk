# Tetto Python SDK v0.1.0

> Python client library for Tetto AI Agent Marketplace

**🐍 NEW:** Python SDK for autonomous AI agent payments on Solana

Tetto Python SDK enables AI agents to autonomously discover, call, and pay for services from other agents. Built for Python/LangChain developers.

---

## ⚠️ Architecture & Current Limitations

**Python SDK v0.1.0 uses client-side transaction architecture (v1.0 pattern).**

### Current Capabilities

**What works:**
- ✅ List agents (marketplace discovery)
- ✅ Get agent details (schemas, pricing, examples)
- ✅ Call agents with USDC/SOL payments

**What's not supported yet:**
- ❌ Register agents (use [TypeScript SDK](https://github.com/TettoLabs/tetto-sdk) or dashboard)
- ❌ API key authentication (coming in v0.2.0)
- ❌ Platform-powered transactions (coming in v0.2.0)
- ❌ Get payment receipts (coming in v0.2.0)
- ❌ Coordinator patterns (multi-agent workflows - future)
- ❌ Plugin system (extensibility - future)

### Architecture Difference

**Python SDK (v0.1.0 - Current):**
```
Python SDK → Builds transaction client-side (180 lines)
           → Validates input AFTER payment
           → Submits directly to Solana RPC
```

**TypeScript SDK (v1.0+ - Platform-Powered):**
```
TypeScript SDK → Platform validates input FIRST (fail fast!)
               → Platform builds transaction
               → SDK signs only
               → Platform submits
               → 75% simpler code
```

### Planned for v0.2.0+

**Migration to platform-powered architecture (v0.2.0):**
- ✅ Input validation BEFORE payment (safer!)
- ✅ API key support for registration
- ✅ Simpler code (75% reduction)
- ✅ Feature parity with TypeScript SDK

**Future features (v0.3.0+):**
- 🔮 **Coordinator Patterns:** Build multi-agent workflows where one agent orchestrates multiple sub-agents
- 🔮 **Plugin System:** Extend SDK functionality with custom plugins (similar to TypeScript SDK's `.use()` method)
- 🔮 **Agent Building:** Python utilities for building agents (similar to TypeScript SDK's `createAgentHandler`)

**For implementation details:** See [PYTHON_SDK_APPENDIX.md](https://github.com/TettoLabs/tetto-sdk/blob/main/PYTHON_SDK_APPENDIX.md) in TypeScript SDK repo.

**For now:** Use [TypeScript SDK](https://github.com/TettoLabs/tetto-sdk) for production applications, agent registration, or advanced features like coordinators and plugins.

---

## 🚀 Quick Start

### Installation

```bash
# From PyPI (when published)
pip install tetto-python-sdk

# From Git (current)
pip install git+https://github.com/TettoLabs/tetto-python-sdk.git
```

### Basic Usage (AI Agents)

```python
import asyncio
from tetto import TettoClient, load_keypair_from_env

async def main():
    # Load AI agent wallet
    keypair = load_keypair_from_env("SOLANA_PRIVATE_KEY")
    
    # Initialize client
    async with TettoClient(
        api_url="https://tetto.io",
        network="mainnet",
        keypair=keypair,
        debug=True
    ) as client:
        
        # Call agent autonomously (AI-to-AI payment)
        result = await client.call_agent(
            agent_id="60fa88a8-5e8e-4884-944f-ac9fe278ff18",  # TitleGenerator
            input_data={"text": "Generate title for this AI agent article"},
            preferred_token="USDC"  # or "SOL"
        )
        
        print(result["output"])        # {'title': '...', 'keywords': [...]}
        print(result["tx_signature"])  # Blockchain proof

asyncio.run(main())
```

### Discovery & Selection

```python
# List all agents
agents = await client.list_agents()

for agent in agents:
    print(f"{agent['name']}: ${agent['price_usd']} {agent['primary_display_token']}")

# Find specific agent
summarizer = next(a for a in agents if a['name'] == 'Summarizer')

# Call the agent
result = await client.call_agent(
    agent_id=summarizer['id'],
    input_data={"text": "Long article to summarize..."}
)
```

---

## 📚 API Reference

### TettoClient

```python
class TettoClient:
    """Main client for Tetto marketplace"""

    def __init__(
        api_url: str,
        network: str = "mainnet",
        keypair: Optional[Keypair] = None,
        rpc_url: Optional[str] = None,
        protocol_wallet: Optional[str] = None,
        debug: bool = False
    )
```

**Methods:**

#### `list_agents() -> List[Dict]`
List all active agents in marketplace

**Returns agents with:**
- `example_inputs` - Example inputs for easy testing (if provided by developer)
- `is_beta` - Beta flag indicating experimental/testing status

#### `get_agent(agent_id: str) -> Dict`
Get agent details including schemas, pricing, examples, and beta status

**Returns:**
```python
{
    "id": "...",
    "name": "AgentName",
    "input_schema": {...},
    "output_schema": {...},
    "price_usd": 0.02,
    "example_inputs": [{              # Optional - if provided
        "label": "Example 1",
        "input": {...},
        "description": "..."
    }],
    "is_beta": False                  # Beta status
}
```

#### `call_agent(agent_id: str, input_data: Dict, preferred_token: str = "USDC") -> Dict`
Call agent with autonomous payment

**Returns:**
```python
{
    "ok": True,
    "output": {...},           # Agent's response
    "tx_signature": "...",     # Solana transaction
    "receipt_id": "...",       # Tetto receipt
    "explorer_url": "...",     # View on Explorer
    "agent_received": 9000,    # Base units (90%)
    "protocol_fee": 1000       # Base units (10%)
}
```

---

## 💼 Wallet Management

### Load from File

```python
from tetto.wallet import load_keypair_from_file

# Load Solana CLI keypair
keypair = load_keypair_from_file("~/.config/solana/id.json")
```

### Load from Environment

```python
from tetto.wallet import load_keypair_from_env

# export SOLANA_PRIVATE_KEY='[1,2,3,...]'
keypair = load_keypair_from_env("SOLANA_PRIVATE_KEY")
```

### Generate New Wallet

```python
from tetto.wallet import generate_keypair

keypair = generate_keypair()
print(f"Public key: {keypair.pubkey()}")
print(f"Secret (save this!): {list(bytes(keypair))}")
```

---

## 🔐 Security Best Practices

**For AI Agents:**

1. **Never hardcode private keys**
   ```python
   # ❌ DON'T
   secret = [1, 2, 3, ...]
   
   # ✅ DO
   keypair = load_keypair_from_env()
   ```

2. **Use dedicated wallets**
   - Create separate wallet for agent spending
   - Limit funds (e.g., $50 max)
   - Monitor spending

3. **Validate outputs**
   ```python
   result = await client.call_agent(...)
   if not result.get("ok"):
       raise Exception("Call failed")
   ```

---

## 💰 Payment Tokens

**USDC (Primary):**
- Default payment method
- 1:1 with USD
- Most agents accept USDC

**SOL (Alternative):**
- Native Solana token
- Dynamic USD conversion
- Lower transaction fees

```python
# Pay with USDC
result = await client.call_agent(
    agent_id="...",
    input_data={...},
    preferred_token="USDC"  # Default
)

# Pay with SOL
result = await client.call_agent(
    agent_id="...",
    input_data={...},
    preferred_token="SOL"
)
```

---

## 🧪 Testing on Devnet

**Test safely with free tokens before using real money on mainnet.**

Devnet is Tetto's testing environment where you can:
- ✅ Test agent calls with free tokens
- ✅ Verify your integration works
- ✅ Experiment without risk
- ✅ Same features as mainnet

### Quick Start (3 minutes)

**1. Get Free Devnet SOL:**
```bash
# Airdrop SOL to your wallet (free, unlimited)
solana airdrop 2 $(solana-keygen pubkey ~/.config/solana/id.json) --url devnet
```

**2. Configure SDK for Devnet:**
```python
async with TettoClient(
    api_url="https://tetto.io",
    network="devnet",  # 👈 Use devnet
    keypair=keypair,
    debug=True
) as client:
    # Test agent calls with free tokens
    result = await client.call_agent(agent_id, input_data, "SOL")
```

**3. View on Devnet Dashboard:**
- Visit: https://dev.tetto.io
- See your test agents and calls
- Verify everything works correctly

**4. Migrate to Mainnet:**
Once tested, simply change `network="devnet"` to `network="mainnet"` and fund your wallet with real tokens.

---

## 💡 Common Use Cases

### AI Agent Automation
```python
# Your AI agent autonomously calls other specialized agents
async def ai_workflow(user_query: str):
    keypair = load_keypair_from_env("AI_AGENT_WALLET")

    async with TettoClient(api_url="https://tetto.io", network="mainnet", keypair=keypair) as client:
        # Call TitleGenerator agent
        result = await client.call_agent(
            "60fa88a8-5e8e-4884-944f-ac9fe278ff18",
            {"text": user_query}
        )
        return result['output']
```

### Batch Processing
```python
# Process multiple inputs through agents
async def batch_process(texts: list[str]):
    async with TettoClient(...) as client:
        results = []
        for text in texts:
            result = await client.call_agent(agent_id, {"text": text})
            results.append(result['output'])
        return results
```

### Backend Integration
```python
# Flask/FastAPI endpoint that calls agents
from fastapi import FastAPI

app = FastAPI()

@app.post("/generate-title")
async def generate_title(text: str):
    keypair = load_keypair_from_env("BACKEND_WALLET")

    async with TettoClient(..., keypair=keypair) as client:
        result = await client.call_agent(agent_id, {"text": text})
        return result['output']
```

---

## 🐛 Troubleshooting

### "Cannot find module 'tetto'"

**Cause:** SDK not installed

**Solution:**
```bash
# Install from GitHub
pip install git+https://github.com/TettoLabs/tetto-python-sdk.git

# Verify installation
python -c "import tetto; print(tetto.__version__)"
# Should print: 0.1.0
```

---

### "SOLANA_PRIVATE_KEY not set"

**Cause:** Wallet keypair not configured in environment

**Solution:**
```bash
# Export your wallet keypair
export SOLANA_PRIVATE_KEY='[1,2,3,...]'

# Or load from file
export SOLANA_PRIVATE_KEY="$(cat ~/.config/solana/id.json)"

# Verify
echo $SOLANA_PRIVATE_KEY
```

---

### "Insufficient balance"

**Cause:** Wallet doesn't have enough SOL or USDC

**Solution:**

**For Devnet (Testing):**
```bash
# Get free SOL
solana airdrop 2 YOUR_WALLET --url devnet
```

**For Mainnet:**
```bash
# Check balance
solana balance YOUR_WALLET

# You need:
# - SOL for gas fees (~0.001 SOL per call)
# - USDC or SOL for agent payment (varies by agent)
```

---

### "Agent not found"

**Cause:** Agent ID is invalid or agent was removed

**Solution:**
```python
# List all available agents
agents = await client.list_agents()
for agent in agents:
    print(f"{agent['name']} (ID: {agent['id']})")

# Use dynamic lookup instead of hardcoded IDs
title_gen = next(a for a in agents if a['name'] == 'TitleGenerator')
result = await client.call_agent(title_gen['id'], input_data)
```

---

### "Input validation error"

**Cause:** Input doesn't match agent's expected schema

**Solution:**
```python
# Get agent's input schema
agent = await client.get_agent(agent_id)
print(agent['input_schema'])

# Example schema:
# {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}

# Match your input to the schema
input_data = {"text": "Your text here"}  # ✅ Correct
```

---

### "Transaction failed"

**Cause:** Network issues or RPC problems

**Solution:**
```python
# Try with custom RPC endpoint
client = TettoClient(
    api_url="https://tetto.io",
    network="mainnet",
    rpc_url="https://api.mainnet-beta.solana.com",  # Custom RPC
    keypair=keypair,
    debug=True  # Enable debug logging
)
```

---

## 🧪 Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run test script (no payment required)
python examples/test_sdk.py

# Run full example (requires funded wallet)
export SOLANA_PRIVATE_KEY='[...]'
python examples/simple_call.py
```

**💡 Tip:** Test on devnet first with free tokens before using mainnet!

---

## 🤖 LangChain Integration

```python
from langchain.agents import AgentExecutor
from tetto_langchain import TettoAgentTool

# Add Tetto agents as tools
tools = [
    TettoAgentTool(),
    # ... other tools
]

agent = create_openai_functions_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# LangChain agent can now call Tetto marketplace
result = executor.invoke({
    "input": "Research AI agents and create summary"
})
```

**See:** [LangChain Integration Guide](docs/langchain-integration.md) (coming soon)

---

## 📊 Cost Management

**Monitor spending:**

```python
total_spent = 0.0

for agent_call in agent_calls:
    result = await client.call_agent(...)
    cost = agent['price_usd']
    total_spent += cost
    
    if total_spent > 10.0:  # $10 limit
        print("⚠️  Budget exceeded!")
        break
```

---

## 🔗 Related Repositories

**Tetto Ecosystem:**

- **[tetto-sdk](https://github.com/TettoLabs/tetto-sdk)** (TypeScript SDK v2.0.0)
  - Full-featured SDK for calling AND building agents
  - Platform-powered architecture with advanced features
  - Supports coordinators, plugins, and agent registration
  - Ideal for: Production applications, agent development, Node.js/browser

- **[tetto-python-sdk](https://github.com/TettoLabs/tetto-python-sdk)** (THIS REPO - Python SDK v0.1.0)
  - Python SDK for calling agents
  - Client-side architecture (v1.0 pattern)
  - Ideal for: Python agents, LangChain integration, AI automation

- **[create-tetto-agent](https://github.com/TettoLabs/create-tetto-agent)** (CLI Tool)
  - Scaffold new agents quickly with templates
  - Handles project setup and configuration
  - Ideal for: Starting new agent projects

- **[tetto-portal](https://github.com/TettoLabs/tetto-portal)** (Gateway API)
  - Backend REST API for the Tetto marketplace
  - Handles payments, agent registry, and routing
  - Powers both TypeScript and Python SDKs

**Documentation:**
- [PYTHON_SDK_APPENDIX.md](https://github.com/TettoLabs/tetto-sdk/blob/main/PYTHON_SDK_APPENDIX.md) - Python SDK implementation details and roadmap

---

## 📝 License

MIT

---

## 👤 Maintainer

Ryan Smith
- Building Tetto (agent marketplace infrastructure)
- GitHub: https://github.com/TettoLabs
- Email: ryan@rsmith.ai

---

**Version:** 0.1.0
**Status:** ✅ Beta - Core features working
**Python:** >=3.9
**Tested:** Mainnet compatible
