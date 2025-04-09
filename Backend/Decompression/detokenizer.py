from typing import List, Tuple, Any
import logging

from ..exceptions import TokenizationError
from ..utils.error_handler import with_error_handling

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LLMPress.Detokenizer')

# Direct API client functions - these are simple pass-throughs
# to maintain backward compatibility

@with_error_handling(
    context="Token decoding",
    handled_exceptions={
        Exception: TokenizationError
    }
)
def decode_tokens(tokens: List[Tuple[str, int]], api_client, window_size: int = 64) -> str:
    """
    Convert a list of encoded tokens into text by using the API.

    Args:
        tokens (List[Tuple[str, int]]): The input tokens to decode.
        api_client: The API client to use for decoding.
        window_size (int): Size of the sliding context window for token prediction.

    Returns:
        str: The decoded text string.

    Raises:
        TokenizationError: If decoding fails for any reason
    """
    logger.info(f"Decoding {len(tokens)} tokens with window size {window_size}")
    result = api_client.detokenize(tokens, window_size)
    logger.info(f"Successfully decoded tokens into text of length {len(result)}")
    return result

@with_error_handling(
    context="Token detokenization",
    handled_exceptions={
        Exception: TokenizationError
    }
)
def detokenize(tokens: List[Any], api_client) -> str:
    """
    Simple pass-through to the API client's detokenize function.

    Args:
        tokens (List[Any]): The input token list to detokenize.
        api_client: The API client to use for detokenization.

    Returns:
        str: The detokenized text.

    Raises:
        TokenizationError: If detokenization fails for any reason
    """
    logger.info(f"Detokenizing {len(tokens)} tokens")
    result = api_client.detokenize(tokens)
    logger.info(f"Successfully detokenized tokens into text of length {len(result)}")
    return result

@with_error_handling(
    context="Multiple token chunks detokenization",
    handled_exceptions={
        Exception: TokenizationError
    }
)
def detokenize_chunks(token_chunks: List[List[Tuple[str, int]]], api_client, window_size=64) -> List[str]:
    """
    Detokenize multiple token chunks using the API client.

    Args:
        token_chunks (List[List[Tuple[str, int]]]): List of token chunks to detokenize.
        api_client: The API client to use.
        window_size (int): Size of the sliding context window for token prediction.

    Returns:
        List[str]: List of detokenized text strings, one for each chunk.

    Raises:
        TokenizationError: If detokenization fails for any reason
    """
    logger.info(f"Detokenizing {len(token_chunks)} token chunks with window size {window_size}")
    result = api_client.detokenize_chunks(token_chunks, window_size)
    logger.info(f"Successfully detokenized {len(token_chunks)} chunks")
    return result

