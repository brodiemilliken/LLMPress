"""
==========Byte Format==========
[Explicit Flag][Double Flag][6x Payload]

Rank Byte Format:
    Used for encoding a rank byte with ranks 0 to 2^6-1
    [0][0][6x Payload]

Double Byte Format:
    Used for encoding two adjacent rank bytes with ranks 0 to 2^3-1
    [0][1][3x Payload][3x Payload]

Explicit Bytes formats:
    - 2-byte token (for values < 2^13):
        Start:  [1][0][upper 6 bits]
        Stop:   [1][7 payload bits]
    - 3-byte token (for values < 2^20):
        Start:  [1][0][top 6 bits]
        Middle: [0][7 payload bits]
        Stop:   [1][7 payload bits]
    - 4-byte token (for values < 2^27):
        Start:  [1][0][top 6 bits]
        Middle1:[0][7 payload bits]
        Middle2:[0][7 payload bits]
        Stop:   [1][7 payload bits]

Continuous Zero Byte Format:
    Used for encoding a series of continuous zeroes
    [1][1][6x Payload] where the payload represents the number of continuous zeroes
    Maximum continuous zeroes: 62 (to avoid 0xFF)

Special Tokens:
    <BREAK> Token: Used to mark chunk boundaries
    Encoded as a single byte with value 11111111 (0xFF)
"""

from typing import Tuple, List
from ..exceptions import EncodingError
from ..utils.error_handler import handle_operation_errors


def is_break_token(token: Tuple[str, int]) -> bool:
    """
    Checks if the token is a <BREAK> token.

    Args:
        token (Tuple[str, int]): The token to check.

    Returns:
        bool: True if the token is a <BREAK> token, False otherwise.
    """
    return token[0] == "<BREAK>"


def handle_break_token() -> bytes:
    """
    Handles the <BREAK> token by encoding it as a special byte.

    Returns:
        bytes: The byte representation of the <BREAK> token (0xFF).
    """
    return bytes([0xFF])  # 11111111 in binary


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


def explicit_bytes_length(bytes_data: bytes, idx: int) -> int:
    """
    Determines the length of the explicit token starting at idx using the revised format:
      - 2-byte token: Start: [1][0][6-bit payload]; Stop: [1][7 payload bits]
      - 3-byte token: Start: [1][0][6-bit payload]; Middle: [0][7 payload bits]; Stop: [1][7 payload bits]
      - 4-byte token: Start: [1][0][6-bit payload]; Middle1: [0][7 payload bits];
                     Middle2: [0][7 payload bits]; Stop: [1][7 payload bits]

    Args:
        bytes_data (bytes): The byte sequence.
        idx (int): The starting index.

    Returns:
        int: The explicit token length (2, 3, or 4).
    """
    if idx + 1 >= len(bytes_data):
        # Not enough bytes – fallback to 1 (or throw an error)
        return 1
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

    The new explicit format is:
        - 2-byte token: [1][0][6-bit payload] (start) followed by [1][7-bit payload] (stop)
          → value = (start_payload << 6) | stop_payload
        - 3-byte token: [1][0][6-bit payload] (start), [0][7-bit payload] (middle), [1][7-bit payload] (stop)
          → value = (start_payload << 13) | (middle_payload << 6) | stop_payload

    Args:
        bytes_data (bytes): The byte sequence representing the token.

    Returns:
        Tuple[str, int]: A tuple with type 'e' and the decoded token value.
    """
    value = 0
    if len(bytes_data) > 4:
        raise ValueError("Invalid explicit token length: must be 1, 2, 3, or 4 bytes.")
    if len(bytes_data) == 1:
        # Single byte explicit token
        value = bytes_data[0] & 0b00111111
    elif len(bytes_data) == 2:
        # 2-byte explicit token
        start_payload = bytes_data[0] & 0b00111111
        stop_payload = bytes_data[1] & 0b01111111  # Stop byte expected to have [1][0] flag.
        value = (start_payload << 6) | stop_payload
    elif len(bytes_data) == 3:
        # 3-byte explicit token
        start_payload = bytes_data[0] & 0b00111111
        middle_payload = bytes_data[1] & 0b01111111  # Middle byte always starts with 0.
        stop_payload = bytes_data[2] & 0b01111111
        value = (start_payload << 13) | (middle_payload << 6) | stop_payload
    elif len(bytes_data) == 4:
        # 4-byte explicit token
        start_payload = bytes_data[0] & 0b00111111
        middle_payload1 = bytes_data[1] & 0b01111111  # First middle byte always starts with 0.
        middle_payload2 = bytes_data[2] & 0b01111111  # Second middle byte always starts with 0.
        stop_payload = bytes_data[3] & 0b01111111
        value = (start_payload << 20) | (middle_payload1 << 13) | (middle_payload2 << 6) | stop_payload
    return ("e", value)


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
    if not (0 <= count <= 62):  # Maximum of 62 to avoid creating 0xFF
        # Split into multiple continuous zero tokens
        first_count = 62
        remaining_count = count - 62
        first_bytes = handle_continuous_zero_bytes(first_count)
        remaining_bytes = handle_continuous_zero_bytes(remaining_count)
        return first_bytes + remaining_bytes

    byte_value = 0b11000000 | count  # [11] + 6-bit payload
    return bytes([byte_value])


def encode_explicit_token(token: Tuple[str, int]) -> bytes:
    """
    Encodes an explicit token tuple into bytes using the revised explicit format.

    Args:
        token (Tuple[str, int]): A tuple such as ("e", value)

    Returns:
        bytes: The encoded explicit token.
    """
    val = token[1]
    if val < (1 << 13):  # 2-byte token (13 bits)
        start = 0b10000000 | ((val >> 7) & 0b00111111)
        stop = 0b10000000 | (val & 0b01111111)
        return bytes([start, stop])
    elif val < (1 << 20):  # 3-byte token (20 bits)
        start = 0b10000000 | ((val >> 14) & 0b00111111)
        middle = (val >> 7) & 0b01111111
        stop = 0b10000000 | (val & 0b01111111)
        return bytes([start, middle, stop])
    elif val < (1 << 27):  # 4-byte token (27 bits)
        start = 0b10000000 | ((val >> 21) & 0b00111111)
        middle1 = (val >> 14) & 0b01111111
        middle2 = (val >> 7) & 0b01111111
        stop = 0b10000000 | (val & 0b01111111)
        return bytes([start, middle1, middle2, stop])
    else:
        raise ValueError("Explicit token value too large.")


def encode_next_bytes(tokens: list[Tuple[str,int]]) -> bytes:
    """
    Encodes the next bytes based on the token type.

    Args:
        tokens (list[Tuple[str,int]]): The list of tokens to encode.

    Returns:
        bytes: The byte representation of the next token/tokens.
    """
    # First check for <BREAK> token
    if tokens and is_break_token(tokens[0]):
        tokens.pop(0)
        return handle_break_token()

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
        return encode_explicit_token(token)


@handle_operation_errors(
    operation_name="Token Encoding",
    specific_exceptions={
        ValueError: (EncodingError, "Invalid token value: {error_message}")
    },
    fallback_exception=EncodingError
)
def encode_tokens(tokens: List[Tuple[str,int]], window_size: int = 64) -> bytes:
    """
    Encodes a list of tokens into bytes, including the window size as the first explicit token.

    Args:
        tokens (List[Tuple[str,int]]): The list of tokens to encode.
        window_size (int): The window size to encode at the beginning of the byte stream.

    Returns:
        bytes: The byte representation of the tokens, with window size at the beginning.

    Raises:
        EncodingError: If there's an error during encoding
    """
    encoded_bytes = bytearray()

    # Encode the window size as an explicit token using the new function:
    window_size_token = ("<WINDOW_SIZE>", window_size)
    encoded_bytes.extend(encode_explicit_token(window_size_token))

    # Make a copy of the tokens list to avoid modifying the original
    tokens_copy = tokens.copy()

    # Then encode the rest of the tokens
    while tokens_copy:
        encoded_bytes.extend(encode_next_bytes(tokens_copy))

    return bytes(encoded_bytes)


