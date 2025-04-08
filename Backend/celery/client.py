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
            'Tokenization'
        )

        self.detokenize_executor = TaskExecutor(
            self.connection,
            'ai.tasks.detokenize_tokens',
            'Detokenization'
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

    # Batch processing methods have been removed

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
