import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from celery import Celery
from celery.result import AsyncResult

# Import tasks using a try-except for flexibility across environments
try:
    # When running inside the Docker container
    from AI.tasks import tokenize_text, detokenize_tokens
except ImportError:
    # Fallback for local development - using relative path without sys.path manipulation
    try:
        from ..AI.tasks import tokenize_text, detokenize_tokens
    except ImportError:
        # Another fallback if running from a different context
        from AI.tasks import tokenize_text, detokenize_tokens

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
        """
        task = detokenize_tokens.delay(tokens, window_size)
        return task.get(timeout=timeout)  # Wait for result instead of returning AsyncResult
    
    def tokenize(self, text, window_size=64):
        """
        Submit tokenization task asynchronously
        
        Args:
            text: The text to tokenize
            window_size: Size of the sliding context window for token prediction
            
        Returns:
            AsyncResult: Celery task result object that can be queried later
        """
        return tokenize_text.delay(text, window_size)
    
    def detokenize_chunks(self, token_chunks, window_size=64, timeout=120):
        """
        Detokenize multiple token chunks in parallel
        
        Args:
            token_chunks: List of token chunks to detokenize
            window_size: Size of the sliding context window
            timeout: Maximum time to wait for all results
            
        Returns:
            List of detokenized text chunks in the same order as input
        """
        if not token_chunks:
            return []
            
        print(f"Detokenizing {len(token_chunks)} chunks in parallel...")
            
        # Submit all detokenization tasks in parallel
        tasks = []
        for chunk in token_chunks:
            task = detokenize_tokens.delay(chunk, window_size)
            tasks.append(task)
            
        # Wait for all tasks to complete, with timeout
        results = []
        start_time = time.time()
        
        for i, task in enumerate(tasks):
            remaining_time = max(1, timeout - (time.time() - start_time))
            try:
                # Get result with remaining timeout
                result = task.get(timeout=remaining_time)
                print(f"Chunk {i} detokenized")
                results.append(result)
            except Exception as e:
                print(f"Error detokenizing chunk {i}: {e}")
                # Fall back to empty string on error
                results.append("")
                
        print(f"Completed detokenizing {len(results)} chunks")
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
        """
        if not texts:
            return []
            
        print(f"Tokenizing {len(texts)} chunks in parallel...")
        
        # Submit all tasks in parallel
        tasks = []
        for text in texts:
            task = tokenize_text.delay(text, window_size)
            tasks.append(task)
        
        # Wait for all tasks to complete, with timeout
        results = []
        start_time = time.time()
        
        for i, task in enumerate(tasks):
            remaining_time = max(1, timeout - (time.time() - start_time))
            try:
                # Get result with remaining timeout
                result = task.get(timeout=remaining_time)
                print(f"Chunk {i} tokenized")
                results.append(result)
            except Exception as e:
                print(f"Error tokenizing chunk {i}: {e}")
                # Fall back to empty list on error
                results.append([])
                
        print(f"Completed tokenizing {len(results)} chunks")
        return results

_client = CeleryClient()

def tokenize(text, window_size=64):
    return _client.tokenize(text, window_size)

def tokenize_chunks(texts, window_size=64, timeout=120):
    return _client.tokenize_chunks(texts, window_size, timeout)

def detokenize(tokens, window_size=64):
    return _client.detokenize(tokens, window_size)

def detokenize_chunks(token_chunks, window_size=64, timeout=120):
    return _client.detokenize_chunks(token_chunks, window_size, timeout)
