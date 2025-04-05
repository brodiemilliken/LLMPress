from typing import Tuple, List
import ChatGPT2 as AI

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

def handle_rank_token(rank: int, context_tokens: List[int], model: AI, window_size: int) -> int:
    """
    Runs AI model to see if next token lands in the top K tokens.
    Uses a sliding window for context.
    
    Args:
        rank (int): The rank of the token.
        context_tokens (List[int]): The list of tokens processed so far.
        model (AI): The AI model to use.
        window_size (int): The size of the sliding context window.

    Returns:
        int: The token corresponding to the rank.
    """        
    # Use only the most recent tokens based on window_size
    start_idx = max(0, len(context_tokens) - window_size)
    window_context = context_tokens[start_idx:]
    
    ranks = model.list_rank_tokens(window_context)
    return ranks[rank]  # Return the token at the specified rank

def handle_next_token(token: Tuple[str, int], context_tokens: List[int], model: AI, window_size: int) -> int:
    """
    Determines how to encode the next token based on rank prediction.
    
    Args:
        token (Tuple[str, int]): The token to process (type, value).
        context_tokens (List[int]): The list of tokens processed so far.
        model (AI): The AI model to use.
        window_size (int): The size of the sliding context window.
    
    Returns:
        int: The processed token.
    """
    if token[0] == 'r':
        return handle_rank_token(token[1], context_tokens, model, window_size)
    else:
        return handle_explicit_token(token[1])
    
def decode_tokens(tokens: list, model: AI, window_size: int) -> str:
    """
    Convert a list of token IDs into a text string using a sliding context window.
    
    Args:
        tokens (list): The input tokens to decode.
        model (AI): The AI model to use for decoding.
        window_size (int): The size of the sliding context window.
        
    Returns:
        str: The decoded text string.
    """
    decoded_tokens = []
    
    for token in tokens:
        next_token = handle_next_token(token, decoded_tokens, model, window_size)
        decoded_tokens.append(next_token)
            
    return model.detokenize(decoded_tokens)






