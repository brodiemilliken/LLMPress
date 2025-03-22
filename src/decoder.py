# decoder.py
# This script decodes the custom byte format produced by encoder.py back into a list of tokens.
# It reads a binary file ("encoded.bin") and prints the recovered tokens.

def decode_byte_stream(byte_stream):
    """Decode the byte stream into a list of tokens.
       Returns a list of tuples (is_raw, value)."""
    tokens = []
    i = 0
    n = len(byte_stream)
    while i < n:
        byte = byte_stream[i]
        is_raw = (byte >> 7) & 1
        if is_raw == 0:
            # Rank token: the payload is the rank value (bits 5-0)
            value = byte & 0x3F
            tokens.append((False, value))
            i += 1
        else:
            # Raw token: decode a variable-length value.
            raw_value = 0
            shift = 0
            # Continue reading bytes until we encounter a byte with is_ascii = 1.
            while True:
                b = byte_stream[i]
                payload = b & 0x3F
                raw_value |= (payload << shift)
                shift += 6
                # Check if this byte is the terminator (both is_raw and is_ascii are 1).
                ascii_flag = (b >> 6) & 1
                i += 1
                if ascii_flag == 1:
                    break
                if i >= n:
                    raise ValueError("Unexpected end of stream while decoding a raw token.")
            tokens.append((True, raw_value))
    return tokens
