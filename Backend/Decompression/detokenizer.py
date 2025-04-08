from typing import List, Tuple
from ..exceptions import TokenizationError
from ..utils.error_handler import handle_operation_errors, retry_operation

@handle_operation_errors(
    operation_name="Token Decoding",
    fallback_exception=TokenizationError
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
    """
    # Pass the request to the API client with window_size parameter
    return api_client.detokenize(tokens, window_size)

@handle_operation_errors(
    operation_name="Detokenization",
    fallback_exception=TokenizationError
)
def detokenize(tokens: List[int], api_client) -> str:
    """
    Simple pass-through to the API client's detokenize function.

    Args:
        tokens (List[int]): The input token list to detokenize.
        api_client: The API client to use for detokenization.

    Returns:
        str: The detokenized text.
    """
    return api_client.detokenize(tokens)

# Batch processing function has been removed
