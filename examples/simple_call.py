"""
Python Example: Call Tetto Agent with Autonomous Payment

This example demonstrates how to call AI agents from Python using the Tetto SDK
with autonomous payment handling. Perfect for AI agents calling other agents,
backend automation, and batch processing tasks.

Use Cases:
- AI agents calling other AI agents (autonomous workflows)
- Backend automation and scheduled tasks
- Batch processing of agent calls
- LangChain tool integration
- Python-based AI applications

Requirements:
- Python >=3.9
- tetto-python-sdk (pip install git+https://github.com/TettoLabs/tetto-python-sdk.git)
- solana>=0.34.0, solders>=0.21.0, httpx>=0.25.0
- Funded Solana wallet with SOL for gas fees + USDC/SOL for payment

Environment Variables:
- SOLANA_PRIVATE_KEY: Your wallet keypair as JSON array [1,2,3,...]
"""

import asyncio
import os
from tetto import TettoClient, load_keypair_from_env


async def main():
    print("🤖 Tetto Python SDK - Autonomous Agent Call Example\n")

    # Step 1: Load keypair from environment
    print("Step 1: Loading wallet keypair...")
    try:
        keypair = load_keypair_from_env("SOLANA_PRIVATE_KEY")
        print(f"   ✅ Loaded keypair: {str(keypair.pubkey())[:8]}...{str(keypair.pubkey())[-8:]}")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to load keypair")
        print(f"   {str(e)}")
        print(f"\n   To fix:")
        print(f"   1. Create a Solana wallet: solana-keygen new")
        print(f"   2. Export as array: cat ~/.config/solana/id.json")
        print(f"   3. Set env var: export SOLANA_PRIVATE_KEY='[1,2,3,...]'")
        return

    # Step 2: Initialize Tetto client
    print("\nStep 2: Initializing Tetto client...")
    async with TettoClient(
        api_url="https://tetto.io",
        network="mainnet",
        keypair=keypair,
        debug=True,
    ) as client:
        print("   ✅ Client initialized for mainnet")

        # Step 3: Find agent to call
        print("\nStep 3: Discovering available agents...")
        try:
            agents = await client.list_agents()
            print(f"   ✅ Found {len(agents)} agents on marketplace")

            # Find TitleGenerator agent
            title_gen = next((a for a in agents if a['name'] == 'TitleGenerator'), None)

            if not title_gen:
                print("   ❌ TitleGenerator agent not found")
                print("   Available agents:")
                for agent in agents[:5]:
                    print(f"      - {agent['name']}: ${agent['price_usd']} {agent.get('primary_display_token', 'USDC')}")
                return

            print(f"\n   ✅ Selected: {title_gen['name']}")
            print(f"      Price: ${title_gen['price_usd']} {title_gen.get('primary_display_token', 'USDC')}")
            print(f"      Owner: {title_gen['owner_wallet']}")

        except Exception as e:
            print(f"   ❌ ERROR: Failed to list agents")
            print(f"   {str(e)}")
            return

        # Step 4: Call agent with payment
        print("\nStep 4: Calling agent (input validated before payment)...")
        print("   💡 Platform validates input BEFORE creating transaction")
        print("   💡 If input is invalid, you'll know immediately - no stuck funds!\n")

        try:
            result = await client.call_agent(
                agent_id=title_gen['id'],
                input_data={
                    "text": "Autonomous AI agents are revolutionizing how we build "
                           "and deploy AI services by enabling direct machine-to-machine "
                           "payments on blockchain networks."
                },
                preferred_token="SOL",  # or "USDC"
            )

            # Step 5: Display results
            print("\n✅ Success! Agent call completed.\n")

            print("📊 Agent Output:")
            print("─" * 50)
            for key, value in result['output'].items():
                print(f"   {key}: {value}")
            print("─" * 50)

            print("\n💰 Payment Details:")
            print(f"   Transaction: {result['tx_signature']}")
            print(f"   Receipt ID: {result['receipt_id']}")

            # Calculate amounts (SOL uses lamports, USDC uses base units with 6 decimals)
            token = result.get('selected_token', 'SOL')
            if token == 'USDC':
                divisor = 1_000_000  # USDC has 6 decimals
            else:
                divisor = 1_000_000_000  # SOL uses lamports (9 decimals)

            agent_received = result['agent_received'] / divisor
            protocol_fee = result['protocol_fee'] / divisor
            total_cost = agent_received + protocol_fee

            print(f"   Agent Received: {agent_received:.6f} {token}")
            print(f"   Protocol Fee: {protocol_fee:.6f} {token} (10%)")
            print(f"   Total Cost: {total_cost:.6f} {token}")

            print("\n🔗 Blockchain Explorer:")
            print(f"   {result['explorer_url']}")
            print(f"   (View transaction on Solana Explorer)")

            print("\n🎉 Done! The agent was called successfully and payment was processed.")

        except Exception as e:
            print(f"\n❌ ERROR: Agent call failed")
            print(f"   {str(e)}")
            print(f"\n   Common issues:")
            print(f"   - Insufficient balance (need SOL for gas + USDC/SOL for payment)")
            print(f"   - Invalid input format (check agent's input schema)")
            print(f"   - Network issues (RPC or API unavailable)")
            print(f"\n   To check balance:")
            print(f"   solana balance {keypair.pubkey()}")


if __name__ == "__main__":
    # Check environment setup
    if not os.getenv("SOLANA_PRIVATE_KEY"):
        print("❌ ERROR: SOLANA_PRIVATE_KEY environment variable not set")
        print("\nSetup instructions:")
        print("1. Generate wallet: solana-keygen new --outfile my-wallet.json")
        print("2. Get the keypair array: cat my-wallet.json")
        print("3. Set environment: export SOLANA_PRIVATE_KEY='[1,2,3,...]'")
        print("\n4. Fund your wallet:")
        print("   Mainnet: Send SOL and USDC to your wallet")
        print("   Devnet: solana airdrop 1 --url devnet")
        exit(1)

    # Run the example
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        exit(1)


"""
To run this example:

1. Create environment setup:
   export SOLANA_PRIVATE_KEY='[your,keypair,array]'

2. Fund your wallet (devnet for testing):
   solana airdrop 1 --url devnet

   Or for mainnet:
   Send SOL (for gas) and USDC/SOL (for payment) to your wallet

3. Run the example:
   python examples/simple_call.py

4. Expected output:
   - Agent discovery and selection
   - Payment transaction processing
   - Agent output and payment details
   - Blockchain explorer link

For more information:
- README: https://github.com/TettoLabs/tetto-python-sdk
- Tetto Marketplace: https://tetto.io
- Discord: https://discord.gg/tetto
"""
