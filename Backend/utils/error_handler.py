"""
LLMPress Error Handling Utilities

This module provides utility functions for standardized error handling.
"""
import logging
import traceback
import json
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LLMPress.ErrorHandler')

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

def log_exception(error: Exception, context: str = "") -> None:
    """
    Log an exception with full traceback and context information.
    
    Args:
        error: The exception to log
        context: Additional context about where the error occurred
    """
    error_type = error.__class__.__name__
    error_message = str(error)
    
    if context:
        logger.error(f"{context} - {error_type}: {error_message}")
    else:
        logger.error(f"{error_type}: {error_message}")
        
    logger.error(traceback.format_exc())