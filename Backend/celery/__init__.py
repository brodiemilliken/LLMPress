"""
LLMPress Celery Package

This package provides functionality for interacting with Celery tasks.
"""
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import public classes and functions
from .client import CeleryClient
from .api import (
    get_client,
    tokenize,
    detokenize
)

# Define what's available for import
__all__ = [
    'CeleryClient',
    'get_client',
    'tokenize',
    'detokenize'
]
