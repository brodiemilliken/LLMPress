from typing import List, Tuple

# Direct API client functions - these are simple pass-throughs
# to maintain backward compatibility

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

def detokenize_chunks(token_chunks: List[List[Tuple[str, int]]], api_client, window_size=64) -> List[str]:
    """
    Detokenize multiple token chunks using the API client.

    Args:
        token_chunks (List[List[Tuple[str, int]]]): List of token chunks to detokenize.
        api_client: The API client to use.
        window_size (int): Size of the sliding context window for token prediction.

    Returns:
        List[str]: List of detokenized text strings, one for each chunk.
    """
    # If the client supports batch processing, use it
    return api_client.detokenize_chunks(token_chunks, window_size)





