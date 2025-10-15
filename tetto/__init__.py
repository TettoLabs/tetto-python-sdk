"""
Tetto Python SDK

Python client for autonomous AI agent payments on Solana.
"""

from .client import TettoClient
from .wallet import (
    load_keypair_from_file,
    load_keypair_from_env,
    generate_keypair,
)

__version__ = "0.1.0"
__all__ = [
    "TettoClient",
    "load_keypair_from_file",
    "load_keypair_from_env",
    "generate_keypair",
]
