import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import logging

from celery import Celery
from celery.result import AsyncResult
from celery.exceptions import CeleryError, TimeoutError

# Import custom exceptions
from Backend.exceptions import APIConnectionError, TokenizationError, ModelOperationError

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LLMPress.CeleryClient')

# Create Celery app without importing AI
app = Celery('llmpress', 
             broker='redis://redis:6379/0',  # Update this if your broker URL is different
             backend='redis://redis:6379/0')  # Update this if your backend URL is different

# Define task signatures
tokenize_text = app.signature('ai.tasks.tokenize_text')
detokenize_tokens = app.signature('ai.tasks.detokenize_tokens')

class CeleryClient:
    def detokenize(self, tokens, window_size=64, timeout=60):
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
            TimeoutError: If the operation times out
        """
        try:
            # Use apply_async instead of delay since we're using signatures
            task = detokenize_tokens.apply_async(args=[tokens, window_size])
            return task.get(timeout=timeout)
        except TimeoutError:
            logger.error(f"Detokenization timed out after {timeout} seconds")
            raise APIConnectionError(f"Detokenization request timed out after {timeout} seconds")
        except CeleryError as e:
            logger.error(f"Celery error during detokenization: {str(e)}")
            raise APIConnectionError(f"Failed to communicate with the AI service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during detokenization: {str(e)}", exc_info=True)
            raise TokenizationError(f"Error during detokenization: {str(e)}")
    
    def tokenize(self, text, window_size=64):
        """
        Submit tokenization task asynchronously
        
        Args:
            text: The text to tokenize
            window_size: Size of the sliding context window for token prediction
            
        Returns:
            AsyncResult: Celery task result object that can be queried later
            
        Raises:
            APIConnectionError: If there's an issue connecting to the Celery worker
        """
        try:
            return tokenize_text.apply_async(args=[text, window_size])
        except CeleryError as e:
            logger.error(f"Celery error during tokenization request: {str(e)}")
            raise APIConnectionError(f"Failed to communicate with the AI service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during tokenization request: {str(e)}", exc_info=True)
            raise TokenizationError(f"Error submitting tokenization request: {str(e)}")
    
    def detokenize_chunks(self, token_chunks, window_size=64, timeout=120):
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
        if not token_chunks:
            return []
            
        logger.info(f"Detokenizing {len(token_chunks)} chunks in parallel...")
            
        # Submit all detokenization tasks in parallel
        tasks = []
        for chunk in token_chunks:
            try:
                task = detokenize_tokens.apply_async(args=[chunk, window_size])
                tasks.append(task)
            except CeleryError as e:
                logger.error(f"Celery error submitting detokenization task: {str(e)}")
                raise APIConnectionError(f"Failed to communicate with the AI service: {str(e)}")
            
        # Wait for all tasks to complete, with timeout
        results = []
        start_time = time.time()
        
        errors = []
        for i, task in enumerate(tasks):
            remaining_time = max(1, timeout - (time.time() - start_time))
            try:
                # Get result with remaining timeout
                result = task.get(timeout=remaining_time)
                logger.info(f"Chunk {i} detokenized")
                results.append(result)
            except TimeoutError:
                logger.warning(f"Detokenization of chunk {i} timed out")
                errors.append(f"Chunk {i}: Timed out after {remaining_time:.1f}s")
                # Fall back to empty string on timeout
                results.append("")
            except Exception as e:
                logger.error(f"Error detokenizing chunk {i}: {str(e)}")
                errors.append(f"Chunk {i}: {str(e)}")
                # Fall back to empty string on error
                results.append("")
        
        if errors:
            logger.warning(f"Completed detokenizing with {len(errors)} errors: {', '.join(errors[:3])}")
            if len(errors) > 3:
                logger.warning(f"...and {len(errors) - 3} more errors")
        else:
            logger.info(f"Successfully detokenized all {len(results)} chunks")
            
        return results
    
    def tokenize_chunks(self, texts, window_size=64, timeout=120):
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
        if not texts:
            return []
            
        logger.info(f"Tokenizing {len(texts)} chunks in parallel...")
        
        # Submit all tasks in parallel
        tasks = []
        for text in texts:
            try:
                task = tokenize_text.apply_async(args=[text, window_size])
                tasks.append(task)
            except CeleryError as e:
                logger.error(f"Celery error submitting tokenization task: {str(e)}")
                raise APIConnectionError(f"Failed to communicate with the AI service: {str(e)}")
        
        # Wait for all tasks to complete, with timeout
        results = []
        start_time = time.time()
        
        errors = []
        for i, task in enumerate(tasks):
            remaining_time = max(1, timeout - (time.time() - start_time))
            try:
                # Get result with remaining timeout
                result = task.get(timeout=remaining_time)
                logger.info(f"Chunk {i} tokenized")
                results.append(result)
            except TimeoutError:
                logger.warning(f"Tokenization of chunk {i} timed out")
                errors.append(f"Chunk {i}: Timed out after {remaining_time:.1f}s")
                # Fall back to empty list on timeout
                results.append([])
            except Exception as e:
                logger.error(f"Error tokenizing chunk {i}: {str(e)}")
                errors.append(f"Chunk {i}: {str(e)}")
                # Fall back to empty list on error
                results.append([])
        
        if errors:
            logger.warning(f"Completed tokenizing with {len(errors)} errors: {', '.join(errors[:3])}")
            if len(errors) > 3:
                logger.warning(f"...and {len(errors) - 3} more errors")
        else:
            logger.info(f"Successfully tokenized all {len(results)} chunks")
                
        return results

_client = CeleryClient()

def tokenize(text, window_size=64):
    """
    Tokenize text using the Celery client.
    
    Args:
        text: The text to tokenize
        window_size: Size of the sliding context window
        
    Returns:
        Tokenized text
        
    Raises:
        APIConnectionError: If there's an issue connecting to the Celery worker
        TokenizationError: If there's an error during tokenization
    """
    return _client.tokenize(text, window_size)

def tokenize_chunks(texts, window_size=64, timeout=120):
    """
    Tokenize multiple text chunks using the Celery client.
    
    Args:
        texts: List of text chunks to tokenize
        window_size: Size of the sliding context window
        timeout: Maximum time to wait for all results
        
    Returns:
        List of tokenized results
        
    Raises:
        APIConnectionError: If there's an issue connecting to the Celery worker
        TokenizationError: If there's an error during tokenization
    """
    return _client.tokenize_chunks(texts, window_size, timeout)

def detokenize(tokens, window_size=64):
    """
    Detokenize tokens using the Celery client.
    
    Args:
        tokens: The tokens to detokenize
        window_size: Size of the sliding context window
        
    Returns:
        Detokenized text
        
    Raises:
        APIConnectionError: If there's an issue connecting to the Celery worker
        TokenizationError: If there's an error during detokenization
    """
    return _client.detokenize(tokens, window_size)

def detokenize_chunks(token_chunks, window_size=64, timeout=120):
    """
    Detokenize multiple token chunks using the Celery client.
    
    Args:
        token_chunks: List of token chunks to detokenize
        window_size: Size of the sliding context window
        timeout: Maximum time to wait for all results
        
    Returns:
        List of detokenized results
        
    Raises:
        APIConnectionError: If there's an issue connecting to the Celery worker
        TokenizationError: If there's an error during detokenization
    """
    return _client.detokenize_chunks(token_chunks, window_size, timeout)
