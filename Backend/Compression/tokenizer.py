from typing import List, Tuple

# Direct API client functions - these are simple pass-throughs
# to maintain backward compatibility

def tokenize(text: str, api_client) -> list:
    """
    Simple pass-through to the API client's tokenize function.

    Args:
        text (str): The input text to tokenize.
        api_client: The API client to use for tokenization.

    Returns:
        list: A list of tokens.
    """
    return api_client.tokenize(text)

def tokenize_chunks(texts: List[str], api_client, window_size: int = 64) -> List[List[Tuple[str, int]]]:
    """
    Tokenize multiple text chunks using the API client.

    Args:
        texts (List[str]): List of text chunks to tokenize.
        api_client: The API client to use.
        window_size (int): Size of the sliding context window for token prediction.

    Returns:
        List[List[Tuple[str, int]]]: A list of lists of encoded tokens.
    """
    return api_client.tokenize_chunks(texts, window_size)
