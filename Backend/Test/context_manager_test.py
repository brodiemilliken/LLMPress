"""
LLMPress Operation Context Test

This script tests the operation_context context manager in more detail.
"""
import os
import sys
import logging
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import from Backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Backend.utils.error_handler import operation_context
from Backend.exceptions import LLMPressError, FileOperationError, CompressionError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ContextManagerTest')

class CustomError(Exception):
    """Custom error for testing."""
    pass

def test_basic_context():
    """Test basic context manager functionality."""
    try:
        with operation_context(
            operation_name="Basic Test",
            specific_exceptions={
                ValueError: (CustomError, "Custom error: {error_message}")
            }
        ):
            raise ValueError("Test error")
        print("❌ Test failed: Should have raised CustomError")
    except CustomError as e:
        if "Custom error: Test error" in str(e):
            print("✅ Test passed: ValueError was converted to CustomError with correct message")
        else:
            print(f"❌ Test failed: Wrong error message: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_multiple_exceptions():
    """Test context manager with multiple exception types."""
    # Test with ValueError
    try:
        with operation_context(
            operation_name="Multiple Exceptions",
            specific_exceptions={
                ValueError: (CustomError, "Custom error: {error_message}"),
                TypeError: (RuntimeError, "Runtime error: {error_message}")
            }
        ):
            raise ValueError("Value error")
        print("❌ Test failed: Should have raised CustomError")
    except CustomError as e:
        if "Custom error: Value error" in str(e):
            print("✅ Test passed: ValueError was converted to CustomError with correct message")
        else:
            print(f"❌ Test failed: Wrong error message: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

    # Test with TypeError
    try:
        with operation_context(
            operation_name="Multiple Exceptions",
            specific_exceptions={
                ValueError: (CustomError, "Custom error: {error_message}"),
                TypeError: (RuntimeError, "Runtime error: {error_message}")
            }
        ):
            raise TypeError("Type error")
        print("❌ Test failed: Should have raised RuntimeError")
    except RuntimeError as e:
        if "Runtime error: Type error" in str(e):
            print("✅ Test passed: TypeError was converted to RuntimeError with correct message")
        else:
            print(f"❌ Test failed: Wrong error message: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_default_exception():
    """Test context manager with default exception for unhandled errors."""
    try:
        with operation_context(
            operation_name="Default Exception",
            specific_exceptions={
                ValueError: (CustomError, "Custom error: {error_message}")
            },
            fallback_exception=RuntimeError
        ):
            raise KeyError("Unexpected error")
        print("❌ Test failed: Should have raised RuntimeError")
    except RuntimeError as e:
        if "Unexpected error during Default Exception" in str(e):
            print("✅ Test passed: KeyError was converted to RuntimeError with correct message")
        else:
            print(f"❌ Test failed: Wrong error message: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_llmpress_exceptions():
    """Test context manager with LLMPress exceptions."""
    # Test with FileOperationError
    try:
        with operation_context(
            operation_name="LLMPress Exceptions",
            specific_exceptions={
                ValueError: (CustomError, "Custom error: {error_message}")
            },
            fallback_exception=CompressionError
        ):
            raise FileOperationError("File error")
        print("❌ Test failed: Should have raised FileOperationError")
    except FileOperationError as e:
        print("✅ Test passed: FileOperationError was passed through unchanged")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_no_exception():
    """Test context manager with no exception."""
    result = None
    try:
        with operation_context(
            operation_name="No Exception",
            specific_exceptions={
                ValueError: (CustomError, "Custom error: {error_message}")
            }
        ):
            result = "Success!"
        if result == "Success!":
            print("✅ Test passed: Context manager completed successfully with no exception")
        else:
            print(f"❌ Test failed: Context manager did not return the correct result: {result}")
    except Exception as e:
        print(f"❌ Test failed: Unexpected exception: {type(e).__name__}: {e}")

def main():
    """Run all tests."""
    print("\n=== Testing Operation Context ===")

    print("\n1. Testing basic context manager:")
    test_basic_context()

    print("\n2. Testing multiple exceptions:")
    test_multiple_exceptions()

    print("\n3. Testing default exception:")
    test_default_exception()

    print("\n4. Testing LLMPress exceptions:")
    test_llmpress_exceptions()

    print("\n5. Testing no exception:")
    test_no_exception()

    print("\nAll context manager tests completed.")

if __name__ == "__main__":
    main()
