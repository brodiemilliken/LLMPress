"""
LLMPress Retry Decorator Test

This script tests the retry_operation decorator in more detail.
"""
import os
import sys
import time
import logging
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import from Backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Backend.utils.error_handler import retry_operation

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RetryTest')

# Test 1: Function that always fails
@retry_operation(
    max_retries=3,
    retry_exceptions=[ValueError],
    base_delay=0.1,
    operation_name="Always Fails"
)
def always_fails():
    """Function that always fails."""
    raise ValueError("This function always fails")

# Test 2: Function that fails with different exceptions
@retry_operation(
    max_retries=3,
    retry_exceptions=[ValueError, RuntimeError],
    base_delay=0.1,
    operation_name="Multiple Exceptions"
)
def multiple_exceptions():
    """Function that fails with different exceptions."""
    if not hasattr(multiple_exceptions, "counter"):
        multiple_exceptions.counter = 0
    
    multiple_exceptions.counter += 1
    
    if multiple_exceptions.counter == 1:
        raise ValueError("First failure")
    elif multiple_exceptions.counter == 2:
        raise RuntimeError("Second failure")
    elif multiple_exceptions.counter == 3:
        raise TypeError("Third failure - should not be retried")
    
    return "Success!"

# Test 3: Function with increasing backoff
@retry_operation(
    max_retries=5,
    retry_exceptions=[ValueError],
    base_delay=0.1,
    backoff_factor=2.0,
    operation_name="Backoff Test"
)
def backoff_test():
    """Function to test backoff timing."""
    if not hasattr(backoff_test, "counter"):
        backoff_test.counter = 0
        backoff_test.timestamps = []
    
    backoff_test.timestamps.append(time.time())
    backoff_test.counter += 1
    
    if backoff_test.counter <= 3:
        raise ValueError(f"Failure #{backoff_test.counter}")
    
    return backoff_test.timestamps

def test_always_fails():
    """Test a function that always fails."""
    try:
        always_fails()
        print("❌ Test failed: Should have raised ValueError")
    except ValueError as e:
        print(f"✅ Test passed: Function failed after max retries with: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_multiple_exceptions():
    """Test a function that fails with different exceptions."""
    # Reset counter
    if hasattr(multiple_exceptions, "counter"):
        multiple_exceptions.counter = 0
    
    try:
        result = multiple_exceptions()
        print("❌ Test failed: Should have raised TypeError")
    except TypeError as e:
        print(f"✅ Test passed: Function correctly raised non-retryable exception: {e}")
    except Exception as e:
        print(f"❌ Test failed: Wrong exception type: {type(e).__name__}")

def test_backoff():
    """Test the backoff timing."""
    # Reset counter and timestamps
    if hasattr(backoff_test, "counter"):
        backoff_test.counter = 0
        backoff_test.timestamps = []
    
    try:
        timestamps = backoff_test()
        
        # Calculate delays between attempts
        delays = []
        for i in range(1, len(timestamps)):
            delays.append(timestamps[i] - timestamps[i-1])
        
        # Check if delays are increasing
        increasing = all(delays[i] > delays[i-1] for i in range(1, len(delays)))
        
        if increasing:
            print(f"✅ Test passed: Backoff delays are increasing: {[round(d, 3) for d in delays]}")
        else:
            print(f"❌ Test failed: Backoff delays are not increasing: {[round(d, 3) for d in delays]}")
    except Exception as e:
        print(f"❌ Test failed: Unexpected exception: {type(e).__name__}: {e}")

def main():
    """Run all tests."""
    print("\n=== Testing Retry Decorator ===")
    
    print("\n1. Testing function that always fails:")
    test_always_fails()
    
    print("\n2. Testing function with multiple exception types:")
    test_multiple_exceptions()
    
    print("\n3. Testing backoff timing:")
    test_backoff()
    
    print("\nAll retry tests completed.")

if __name__ == "__main__":
    main()
