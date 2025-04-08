"""
LLMPress Error Handling Test

This script tests the error handling utilities in the codebase.
"""
import os
import sys
import logging
import tempfile
import time
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import from Backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Backend.Compression.compressor import compress
from Backend.Decompression.decompressor import decompress
from Backend.Compression.file_splitter import chunk_file, split_text
from Backend.Compression.tokenizer import tokenize, tokenize_chunks
from Backend.Compression.encoder import encode_tokens
from Backend.Decompression.decoder import decode_bytes
from Backend.Decompression.detokenizer import detokenize, detokenize_chunks
from Backend.celery import CeleryClient
from Backend.utils.error_handler import (
    handle_operation_errors,
    operation_context,
    retry_operation
)
from Backend.exceptions import (
    FileOperationError,
    CompressionError,
    DecompressionError,
    TokenizationError,
    EncodingError,
    DecodingError,
    ChunkingError,
    LLMPressError
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ErrorHandlingTest')

def test_file_not_found():
    """Test error handling for a non-existent file."""
    try:
        chunks = chunk_file("non_existent_file.txt")
        print("❌ Test failed: Should have raised FileOperationError")
    except FileOperationError as e:
        print(f"✅ Test passed: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_compression_error():
    """Test error handling for compression."""
    try:
        # Pass an invalid input type
        result = compress(123, None)
        print("❌ Test failed: Should have raised CompressionError")
    except CompressionError as e:
        print(f"✅ Test passed: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_decompression_error():
    """Test error handling for decompression."""
    try:
        # Pass an invalid input type
        result = decompress("not bytes", None)
        print("❌ Test failed: Should have raised DecompressionError")
    except DecompressionError as e:
        print(f"✅ Test passed: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_nested_error_handling():
    """Test nested error handling."""
    try:
        # This should trigger a FileOperationError in chunk_file,
        # which should be wrapped in a CompressionError
        result = compress("non_existent_file.txt", None)
        print("❌ Test failed: Should have raised CompressionError")
    except CompressionError as e:
        print(f"✅ Test passed: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_invalid_token_encoding():
    """Test error handling for token encoding with invalid values."""
    try:
        # Create a token with a value that's too large
        invalid_token = ("e", 2**30)  # Way too large for our encoding format
        result = encode_tokens([invalid_token], 64)
        print("❌ Test failed: Should have raised EncodingError")
    except EncodingError as e:
        print(f"✅ Test passed: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_empty_data_decoding():
    """Test error handling for decoding empty data."""
    try:
        # Try to decode empty bytes
        result = decode_bytes(b"")
        print("❌ Test failed: Should have raised DecodingError")
    except DecodingError as e:
        print(f"✅ Test passed: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_chunking_error():
    """Test error handling for text chunking."""
    try:
        # Pass None instead of a string
        result = split_text(None)
        print("❌ Test failed: Should have raised ChunkingError")
    except ChunkingError as e:
        print(f"✅ Test passed: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

@retry_operation(
    max_retries=3,
    retry_exceptions=[ValueError],
    base_delay=0.1,  # Short delay for testing
    operation_name="Test Retry"
)
def function_that_fails_then_succeeds():
    """Function that fails a few times then succeeds."""
    # Use a global counter to track calls
    if not hasattr(function_that_fails_then_succeeds, "counter"):
        function_that_fails_then_succeeds.counter = 0

    function_that_fails_then_succeeds.counter += 1

    # Fail on the first two calls, succeed on the third
    if function_that_fails_then_succeeds.counter < 3:
        raise ValueError(f"Intentional failure #{function_that_fails_then_succeeds.counter}")

    return "Success!"

def test_retry_decorator():
    """Test the retry_operation decorator."""
    # Reset the counter
    if hasattr(function_that_fails_then_succeeds, "counter"):
        function_that_fails_then_succeeds.counter = 0

    try:
        result = function_that_fails_then_succeeds()
        if result == "Success!":
            print(f"✅ Test passed: Retry succeeded after {function_that_fails_then_succeeds.counter} attempts")
        else:
            print(f"❌ Test failed: Unexpected result: {result}")
    except ValueError as e:
        print(f"❌ Test failed: Retry didn't work: {e}")
    except Exception as e:
        print(f"❌ Test failed: Unexpected exception: {type(e).__name__}: {e}")

# Note: Fallback functionality has been removed as it's not compatible with our compression algorithm

def test_context_manager():
    """Test the operation_context context manager."""
    try:
        with operation_context(
            operation_name="Test Operation",
            specific_exceptions={
                ValueError: (RuntimeError, "Converted error: {error_message}")
            }
        ):
            # Raise a ValueError, which should be converted to RuntimeError
            raise ValueError("Test error")
        print("❌ Test failed: Should have raised RuntimeError")
    except RuntimeError as e:
        if "Converted error: Test error" in str(e):
            print("✅ Test passed: ValueError was converted to RuntimeError with correct message")
        else:
            print(f"❌ Test failed: Wrong error message: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_file_operations_with_temp_file():
    """Test error handling with a real temporary file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write("This is a test file.\n" * 100)  # Write some content
        temp_path = temp_file.name

    try:
        # This should work
        chunks = chunk_file(temp_path, 10, 50)
        if chunks and len(chunks) > 1:
            print(f"✅ Test passed: Successfully chunked temp file into {len(chunks)} chunks")
        else:
            print(f"❌ Test failed: Chunking didn't work properly, got {len(chunks) if chunks else 0} chunks")

        # Now delete the file and try again - should fail with FileOperationError
        os.unlink(temp_path)
        chunk_file(temp_path, 10, 50)
        print("❌ Test failed: Should have raised FileOperationError after deleting the file")
    except FileOperationError as e:
        print(f"✅ Test passed: Got expected FileOperationError after deleting the file: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type after deleting the file: {type(e).__name__}")
    finally:
        # Clean up in case the test fails
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def main():
    """Run all tests."""
    print("\n=== Testing Error Handling ===")

    print("\n1. Testing file not found error:")
    test_file_not_found()

    print("\n2. Testing compression error:")
    test_compression_error()

    print("\n3. Testing decompression error:")
    test_decompression_error()

    print("\n4. Testing nested error handling:")
    test_nested_error_handling()

    print("\n5. Testing token encoding error:")
    test_invalid_token_encoding()

    print("\n6. Testing empty data decoding error:")
    test_empty_data_decoding()

    print("\n7. Testing chunking error:")
    test_chunking_error()

    print("\n8. Testing retry decorator:")
    test_retry_decorator()

    # Note: Fallback test has been removed

    print("\n10. Testing context manager:")
    test_context_manager()

    print("\n11. Testing file operations with temp file:")
    test_file_operations_with_temp_file()

    print("\nAll tests completed.")

if __name__ == "__main__":
    main()
