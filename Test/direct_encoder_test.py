#!/usr/bin/env python
"""
Direct test for encoder and decoder modules.
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DirectEncoderTest')

# Import the modules directly
sys.path.insert(0, '..')  # Add the parent directory to the path

# Direct imports
from Compression.Encoder import handle_rank_byte, handle_double_byte, encode_explicit_token
from Decompression.Decoder import handle_explicit_bytes

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

def main():
    """Run the encoder/decoder tests."""
    logger.info("=== Direct Encoder/Decoder Test ===")
    
    # Run the tests
    tests = [
        test_rank_byte,
        test_double_byte,
        test_explicit_token
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
