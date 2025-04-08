"""
LLMPress Celery Client

This module provides a client for interacting with LLMPress AI services through Celery tasks.
"""
import logging
from typing import List, Any, Optional

from Backend.exceptions import APIConnectionError, TokenizationError
from .connection import CeleryConnection
from .executor import TaskExecutor

# Set up logging
logger = logging.getLogger('LLMPress.CeleryClient')

class CeleryClient:
    """
    Client for interacting with LLMPress AI services through Celery tasks.
    Provides methods for tokenization and detokenization operations.
    """
    
    def __init__(self, broker_url: Optional[str] = None, backend_url: Optional[str] = None):
        """
        Initialize a new Celery client.
        
        Args:
            broker_url: URL for the Celery broker (default: from environment or redis://redis:6379/0)
            backend_url: URL for the Celery result backend (default: same as broker_url)
        """
        # Create connection
        self.connection = CeleryConnection(broker_url, backend_url)
        
        # Create task executors
        self.tokenize_executor = TaskExecutor(
            self.connection, 
            'ai.tasks.tokenize_text',
            'Tokenization',
            []  # Fallback value for tokenization
        )
        
        self.detokenize_executor = TaskExecutor(
            self.connection, 
            'ai.tasks.detokenize_tokens',
            'Detokenization',
            ""  # Fallback value for detokenization
        )
    
    def tokenize(self, text: str, window_size: int = 64, timeout: int = 60) -> List[List[Any]]:
        """
        Tokenize text using Celery worker.
        
        Args:
            text: The text to tokenize
            window_size: Size of the sliding context window for token prediction
            timeout: Maximum time to wait for result in seconds
            
        Returns:
            Tokenized result
            
        Raises:
            APIConnectionError: If there's an issue connecting to the Celery worker
            TokenizationError: If there's an error during tokenization
        """
        return self.tokenize_executor.execute_task(text, window_size, timeout)
    
    def detokenize(self, tokens: List[List[Any]], window_size: int = 64, timeout: int = 60) -> str:
        """
        Detokenize tokens using Celery worker.
        
        Args:
            tokens: The token sequences to decode
            window_size: Size of the sliding context window for token prediction
            timeout: Maximum time to wait for result in seconds
            
        Returns:
            Reconstructed text
            
        Raises:
            APIConnectionError: If there's an issue connecting to the Celery worker
            TokenizationError: If there's an error during detokenization
        """
        return self.detokenize_executor.execute_task(tokens, window_size, timeout)
    
    def tokenize_chunks(self, texts: List[str], window_size: int = 64, timeout: int = 120) -> List[List[List[Any]]]:
        """
        Tokenize multiple text chunks in parallel.
        
        Args:
            texts: List of text chunks to tokenize
            window_size: Size of the sliding context window
            timeout: Maximum time to wait for all results
            
        Returns:
            List of tokenized results in the same order as input texts
            
        Raises:
            APIConnectionError: If there's an issue connecting to the Celery worker
        """
        return self.tokenize_executor.execute_batch(texts, window_size, timeout)
    
    def detokenize_chunks(self, token_chunks: List[List[List[Any]]], window_size: int = 64, timeout: int = 120) -> List[str]:
        """
        Detokenize multiple token chunks in parallel.
        
        Args:
            token_chunks: List of token chunks to detokenize
            window_size: Size of the sliding context window
            timeout: Maximum time to wait for all results
            
        Returns:
            List of detokenized text chunks in the same order as input
            
        Raises:
            APIConnectionError: If there's an issue connecting to the Celery worker
        """
        return self.detokenize_executor.execute_batch(token_chunks, window_size, timeout)
    
    def ping(self, timeout: int = 5) -> bool:
        """
        Check if the AI service is responsive.
        
        Args:
            timeout: Maximum time to wait for response in seconds
            
        Returns:
            True if service is responsive, False otherwise
        """
        try:
            task = self.connection.send_task('ai.tasks.ping')
            task.get(timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Ping failed: {str(e)}")
            return False
