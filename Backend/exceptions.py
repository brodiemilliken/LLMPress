"""
LLMPress Exception Classes

This module defines custom exceptions used throughout the LLMPress backend.
All exceptions include context information and support for chained exceptions.
"""
from typing import Optional, Any, Dict

class LLMPressError(Exception):
    """Base exception class for all LLMPress errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        """
        Initialize a new LLMPress error.

        Args:
            message: Error message
            details: Additional error details
            cause: The original exception that caused this error
        """
        self.details = details or {}
        super().__init__(message)

        if cause:
            self.__cause__ = cause

class FileOperationError(LLMPressError):
    """Raised when file operations fail (reading, writing, etc.)"""

    def __init__(self, message: str, file_path: Optional[str] = None, details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        """
        Initialize a new file operation error.

        Args:
            message: Error message
            file_path: Path to the file that caused the error
            details: Additional error details
            cause: The original exception that caused this error
        """
        if file_path:
            if details is None:
                details = {}
            details['file_path'] = file_path
            if not message.endswith('.'):
                message += '.'
            message = f"{message} File: {file_path}"

        super().__init__(message, details, cause)

class ChunkingError(LLMPressError):
    """Raised when text chunking operations fail."""

    def __init__(self, message: str, chunk_size: Optional[int] = None, details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        """
        Initialize a new chunking error.

        Args:
            message: Error message
            chunk_size: Size of the chunk that caused the error
            details: Additional error details
            cause: The original exception that caused this error
        """
        if chunk_size is not None:
            if details is None:
                details = {}
            details['chunk_size'] = chunk_size

        super().__init__(message, details, cause)

class TokenizationError(LLMPressError):
    """Raised when tokenization operations fail."""

    def __init__(self, message: str, model_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        """
        Initialize a new tokenization error.

        Args:
            message: Error message
            model_name: Name of the model that caused the error
            details: Additional error details
            cause: The original exception that caused this error
        """
        if model_name:
            if details is None:
                details = {}
            details['model_name'] = model_name
            if not message.endswith('.'):
                message += '.'
            message = f"{message} Model: {model_name}"

        super().__init__(message, details, cause)

class CompressionError(LLMPressError):
    """Raised when compression operations fail."""

    def __init__(self, message: str, window_size: Optional[int] = None, details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        """
        Initialize a new compression error.

        Args:
            message: Error message
            window_size: Window size used for compression
            details: Additional error details
            cause: The original exception that caused this error
        """
        if window_size is not None:
            if details is None:
                details = {}
            details['window_size'] = window_size

        super().__init__(message, details, cause)

class DecompressionError(LLMPressError):
    """Raised when decompression operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message, details, cause)

class APIConnectionError(LLMPressError):
    """Raised when API communication fails."""

    def __init__(self, message: str, endpoint: Optional[str] = None, timeout: Optional[int] = None, details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        """
        Initialize a new API connection error.

        Args:
            message: Error message
            endpoint: API endpoint that failed
            timeout: Timeout value in seconds
            details: Additional error details
            cause: The original exception that caused this error
        """
        if details is None:
            details = {}

        if endpoint:
            details['endpoint'] = endpoint

        if timeout is not None:
            details['timeout'] = timeout

        super().__init__(message, details, cause)

class ModelOperationError(LLMPressError):
    """Raised when model operations fail."""

    def __init__(self, message: str, model_name: Optional[str] = None, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        """
        Initialize a new model operation error.

        Args:
            message: Error message
            model_name: Name of the model
            operation: Operation that failed
            details: Additional error details
            cause: The original exception that caused this error
        """
        if details is None:
            details = {}

        if model_name:
            details['model_name'] = model_name

        if operation:
            details['operation'] = operation

        super().__init__(message, details, cause)

class EncodingError(LLMPressError):
    """Raised when encoding operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message, details, cause)

class DecodingError(LLMPressError):
    """Raised when decoding operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message, details, cause)