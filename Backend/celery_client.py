import sys
import os
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
    def tokenize(self, text, timeout=20):
        task = tokenize_text.delay(text)
        return task.get(timeout=timeout)

    def detokenize(self, tokens, timeout=20):
        task = detokenize_tokens.delay(tokens)
        return task.get(timeout=timeout)
    
_client = CeleryClient()

def tokenize(text, timeout=20):
    return _client.tokenize(text, timeout=timeout)

def detokenize(tokens, timeout=20):
    return _client.detokenize(tokens, timeout=timeout)

# Example usage
if __name__ == "__main__":
    client = CeleryClient()

    text = "This is an example of tokenization."
    print("\nTokenizing text:")
    tokens = client.tokenize(text)
    print("Tokenized result:", tokens)

    print("\nDetokenizing tokens:")
    result = client.detokenize(tokens)
    print("Detokenized result:", result)
