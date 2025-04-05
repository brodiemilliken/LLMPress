"""
LLMPress Exception Classes

This module defines custom exceptions used throughout the LLMPress backend.
"""

class LLMPressError(Exception):
    """Base exception class for all LLMPress errors."""
    pass

class FileOperationError(LLMPressError):
    """Raised when file operations fail (reading, writing, etc.)"""
    pass

class ChunkingError(LLMPressError):
    """Raised when text chunking operations fail."""
    pass

class TokenizationError(LLMPressError):
    """Raised when tokenization operations fail."""
    pass

class CompressionError(LLMPressError):
    """Raised when compression operations fail."""
    pass

class DecompressionError(LLMPressError):
    """Raised when decompression operations fail."""
    pass

class APIConnectionError(LLMPressError):
    """Raised when API communication fails."""
    pass

class ModelOperationError(LLMPressError):
    """Raised when model operations fail."""
    pass

class EncodingError(LLMPressError):
    """Raised when encoding operations fail."""
    pass

class DecodingError(LLMPressError):
    """Raised when decoding operations fail."""
    pass