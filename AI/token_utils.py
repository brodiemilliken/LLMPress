"""
Token handling utilities for the AI side.

This module provides all functions for tokenization and detokenization
used by the LLMPress AI system.
"""
from typing import Tuple, List, Any
import ChatGPT2 as AI

# Token type constants
TOKEN_TYPE_RANK = "r"
TOKEN_TYPE_EXPLICIT = "e"
TOKEN_TYPE_BREAK = "<BREAK>"

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

def create_explicit_token(token: Any) -> Tuple[str, int]:
    """
    Creates an explicit token.

    Args:
        token (Any): The token value.

    Returns:
        Tuple[str, int]: A tuple with type TOKEN_TYPE_EXPLICIT and the token as int.
    """
    return (TOKEN_TYPE_EXPLICIT, int(token))

def create_rank_token(rank: int) -> Tuple[str, int]:
    """
    Creates a rank token.

    Args:
        rank (int): The rank value.

    Returns:
        Tuple[str, int]: A tuple with type TOKEN_TYPE_RANK and the rank value.
    """
    return (TOKEN_TYPE_RANK, rank)

def create_break_token() -> Tuple[str, int]:
    """
    Creates a break token.

    Returns:
        Tuple[str, int]: A tuple with type TOKEN_TYPE_BREAK and value 0.
    """
    return (TOKEN_TYPE_BREAK, 0)

def find_token_rank(current_index: int, tokens: List[Any], model: AI, window_size: int) -> int:
    """
    Runs AI model to see if next token lands in the top K predicted tokens.
    Uses a sliding window for context.

    Args:
        current_index (int): The current token index.
        tokens (List[Any]): The list of tokens.
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

def handle_token_for_encoding(current_index: int, tokens: List[Any], model: AI, window_size: int) -> Tuple[str, int]:
    """
    Determines how to encode a token based on rank prediction.

    Args:
        current_index (int): The current token index.
        tokens (List[Any]): The list of tokens.
        model (AI): The AI model to use.
        window_size (int): The size of the sliding context window.
    Returns:
        Tuple[str, int]:
            (TOKEN_TYPE_RANK, position) if found in ranks,
            (TOKEN_TYPE_EXPLICIT, token_as_int) if not found.
    """
    if current_index >= len(tokens):
        raise ValueError(f"Current index {current_index} out of bounds")

    position = find_token_rank(current_index, tokens, model, window_size)

    if position != -1:
        return create_rank_token(position)
    else:
        return create_explicit_token(tokens[current_index])


# Detokenization functions
def handle_token_for_decoding(token: Tuple[str, int], context_tokens: List[int], model: AI, window_size: int) -> int:
    """
    Determines how to decode a token based on its type.

    Args:
        token (Tuple[str, int]): The token to process (type, value).
        context_tokens (List[int]): The list of tokens processed so far.
        model (AI): The AI model to use.
        window_size (int): The size of the sliding context window.

    Returns:
        int: The processed token.
    """
    if token[0] == TOKEN_TYPE_RANK:
        # Handle rank token - get the token at the specified rank
        rank = token[1]
        # Use only the most recent tokens based on window_size
        start_idx = max(0, len(context_tokens) - window_size)
        window_context = context_tokens[start_idx:]

        ranks = model.list_rank_tokens(window_context)
        return ranks[rank]  # Return the token at the specified rank
    elif token[0] == TOKEN_TYPE_EXPLICIT:
        # Handle explicit token - just return the value
        return token[1]
    elif token[0] == TOKEN_TYPE_BREAK:
        # Skip break tokens
        return None
    else:
        raise ValueError(f"Unknown token type: {token[0]}")

def decode_tokens(tokens: List[Tuple[str, int]], model: AI, window_size: int = 64) -> str:
    """
    Convert a list of token IDs into a text string using a sliding context window.

    Args:
        tokens (List[Tuple[str, int]]): The input tokens to decode.
        model (AI): The AI model to use for decoding.
        window_size (int): The size of the sliding context window.

    Returns:
        str: The decoded text string.
    """
    decoded_tokens = []

    for token in tokens:
        next_token = handle_token_for_decoding(token, decoded_tokens, model, window_size)
        if next_token is not None:  # Skip None values (from break tokens)
            decoded_tokens.append(next_token)

    return detokenize(decoded_tokens, model)


def split_tokens_by_breaks(tokens: List[Tuple[str, int]]) -> List[List[Tuple[str, int]]]:
    """
    Splits a list of tokens at <BREAK> markers.

    Args:
        tokens (List[Tuple[str, int]]): The list of tokens to split.

    Returns:
        List[List[Tuple[str, int]]]: A list of token chunks.
    """
    chunks = []
    current_chunk = []

    for token in tokens:
        if token[0] == TOKEN_TYPE_BREAK:
            if current_chunk:  # Only add non-empty chunks
                chunks.append(current_chunk)
                current_chunk = []
        else:
            current_chunk.append(token)

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def combine_token_chunks(chunks: List[List[Tuple[str, int]]]) -> List[Tuple[str, int]]:
    """
    Combine multiple lists of tokenized chunks into a single flat list of tokens,
    with <BREAK> markers inserted between chunks.

    Args:
        chunks (List[List[Tuple[str, int]]]): List of lists of token tuples

    Returns:
        List[Tuple[str, int]]: List of token tuples with break markers between chunks
    """
    if not chunks:
        return []

    # Special break token to mark chunk boundaries
    break_token = create_break_token()

    combined_tokens = []

    # Add first chunk
    if chunks[0]:
        combined_tokens.extend(chunks[0])

    # Add remaining chunks with break tokens in between
    for chunk in chunks[1:]:
        combined_tokens.append(break_token)  # Add break token between chunks
        if chunk:  # Only add non-empty chunks
            combined_tokens.extend(chunk)

    return combined_tokens


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
    # First token is always encoded explicitly
    encoded_tokens.append(create_explicit_token(tokens[0]))

    # Encode remaining tokens using rank prediction when possible
    for i in range(1, len(tokens)):
        encoded_tokens.append(handle_token_for_encoding(i, tokens, model, window_size))

    return encoded_tokens
