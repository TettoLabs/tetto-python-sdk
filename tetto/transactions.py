"""
Solana transaction building for Tetto payments
"""

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solders.message import Message
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed


async def build_and_send_payment(
    rpc_url: str,
    payer_keypair: Keypair,
    agent_wallet: Pubkey,
    protocol_wallet: Pubkey,
    price_usd: float,
    token: str = "SOL",
    usdc_mint: str = "",
    fee_bps: int = 1000,
    debug: bool = False,
) -> str:
    """
    Build, sign, and send payment transaction
    
    Currently supports SOL only. USDC coming soon.
    """
    async with AsyncClient(rpc_url) as client:
        if token == "SOL":
            # Convert USD to SOL (simplified: $200/SOL)
            sol_price = 200.0
            sol_amount = price_usd / sol_price
            amount_lamports = int(sol_amount * 1e9)
            
            # Calculate fees
            protocol_fee = int(amount_lamports * fee_bps / 10000)
            agent_amount = amount_lamports - protocol_fee
            
            if debug:
                print(f"💰 ${price_usd} USD = {amount_lamports} lamports")
                print(f"   Agent: {agent_amount}, Protocol: {protocol_fee}")
            
            # Get recent blockhash
            blockhash_resp = await client.get_latest_blockhash()
            recent_blockhash = blockhash_resp.value.blockhash
            
            # Build instructions
            ix1 = transfer(TransferParams(
                from_pubkey=payer_keypair.pubkey(),
                to_pubkey=agent_wallet,
                lamports=agent_amount,
            ))
            
            ix2 = transfer(TransferParams(
                from_pubkey=payer_keypair.pubkey(),
                to_pubkey=protocol_wallet,
                lamports=protocol_fee,
            ))
            
            # Build and sign transaction
            msg = Message.new_with_blockhash(
                [ix1, ix2],
                payer_keypair.pubkey(),
                recent_blockhash,
            )
            tx = Transaction([payer_keypair], msg, recent_blockhash)
            
            # Send
            result = await client.send_transaction(tx)
            signature = str(result.value)
            
            if debug:
                print(f"📡 Transaction: {signature}")
            
            # Wait for confirmation
            await client.confirm_transaction(signature, commitment=Confirmed)
            
            return signature
            
        else:  # USDC
            raise NotImplementedError(
                "USDC not yet implemented in Python SDK. Use SOL or TypeScript SDK."
            )
