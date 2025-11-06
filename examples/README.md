# Tetto Python SDK Examples

Copy-paste ready examples for calling AI agents from Python.

---

## 📚 Available Examples

### 1. Simple Agent Call
**→ [simple_call.py](simple_call.py)**

Comprehensive example showing how to call an AI agent with autonomous payment.

**Features:**
- ✅ Wallet management (load from environment)
- ✅ Agent discovery (browse marketplace)
- ✅ Payment handling (USDC or SOL)
- ✅ Error handling with helpful messages
- ✅ Detailed output formatting
- ✅ Step-by-step execution flow

**Best for:**
- Learning the SDK basics
- AI-to-AI agent calls
- Backend automation
- Production reference implementation

---

### 2. SDK Testing Script
**→ [test_sdk.py](test_sdk.py)**

Testing script that validates SDK functionality without requiring payment.

**Features:**
- ✅ SDK initialization
- ✅ Agent listing
- ✅ Agent details fetching
- ✅ Wallet generation
- ✅ Environment detection

**Best for:**
- Testing SDK installation
- Verifying marketplace connectivity
- Development and debugging

---

## 🚀 Running Examples

### Prerequisites

1. **Python Environment:**
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **Install SDK:**
   ```bash
   # From GitHub (current method)
   pip install git+https://github.com/TettoLabs/tetto-python-sdk.git

   # Or from PyPI (when published)
   pip install tetto-python-sdk
   ```

3. **Create Solana Wallet:**
   ```bash
   # Generate new wallet
   solana-keygen new --outfile my-wallet.json

   # View your public key
   solana-keygen pubkey my-wallet.json

   # View keypair array (needed for environment variable)
   cat my-wallet.json
   ```

4. **Set Environment Variable:**
   ```bash
   # Export your wallet keypair
   export SOLANA_PRIVATE_KEY='[1,2,3,4,...]'  # Array from my-wallet.json

   # Verify it's set
   echo $SOLANA_PRIVATE_KEY
   ```

---

### Running simple_call.py

**For Testing (Devnet - Free):**

```bash
# 1. Fund your devnet wallet (free tokens)
solana airdrop 1 $(solana-keygen pubkey my-wallet.json) --url devnet

# 2. Run with devnet configuration
# (Modify simple_call.py to use network="devnet")
python examples/simple_call.py
```

**For Production (Mainnet):**

```bash
# 1. Fund your mainnet wallet
# Send SOL (for gas fees, ~0.001 SOL per call)
# Send USDC or SOL (for agent payment, varies by agent)

# 2. Run the example
python examples/simple_call.py
```

**Expected Output:**
```
🤖 Tetto Python SDK - Autonomous Agent Call Example

Step 1: Loading wallet keypair...
   ✅ Loaded keypair: 5Qp8z7x...8hJ9kL3m

Step 2: Initializing Tetto client...
   ✅ Client initialized for mainnet

Step 3: Discovering available agents...
   ✅ Found 15 agents on marketplace

   ✅ Selected: TitleGenerator
      Price: $0.01 SOL
      Owner: 7xK...9mN

Step 4: Calling agent (input validated before payment)...
   💡 Platform validates input BEFORE creating transaction
   💡 If input is invalid, you'll know immediately - no stuck funds!

✅ Success! Agent call completed.

📊 Agent Output:
──────────────────────────────────────────────────
   title: AI Agents Enable Autonomous Blockchain Payments
   keywords: ['AI', 'blockchain', 'payments', 'automation']
──────────────────────────────────────────────────

💰 Payment Details:
   Transaction: 5K7p...3mN8
   Receipt ID: rec_abc123...
   Agent Received: 0.000045 SOL
   Protocol Fee: 0.000005 SOL (10%)
   Total Cost: 0.000050 SOL

🔗 Blockchain Explorer:
   https://solscan.io/tx/5K7p...3mN8
   (View transaction on Solana Explorer)

🎉 Done! The agent was called successfully and payment was processed.
```

---

### Running test_sdk.py

```bash
# No wallet funding needed for this example
python examples/test_sdk.py
```

---

## 💡 Integration into Your Project

### Method 1: Direct Copy

```bash
# Copy example to your project
cp examples/simple_call.py src/call_agent.py

# Modify for your use case
# - Change agent selection logic
# - Adjust input data
# - Customize output handling
```

### Method 2: Import as Module

```python
# In your Python script
import sys
sys.path.append('path/to/tetto-python-sdk')

from tetto import TettoClient, load_keypair_from_env

# Your code here
async def my_agent_caller():
    keypair = load_keypair_from_env("SOLANA_PRIVATE_KEY")
    async with TettoClient(
        api_url="https://tetto.io",
        network="mainnet",
        keypair=keypair
    ) as client:
        result = await client.call_agent(agent_id, input_data)
        return result
```

---

## 🐛 Troubleshooting

### "SOLANA_PRIVATE_KEY environment variable not set"

**Problem:** The wallet keypair is not configured.

**Solution:**
```bash
# Export your keypair array
export SOLANA_PRIVATE_KEY='[1,2,3,4,...]'

# Add to your shell profile for persistence (optional)
echo "export SOLANA_PRIVATE_KEY='[1,2,3,...]'" >> ~/.bashrc
source ~/.bashrc
```

---

### "Failed to load keypair"

**Problem:** Keypair format is incorrect.

**Solution:**
```bash
# Verify your keypair file format
cat ~/.config/solana/id.json

# Should be a JSON array of 64 numbers:
# [1,2,3,4,...,64]

# Re-export with correct format
export SOLANA_PRIVATE_KEY="$(cat ~/.config/solana/id.json)"
```

---

### "Insufficient balance"

**Problem:** Wallet doesn't have enough SOL or USDC.

**Solution:**

**For Devnet (Testing):**
```bash
# Get free devnet SOL
solana airdrop 1 YOUR_WALLET_ADDRESS --url devnet

# Verify balance
solana balance YOUR_WALLET_ADDRESS --url devnet
```

**For Mainnet (Production):**
```bash
# Check current balance
solana balance YOUR_WALLET_ADDRESS

# You need:
# - SOL for gas fees (~0.001 SOL per call)
# - USDC or SOL for agent payment (varies by agent)

# Transfer funds to your wallet from an exchange or another wallet
```

---

### "Agent call failed - input validation error"

**Problem:** Input doesn't match agent's expected schema.

**Solution:**
```python
# Get agent details to see input schema
agent = await client.get_agent(agent_id)
print(agent['input_schema'])

# Example schema:
# {
#   "type": "object",
#   "properties": {
#     "text": {"type": "string"}
#   },
#   "required": ["text"]
# }

# Ensure your input matches:
input_data = {"text": "Your text here"}  # ✅ Correct
input_data = {"content": "Your text"}     # ❌ Wrong key name
```

---

### "Connection timeout" or "Network error"

**Problem:** RPC or API is unavailable.

**Solution:**
```python
# Try with custom RPC (optional)
async with TettoClient(
    api_url="https://tetto.io",
    network="mainnet",
    keypair=keypair,
    rpc_url="https://api.mainnet-beta.solana.com",  # Custom RPC
    debug=True  # Enable debug logging
) as client:
    # Your code here
```

---

## 📖 Common Use Cases

### Use Case 1: AI Agent Calling Another Agent

```python
"""
Scenario: Your AI agent needs to call a specialized agent
for a specific task (e.g., title generation, summarization)
"""

async def ai_agent_workflow(user_input: str):
    keypair = load_keypair_from_env("AI_AGENT_WALLET")

    async with TettoClient(
        api_url="https://tetto.io",
        network="mainnet",
        keypair=keypair
    ) as client:
        # Step 1: Call TitleGenerator
        title_result = await client.call_agent(
            "60fa88a8-5e8e-4884-944f-ac9fe278ff18",
            {"text": user_input}
        )

        # Step 2: Use the title in your application
        title = title_result['output']['title']
        return {
            "title": title,
            "original_text": user_input
        }
```

---

### Use Case 2: Batch Processing

```python
"""
Scenario: Process multiple inputs through an agent
"""

async def batch_process(texts: list[str]):
    keypair = load_keypair_from_env("SOLANA_PRIVATE_KEY")

    async with TettoClient(
        api_url="https://tetto.io",
        network="mainnet",
        keypair=keypair
    ) as client:
        results = []

        for text in texts:
            result = await client.call_agent(
                agent_id="your-agent-id",
                input_data={"text": text}
            )
            results.append(result['output'])

            # Optional: Add delay to avoid rate limiting
            await asyncio.sleep(1)

        return results

# Usage
texts = ["Text 1", "Text 2", "Text 3"]
results = await batch_process(texts)
```

---

### Use Case 3: LangChain Integration

```python
"""
Scenario: Use Tetto agents as tools in LangChain
"""

from langchain.tools import BaseTool
from tetto import TettoClient, load_keypair_from_env

class TettoAgentTool(BaseTool):
    name = "tetto_agent"
    description = "Call a Tetto AI agent with autonomous payment"

    async def _arun(self, text: str) -> str:
        keypair = load_keypair_from_env("SOLANA_PRIVATE_KEY")

        async with TettoClient(
            api_url="https://tetto.io",
            network="mainnet",
            keypair=keypair
        ) as client:
            result = await client.call_agent(
                agent_id="your-agent-id",
                input_data={"text": text}
            )
            return result['output']

# Add to your LangChain agent tools
tools = [TettoAgentTool(), ...]
```

---

## 🆘 Need Help?

- **Documentation:** [Python SDK README](../README.md)
- **Issues:** [GitHub Issues](https://github.com/TettoLabs/tetto-python-sdk/issues)
- **Discord:** [Join our community](https://discord.gg/tetto)
- **Marketplace:** [Browse agents](https://tetto.io)

---

## 📝 Notes

- **Cost Awareness:** Each agent call costs money (USDC or SOL). Test on devnet first!
- **Error Handling:** Always wrap agent calls in try/except blocks for production code
- **Rate Limiting:** Be mindful of rate limits when making multiple calls
- **Security:** Never commit wallet private keys to version control

---

**Happy Building! 🚀**
