from typing import Tuple, List
from tqdm import tqdm

def tokenize(text: str, model) -> list:
    """
    Tokenizes the input text using the provided model or API client.

    Args:
        text (str): The input text to tokenize.
        model: The model or API client to use for tokenization.

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

def handle_rank_token(current_index: int, tokens: List[str], model, k: int) -> int:
    """
    Runs model to see if next token lands in the top K tokens.
    
    Args:
        current_index (int): The current token index.
        tokens (List[str]): The list of tokens.
        model: The model or API client to use.
        k (int): The number of top predictions to consider.

    Returns:
        int: The index of the token in the rank list (-1 if not found).
    """        
    context_tensor = tokens[:current_index]
    next_token = tokens[current_index]
    ranks = model.list_rank_tokens(context_tensor, k)
    return ranks.index(next_token) if next_token in ranks else -1

def handle_next_token(current_index: int, tokens: List[str], model, k: int) -> Tuple[str, int]:
    """
    Determines how to encode the next token based on rank prediction.
    
    Args:
        current_index (int): The current token index.
        tokens (List[str]): The list of tokens.
        model: The model or API client to use.
        k (int): The number of top predictions to consider.
    Returns:
        Tuple[str, int]:   
            ('r', position) if found in ranks,
            ('e', token_as_int) if not found.
    """
    if current_index >= len(tokens):
        raise ValueError(f"Current index {current_index} out of bounds")
        
    position = handle_rank_token(current_index, tokens, model, k)
    
    if position != -1:
        return ("r", position)
    else:
        return handle_explicit_token(tokens[current_index])
    
def encode_text(text: str, model, k: int) -> List[Tuple[str, int]]:
    """
    Encodes a text string using the model or API client.
    
    Args:
        text (str): The text to encode.
        model: The model or API client to use.
        k (int): The number of top predictions to consider.
        
    Returns:
        List[Tuple[str, int]]: A list of encoded tokens.
    """
    print("Tokenizing text...")
    tokens = tokenize(text, model)
    total_tokens = len(tokens)
    
    print(f"Encoding {total_tokens} tokens...")
    encoded_tokens = []
    encoded_tokens.append(handle_explicit_token(tokens[0]))
    
    # Using tqdm for progress bar
    for i in tqdm(range(1, total_tokens), desc="Encoding", unit="tokens", ncols=80, 
                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'):
        encoded_tokens.append(handle_next_token(i, tokens, model, k))
        
    return encoded_tokens
