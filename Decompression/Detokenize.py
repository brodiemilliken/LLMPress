from AI.ai_interface import AI
from typing import Tuple, List

def detokenize(tokens: List[int], model: AI) -> str:
    """
    Detokenizes the input token list using the provided AI model.
    
    Args:
        tokens (List[int]): The input token list to detokenize.
        model (AI): The AI model to use for detokenization.
        
    Returns:
        str: The detokenized text.
    """
    return model.detokenize(tokens)

def handle_explicit_token(token: int) -> str:
    return token

def handle_rank_token(rank: int, context_tokens: List[int], model: AI, k: int) -> int:
    """
    Runs AI model to see if next token lands in the top K tokens.
    
    Args:
        rank (int): The rank of the token.
        context_tokens (List[int]): The list of tokens processed so far.
        model (AI): The AI model to use.
        k (int): The number of top predictions to consider.

    Returns:
        int: The token corresponding to the rank.
    """        
    ranks = model.list_rank_tokens(context_tokens, k)
    return ranks[rank]  # Return the token at the specified rank

def handle_next_token(token: Tuple[str, int], context_tokens: List[int], model: AI, k: int) -> int:
    """
    Determines how to encode the next token based on rank prediction.
    
    Args:
        token (Tuple[str, int]): The token to process (type, value).
        context_tokens (List[int]): The list of tokens processed so far.
        model (AI): The AI model to use.
        k (int): The number of top predictions to consider.
    
    Returns:
        int: The processed token.
    """
    if token[0] == 'r':
        return handle_rank_token(token[1], context_tokens, model, k)
    else:
        return handle_explicit_token(token[1])
    
def decode_tokens(tokens: list, model: AI, k: int) -> str:
    """
    Convert a list of token IDs into a text string.
    
    Args:
        tokens (list): The input tokens to decode.
        model (AI): The AI model to use for decoding.
        k (int): The number of top predictions to consider.
        
    Returns:
        str: The decoded text string.
    """
    decoded_tokens = []
    for token in tokens:
        next_token = handle_next_token(token, decoded_tokens, model, k)
        decoded_tokens.append(next_token)
    return model.detokenize(decoded_tokens)






