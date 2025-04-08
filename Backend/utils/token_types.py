"""
Common token type definitions for both compression and decompression.

This module provides common token type definitions and utility functions
for working with tokens in both the compression and decompression processes.
"""
from typing import Tuple, List, Union, Any, Optional

# Define token types as constants
TOKEN_TYPE_RANK = "r"
TOKEN_TYPE_EXPLICIT = "e"
TOKEN_TYPE_BREAK = "<BREAK>"

# Define a Token type as a tuple of (token_type, value)
Token = Tuple[str, int]

def create_rank_token(rank: int) -> Token:
    """
    Creates a rank token.

    Args:
        rank (int): The rank value.

    Returns:
        Token: A tuple with type 'r' and the rank value.
    """
    return (TOKEN_TYPE_RANK, rank)

def create_explicit_token(value: int) -> Token:
    """
    Creates an explicit token.

    Args:
        value (int): The token value.

    Returns:
        Token: A tuple with type 'e' and the token value.
    """
    return (TOKEN_TYPE_EXPLICIT, value)

def create_break_token() -> Token:
    """
    Creates a break token.

    Returns:
        Token: A tuple with type '<BREAK>' and value 0.
    """
    return (TOKEN_TYPE_BREAK, 0)

def is_rank_token(token: Token) -> bool:
    """
    Checks if a token is a rank token.

    Args:
        token (Token): The token to check.

    Returns:
        bool: True if the token is a rank token, False otherwise.
    """
    return token[0] == TOKEN_TYPE_RANK

def is_explicit_token(token: Token) -> bool:
    """
    Checks if a token is an explicit token.

    Args:
        token (Token): The token to check.

    Returns:
        bool: True if the token is an explicit token, False otherwise.
    """
    return token[0] == TOKEN_TYPE_EXPLICIT

def is_break_token(token: Token) -> bool:
    """
    Checks if a token is a break token.

    Args:
        token (Token): The token to check.

    Returns:
        bool: True if the token is a break token, False otherwise.
    """
    return token[0] == TOKEN_TYPE_BREAK


def split_tokens_by_breaks(tokens: List[Token]) -> List[List[Token]]:
    """
    Splits a list of tokens at <BREAK> markers.

    Args:
        tokens (List[Token]): The list of tokens to split.

    Returns:
        List[List[Token]]: A list of token chunks.
    """
    chunks = []
    current_chunk = []

    for token in tokens:
        if is_break_token(token):
            if current_chunk:  # Only add non-empty chunks
                chunks.append(current_chunk)
                current_chunk = []
        else:
            current_chunk.append(token)

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def combine_token_chunks(chunks: List[List[Token]]) -> List[Token]:
    """
    Combine multiple lists of tokenized chunks into a single flat list of tokens,
    with <BREAK> markers inserted between chunks.

    Args:
        chunks (List[List[Token]]): List of lists of token tuples

    Returns:
        List[Token]: List of token tuples with break markers between chunks
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
