"""
LLMPress Celery Task Executor

This module provides task execution with standardized error handling.
"""
import time
import logging
from typing import List, Any, TypeVar, Generic

from celery.exceptions import CeleryError, TimeoutError

from ..exceptions import APIConnectionError, TokenizationError
from ..utils.error_handler import with_error_handling
from .connection import CeleryConnection

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
                operation_name: str,
                fallback_value: U):
        """
        Initialize a new task executor.

        Args:
            connection: Celery connection
            task_name: Name of the Celery task
            operation_name: Human-readable name of the operation (for error messages)
            fallback_value: Value to return on error in batch operations
        """
        self.connection = connection
        self.task_signature = connection.create_task_signature(task_name)
        self.operation_name = operation_name
        self.fallback_value = fallback_value

    @with_error_handling(
        context="Task execution",
        handled_exceptions={
            TimeoutError: APIConnectionError,
            CeleryError: APIConnectionError,
            Exception: TokenizationError
        }
    )
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
        logger.info(f"Executing {self.operation_name} task with window size {window_size} and timeout {timeout}s")

        # Submit the task
        task = self.task_signature.apply_async(args=[input_data, window_size])

        # Wait for the result with timeout
        if isinstance(timeout, (int, float)) and timeout > 0:
            result = task.get(timeout=timeout)
        else:
            # If timeout is invalid, use a default timeout
            logger.warning(f"Invalid timeout value: {timeout}, using default 60s")
            result = task.get(timeout=60)

        logger.info(f"{self.operation_name} task completed successfully")
        return result

    @with_error_handling(
        context="Batch task execution",
        handled_exceptions={
            CeleryError: APIConnectionError,
            Exception: TokenizationError
        }
    )
    def execute_batch(self,
                     items: List[T],
                     window_size: int,
                     timeout: int) -> List[U]:
        """
        Execute multiple tasks in parallel with error handling.

        Args:
            items: List of input items
            window_size: Size of the sliding context window
            timeout: Maximum time to wait for all results

        Returns:
            List of results in the same order as input items

        Raises:
            APIConnectionError: If there's an issue connecting to the Celery worker
            TokenizationError: If there's an error during batch execution
        """
        if not items:
            return []

        logger.info(f"Executing {self.operation_name} on {len(items)} items in parallel with window size {window_size} and timeout {timeout}s")

        # Submit all tasks in parallel
        tasks = []
        for item in items:
            task = self.task_signature.apply_async(args=[item, window_size])
            tasks.append(task)

        # Wait for all tasks to complete, with timeout
        results = []
        start_time = time.time()

        errors = []
        for i, task in enumerate(tasks):
            remaining_time = max(1, timeout - (time.time() - start_time))
            try:
                # Get result with remaining timeout
                result = task.get(timeout=remaining_time)
                logger.info(f"Item {i} processed successfully")
                results.append(result)
            except TimeoutError:
                logger.warning(f"{self.operation_name} of item {i} timed out after {remaining_time:.1f}s")
                errors.append(f"Item {i}: Timed out after {remaining_time:.1f}s")
                # Fall back to empty value on timeout
                results.append(self.fallback_value)
            except Exception as e:
                logger.error(f"Error processing item {i}: {str(e)}")
                errors.append(f"Item {i}: {str(e)}")
                # Fall back to empty value on error
                results.append(self.fallback_value)

        if errors:
            logger.warning(f"Batch completed with {len(errors)} errors: {', '.join(errors[:3])}")
            if len(errors) > 3:
                logger.warning(f"...and {len(errors) - 3} more errors")
        else:
            logger.info(f"Successfully processed all {len(results)} items")

        return results
