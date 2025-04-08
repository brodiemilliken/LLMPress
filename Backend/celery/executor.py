"""
LLMPress Celery Task Executor

This module provides task execution with standardized error handling.
"""
import time
import logging
from typing import List, Any, TypeVar, Generic

from celery.exceptions import CeleryError, TimeoutError

from Backend.exceptions import APIConnectionError, TokenizationError
from .connection import CeleryConnection

# Set up logging
logger = logging.getLogger('LLMPress.TaskExecutor')

# Generic type for task results
T = TypeVar('T')  # Input type
U = TypeVar('U')  # Output type

class TaskExecutor(Generic[T, U]):
    """
    Executes Celery tasks with standardized error handling.
    """

    def __init__(self,
                connection: CeleryConnection,
                task_name: str,
                operation_name: str):
        """
        Initialize a new task executor.

        Args:
            connection: Celery connection
            task_name: Name of the Celery task
            operation_name: Human-readable name of the operation (for error messages)
        """
        self.connection = connection
        self.task_signature = connection.create_task_signature(task_name)
        self.operation_name = operation_name

    def execute_task(self, input_data: T, window_size: int, timeout: int) -> Any:
        """
        Execute a single task with error handling.

        Args:
            input_data: Input data for the task
            window_size: Size of the sliding context window
            timeout: Maximum time to wait for result

        Returns:
            Task result

        Raises:
            APIConnectionError: If there's an issue connecting to the Celery worker
            TokenizationError: If there's an error during task execution
        """
        try:
            task = self.task_signature.apply_async(args=[input_data, window_size])
            return task.get(timeout=timeout)
        except TimeoutError:
            logger.error(f"{self.operation_name} timed out after {timeout} seconds")
            raise APIConnectionError(f"{self.operation_name} request timed out after {timeout} seconds")
        except CeleryError as e:
            logger.error(f"Celery error during {self.operation_name.lower()}: {str(e)}")
            raise APIConnectionError(f"Failed to communicate with the AI service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during {self.operation_name.lower()}: {str(e)}", exc_info=True)
            raise TokenizationError(f"Error during {self.operation_name.lower()}: {str(e)}")

    # Batch processing method has been removed
