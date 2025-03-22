# encoder.py
# This script encodes a list of tokens into a custom byte format.
# Each token is a tuple: (is_raw, value)
#   - If is_raw is False, value is a rank (0–63) and is encoded in one byte.
#   - If is_raw is True, value is a raw token value and is encoded in a variable-length manner:
#       * Each byte uses base-64 (6-bit payload). 
#       * All bytes for a raw token have is_raw=1.
#       * For each raw token byte, the is_ascii flag (bit 6) is 0 except for the final byte,
#         which has is_ascii=1 to signal termination.

def encode_rank_token(value):
    """Encode a rank token (is_raw = 0) into a single byte.
       value must be in the range 0-63."""
    assert 0 <= value < 64, "Rank token must be between 0 and 63."
    # Bits: is_raw=0, is_ascii=0, payload = value
    return bytes([value & 0x3F])


def encode_raw_token(value):
    """Encode a raw token (is_raw = 1) using a variable-length base-64 encoding.
       The value is split into 6-bit chunks (little-endian).
       Each byte has the high bit set (is_raw=1).
       The final byte has its second-highest bit set (is_ascii=1) to signal termination."""
    result = []
    # If the value fits in 6 bits, output one byte with termination.
    if value < 64:
        result.append((1 << 7) | (1 << 6) | (value & 0x3F))
    else:
        while value >= 64:
            chunk = value & 0x3F
            # Intermediate byte: is_raw=1, is_ascii=0, payload = chunk
            result.append((1 << 7) | (0 << 6) | chunk)
            value >>= 6
        # Final byte: is_raw=1, is_ascii=1, payload = remaining value
        result.append((1 << 7) | (1 << 6) | (value & 0x3F))
    return bytes(result)


def encode_tokens(token_list):
    """Encode a list of tokens into a byte stream.
       token_list: list of tuples (is_raw, value).
       Returns a bytes object."""
    encoded_bytes = bytearray()
    for is_raw, value in token_list:
        if is_raw:
            encoded_bytes.extend(encode_raw_token(value))
        else:
            encoded_bytes.extend(encode_rank_token(value))
    return bytes(encoded_bytes)
