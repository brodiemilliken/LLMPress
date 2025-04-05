from typing import Tuple, List
import ChatGPT2 as AI

def tokenize(text: str, model: AI) -> list:
    """
    Tokenizes the input text using the provided AI model.

    Args:
        text (str): The input text to tokenize.
        model (AI): The AI model to use for tokenization.

    Returns:
        list: A list of tokens.
    """
    return model.tokenize(text)

def handle_explicit_token(token: str) -> Tuple[str, int]:
    """
    Encodes a token explicitly with an 'e' marker.
    
    Args:
        token (str): The token to encode explicitly.
        
    Returns:
        Tuple[str, int]: A tuple with marker 'e' and the token as int.
    """
    return ("e", int(token))

def handle_rank_token(current_index: int, tokens: List[str], model: AI, window_size: int) -> int:
    """
    Runs AI model to see if next token lands in the top K predicted tokens.
    Uses a sliding window for context.
    
    Args:
        current_index (int): The current token index.
        tokens (List[str]): The list of tokens.
        model (AI): The AI model to use.
        window_size (int): The size of the sliding context window.

    Returns:
        int: The index of the token in the rank list (-1 if not found).
    """        
    # Use only the most recent tokens based on window_size
    start_idx = max(0, current_index - window_size)
    context_tensor = tokens[start_idx:current_index]
    next_token = tokens[current_index]
    
    ranks = model.list_rank_tokens(context_tensor)
    return ranks.index(next_token) if next_token in ranks else -1

def handle_next_token(current_index: int, tokens: List[str], model: AI, window_size: int) -> Tuple[str, int]:
    """
    Determines how to encode the next token based on rank prediction.
    
    Args:
        current_index (int): The current token index.
        tokens (List[str]): The list of tokens.
        model (AI): The AI model to use.
        window_size (int): The size of the sliding context window.
    Returns:
        Tuple[str, int]:   
            ('r', position) if found in ranks,
            ('e', token_as_int) if not found.
    """
    if current_index >= len(tokens):
        raise ValueError(f"Current index {current_index} out of bounds")
        
    position = handle_rank_token(current_index, tokens, model, window_size)
    
    if position != -1:
        return ("r", position)
    else:
        return handle_explicit_token(tokens[current_index])
    
def encode_text(text: str, model: AI, window_size: int) -> List[Tuple[str, int]]:
    """
    Encodes a text string using the AI model with a sliding context window.
    
    Args:
        text (str): The text to encode.
        model (AI): The AI model to use.
        window_size (int): The size of the sliding context window.
        
    Returns:
        List[Tuple[str, int]]: A list of encoded tokens.
    """
    tokens = tokenize(text, model)
    
    encoded_tokens = []
    encoded_tokens.append(handle_explicit_token(tokens[0]))
    
    for i in range(1, len(tokens)):
        encoded_tokens.append(handle_next_token(i, tokens, model, window_size))
        
    return encoded_tokens
