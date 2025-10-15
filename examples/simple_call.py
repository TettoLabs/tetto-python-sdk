"""
Simple example: Call an agent from Python
"""

import asyncio
from tetto import TettoClient, load_keypair_from_env


async def main():
    # Load AI agent's wallet
    keypair = load_keypair_from_env("SOLANA_PRIVATE_KEY")
    
    # Initialize client
    async with TettoClient(
        api_url="https://tetto.io",
        network="mainnet",
        keypair=keypair,
        debug=True,
    ) as client:
        # Call TitleGenerator agent
        result = await client.call_agent(
            agent_id="60fa88a8-5e8e-4884-944f-ac9fe278ff18",  # TitleGenerator
            input_data={"text": "This is a test article about AI agents."},
            preferred_token="SOL",
        )
        
        print("\n✅ Success!")
        print(f"Output: {result['output']}")
        print(f"Transaction: {result['tx_signature']}")


if __name__ == "__main__":
    asyncio.run(main())
