"""
LLMPress Celery API

This module provides convenience functions for interacting with the Celery client.
"""
from typing import List, Any, Optional

from .client import CeleryClient

# Create singleton instance
_client = None

def get_client(broker_url: Optional[str] = None, backend_url: Optional[str] = None) -> CeleryClient:
    """
    Get or create a singleton CeleryClient instance.

    Args:
        broker_url: Optional broker URL to override default
        backend_url: Optional backend URL to override default

    Returns:
        Shared CeleryClient instance
    """
    global _client
    if _client is None or broker_url is not None or backend_url is not None:
        _client = CeleryClient(broker_url, backend_url)
    return _client


# Convenience functions that use the singleton client
def tokenize(text: str, window_size: int = 64, timeout: int = 60) -> List[List[Any]]:
    """
    Tokenize text using the default client.

    Args:
        text: The text to tokenize
        window_size: Size of the sliding context window
        timeout: Maximum time to wait for result

    Returns:
        Tokenized result
    """
    return get_client().tokenize(text, window_size, timeout)

def detokenize(tokens: List[List[Any]], window_size: int = 64, timeout: int = 60) -> str:
    """
    Detokenize tokens using the default client.

    Args:
        tokens: The token sequences to decode
        window_size: Size of the sliding context window
        timeout: Maximum time to wait for result

    Returns:
        Reconstructed text
    """
    return get_client().detokenize(tokens, window_size, timeout)

# Batch processing functions have been removed
