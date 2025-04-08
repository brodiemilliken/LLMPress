#!/usr/bin/env python
"""
Test script for the encoder and decoder modules.
"""
import os
import sys
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', force=True)
logger = logging.getLogger('EncoderDecoderTest')
logger.setLevel(logging.DEBUG)

# Add a console handler to ensure output is visible
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

print("Starting encoder/decoder test...")

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import sys
import os

# Import the modules directly
from Backend.Compression.encoder import handle_rank_byte, handle_double_byte, encode_explicit_token, encode_tokens
from Backend.Decompression.decoder import handle_explicit_bytes, decode_bytes

print("Modules imported successfully")

def test_rank_byte():
    """Test encoding and decoding a rank byte."""
    logger.info("Testing rank byte encoding/decoding...")

    # Create a rank token
    token = ("r", 42)

    # Encode the token
    encoded = handle_rank_byte(token)

    # Check the encoded value
    if encoded == bytes([42]):
        logger.info("✅ Rank byte encoded correctly: %s", encoded.hex())
    else:
        logger.error("❌ Rank byte encoded incorrectly: %s", encoded.hex())
        return False

    return True

def test_double_byte():
    """Test encoding and decoding a double byte."""
    logger.info("Testing double byte encoding/decoding...")

    # Create two rank tokens
    token1 = ("r", 3)
    token2 = ("r", 5)

    # Encode the tokens
    encoded = handle_double_byte(token1, token2)

    # Check the encoded value (3 << 3 | 5 = 24 + 5 = 29, with 0x40 flag = 0x5D)
    expected = bytes([0x40 | (3 << 3) | 5])
    if encoded == expected:
        logger.info("✅ Double byte encoded correctly: %s", encoded.hex())
    else:
        logger.error("❌ Double byte encoded incorrectly: %s, expected %s", encoded.hex(), expected.hex())
        return False

    return True

def test_explicit_token():
    """Test encoding and decoding an explicit token."""
    logger.info("Testing explicit token encoding/decoding...")

    # Create an explicit token
    token = ("e", 1000)

    # Encode the token
    encoded = encode_explicit_token(token)

    # Check the encoded value
    if len(encoded) == 2:
        logger.info("✅ Explicit token encoded with correct length: %d bytes", len(encoded))
    else:
        logger.error("❌ Explicit token encoded with incorrect length: %d bytes, expected 2", len(encoded))
        return False

    # Try to decode it
    try:
        decoded = handle_explicit_bytes(encoded)
        if decoded == token:
            logger.info("✅ Explicit token decoded correctly: %s", str(decoded))
        else:
            logger.error("❌ Explicit token decoded incorrectly: %s, expected %s", str(decoded), str(token))
            return False
    except Exception as e:
        logger.error("❌ Failed to decode explicit token: %s", str(e))
        return False

    return True

def test_encode_decode_simple():
    """Test encoding and decoding with simple rank tokens."""
    logger.info("Testing simple rank tokens encoding/decoding...")

    # Create a list of simple rank tokens
    tokens = [("r", i) for i in range(10)]

    # Encode the tokens
    encoded = encode_tokens(tokens)

    # Decode the encoded bytes
    decoded_tokens, window_size = decode_bytes(encoded)

    # Check if the decoded tokens match the original tokens
    if len(decoded_tokens) == len(tokens):
        logger.info("✅ Token count matches: %d", len(tokens))
    else:
        logger.error("❌ Token count mismatch: expected %d, got %d", len(tokens), len(decoded_tokens))

    # Check if the tokens match
    matches = sum(1 for i in range(len(tokens)) if tokens[i] == decoded_tokens[i])
    if matches == len(tokens):
        logger.info("✅ All tokens match")
    else:
        logger.error("❌ Token mismatch: %d/%d tokens match", matches, len(tokens))
        for i in range(len(tokens)):
            if i < len(decoded_tokens) and tokens[i] != decoded_tokens[i]:
                logger.error("  - Token %d: expected %s, got %s", i, tokens[i], decoded_tokens[i])

    return matches == len(tokens)

def test_encode_decode_explicit():
    """Test encoding and decoding with explicit tokens."""
    logger.info("Testing explicit tokens encoding/decoding...")

    # Create a list of explicit tokens with different sizes
    tokens = [
        ("e", 42),             # Small value (fits in 1 byte)
        ("e", 1000),           # Medium value (fits in 2 bytes)
        ("e", 100000),         # Large value (fits in 3 bytes)
        ("e", 10000000)        # Very large value (fits in 4 bytes)
    ]

    # Encode the tokens
    encoded = encode_tokens(tokens)

    # Decode the encoded bytes
    decoded_tokens, window_size = decode_bytes(encoded)

    # Check if the decoded tokens match the original tokens
    if len(decoded_tokens) == len(tokens):
        logger.info("✅ Token count matches: %d", len(tokens))
    else:
        logger.error("❌ Token count mismatch: expected %d, got %d", len(tokens), len(decoded_tokens))

    # Check if the tokens match
    matches = sum(1 for i in range(len(tokens)) if tokens[i] == decoded_tokens[i])
    if matches == len(tokens):
        logger.info("✅ All tokens match")
    else:
        logger.error("❌ Token mismatch: %d/%d tokens match", matches, len(tokens))
        for i in range(len(tokens)):
            if i < len(decoded_tokens) and tokens[i] != decoded_tokens[i]:
                logger.error("  - Token %d: expected %s, got %s", i, tokens[i], decoded_tokens[i])

    return matches == len(tokens)

def test_encode_decode_mixed():
    """Test encoding and decoding with a mix of rank and explicit tokens."""
    logger.info("Testing mixed tokens encoding/decoding...")

    # Create a list of mixed tokens
    tokens = [
        ("r", 0),              # Rank 0
        ("r", 63),             # Max rank (6 bits)
        ("e", 100),            # Small explicit value
        ("r", 10),             # Another rank
        ("e", 50000),          # Medium explicit value
        ("r", 20),             # Another rank
        ("<BREAK>", 0),        # Break token
        ("r", 30),             # Another rank
        ("e", 5000000)         # Large explicit value
    ]

    # Encode the tokens
    encoded = encode_tokens(tokens)

    # Decode the encoded bytes
    decoded_tokens, window_size = decode_bytes(encoded)

    # Check if the decoded tokens match the original tokens
    if len(decoded_tokens) == len(tokens):
        logger.info("✅ Token count matches: %d", len(tokens))
    else:
        logger.error("❌ Token count mismatch: expected %d, got %d", len(tokens), len(decoded_tokens))

    # Check if the tokens match
    matches = sum(1 for i in range(len(tokens)) if tokens[i] == decoded_tokens[i])
    if matches == len(tokens):
        logger.info("✅ All tokens match")
    else:
        logger.error("❌ Token mismatch: %d/%d tokens match", matches, len(tokens))
        for i in range(len(tokens)):
            if i < len(decoded_tokens) and tokens[i] != decoded_tokens[i]:
                logger.error("  - Token %d: expected %s, got %s", i, tokens[i], decoded_tokens[i])

    return matches == len(tokens)

def test_encode_decode_continuous_zeros():
    """Test encoding and decoding with continuous zeros."""
    logger.info("Testing continuous zeros encoding/decoding...")

    # Create a list with many continuous zeros
    tokens = [("r", 0) for _ in range(100)]

    # Encode the tokens
    encoded = encode_tokens(tokens)

    # Decode the encoded bytes
    decoded_tokens, window_size = decode_bytes(encoded)

    # Check if the decoded tokens match the original tokens
    if len(decoded_tokens) == len(tokens):
        logger.info("✅ Token count matches: %d", len(tokens))
    else:
        logger.error("❌ Token count mismatch: expected %d, got %d", len(tokens), len(decoded_tokens))

    # Check if the tokens match
    matches = sum(1 for i in range(len(tokens)) if tokens[i] == decoded_tokens[i])
    if matches == len(tokens):
        logger.info("✅ All tokens match")
    else:
        logger.error("❌ Token mismatch: %d/%d tokens match", matches, len(tokens))

    # Check the size of the encoded data (should be much smaller than 100 bytes)
    logger.info("Encoded size: %d bytes (compression ratio: %.2f)", len(encoded), len(tokens) / len(encoded))

    return matches == len(tokens)

def test_encode_decode_random():
    """Test encoding and decoding with random tokens."""
    logger.info("Testing random tokens encoding/decoding...")

    # Create a list of random tokens
    tokens = []
    for _ in range(1000):
        token_type = random.choice(["r", "e"])
        if token_type == "r":
            token_value = random.randint(0, 63)  # 6-bit rank
        else:
            token_value = random.randint(0, 1000000)  # Explicit value
        tokens.append((token_type, token_value))

    # Encode the tokens
    encoded = encode_tokens(tokens)

    # Decode the encoded bytes
    decoded_tokens, window_size = decode_bytes(encoded)

    # Check if the decoded tokens match the original tokens
    if len(decoded_tokens) == len(tokens):
        logger.info("✅ Token count matches: %d", len(tokens))
    else:
        logger.error("❌ Token count mismatch: expected %d, got %d", len(tokens), len(decoded_tokens))

    # Check if the tokens match
    matches = sum(1 for i in range(len(tokens)) if tokens[i] == decoded_tokens[i])
    match_percentage = (matches / len(tokens)) * 100
    logger.info("Match percentage: %.2f%% (%d/%d tokens match)", match_percentage, matches, len(tokens))

    return match_percentage > 99.9  # Allow for a tiny margin of error

def main():
    """Run the encoder/decoder tests."""
    logger.info("=== Encoder/Decoder Test ===")

    # Run the tests
    tests = [
        test_rank_byte,
        test_double_byte,
        test_explicit_token,
        test_encode_decode_simple,
        test_encode_decode_explicit,
        test_encode_decode_mixed,
        test_encode_decode_continuous_zeros,
        test_encode_decode_random
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            logger.error("❌ Test %s failed with error: %s", test.__name__, str(e))
            results.append(False)

    # Print summary
    logger.info("=== Test Summary ===")
    for i, test in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        logger.info("%s: %s", test.__name__, status)

    # Overall result
    if all(results):
        logger.info("✅ All tests passed!")
    else:
        logger.error("❌ Some tests failed!")

    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
