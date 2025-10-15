"""
Tetto Python SDK - Main Client

Enables AI agents to autonomously call and pay for services from other agents.
"""

import httpx
from typing import Dict, List, Optional
from solders.keypair import Keypair
from solders.pubkey import Pubkey


class TettoClient:
    """
    Python SDK for Tetto AI Agent Marketplace

    Example:
        >>> from tetto import TettoClient
        >>> from tetto.wallet import load_keypair_from_file
        >>>
        >>> keypair = load_keypair_from_file("~/.config/solana/id.json")
        >>> client = TettoClient(
        ...     api_url="https://tetto.io",
        ...     network="mainnet",
        ...     keypair=keypair
        ... )
        >>> result = await client.call_agent(
        ...     agent_id="uuid",
        ...     input_data={"text": "Hello"}
        ... )
    """

    def __init__(
        self,
        api_url: str,
        network: str = "mainnet",
        keypair: Optional[Keypair] = None,
        rpc_url: Optional[str] = None,
        protocol_wallet: Optional[str] = None,
        debug: bool = False,
    ):
        """
        Initialize Tetto client

        Args:
            api_url: Tetto API URL (e.g., "https://tetto.io")
            network: "mainnet" or "devnet"
            keypair: Solana keypair for signing transactions
            rpc_url: Custom RPC URL (optional)
            protocol_wallet: Custom protocol wallet (optional)
            debug: Enable debug logging
        """
        self.api_url = api_url.rstrip("/")
        self.network = network
        self.keypair = keypair
        self.debug = debug

        # Network configuration
        if network == "mainnet":
            self.rpc_url = rpc_url or "https://api.mainnet-beta.solana.com"
            self.protocol_wallet = protocol_wallet or "CYSnefexbvrRU6VxzGfvZqKYM4UixupvDeZg3sUSWm84"
            self.usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        else:  # devnet
            self.rpc_url = rpc_url or "https://api.devnet.solana.com"
            self.protocol_wallet = protocol_wallet or "BubFsAG8cSEH7NkLpZijctRpsZkCiaWqCdRfh8kUpXEt"
            self.usdc_mint = "EGzSiubUqhzWFR2KxWCx6jHD6XNsVhKrnebjcQdN6qK4"

        self.http_client = httpx.AsyncClient(timeout=30.0)

        if self.debug:
            print(f"=' TettoClient initialized")
            print(f"   API: {self.api_url}")
            print(f"   Network: {self.network}")
            print(f"   RPC: {self.rpc_url}")
            if self.keypair:
                print(f"   Wallet: {str(self.keypair.pubkey())[:8]}...")

    async def list_agents(self) -> List[Dict]:
        """
        List all active agents in the marketplace

        Returns:
            List of agent dictionaries

        Example:
            >>> agents = await client.list_agents()
            >>> for agent in agents:
            ...     print(f"{agent['name']}: ${agent['price_usd']}")
        """
        response = await self.http_client.get(f"{self.api_url}/api/agents")
        data = response.json()

        if not data.get("ok"):
            raise Exception(data.get("error", "Failed to list agents"))

        if self.debug:
            print(f"=Ë Found {len(data['agents'])} agents")

        return data["agents"]

    async def get_agent(self, agent_id: str) -> Dict:
        """
        Get agent details by ID

        Args:
            agent_id: Agent UUID

        Returns:
            Agent dictionary with schemas, price, etc.
        """
        response = await self.http_client.get(f"{self.api_url}/api/agents/{agent_id}")
        data = response.json()

        if not data.get("ok"):
            raise Exception(data.get("error", "Agent not found"))

        return data["agent"]

    async def call_agent(
        self,
        agent_id: str,
        input_data: Dict,
        preferred_token: str = "USDC",
    ) -> Dict:
        """
        Call an agent with autonomous payment

        This is the core method for AI-to-AI transactions. Your AI agent
        will build, sign, and send a payment transaction, then call the
        target agent's endpoint.

        Args:
            agent_id: Agent UUID
            input_data: Input matching agent's input schema
            preferred_token: 'USDC' or 'SOL' (default: USDC)

        Returns:
            {
                "ok": True,
                "output": {...},  # Agent's output
                "tx_signature": "...",  # Solana transaction
                "receipt_id": "...",  # Tetto receipt
                "explorer_url": "...",  # View on Solana Explorer
                "agent_received": 1234,  # Base units agent received
                "protocol_fee": 123,  # Base units protocol fee
            }

        Raises:
            Exception: If no keypair, insufficient funds, or call fails
        """
        if not self.keypair:
            raise Exception(
                "Keypair required for payments. "
                "Initialize TettoClient with keypair parameter."
            )

        # Get agent details
        agent = await self.get_agent(agent_id)

        if self.debug:
            print(f"> Calling agent: {agent['name']}")
            print(f"   Price: ${agent['price_usd']} USD")
            print(f"   Token: {preferred_token}")

        # Build, sign, and send payment transaction
        from .transactions import build_and_send_payment

        tx_signature = await build_and_send_payment(
            rpc_url=self.rpc_url,
            payer_keypair=self.keypair,
            agent_wallet=Pubkey.from_string(agent["owner_wallet"]),
            protocol_wallet=Pubkey.from_string(self.protocol_wallet),
            price_usd=agent["price_usd"],
            token=preferred_token,
            usdc_mint=self.usdc_mint,
            fee_bps=agent.get("fee_bps", 1000),
            debug=self.debug,
        )

        if self.debug:
            print(f"    Transaction sent: {tx_signature}")
            print(f"   Calling backend API...")

        # Call backend API with transaction proof
        response = await self.http_client.post(
            f"{self.api_url}/api/agents/call",
            json={
                "agent_id": agent_id,
                "input": input_data,
                "caller_wallet": str(self.keypair.pubkey()),
                "tx_signature": tx_signature,
                "selected_token": preferred_token,
            },
        )

        data = response.json()

        if not data.get("ok"):
            raise Exception(data.get("error", "Agent call failed"))

        if self.debug:
            print(f"    Call successful!")
            print(f"   Output keys: {list(data.get('output', {}).keys())}")

        return data

    async def close(self):
        """Close HTTP client connection"""
        await self.http_client.aclose()

    async def __aenter__(self):
        """Async context manager support"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager support"""
        await self.close()
