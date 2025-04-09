"""
LLMPress Error Handling Utilities

This module provides utility functions for standardized error handling.
"""
import logging
import traceback
from typing import Dict, Any, Optional, Type, TypeVar, Callable
from functools import wraps

from ..exceptions import LLMPressError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LLMPress.ErrorHandler')

# Type variable for the exception type
E = TypeVar('E', bound=Exception)

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

def log_exception(error: Exception, context: str = "", log_level: int = logging.ERROR) -> None:
    """
    Log an exception with full traceback and context information.

    Args:
        error: The exception to log
        context: Additional context about where the error occurred
        log_level: The logging level to use (default: ERROR)
    """
    error_type = error.__class__.__name__
    error_message = str(error)

    if context:
        logger.log(log_level, f"{context} - {error_type}: {error_message}")
    else:
        logger.log(log_level, f"{error_type}: {error_message}")

    logger.log(log_level, traceback.format_exc())

def enrich_exception(exception: E, context: str) -> E:
    """
    Add context to an exception without changing its type.

    Args:
        exception: The original exception
        context: Context information to add

    Returns:
        The same exception with enriched message
    """
    # Get the original message
    original_message = str(exception)

    # Create a new message with context
    new_message = f"{context}: {original_message}"

    # Set the new message (this works for most exception types)
    exception.args = (new_message,) + exception.args[1:]

    return exception

def handle_error(
    error_type: Type[E],
    context: str = "",
    log_level: int = logging.ERROR,
    reraise_as: Optional[Type[Exception]] = None
) -> Callable[[Callable], Callable]:
    """
    Decorator for standardized error handling.

    Args:
        error_type: The type of exception to catch
        context: Context information to add to the exception
        log_level: The logging level to use
        reraise_as: If provided, the caught exception will be reraised as this type

    Returns:
        Decorated function with standardized error handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_type as e:
                # Get function information for better context
                module_name = func.__module__
                func_name = func.__name__

                # Create detailed context
                detailed_context = context or f"Error in {module_name}.{func_name}"

                # Log the exception
                log_exception(e, detailed_context, log_level)

                # Reraise with appropriate type
                if reraise_as:
                    raise reraise_as(f"{detailed_context}: {str(e)}") from e
                else:
                    # Enrich the original exception and reraise
                    raise enrich_exception(e, detailed_context)

        return wrapper
    return decorator

def with_error_handling(
    context: str = "",
    handled_exceptions: Dict[Type[Exception], Type[Exception]] = None
) -> Callable[[Callable], Callable]:
    """
    Comprehensive error handling decorator that can handle multiple exception types.

    Args:
        context: Base context information to add to exceptions
        handled_exceptions: Mapping of {caught_exception_type: reraised_exception_type}
                           If reraised_exception_type is None, the original type is preserved

    Returns:
        Decorated function with comprehensive error handling
    """
    if handled_exceptions is None:
        handled_exceptions = {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function information for better context
            module_name = func.__module__
            func_name = func.__name__

            # Create detailed context
            detailed_context = context or f"Error in {module_name}.{func_name}"

            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Check if this exception type should be handled specifically
                for exc_type, reraise_type in handled_exceptions.items():
                    if isinstance(e, exc_type):
                        # Log the exception
                        log_exception(e, detailed_context)

                        # Reraise with appropriate type
                        if reraise_type:
                            raise reraise_type(f"{detailed_context}: {str(e)}") from e
                        else:
                            # Enrich the original exception and reraise
                            raise enrich_exception(e, detailed_context)

                # If not a specifically handled exception, just reraise
                # (but still log it if it's a LLMPressError)
                if isinstance(e, LLMPressError):
                    log_exception(e, detailed_context)
                raise

        return wrapper
    return decorator