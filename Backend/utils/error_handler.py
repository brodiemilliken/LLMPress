"""
LLMPress Error Handling Utilities

This module provides utility functions, decorators, and context managers for standardized error handling.
"""
import logging
import traceback
import functools
import time
from typing import Dict, Any, Optional, Type, Callable, TypeVar, List, Tuple, Iterator
from contextlib import contextmanager
from ..exceptions import LLMPressError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LLMPress.ErrorHandler')

# Type variables for generic function signatures
T = TypeVar('T')  # Return type
F = TypeVar('F', bound=Callable)  # Function type

def format_error_response(error: Exception, status_code: int = 500, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format a standardized error response for API endpoints.

    Args:
        error: The exception that occurred
        status_code: HTTP status code to return
        details: Additional error details

    Returns:
        Dict with error information
    """
    error_type = error.__class__.__name__
    error_message = str(error)

    response = {
        "success": False,
        "error": {
            "type": error_type,
            "message": error_message,
            "status_code": status_code
        }
    }

    if details:
        response["error"]["details"] = details

    # Log the error
    logger.error(f"{error_type}: {error_message}")

    return response

def log_exception(error: Exception, context: str = "", log_level: str = "error") -> None:
    """
    Log an exception with full traceback and context information.

    Args:
        error: The exception to log
        context: Additional context about where the error occurred
        log_level: Logging level to use (default: error)
    """
    error_type = error.__class__.__name__
    error_message = str(error)

    log_message = f"{error_type}: {error_message}"
    if context:
        log_message = f"{context} - {log_message}"

    if log_level == "critical":
        logger.critical(log_message)
    elif log_level == "warning":
        logger.warning(log_message)
    elif log_level == "info":
        logger.info(log_message)
    else:  # Default to error
        logger.error(log_message)

    # Only log traceback for error and critical levels
    if log_level in ["error", "critical"]:
        logger.error(traceback.format_exc())

def handle_operation_errors(
    operation_name: str,
    specific_exceptions: Dict[Type[Exception], Tuple[Type[Exception], str]] = None,
    fallback_exception: Type[Exception] = LLMPressError,
    log_level: str = "error"
) -> Callable[[F], F]:
    """
    Decorator for standardized error handling in operations.

    Args:
        operation_name: Human-readable name of the operation (for error messages)
        specific_exceptions: Mapping of caught exceptions to (raised exception, message template)
            The message template can include {operation_name} and {error_message}
        fallback_exception: Exception type to raise for unhandled exceptions
        log_level: Logging level to use (default: error)

    Returns:
        Decorated function with standardized error handling

    Example:
        @handle_operation_errors(
            operation_name="File Compression",
            specific_exceptions={
                FileNotFoundError: (FileOperationError, "File not found: {error_message}"),
                PermissionError: (FileOperationError, "Permission denied: {error_message}")
            }
        )
        def compress_file(file_path):
            # Function implementation
    """
    if specific_exceptions is None:
        specific_exceptions = {}

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except tuple(specific_exceptions.keys()) as e:
                # Handle specific exceptions
                exception_class, message_template = specific_exceptions[type(e)]
                error_message = message_template.format(
                    operation_name=operation_name,
                    error_message=str(e)
                )
                log_exception(e, f"Error during {operation_name}", log_level)
                raise exception_class(error_message) from e
            except Exception as e:
                # Handle unexpected exceptions
                if not isinstance(e, LLMPressError):  # Don't wrap already wrapped exceptions
                    error_message = f"Unexpected error during {operation_name}: {str(e)}"
                    log_exception(e, f"Unexpected error during {operation_name}", log_level)
                    raise fallback_exception(error_message) from e
                # Re-raise LLMPress exceptions as-is
                raise
        return wrapper
    return decorator

@contextmanager
def operation_context(
    operation_name: str,
    specific_exceptions: Dict[Type[Exception], Tuple[Type[Exception], str]] = None,
    fallback_exception: Type[Exception] = LLMPressError,
    log_level: str = "error"
) -> Iterator[None]:
    """
    Context manager for standardized error handling in operations.

    Args:
        operation_name: Human-readable name of the operation (for error messages)
        specific_exceptions: Mapping of caught exceptions to (raised exception, message template)
        fallback_exception: Exception type to raise for unhandled exceptions
        log_level: Logging level to use (default: error)

    Yields:
        None

    Example:
        with operation_context(
            operation_name="File Reading",
            specific_exceptions={
                FileNotFoundError: (FileOperationError, "File not found: {error_message}"),
                PermissionError: (FileOperationError, "Permission denied: {error_message}")
            }
        ):
            # Code that might raise exceptions
    """
    if specific_exceptions is None:
        specific_exceptions = {}

    try:
        yield
    except tuple(specific_exceptions.keys()) as e:
        # Handle specific exceptions
        exception_class, message_template = specific_exceptions[type(e)]
        error_message = message_template.format(
            operation_name=operation_name,
            error_message=str(e)
        )
        log_exception(e, f"Error during {operation_name}", log_level)
        raise exception_class(error_message) from e
    except Exception as e:
        # Handle unexpected exceptions
        if not isinstance(e, LLMPressError):  # Don't wrap already wrapped exceptions
            error_message = f"Unexpected error during {operation_name}: {str(e)}"
            log_exception(e, f"Unexpected error during {operation_name}", log_level)
            raise fallback_exception(error_message) from e
        # Re-raise LLMPress exceptions as-is
        raise

def retry_operation(
    max_retries: int = 3,
    retry_exceptions: List[Type[Exception]] = None,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    operation_name: str = "operation"
) -> Callable[[F], F]:
    """
    Decorator for retrying operations that might fail temporarily.

    Args:
        max_retries: Maximum number of retry attempts
        retry_exceptions: List of exception types that should trigger a retry
        base_delay: Initial delay between retries in seconds
        backoff_factor: Factor by which the delay increases with each retry
        operation_name: Name of the operation for logging

    Returns:
        Decorated function with retry logic

    Example:
        @retry_operation(
            max_retries=3,
            retry_exceptions=[ConnectionError, TimeoutError],
            operation_name="API Request"
        )
        def call_api(url):
            # Function implementation
    """
    if retry_exceptions is None:
        retry_exceptions = [Exception]

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt}/{max_retries} for {operation_name}")
                    return func(*args, **kwargs)
                except tuple(retry_exceptions) as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (backoff_factor ** attempt)
                        logger.warning(f"{operation_name} failed with {e.__class__.__name__}: {str(e)}. Retrying in {delay:.2f}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"{operation_name} failed after {max_retries} retries. Last error: {e.__class__.__name__}: {str(e)}")
                except Exception as e:
                    # Don't retry exceptions not in retry_exceptions
                    logger.error(f"{operation_name} failed with non-retryable exception: {e.__class__.__name__}: {str(e)}")
                    raise

            # If we get here, all retries failed
            if last_exception:
                raise last_exception

        return wrapper
    return decorator

# The fallback_on_error decorator has been removed as it's not compatible with our compression algorithm
# which requires either perfect results or no compression at all.