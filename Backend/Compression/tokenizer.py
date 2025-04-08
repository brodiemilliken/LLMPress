from typing import List, Tuple
from ..exceptions import TokenizationError
from ..utils.error_handler import handle_operation_errors, retry_operation

@handle_operation_errors(
    operation_name="Text Encoding",
    fallback_exception=TokenizationError
)
def encode_text(text: str, api_client, window_size: int = 64) -> List[Tuple[str, int]]:
    """
    Encode text by using the API.

    Args:
        text (str): The text to encode.
        api_client: The API client to use.
        window_size (int): Size of the sliding context window for token prediction.

    Returns:
        List[Tuple[str, int]]: A list of encoded tokens.
    """
    # Pass the request to the API client with window_size parameter
    return api_client.tokenize(text, window_size)

@handle_operation_errors(
    operation_name="Tokenization",
    fallback_exception=TokenizationError
)
def tokenize(text: str, api_client) -> list:
    """
    Simple pass-through to the API client's tokenize function.

    Args:
        text (str): The input text to tokenize.
        api_client: The API client to use for tokenization.

    Returns:
        list: A list of tokens.
    """
    # This is for compatibility with code that expects this function
    return api_client.tokenize(text)

# Batch processing function has been removed
