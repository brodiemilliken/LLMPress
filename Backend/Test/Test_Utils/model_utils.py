import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Backend.celery_client import CeleryClient

def initialize_model(model_name="gpt2", k=64):
    """
    Initialize a Celery client for distributed model access.
    
    Args:
        model_name (str): The name of the model to initialize (for compatibility)
        k (int): Context size (for compatibility)
        
    Returns:
        The initialized Celery client
    """
    print("Using Celery client for distributed processing...")
    return CeleryClient()

# Backward compatibility function for direct model initialization
def initialize_direct_model(model_name="gpt2"):
    """
    This function is kept for backward compatibility but raises an error
    when run in Docker environment.
    """
    print("Direct model initialization is disabled in Docker environment.")
    raise NotImplementedError(
        "Direct model access is not supported in the Docker environment. "
        "Use the Celery client instead to avoid CUDA subprocess issues."
    )