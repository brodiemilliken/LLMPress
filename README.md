# LLMPress

LLMPress is a tool for compressing files and folders using advanced language models. It leverages the predictive capabilities of language models to achieve better compression ratios than traditional algorithms for text-based content.

## Features
- Compress a single file or an entire folder of files
- Configurable chunking parameters for optimal compression
- Adjustable context window size for language model predictions
- Multiple logging levels for debugging and information
- Distributed processing with Celery for improved performance
- GPU-accelerated compression with CUDA support
- Robust error handling and recovery mechanisms
- Consistent logging across all components

## Architecture

LLMPress consists of several key components:

### Core Components
- **Compression Pipeline**: Handles the end-to-end compression process
  - **File Splitter**: Divides files into optimal chunks for processing
  - **Tokenizer**: Converts text into tokens using language models
  - **Encoder**: Encodes tokens into a compact binary format

### Backend Services
- **Celery Integration**: Provides distributed task processing
  - **Connection Manager**: Handles communication with Redis broker
  - **Task Executor**: Manages task submission and result retrieval
  - **Client API**: Provides a simple interface for task execution

### Error Handling
- **Exception Hierarchy**: Specialized exceptions for different error types
- **Error Handler**: Decorator-based approach for consistent error handling
- **Logging System**: Configurable logging with context-rich messages

## Installation

### Using Docker (Recommended)
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/LLMPress.git
   cd LLMPress
   ```

2. Start the services using Docker Compose:
   ```bash
   cd Deployment
   ./llmpress-start.bat    # Windows
   # OR
   ./start-llmpress.ps1    # PowerShell with GPU support
   ```

### Manual Installation
1. Install dependencies:
   ```bash
   pip install -r Backend/requirements.txt
   pip install -r AI/requirements.txt
   ```

2. Start the Redis server:
   ```bash
   docker run -d -p 6379:6379 redis
   ```

3. Start a Celery worker:
   ```bash
   cd AI
   celery -A tasks worker --loglevel=info
   ```

## Usage

### Using the PowerShell Helper Script

The easiest way to run LLMPress commands is using the provided PowerShell helper script:

```powershell
# From the Deployment directory
.\docker-run.ps1 backend python Test/file_test.py -i Test/small_files/sample.txt --model gpt2
```

### Single File Compression

```bash
docker exec -it llmpress-backend python Test/file_test.py \
  -i Test/small_files/sample.txt \
  --window-size 128 --min-chunk 200 --max-chunk 500 \
  --model gpt2 --log-level verbose
```

Parameters:
- `-i, --input`: Path to the file to compress (required)
- `-o, --output`: Output directory (default: `Output`)
- `--window-size, -w`: Context window size (default: from model config)
- `--min-chunk, -min`: Minimum chunk size in bytes (default: from model config)
- `--max-chunk, -max`: Maximum chunk size in bytes (default: from model config)
- `--model`: Model preset to use (default: gpt2)
- `--log-level`: Logging verbosity (choices: quiet, normal, verbose, debug)
- `--debug, -d`: Enable debug mode to save token information

### Batch Compression

```bash
docker exec -it llmpress-backend python Test/batch_test.py \
  -i Test/small_files \
  --window-size 128 --min-chunk 200 --max-chunk 500 \
  --model gpt2 --log-level normal
```

### Window Size Benchmark

Test different window sizes to find the optimal setting:

```bash
docker exec -it llmpress-backend python Test/window_test.py \
  -i Test/small_files/sample.txt \
  --model gpt2 --min-window 64 --max-window 256 --step 32
```

### Chunk Size Test

Analyze how different chunking strategies affect compression:

```bash
docker exec -it llmpress-backend python Test/chunk_test.py \
  -i Test/small_files/sample.txt \
  --min-chunk 100 --max-chunk 500 \
  --model gpt2 --log-level debug
```

## Logging System

LLMPress implements a comprehensive logging system that provides detailed information about the compression process.

### Logging Levels

LLMPress supports different logging levels to control the verbosity of output:

| Level | Description |
|-------|-------------|
| `quiet` | Show only errors |
| `normal` | Show warnings and errors |
| `verbose` | Show info, warnings, and errors |
| `debug` | Show all messages including debug information |

Example:
```bash
docker exec -it llmpress-backend python Test/file_test.py -i Test/small_files/sample.txt --log-level verbose
```

### Log Format

Logs include timestamps, component names, and contextual information:

```
2025-04-08 19:45:23 - LLMPress.Tokenizer - INFO - Tokenizing text of length 223
2025-04-08 19:45:24 - LLMPress.Tokenizer - INFO - Successfully tokenized text into 52 tokens
```

## Error Handling

LLMPress implements a robust error handling system that provides detailed information about errors and helps with debugging.

### Exception Hierarchy

- **LLMPressError**: Base exception for all LLMPress errors
  - **CompressionError**: Errors during compression
  - **DecompressionError**: Errors during decompression
  - **TokenizationError**: Errors during tokenization/detokenization
  - **EncodingError**: Errors during binary encoding/decoding
  - **APIConnectionError**: Errors communicating with external services

### Decorator-Based Error Handling

LLMPress uses a decorator-based approach for consistent error handling across the codebase:

```python
@with_error_handling(
    context="Text tokenization",
    handled_exceptions={
        Exception: TokenizationError
    }
)
def tokenize(text: str, api_client) -> List[Any]:
    # Function implementation
    # Any exceptions will be caught, logged, and wrapped in TokenizationError
```

This approach provides several benefits:
- Separation of error handling from business logic
- Consistent error handling across the codebase
- Detailed context information in error messages
- Proper exception chaining for debugging

### Error Recovery

LLMPress includes mechanisms to recover from errors when possible:

- Automatic retries for transient errors
- Fallback mechanisms for certain operations
- Detailed error messages with context information

## Scaling with Multiple Workers

LLMPress supports horizontal scaling with multiple worker instances:

```bash
# Start with 3 worker instances
docker compose up --scale llmpress-worker=3

# For GPU support
docker compose --profile gpu up --scale llmpress-worker=3
```

## Configuration

LLMPress uses a configuration system that supports different model presets. Each preset defines default values for:

- Window size
- Chunk size range
- Logging level
- Model-specific parameters

You can specify a model preset using the `--model` parameter:

```bash
docker exec -it llmpress-backend python Test/file_test.py -i Test/small_files/sample.txt --model gpt2
```

## License
This project is licensed under the MIT License.
