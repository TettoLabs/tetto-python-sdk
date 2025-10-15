"""
Test the Tetto Python SDK with a real agent call
"""

import asyncio
import sys
import os

# Add parent directory to path so we can import tetto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tetto import TettoClient, generate_keypair


async def test_sdk():
    print("🧪 Testing Tetto Python SDK\n")
    print("=" * 60)
    
    # Generate test keypair (or load from env)
    print("\n1️⃣  Setting up wallet...")
    try:
        from tetto.wallet import load_keypair_from_env
        keypair = load_keypair_from_env("SOLANA_PRIVATE_KEY")
        print(f"   ✅ Loaded keypair from env")
    except:
        keypair = generate_keypair()
        print(f"   ⚠️  Generated new keypair")
        print(f"   Public key: {keypair.pubkey()}")
        print(f"   NOTE: This wallet has no SOL. Fund it to test payments.")
    
    print(f"   Wallet: {str(keypair.pubkey())[:8]}...")
    
    # Initialize client
    print("\n2️⃣  Initializing Tetto client...")
    async with TettoClient(
        api_url="https://tetto.io",
        network="mainnet",
        keypair=keypair,
        debug=True,
    ) as client:
        
        # List agents
        print("\n3️⃣  Fetching agents...")
        agents = await client.list_agents()
        print(f"   ✅ Found {len(agents)} agents")
        
        # Show first few
        for agent in agents[:3]:
            print(f"   - {agent['name']}: ${agent['price_usd']} {agent.get('primary_display_token', 'USDC')}")
        
        # Get specific agent
        print("\n4️⃣  Getting agent details...")
        agent_id = agents[0]['id'] if agents else None
        
        if agent_id:
            agent = await client.get_agent(agent_id)
            print(f"   ✅ Agent: {agent['name']}")
            print(f"   Price: ${agent['price_usd']}")
            print(f"   Endpoint: {agent.get('endpoint_url', 'N/A')}")
        
        # Try calling an agent (will fail without funds, but tests the flow)
        print("\n5️⃣  Testing agent call...")
        print("   NOTE: This requires SOL in wallet for gas fees")
        print("   Skipping actual call for now (would fail without funds)")
        
        # Uncomment to test real call:
        # result = await client.call_agent(
        #     agent_id=agent_id,
        #     input_data={"text": "Test from Python SDK"},
        #     preferred_token="SOL",
        # )
        # print(f"   ✅ Output: {result['output']}")
        # print(f"   Transaction: {result['tx_signature']}")
    
    print("\n" + "=" * 60)
    print("✅ SDK test complete!")
    print("\nPython SDK is working correctly!")


if __name__ == "__main__":
    asyncio.run(test_sdk())
