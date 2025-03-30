from typing import List, Tuple

def decode_tokens(tokens: List[Tuple[str, int]], api_client, k: int = 64) -> str:
    """
    Convert a list of encoded tokens into text by using the API.
    
    Args:
        tokens (List[Tuple[str, int]]): The input tokens to decode.
        api_client: The API client to use for decoding.
        k (int): The number of top predictions to consider.
        
    Returns:
        str: The decoded text string.
    """
    # Simply pass the request to the API client
    return api_client.detokenize(tokens)
    
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






