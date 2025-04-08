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
        """
        if not items:
            return []
        
        logger.info(f"{self.operation_name} {len(items)} items in parallel")
        
        # Submit all tasks in parallel
        tasks = []
        for item in items:
            try:
                task = self.task_signature.apply_async(args=[item, window_size])
                tasks.append(task)
            except CeleryError as e:
                logger.error(f"Celery error submitting {self.operation_name.lower()} task: {str(e)}")
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
                logger.info(f"Item {i} processed")
                results.append(result)
            except TimeoutError:
                logger.warning(f"{self.operation_name} of item {i} timed out")
                errors.append(f"Item {i}: Timed out after {remaining_time:.1f}s")
                # Fall back to empty value on timeout
                results.append(self.fallback_value)
            except Exception as e:
                logger.error(f"Error processing item {i}: {str(e)}")
                errors.append(f"Item {i}: {str(e)}")
                # Fall back to empty value on error
                results.append(self.fallback_value)
        
        if errors:
            logger.warning(f"Completed with {len(errors)} errors: {', '.join(errors[:3])}")
            if len(errors) > 3:
                logger.warning(f"...and {len(errors) - 3} more errors")
        else:
            logger.info(f"Successfully processed all {len(results)} items")
        
        return results
