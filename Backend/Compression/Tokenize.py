from typing import List, Tuple

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
