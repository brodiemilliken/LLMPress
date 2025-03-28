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

from typing import Tuple, List
from typing import Tuple, List, Union

def handle_rank_byte(byte: int) -> Tuple[str, int]:
    """
    Handles the rank byte case.
    
    Args:
        byte (int): The byte value to handle.
        
    Returns:
        Tuple[str, int]: A tuple with the type 'r' and the rank value.
    """
    rank = byte & 0b00111111  # Extract the last 6 bits
    return ("r", rank)

def handle_double_byte(byte: int) -> list[Tuple[str,int]]:
    """
    Handles the double byte case.
    
    Args:
        byte (int): The byte value to handle.
        
    Returns:
        list[Tuple[str,int]]: A list of tuples with the type 'r' and the rank values.
    """
    rank1 = (byte & 0b00111000) >> 3  # Extract bits 3-5 and shift right
    rank2 = byte & 0b00000111  # Extract the last 3 bits
    return [("r", rank1), ("r", rank2)]

def explicit_bytes_length(bytes_data: bytes, idx: int) -> int:
    """
    Determines the length of the explicit bytes.
    
    Args:
        bytes_data (bytes): The byte data to check.
        idx (int): The index of the byte to check.
        
    Returns:
        int: The length of the explicit bytes (2 or 3).
    """
    if idx + 1 < len(bytes_data) and (bytes_data[idx+1] & 0b10000000):  # Check if the first bit is set
        return 2
    elif idx + 2 < len(bytes_data):
        return 3
    return 2  # Default to 2 if we're at the end of the data

def handle_explicit_bytes(bytes_data: bytes) -> Tuple[str, int]:
    """
    Handles the explicit byte case.
    
    Args:
        bytes_data (bytes): The relevant bytes for decoding (2 or 3 bytes)
        
    Returns:
        Tuple[str, int]: A tuple with the type 'e' and the token value
    """
    first_byte = bytes_data[0]
    second_byte = bytes_data[1]
    
    # Extract the 6-bit payload from first byte
    first_payload = first_byte & 0b00111111
    
    # Extract the payload from second byte
    second_payload = second_byte & 0b01111111
    
    if len(bytes_data) == 2:  # Two bytes format
        # Combine payloads from first and second bytes
        value = (first_payload << 7) | second_payload
    else:  # Three bytes format
        # Process the third byte
        third_byte = bytes_data[2]
        third_payload = third_byte & 0b01111111
        
        # Combine payloads from all three bytes
        value = (first_payload << 14) | (second_payload << 7) | third_payload
    
    return ("e", value)

def handle_continuous_zero_byte(byte: int) -> Tuple[List[Tuple[str,int]], int]:
    """
    Handles the continuous zero byte case.
    
    Args:
        byte (int): The byte value to handle.
        
    Returns:
        Tuple[List[Tuple[str,int]], int]: A tuple containing:
            - A list of tuples with the type 'r' and the rank 0
            - The count of continuous zeroes (for index advancement)
    """
    count = byte & 0b00111111  # Extract the last 6 bits
    return [("r", 0) for _ in range(count)], 1  # Return zeroes and advance 1 byte

def handle_next_bytes(bytes_data: bytes, idx: int) -> Tuple[List[Tuple[str,int]], int]:
    """
    Handles the next bytes based on the byte format.
    
    Args:
        bytes_data (bytes): The byte data to handle.
        idx (int): The index of the byte to check.
        
    Returns:
        Tuple[List[Tuple[str,int]], int]: A tuple containing:
            - A list of tuples with the type and rank or token value
            - The updated index after processing the bytes
    """
    if idx >= len(bytes_data):
        return [], idx  # Safety check for end of data
        
    if (bytes_data[idx] & 0b11000000) == 0b00000000:  # Rank byte
        return [handle_rank_byte(bytes_data[idx])], idx + 1
    elif (bytes_data[idx] & 0b11000000) == 0b01000000:  # Double byte
        return handle_double_byte(bytes_data[idx]), idx + 1
    elif (bytes_data[idx] & 0b11000000) == 0b10000000:  # Explicit byte
        length = explicit_bytes_length(bytes_data, idx)
        if idx + length <= len(bytes_data):  # Safety check
            return [handle_explicit_bytes(bytes_data[idx:idx+length])], idx + length
        else:
            return [("e", 0)], len(bytes_data)  # Fallback at end of data
    elif (bytes_data[idx] & 0b11000000) == 0b11000000:  # Continuous zero byte
        tokens, count = handle_continuous_zero_byte(bytes_data[idx])
        return tokens, idx + count
    else:
        # Default case to prevent infinite loops
        return [], idx + 1

def decode_bytes(data: bytes) -> list[Tuple[str,int]]:
    """
    Decodes binary data into a list of token tuples.
    
    Args:
        data (bytes): The binary data to decode.
        
    Returns:
        list[Tuple[str,int]]: A list of tuples with the type and rank or token value.
    """
    tokens = []
    idx = 0
    while idx < len(data):
        new_tokens, new_idx = handle_next_bytes(data, idx)
        if new_idx == idx:  # Prevent infinite loops
            idx += 1
        else:
            idx = new_idx
        tokens.extend(new_tokens)
    return tokens
