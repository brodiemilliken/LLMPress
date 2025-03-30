from typing import List, Tuple

def encode_text(text: str, api_client, k: int = 64) -> List[Tuple[str, int]]:
    """
    Encode text by using the API.
    
    Args:
        text (str): The text to encode.
        api_client: The API client to use.
        k (int): The number of top predictions to consider.
        
    Returns:
        List[Tuple[str, int]]: A list of encoded tokens.
    """
    # Simply pass the request to the API client
    return api_client.tokenize(text)

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
