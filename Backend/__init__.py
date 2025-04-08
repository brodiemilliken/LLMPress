"""
LLMPress Backend

The main package for LLMPress compression and decompression functionality.
"""

from .celery import CeleryClient, tokenize, detokenize