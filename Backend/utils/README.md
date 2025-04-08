# LLMPress Error Handling Utilities

This directory contains utility functions for standardized error handling in the LLMPress codebase.

## Error Handling Patterns

The `error_handler.py` module provides several utilities for standardized error handling:

### 1. Decorator: `handle_operation_errors`

This decorator provides standardized error handling for functions:

```python
@handle_operation_errors(
    operation_name="File Compression",
    specific_exceptions={
        FileNotFoundError: (FileOperationError, "File not found: {error_message}"),
        PermissionError: (FileOperationError, "Permission denied: {error_message}")
    },
    fallback_exception=CompressionError
)
def compress_file(file_path):
    # Function implementation
```

### 2. Context Manager: `operation_context`

This context manager provides standardized error handling for code blocks:

```python
with operation_context(
    operation_name="File Reading",
    specific_exceptions={
        FileNotFoundError: (FileOperationError, "File not found: {error_message}"),
        PermissionError: (FileOperationError, "Permission denied: {error_message}")
    }
):
    # Code that might raise exceptions
```

### 3. Retry Decorator: `retry_operation`

This decorator adds retry logic to functions that might fail temporarily:

```python
@retry_operation(
    max_retries=3,
    retry_exceptions=[ConnectionError, TimeoutError],
    operation_name="API Request"
)
def call_api(url):
    # Function implementation
```

### 4. Utility Functions

- `log_exception`: Log an exception with full traceback and context information
- `format_error_response`: Format a standardized error response for API endpoints

## Best Practices

1. **Use Descriptive Operation Names**: The `operation_name` parameter should clearly describe what the operation is doing.

2. **Map Specific Exceptions**: Use the `specific_exceptions` parameter to map specific exceptions to custom exceptions with more context.

3. **Use Retry Logic Sparingly**: Only use `retry_operation` for operations that might fail temporarily, like network requests.

4. **Combine Decorators**: You can combine multiple decorators for more complex error handling:

```python
@retry_operation(max_retries=3, retry_exceptions=[ConnectionError])
@handle_operation_errors(operation_name="API Request")
def call_api(url):
    # Function implementation
```

## Important Note

LLMPress does not support fallback mechanisms for compression operations. Due to the nature of the compression algorithm, which relies on ChatGPT, the compression must either succeed completely or fail with an error. Partial or fallback results are not supported.

## Example

See `Backend/examples/error_handling_example.py` for a complete example of how to use these utilities.
