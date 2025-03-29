from typing import Tuple, List
from tqdm import tqdm

def detokenize(tokens: List[int], model) -> str:
    """
    Detokenizes the input token list using the provided model or API client.
    
    Args:
        tokens (List[int]): The input token list to detokenize.
        model: The model or API client to use for detokenization.
        
    Returns:
        str: The detokenized text.
    """
    return model.detokenize(tokens)

def handle_explicit_token(token: int) -> str:
    return token

def handle_rank_token(rank: int, context_tokens: List[int], model, k: int) -> int:
    """
    Runs model to see if next token lands in the top K tokens.
    
    Args:
        rank (int): The rank of the token.
        context_tokens (List[int]): The list of tokens processed so far.
        model: The model or API client to use.
        k (int): The number of top predictions to consider.

    Returns:
        int: The token corresponding to the rank.
    """        
    ranks = model.list_rank_tokens(context_tokens, k)
    return ranks[rank]  # Return the token at the specified rank

def handle_next_token(token: Tuple[str, int], context_tokens: List[int], model, k: int) -> int:
    """
    Determines how to encode the next token based on rank prediction.
    
    Args:
        token (Tuple[str, int]): The token to process (type, value).
        context_tokens (List[int]): The list of tokens processed so far.
        model: The model or API client to use.
        k (int): The number of top predictions to consider.
    
    Returns:
        int: The processed token.
    """
    if token[0] == 'r':
        return handle_rank_token(token[1], context_tokens, model, k)
    else:
        return handle_explicit_token(token[1])
    
def decode_tokens(tokens: list, model, k: int) -> str:
    """
    Convert a list of token IDs into a text string.
    
    Args:
        tokens (list): The input tokens to decode.
        model: The model or API client to use for decoding.
        k (int): The number of top predictions to consider.
        
    Returns:
        str: The decoded text string.
    """
    print(f"Decoding {len(tokens)} tokens...")
    decoded_tokens = []
    
    # Using tqdm for progress bar
    for token in tqdm(tokens, desc="Decoding", unit="tokens", ncols=80,
                     bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'):
        next_token = handle_next_token(token, decoded_tokens, model, k)
        decoded_tokens.append(next_token)
    
    return model.detokenize(decoded_tokens)






