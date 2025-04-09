"""
LLMPress Celery API

This module provides convenience functions for interacting with the Celery client.
"""
import logging
from typing import List, Any, Optional

from ..exceptions import APIConnectionError, TokenizationError
from ..utils.error_handler import with_error_handling
from .client import CeleryClient

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LLMPress.CeleryAPI')

# Create singleton instance
_client = None

@with_error_handling(
    context="Celery client initialization",
    handled_exceptions={
        Exception: APIConnectionError
    }
)
def get_client(broker_url: Optional[str] = None, backend_url: Optional[str] = None) -> CeleryClient:
    """
    Get or create a singleton CeleryClient instance.

    Args:
        broker_url: Optional broker URL to override default
        backend_url: Optional backend URL to override default

    Returns:
        Shared CeleryClient instance

    Raises:
        APIConnectionError: If there's an issue creating the Celery client
    """
    global _client
    logger.info("Getting or creating Celery client")

    if _client is None or broker_url is not None or backend_url is not None:
        logger.info(f"Creating new Celery client with broker URL: {broker_url or 'default'}")
        _client = CeleryClient(broker_url, backend_url)

    return _client


# Convenience functions that use the singleton client
@with_error_handling(
    context="API tokenization",
    handled_exceptions={
        APIConnectionError: None,  # Preserve APIConnectionError
        TokenizationError: None,  # Preserve TokenizationError
        Exception: TokenizationError  # Wrap other exceptions in TokenizationError
    }
)
def tokenize(text: str, window_size: int = 64, timeout: int = 60) -> List[Any]:
    """
    Tokenize text using the default client.

    Args:
        text: The text to tokenize
        window_size: Size of the sliding context window
        timeout: Maximum time to wait for result

    Returns:
        Tokenized result

    Raises:
        APIConnectionError: If there's an issue connecting to the Celery worker
        TokenizationError: If there's an error during tokenization
    """
    logger.info(f"API tokenizing text of length {len(text)} with window size {window_size}")
    result = get_client().tokenize(text, window_size, timeout)
    logger.info(f"API tokenization completed successfully")
    return result

@with_error_handling(
    context="API detokenization",
    handled_exceptions={
        APIConnectionError: None,  # Preserve APIConnectionError
        TokenizationError: None,  # Preserve TokenizationError
        Exception: TokenizationError  # Wrap other exceptions in TokenizationError
    }
)
def detokenize(tokens: List[Any], window_size: int = 64, timeout: int = 60) -> str:
    """
    Detokenize tokens using the default client.

    Args:
        tokens: The token sequences to decode
        window_size: Size of the sliding context window
        timeout: Maximum time to wait for result

    Returns:
        Reconstructed text

    Raises:
        APIConnectionError: If there's an issue connecting to the Celery worker
        TokenizationError: If there's an error during detokenization
    """
    logger.info(f"API detokenizing tokens with window size {window_size}")
    result = get_client().detokenize(tokens, window_size, timeout)
    logger.info(f"API detokenization completed successfully")
    return result

@with_error_handling(
    context="API batch tokenization",
    handled_exceptions={
        APIConnectionError: None,  # Preserve APIConnectionError
        TokenizationError: None,  # Preserve TokenizationError
        Exception: TokenizationError  # Wrap other exceptions in TokenizationError
    }
)
def tokenize_chunks(texts: List[str], window_size: int = 64, timeout: int = 120) -> List[List[Any]]:
    """
    Tokenize multiple text chunks using the default client.

    Args:
        texts: List of text chunks to tokenize
        window_size: Size of the sliding context window
        timeout: Maximum time to wait for all results

    Returns:
        List of tokenized results

    Raises:
        APIConnectionError: If there's an issue connecting to the Celery worker
        TokenizationError: If there's an error during batch tokenization
    """
    logger.info(f"API tokenizing {len(texts)} text chunks with window size {window_size}")
    result = get_client().tokenize_chunks(texts, window_size, timeout)
    logger.info(f"API batch tokenization completed successfully")
    return result

@with_error_handling(
    context="API batch detokenization",
    handled_exceptions={
        APIConnectionError: None,  # Preserve APIConnectionError
        TokenizationError: None,  # Preserve TokenizationError
        Exception: TokenizationError  # Wrap other exceptions in TokenizationError
    }
)
def detokenize_chunks(token_chunks: List[List[Any]], window_size: int = 64, timeout: int = 120) -> List[str]:
    """
    Detokenize multiple token chunks using the default client.

    Args:
        token_chunks: List of token chunks to detokenize
        window_size: Size of the sliding context window
        timeout: Maximum time to wait for all results

    Returns:
        List of detokenized text chunks

    Raises:
        APIConnectionError: If there's an issue connecting to the Celery worker
        TokenizationError: If there's an error during batch detokenization
    """
    logger.info(f"API detokenizing {len(token_chunks)} token chunks with window size {window_size}")
    result = get_client().detokenize_chunks(token_chunks, window_size, timeout)
    logger.info(f"API batch detokenization completed successfully")
    return result
