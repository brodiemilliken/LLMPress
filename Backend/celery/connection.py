"""
LLMPress Celery Connection

This module provides a connection to Celery for task execution.
"""
import logging
import os
from typing import Optional

from celery import Celery

# Set up logging
logger = logging.getLogger('LLMPress.CeleryConnection')

class CeleryConnection:
    """
    Handles connection to Celery broker and result backend.
    """
    
    def __init__(self, broker_url: Optional[str] = None, backend_url: Optional[str] = None):
        """
        Initialize a new Celery connection.
        
        Args:
            broker_url: URL for the Celery broker (default: from environment or redis://redis:6379/0)
            backend_url: URL for the Celery result backend (default: same as broker_url)
        """
        self.broker_url = broker_url or os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
        self.backend_url = backend_url or os.environ.get('CELERY_RESULT_BACKEND', self.broker_url)
        
        # Create Celery app
        self.app = Celery('llmpress', 
                         broker=self.broker_url,
                         backend=self.backend_url)
        
        logger.info(f"Celery connection initialized with broker: {self.broker_url}")
    
    def create_task_signature(self, task_name: str):
        """
        Create a task signature for the specified task.
        
        Args:
            task_name: Name of the Celery task
            
        Returns:
            Task signature
        """
        return self.app.signature(task_name)
    
    def send_task(self, task_name: str, *args, **kwargs):
        """
        Send a task directly to Celery.
        
        Args:
            task_name: Name of the Celery task
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task
            
        Returns:
            AsyncResult object
        """
        return self.app.send_task(task_name, args=args, kwargs=kwargs)
