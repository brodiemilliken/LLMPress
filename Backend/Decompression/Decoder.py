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

Special Tokens:
    <BREAK> Token: Used to mark chunk boundaries
    Encoded as a single byte with value 11111111 (0xFF)
"""

from typing import Tuple, List
from ..exceptions import DecodingError
from ..utils.error_handler import handle_operation_errors

def handle_break_token() -> Tuple[str, int]:
    """
    Handles the special <BREAK> token (0xFF).

    Returns:
        Tuple[str, int]: A tuple with the special token "<BREAK>" and a value of 0.
    """
    return ("<BREAK>", 0)

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
    Determines the length of the explicit token starting at idx.

    Args:
        bytes_data (bytes): The byte sequence.
        idx (int): The starting index.

    Returns:
        int: The explicit token length (2, 3, or 4).
    """
    if idx + 1 >= len(bytes_data):
        return 1  # Fallback, though normally explicit tokens are at least 2 bytes.

    # Check the second byte
    if (bytes_data[idx+1] & 0b10000000) != 0:
        return 2  # 2-byte token: second byte is stop (msb=1)
    else:
        # Byte at idx+1 is a middle byte (msb=0). Check byte at idx+2.
        if idx + 2 < len(bytes_data):
            if (bytes_data[idx+2] & 0b10000000) != 0:
                return 3  # 3-byte token: third byte is stop (msb=1)
            else:
                # Both idx+1 and idx+2 are middle bytes. Now, if byte at idx+3 exists and is stop:
                if idx + 3 < len(bytes_data) and ((bytes_data[idx+3] & 0b10000000) != 0):
                    return 4  # 4-byte token
                else:
                    # Fallback if not enough bytes – default to 3-byte token
                    return 3
        else:
            # Not enough bytes after middle – fallback to 2
            return 2

def handle_explicit_bytes(bytes_data: bytes) -> Tuple[str, int]:
    """
    Decodes an explicit token.
    
    Args:
        bytes_data (bytes): The byte sequence representing the token.

    Returns:
        Tuple[str, int]: A tuple with type 'e' and the decoded token value.

    Raises:
        ValueError: If the token length is invalid or the byte format is incorrect.
    """
    if not bytes_data:
        raise ValueError("Empty bytes provided for explicit token decoding")

    if len(bytes_data) > 4:
        raise ValueError(f"Invalid explicit token length: must be 1-4 bytes, got {len(bytes_data)}.")

    # Validate the first byte has the explicit token flag
    if (bytes_data[0] & 0b10000000) == 0:
        raise ValueError(f"First byte of explicit token must have MSB set, got {bin(bytes_data[0])}")

    if len(bytes_data) == 1:
        # Single byte explicit token
        value = bytes_data[0] & 0b00111111
        return ("e", value)

    elif len(bytes_data) == 2:
        # 2-byte explicit token
        start_payload = bytes_data[0] & 0b00111111

        # Validate the stop byte has the stop flag
        if (bytes_data[1] & 0b10000000) == 0:
            raise ValueError(f"Stop byte must have MSB set, got {bin(bytes_data[1])}")

        stop_payload = bytes_data[1] & 0b01111111
        value = (start_payload << 7) | stop_payload
        return ("e", value)

    elif len(bytes_data) == 3:
        # 3-byte explicit token
        start_payload = bytes_data[0] & 0b00111111

        # Validate the middle byte doesn't have the stop flag
        if (bytes_data[1] & 0b10000000) != 0:
            raise ValueError(f"Middle byte must not have MSB set, got {bin(bytes_data[1])}")

        # Validate the stop byte has the stop flag
        if (bytes_data[2] & 0b10000000) == 0:
            raise ValueError(f"Stop byte must have MSB set, got {bin(bytes_data[2])}")

        middle_payload = bytes_data[1] & 0b01111111
        stop_payload = bytes_data[2] & 0b01111111
        value = (start_payload << 14) | (middle_payload << 7) | stop_payload
        return ("e", value)

    elif len(bytes_data) == 4:
        # 4-byte explicit token
        start_payload = bytes_data[0] & 0b00111111

        # Validate the middle bytes don't have the stop flag
        if (bytes_data[1] & 0b10000000) != 0:
            raise ValueError(f"First middle byte must not have MSB set, got {bin(bytes_data[1])}")
        if (bytes_data[2] & 0b10000000) != 0:
            raise ValueError(f"Second middle byte must not have MSB set, got {bin(bytes_data[2])}")

        # Validate the stop byte has the stop flag
        if (bytes_data[3] & 0b10000000) == 0:
            raise ValueError(f"Stop byte must have MSB set, got {bin(bytes_data[3])}")

        middle_payload1 = bytes_data[1] & 0b01111111
        middle_payload2 = bytes_data[2] & 0b01111111
        stop_payload = bytes_data[3] & 0b01111111
        value = (start_payload << 21) | (middle_payload1 << 14) | (middle_payload2 << 7) | stop_payload
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

    # Check for special <BREAK> token (0xFF)
    if bytes_data[idx] == 0xFF:
        return [handle_break_token()], idx + 1

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

def extract_window_size(data: bytes) -> Tuple[int, int]:
    """
    Extracts the window size from the beginning of the encoded data.

    Args:
        data (bytes): The binary data to extract the window size from.

    Returns:
        Tuple[int, int]: A tuple containing:
            - The extracted window size (default 64 if not found)
            - The updated index after the window size token
    """
    idx = 0

    if len(data) >= 2:  # We need at least 2 bytes for an explicit token
        # Check if the first byte indicates an explicit token
        if (data[0] & 0b11000000) == 0b10000000:
            length = explicit_bytes_length(data, 0)
            if length <= len(data):
                token_type, token_value = handle_explicit_bytes(data[0:length])
                idx = length  # Move past the window size token
                return token_value, idx

    # Default window size if no valid token found
    return 64, idx

@handle_operation_errors(
    operation_name="Binary Decoding",
    specific_exceptions={
        ValueError: (DecodingError, "Invalid byte format: {error_message}")
    },
    fallback_exception=DecodingError
)
def decode_bytes(data: bytes) -> Tuple[List[Tuple[str,int]], int]:
    """
    Decodes binary data into a list of token tuples and extracts the window size.

    Args:
        data (bytes): The binary data to decode.

    Returns:
        Tuple[List[Tuple[str,int]], int]: A tuple containing:
            - A list of tuples with the type and rank or token value
            - The window size extracted from the beginning of the data

    Raises:
        DecodingError: If there's an error during decoding
    """
    if not data:
        raise DecodingError("Empty data provided for decoding")

    tokens = []

    # Extract the window size from the beginning of the data
    window_size, idx = extract_window_size(data)

    # Continue decoding the rest of the tokens
    while idx < len(data):
        new_tokens, new_idx = handle_next_bytes(data, idx)
        if new_idx == idx:  # Prevent infinite loops
            idx += 1
        else:
            idx = new_idx
        tokens.extend(new_tokens)

    return tokens, window_size
