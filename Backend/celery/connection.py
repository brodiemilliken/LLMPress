"""
LLMPress Celery Connection

This module provides a connection to Celery for task execution.
"""
import logging
import os
from typing import Optional

from celery import Celery
from celery.exceptions import CeleryError

from ..exceptions import APIConnectionError
from ..utils.error_handler import with_error_handling

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LLMPress.CeleryConnection')

class CeleryConnection:
    """
    Handles connection to Celery broker and result backend.
    """

    @with_error_handling(
        context="Celery connection initialization",
        handled_exceptions={
            CeleryError: APIConnectionError,
            Exception: APIConnectionError
        }
    )
    def __init__(self, broker_url: Optional[str] = None, backend_url: Optional[str] = None):
        """
        Initialize a new Celery connection.

        Args:
            broker_url: URL for the Celery broker (default: from environment or redis://redis:6379/0)
            backend_url: URL for the Celery result backend (default: same as broker_url)

        Raises:
            APIConnectionError: If there's an issue initializing the Celery connection
        """
        logger.info("Initializing Celery connection")

        # Get broker and backend URLs from parameters or environment variables
        self.broker_url = broker_url or os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
        self.backend_url = backend_url or os.environ.get('CELERY_RESULT_BACKEND', self.broker_url)

        logger.info(f"Using broker URL: {self.broker_url}")
        logger.info(f"Using backend URL: {self.backend_url}")

        # Create Celery app
        self.app = Celery('llmpress',
                         broker=self.broker_url,
                         backend=self.backend_url)

        logger.info(f"Celery connection initialized successfully")

    @with_error_handling(
        context="Creating Celery task signature",
        handled_exceptions={
            CeleryError: APIConnectionError,
            Exception: APIConnectionError
        }
    )
    def create_task_signature(self, task_name: str):
        """
        Create a task signature for the specified task.

        Args:
            task_name: Name of the Celery task

        Returns:
            Task signature

        Raises:
            APIConnectionError: If there's an issue creating the task signature
        """
        logger.info(f"Creating task signature for task: {task_name}")
        result = self.app.signature(task_name)
        logger.info(f"Task signature created successfully")
        return result

    @with_error_handling(
        context="Sending Celery task",
        handled_exceptions={
            CeleryError: APIConnectionError,
            Exception: APIConnectionError
        }
    )
    def send_task(self, task_name: str, *args, **kwargs):
        """
        Send a task directly to Celery.

        Args:
            task_name: Name of the Celery task
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task

        Returns:
            AsyncResult object

        Raises:
            APIConnectionError: If there's an issue sending the task
        """
        logger.info(f"Sending task: {task_name}")
        result = self.app.send_task(task_name, args=args, kwargs=kwargs)
        logger.info(f"Task sent successfully with ID: {result.id}")
        return result
