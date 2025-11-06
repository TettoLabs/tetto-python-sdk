"""
Tetto Python SDK v2.0 - Main Client

Platform-powered architecture with input validation before payment.
"""

import httpx
from typing import Dict, List, Optional
from solders.keypair import Keypair
from solders.pubkey import Pubkey


class TettoClient:
    """
    Python SDK for Tetto AI Agent Marketplace (v2.0 Platform-Powered)

    Platform validates input BEFORE payment (fail fast!)
    Platform builds transactions (you only sign)
    No RPC connection needed (simpler!)

    Example:
        >>> from tetto import TettoClient
        >>> from tetto.wallet import load_keypair_from_file
        >>>
        >>> keypair = load_keypair_from_file("~/.config/solana/id.json")
        >>> async with TettoClient(
        ...     api_url="https://tetto.io",
        ...     network="mainnet",
        ...     keypair=keypair
        ... ) as client:
        ...     result = await client.call_agent(
        ...         agent_id="uuid",
        ...         input_data={"text": "Hello"}
        ...     )
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
        Initialize Tetto client (v2.0 Platform-Powered)

        Args:
            api_url: Tetto API URL (e.g., "https://tetto.io")
            network: "mainnet" or "devnet"
            keypair: Solana keypair for signing transactions
            rpc_url: Custom RPC URL (optional, not used in v2.0)
            protocol_wallet: Custom protocol wallet (optional, for reference)
            debug: Enable debug logging
        """
        self.api_url = api_url.rstrip("/")
        self.network = network
        self.keypair = keypair
        self.debug = debug

        # Network configuration (kept for reference, RPC not used in v2.0)
        if network == "mainnet":
            self.rpc_url = rpc_url or "https://api.mainnet-beta.solana.com"
            self.protocol_wallet = protocol_wallet or "CYSnefexbvrRU6VxzGfvZqKYM4UixupvDeZg3sUSWm84"
            self.usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        else:  # devnet
            self.rpc_url = rpc_url or "https://api.devnet.solana.com"
            self.protocol_wallet = protocol_wallet or "BubFsAG8cSEH7NkLpZijctRpsZkCiaWqCdRfh8kUpXEt"
            self.usdc_mint = "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"

        self.http_client = httpx.AsyncClient(timeout=30.0)

        if self.debug:
            print(f"🚀 TettoClient v2.0 initialized (platform-powered)")
            print(f"   API: {self.api_url}")
            print(f"   Network: {self.network}")
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
            ...     print(f"{agent['name']}: ${agent['price_display']}")
        """
        response = await self.http_client.get(f"{self.api_url}/api/agents")
        data = response.json()

        if not data.get("ok"):
            raise Exception(data.get("error", "Failed to list agents"))

        if self.debug:
            print(f"📋 Found {len(data['agents'])} agents")

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
        Call an agent with autonomous payment (v2.0 Platform-Powered)

        Platform validates input BEFORE payment (fail fast!)
        Platform builds transaction (you only sign)
        No RPC connection needed (simpler!)

        This method implements the v2.0.0 platform-powered architecture
        where the Tetto platform handles transaction building and validation,
        eliminating the risk of stuck funds from invalid input.

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

        # Step 1: Get agent details
        agent = await self.get_agent(agent_id)

        if self.debug:
            print(f"🤖 Calling agent: {agent['name']}")
            print(f"   Price: ${agent.get('price_display', 0)} {agent.get('token', 'USDC')}")
            print(f"   Payer: {str(self.keypair.pubkey())[:8]}...")

        # Step 2: Request unsigned transaction from platform
        # Platform validates input BEFORE payment (fail fast!)
        if self.debug:
            print("   Requesting transaction from platform (with input validation)...")

        build_response = await self.http_client.post(
            f"{self.api_url}/api/agents/{agent_id}/build-transaction",
            json={
                "payer_wallet": str(self.keypair.pubkey()),
                "selected_token": preferred_token,
                "input": input_data,  # Input validated at build-time (fail fast!)
            },
        )

        build_result = build_response.json()

        if not build_result.get("ok"):
            if self.debug:
                print(f"   ❌ Transaction building failed: {build_result.get('error')}")
            raise Exception(build_result.get("error", "Transaction building failed"))

        if self.debug:
            print(f"   ✅ Transaction built (input validated)")
            print(f"   Payment intent: {build_result['payment_intent_id']}")
            print(f"   Amount: {build_result['amount_base']} base units")
            print(f"   Token: {build_result['token']}")

        # Step 3: Deserialize and sign transaction
        from solders.transaction import VersionedTransaction
        from base64 import b64decode, b64encode

        if self.debug:
            print("   Signing transaction...")

        transaction_bytes = b64decode(build_result['transaction'])
        transaction = VersionedTransaction.from_bytes(transaction_bytes)

        # Sign the transaction
        signature = self.keypair.sign_message(bytes(transaction.message.serialize()))

        # Create signed transaction
        signed_transaction = VersionedTransaction.populate(
            transaction.message,
            [signature]
        )

        if self.debug:
            print("   ✅ Transaction signed (platform will submit)")

        # Step 4: Submit signed transaction to platform
        if self.debug:
            print("   Sending signed transaction to platform...")

        response = await self.http_client.post(
            f"{self.api_url}/api/agents/call",
            json={
                "payment_intent_id": build_result['payment_intent_id'],
                "signed_transaction": b64encode(bytes(signed_transaction)).decode('utf-8'),
            },
        )

        data = response.json()

        if not data.get("ok"):
            if self.debug:
                print(f"   ❌ Agent call failed: {data.get('error')}")
            raise Exception(data.get("error", "Agent call failed"))

        if self.debug:
            print(f"   ✅ Agent call successful")

        return {
            "ok": data.get("ok"),
            "message": data.get("message", ""),
            "output": data.get("output", {}),
            "tx_signature": data.get("tx_signature", ""),
            "receipt_id": data.get("receipt_id", ""),
            "explorer_url": data.get("explorer_url", ""),
            "agent_received": data.get("agent_received", 0),
            "protocol_fee": data.get("protocol_fee", 0),
        }

    async def close(self):
        """Close HTTP client connection"""
        await self.http_client.aclose()

    async def __aenter__(self):
        """Async context manager support"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager support"""
        await self.close()
