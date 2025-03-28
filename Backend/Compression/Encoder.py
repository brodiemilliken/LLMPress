"""
==========Byte Format==========
[Explicit Flag][Double Flag][6x Payload]

Rank Byte Format:
    Used for encoding a rank byte with ranks 0 to 2^6-1
    [0][0][6x Payload]

Double Byte Format:
    Used for encoding two adjacent rank bytes with ranks 0 to 2^3-1
    [0][1][3x Payload][3x Payload]

Exlpicit Byte Format:
    Used for encoding an explicit token that requires an unknown number of bits
    Start Byte: [1][0][6x Payload] (maximum token size: 2^6-1)
    Middle/End Byte: [Stop Flag][7x Payload] (2 bytes maximum token size: 2^13-1, 3 bytes maximum token size: 2^20-1)

Continuous Zero Byte Format:
    Used for encoding a series of continuous zeroes
    [1][1][6x Payload] where the payload represents the number of continuous zeroes
"""

from typing import Tuple


def handle_rank_byte(token: Tuple[str,int]) -> bytes:
    """
    Handles the rank byte case.

    Args:
        rank (int): The rank to handle in range 0-63.
    
    Returns:
        bytes: The byte representation of the rank.
    """
    rank = token[1]
    if not (0 <= rank <= 63):
        raise ValueError("Rank must be in the range 0-63.")
    return bytes([0b00000000 | rank])  # Encodes integers 0-63 (6 bits) in a single byte

def check_double_byte(token1: Tuple[str, int], token2: Tuple[str, int]) -> bool:
    """
    Checks if two tokens can be encoded as a double byte.
    
    Args:
        token1 (Tuple[str, int]): The first token to check.
        token2 (Tuple[str, int]): The second token to check.
        
    Returns:
        bool: True if both tokens can be encoded as a double byte, False otherwise.
    """
    return token1[0] == "r" and token2[0] == "r" and token1[1] < 8 and token2[1] < 8

def handle_double_byte(token1: Tuple[str,int], token2: Tuple[str,int]) -> bytes:
    """
    Handles the double byte case.
    
    Args:
        rank1 (int): The first rank to handle in range 0-7.
        rank2 (int): The second rank to handle in range 0-7.
        
    Returns:
        bytes: The byte representation of the ranks.
    """
    rank1 = token1[1]
    rank2 = token2[1]
    if not (0 <= rank1 <= 7 and 0 <= rank2 <= 7):
        raise ValueError("Both ranks must be in the range 0-7.")
    return bytes([0b01000000 | (rank1 << 3) | rank2])  # Encodes two adjacent ranks in a single byte

def handle_explicit_bytes(token: Tuple[str,int]) -> bytes:
    """
    Handles the explicit token case.
    
    Args:
        token: Tuple[str,int]: The token to handle.
        
    Returns:
        bytes: The byte representation of the token.
    """
    val = token[1]
    bit_length = val.bit_length()
    
    if bit_length <= 7:
        # For values under 7 bits, use an empty start byte and put all bits in end byte
        start_byte = 0b10000000  # Start byte with [1][0] and empty payload
        end_byte = 0b10000000 | val  # End byte with stop flag [1] and the value as payload
        return bytes([start_byte, end_byte])
    elif bit_length <= 13:
        # For values with 7-13 bits, distribute the bits between two bytes
        start_byte = 0b10000000 | (val >> 7)  # Start byte with [1][0] and 6-bit payload
        end_byte = 0b10000000 | (val & 0b01111111)  # End byte with stop flag [1] and 7-bit payload
        return bytes([start_byte, end_byte])
    elif bit_length <= 20:
        # For values with 14-20 bits, use three bytes
        start_byte = 0b10000000 | (val >> 14)  # Start byte with most significant 6 bits
        middle_byte = 0b00000000 | ((val >> 7) & 0b01111111)  # Middle byte with next 7 bits
        end_byte = 0b10000000 | (val & 0b01111111)  # End byte with least significant 7 bits
        return bytes([start_byte, middle_byte, end_byte])
    
    # Handle larger tokens
    return bytes([0b10111111, 0b10111111])  # Placeholder for larger tokens

def count_leading_zeros(tokens: list[Tuple[str,int]]) -> int:
    """
    Counts the number of leading zeroes in the token list until the first non-zero or explicit token.

    Args:
        tokens (list[Tuple[str,int]]): The token list to check.

    Returns:
        int: The count of leading zeroes.
    """
    count = 0
    for token in tokens:
        if token[0] == "r" and token[1] == 0:
            count += 1
        else:
            break
    return count 

def handle_continuous_zero_bytes(count: int) -> bytes:
    """
    Handles the continuous zero byte case.
    
    Args:
        count (int): The number of continuous zeroes to handle.
        
    Returns:
        bytes: The byte representation of the continuous zeroes.
    """
    if not (0 <= count <= 63):
        raise ValueError("Count must be in the range 0-63.")
    return bytes([0b11000000 | count])  # Encodes integers 0-63 (6 bits) in a single byte

def encode_next_bytes(tokens: list[Tuple[str,int]]) -> bytes:
    """
    Encodes the next bytes based on the token type.

    Args:
        tokens (list[Tuple[str,int]]): The list of tokens to encode.
    
    Returns:
        bytes: The byte representation of the next token/tokens.
    """
    leading_zeros = count_leading_zeros(tokens)
    if leading_zeros >= 2:
        for _ in range(leading_zeros):
            tokens.pop(0)
        return handle_continuous_zero_bytes(leading_zeros)
    if len(tokens) > 1 and check_double_byte(tokens[0], tokens[1]):
        token1 = tokens.pop(0)
        token2 = tokens.pop(0)
        return handle_double_byte(token1, token2)
    if tokens[0][0] == "r":
        token = tokens.pop(0)
        return handle_rank_byte(token)
    else:
        token = tokens.pop(0)
        return handle_explicit_bytes(token)
    

def encode_tokens(tokens: list[Tuple[str,int]]) -> bytes:
    """
    Encodes a list of tokens into bytes.

    Args:
        tokens (list[Tuple[str,int]]): The list of tokens to encode.

    Returns:
        bytes: The byte representation of the tokens.
    """
    encoded_bytes = bytearray()
    while tokens:
        encoded_bytes.extend(encode_next_bytes(tokens))
    return bytes(encoded_bytes)
   