"""
Solana transaction building for Tetto payments

Handles USDC (primary) and SOL payments with automatic fee splitting.
"""

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction, AccountMeta
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import struct


# SPL Token Program ID
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")


def get_associated_token_address(wallet: Pubkey, mint: Pubkey) -> Pubkey:
    """
    Derive Associated Token Account (ATA) address
    
    This is deterministic - same wallet + mint = same ATA
    """
    from solders.sysvar import SYSVAR_RENT_PUBKEY
    from solders.pubkey import Pubkey as PubkeyClass
    
    # Associated Token Program ID
    ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
    
    # Find PDA: [wallet, TOKEN_PROGRAM_ID, mint]
    seeds = [
        bytes(wallet),
        bytes(TOKEN_PROGRAM_ID),
        bytes(mint),
    ]
    
    pda, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
    return pda


async def build_and_send_payment(
    rpc_url: str,
    payer_keypair: Keypair,
    agent_wallet: Pubkey,
    protocol_wallet: Pubkey,
    price_usd: float,
    token: str = "USDC",
    usdc_mint: str = "",
    fee_bps: int = 1000,
    debug: bool = False,
) -> str:
    """
    Build, sign, and send payment transaction
    
    Supports USDC (primary) and SOL.
    """
    async with AsyncClient(rpc_url) as client:
        if token == "USDC":
            # USDC: 1 USD = 1 USDC (6 decimals)
            amount_base = int(price_usd * 1_000_000)
            
            # Calculate fees
            protocol_fee = int(amount_base * fee_bps / 10000)
            agent_amount = amount_base - protocol_fee
            
            if debug:
                print(f"💰 ${price_usd} USD = {amount_base} USDC base units")
                print(f"   Agent: {agent_amount}, Protocol: {protocol_fee}")
            
            # Get mint pubkey
            mint_pubkey = Pubkey.from_string(usdc_mint)
            
            # Derive ATAs
            payer_ata = get_associated_token_address(payer_keypair.pubkey(), mint_pubkey)
            agent_ata = get_associated_token_address(agent_wallet, mint_pubkey)
            protocol_ata = get_associated_token_address(protocol_wallet, mint_pubkey)
            
            if debug:
                print(f"📋 Token Accounts:")
                print(f"   Payer ATA: {payer_ata}")
                print(f"   Agent ATA: {agent_ata}")
                print(f"   Protocol ATA: {protocol_ata}")
            
            # Get recent blockhash
            blockhash_resp = await client.get_latest_blockhash()
            recent_blockhash = blockhash_resp.value.blockhash
            
            # Build SPL Token transfer instructions
            # TransferChecked instruction (safer than Transfer)
            
            # Transfer to agent
            transfer_to_agent_ix = Instruction(
                program_id=TOKEN_PROGRAM_ID,
                accounts=[
                    AccountMeta(pubkey=payer_ata, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=agent_ata, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=payer_keypair.pubkey(), is_signer=True, is_writable=False),
                ],
                data=bytes([12]) + struct.pack("<QB", agent_amount, 6),  # TransferChecked: amount, decimals
            )
            
            # Transfer to protocol
            transfer_to_protocol_ix = Instruction(
                program_id=TOKEN_PROGRAM_ID,
                accounts=[
                    AccountMeta(pubkey=payer_ata, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=protocol_ata, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=payer_keypair.pubkey(), is_signer=True, is_writable=False),
                ],
                data=bytes([12]) + struct.pack("<QB", protocol_fee, 6),
            )
            
            # Build and sign transaction
            msg = Message.new_with_blockhash(
                [transfer_to_agent_ix, transfer_to_protocol_ix],
                payer_keypair.pubkey(),
                recent_blockhash,
            )
            tx = Transaction([payer_keypair], msg, recent_blockhash)
            
        else:  # SOL
            # Convert USD to SOL (fetch from API or use estimate)
            sol_price = 200.0  # TODO: Fetch from /api/price/sol
            sol_amount = price_usd / sol_price
            amount_lamports = int(sol_amount * 1e9)
            
            # Calculate fees
            protocol_fee = int(amount_lamports * fee_bps / 10000)
            agent_amount = amount_lamports - protocol_fee
            
            if debug:
                print(f"💰 ${price_usd} USD = {amount_lamports} lamports (at ${sol_price}/SOL)")
                print(f"   Agent: {agent_amount}, Protocol: {protocol_fee}")
            
            # Get recent blockhash
            blockhash_resp = await client.get_latest_blockhash()
            recent_blockhash = blockhash_resp.value.blockhash
            
            # Build SOL transfer instructions
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
        
        # Send transaction
        if debug:
            print(f"📡 Sending transaction...")
        
        result = await client.send_transaction(tx)
        signature = str(result.value)
        
        if debug:
            print(f"   ✅ Transaction sent: {signature}")
            print(f"   Waiting for confirmation...")
        
        # Wait for confirmation
        await client.confirm_transaction(signature, commitment=Confirmed)
        
        if debug:
            print(f"   ✅ Confirmed!")
        
        return signature
