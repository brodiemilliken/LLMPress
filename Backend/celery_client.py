import sys
from pathlib import Path

from celery import Celery
from celery.result import AsyncResult

# Import Celery tasks from the AI worker
try:
    # When running inside the Docker container
    from AI.tasks import tokenize_text, detokenize_tokens
except ImportError:
    # Fallback for local development
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    from AI.tasks import tokenize_text, detokenize_tokens

class CeleryClient:
    def tokenize(self, text, window_size=64, timeout=60):
        """
        Tokenize text using Celery worker
        
        Args:
            text: The text to tokenize
            window_size: Size of the sliding context window for token prediction
            timeout: Maximum time to wait for result in seconds
            
        Returns:
            List of tokens with their positions
        """
        task = tokenize_text.delay(text, window_size)
        return task.get(timeout=timeout)

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
        return task.get(timeout=timeout)
    
_client = CeleryClient()

def tokenize(text, window_size=64):
    return _client.tokenize(text, window_size)

def detokenize(tokens, window_size=64):
    return _client.detokenize(tokens, window_size)

# Example usage
if __name__ == "__main__":
    client = CeleryClient()

    text = "This is an example of tokenization."
    print("\nTokenizing text:")
    tokens = client.tokenize(text)
    print("Tokenized result:", tokens)

    print("\nDetokenizing tokens:")
    text_back = client.detokenize(tokens)
    print("Detokenized result:", text_back)
