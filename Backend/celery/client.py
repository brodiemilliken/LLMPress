"""
LLMPress Celery Client

This module provides a client for interacting with LLMPress AI services through Celery tasks.
"""
import logging
from typing import List, Any, Optional

from ..exceptions import APIConnectionError, TokenizationError
from ..utils.error_handler import with_error_handling
from .connection import CeleryConnection
from .executor import TaskExecutor

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        self.tokenize_executor = TaskExecutor[str, List[Any]](
            self.connection,
            'ai.tasks.tokenize_text',
            'Tokenization',
            []  # Empty list as fallback value
        )

        self.detokenize_executor = TaskExecutor[List[Any], str](
            self.connection,
            'ai.tasks.detokenize_tokens',
            'Detokenization',
            ''  # Empty string as fallback value
        )

        logger.info(f"CeleryClient initialized with broker: {self.connection.broker_url}")

    @with_error_handling(
        context="Celery detokenization",
        handled_exceptions={
            APIConnectionError: None,  # Preserve APIConnectionError
            TokenizationError: None,  # Preserve TokenizationError
            Exception: TokenizationError  # Wrap other exceptions in TokenizationError
        }
    )
    def detokenize(self, tokens: List[Any], window_size: int = 64, timeout: int = 60) -> str:
        """
        Detokenize tokens using Celery worker

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
        logger.info(f"Detokenizing tokens with window size {window_size} and timeout {timeout}s")
        result = self.detokenize_executor.execute_task(tokens, window_size, timeout)
        logger.info(f"Successfully detokenized tokens into text of length {len(result)}")
        return result

    @with_error_handling(
        context="Celery tokenization",
        handled_exceptions={
            APIConnectionError: None,  # Preserve APIConnectionError
            TokenizationError: None,  # Preserve TokenizationError
            Exception: TokenizationError  # Wrap other exceptions in TokenizationError
        }
    )
    def tokenize(self, text: str, window_size: int = 64, timeout: int = 60) -> List[Any]:
        """
        Tokenize text using Celery worker

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
        logger.info(f"Tokenizing text of length {len(text)} with window size {window_size} and timeout {timeout}s")
        result = self.tokenize_executor.execute_task(text, window_size, timeout)
        logger.info(f"Successfully tokenized text into {len(result)} tokens")
        return result

    @with_error_handling(
        context="Celery batch detokenization",
        handled_exceptions={
            APIConnectionError: None,  # Preserve APIConnectionError
            TokenizationError: None,  # Preserve TokenizationError
            Exception: TokenizationError  # Wrap other exceptions in TokenizationError
        }
    )
    def detokenize_chunks(self, token_chunks: List[List[Any]],
                         window_size: int = 64,
                         timeout: int = 120) -> List[str]:
        """
        Detokenize multiple token chunks in parallel

        Args:
            token_chunks: List of token chunks to detokenize
            window_size: Size of the sliding context window
            timeout: Maximum time to wait for all results

        Returns:
            List of detokenized text chunks in the same order as input

        Raises:
            APIConnectionError: If there's an issue connecting to the Celery worker
            TokenizationError: If there's an error during detokenization
        """
        logger.info(f"Detokenizing {len(token_chunks)} token chunks with window size {window_size} and timeout {timeout}s")
        result = self.detokenize_executor.execute_batch(token_chunks, window_size, timeout)
        logger.info(f"Successfully detokenized {len(token_chunks)} chunks")
        return result

    @with_error_handling(
        context="Celery batch tokenization",
        handled_exceptions={
            APIConnectionError: None,  # Preserve APIConnectionError
            TokenizationError: None,  # Preserve TokenizationError
            Exception: TokenizationError  # Wrap other exceptions in TokenizationError
        }
    )
    def tokenize_chunks(self, texts: List[str],
                       window_size: int = 64,
                       timeout: int = 120) -> List[List[Any]]:
        """
        Tokenize multiple text chunks in parallel

        Args:
            texts: List of text chunks to tokenize
            window_size: Size of the sliding context window
            timeout: Maximum time to wait for all results

        Returns:
            List of tokenized results in the same order as input texts

        Raises:
            APIConnectionError: If there's an issue connecting to the Celery worker
            TokenizationError: If there's an error during tokenization
        """
        logger.info(f"Tokenizing {len(texts)} text chunks with window size {window_size} and timeout {timeout}s")
        result = self.tokenize_executor.execute_batch(texts, window_size, timeout)
        logger.info(f"Successfully tokenized {len(texts)} chunks")
        return result
