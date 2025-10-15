"""
Wallet management utilities
"""

import os
import json
from pathlib import Path
from solders.keypair import Keypair


def load_keypair_from_file(path: str) -> Keypair:
    """Load Solana keypair from file"""
    expanded_path = Path(path).expanduser()
    
    if not expanded_path.exists():
        raise FileNotFoundError(f"Keypair file not found: {expanded_path}")
    
    with open(expanded_path, "r") as f:
        secret_key = json.load(f)
    
    if not isinstance(secret_key, list) or len(secret_key) != 64:
        raise ValueError("Invalid keypair format")
    
    return Keypair.from_bytes(bytes(secret_key))


def load_keypair_from_env(env_var: str = "SOLANA_PRIVATE_KEY") -> Keypair:
    """Load Solana keypair from environment variable"""
    secret_key_str = os.getenv(env_var)
    
    if not secret_key_str:
        raise ValueError(f"{env_var} not set")
    
    secret_key = json.loads(secret_key_str)
    return Keypair.from_bytes(bytes(secret_key))


def generate_keypair() -> Keypair:
    """Generate new random keypair"""
    return Keypair()
