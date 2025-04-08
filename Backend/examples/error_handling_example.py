"""
LLMPress Error Handling Examples

This module demonstrates how to use the error handling utilities.
"""
import os
import sys
import logging

# Add the parent directory to the path so we can import from Backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Backend.utils.error_handler import (
    handle_operation_errors,
    operation_context,
    retry_operation,
    log_exception
)
from Backend.exceptions import (
    FileOperationError,
    TokenizationError,
    CompressionError
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ErrorHandlingExample')

# Example 1: Using the handle_operation_errors decorator
@handle_operation_errors(
    operation_name="File Reading",
    specific_exceptions={
        FileNotFoundError: (FileOperationError, "File not found: {error_message}"),
        PermissionError: (FileOperationError, "Permission denied: {error_message}")
    }
)
def read_file(file_path):
    """Read a file with standardized error handling."""
    with open(file_path, 'r') as f:
        return f.read()

# Example 2: Using the operation_context context manager
def process_file(file_path):
    """Process a file with standardized error handling."""
    with operation_context(
        operation_name="File Processing",
        specific_exceptions={
            FileNotFoundError: (FileOperationError, "File not found: {error_message}"),
            PermissionError: (FileOperationError, "Permission denied: {error_message}")
        }
    ):
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()

        # Process the content
        processed_content = content.upper()

        return processed_content

# Example 3: Using the retry_operation decorator
@retry_operation(
    max_retries=3,
    retry_exceptions=[ConnectionError, TimeoutError],
    operation_name="API Request"
)
def call_api(url):
    """Call an API with retry logic."""
    # Simulate an API call that might fail
    import random
    if random.random() < 0.7:  # 70% chance of failure on first attempt
        raise ConnectionError("Connection refused")
    return {"status": "success"}

# Note: Fallback functionality has been removed as it's not compatible with our compression algorithm

def main():
    """Run the examples."""
    # Example 1: handle_operation_errors decorator
    print("\n=== Example 1: handle_operation_errors decorator ===")
    try:
        content = read_file("non_existent_file.txt")
        print(f"File content: {content}")
    except FileOperationError as e:
        print(f"Caught expected error: {e}")

    # Example 2: operation_context context manager
    print("\n=== Example 2: operation_context context manager ===")
    try:
        content = process_file("non_existent_file.txt")
        print(f"Processed content: {content}")
    except FileOperationError as e:
        print(f"Caught expected error: {e}")

    # Example 3: retry_operation decorator
    print("\n=== Example 3: retry_operation decorator ===")
    try:
        result = call_api("https://example.com/api")
        print(f"API result: {result}")
    except ConnectionError as e:
        print(f"API call failed after retries: {e}")

    # Note: Fallback example has been removed

if __name__ == "__main__":
    main()
