import multiprocessing

# Set the start method to 'spawn' before any other imports
multiprocessing.set_start_method('spawn', force=True)

from celery import Celery
from typing import List, Tuple, Any
import os
import time

# Set default broker URL if not specified in environment
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'llmpress_tasks',
    broker=broker_url,
    result_backend=result_backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    task_track_started=True,
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,  # Only acknowledge task after processing completed
)

# Global model instance
_model = None

# Model initialization function
def get_model():
    global _model
    if _model is None:
        # Import here to avoid circular imports
        from ChatGPT2 import GPT2
        print("Loading GPT-2 model in Celery worker...")
        _model = GPT2()
        print("Model loaded successfully in worker!")
    return _model

# Define tasks
@celery_app.task(name="tokenize_text", soft_time_limit=60)
def tokenize_text(text: str, window_size: int = 64) -> List[Tuple[str, int]]:
    """
    Task to tokenize text
    
    Args:
        text: The text to tokenize
        window_size: Size of the sliding context window for token prediction
    """
    from llm_tokenize import encode_text
    model = get_model()
    return encode_text(text, model, window_size)

@celery_app.task(name="detokenize_tokens", soft_time_limit=60)
def detokenize_tokens(tokens: List[List[Any]], window_size: int = 64) -> str:
    """
    Task to detokenize tokens
    
    Args:
        tokens: The token sequences to decode
        window_size: Size of the sliding context window for token prediction
    """
    from llm_detokenize import decode_tokens
    model = get_model()
    return decode_tokens(tokens, model, window_size)

# Worker startup
@celery_app.on_after_configure.connect
def setup_worker(sender, **kwargs):
    print("Celery worker starting up...")
    # Pre-load the model to avoid cold start on first request
    get_model()