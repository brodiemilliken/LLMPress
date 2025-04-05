# LLMPress

LLMPress is a tool for compressing files and folders using advanced language models. It leverages predictive capabilities of language models to achieve better compression ratios than traditional algorithms for text-based content.

## Features
- Compress a single file or an entire folder of files
- Configurable chunking parameters for optimal compression
- Adjustable context window size for language model predictions
- Multiple logging levels for debugging and information
- Distributed processing with Celery for improved performance
- GPU-accelerated compression with CUDA support

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

### Single File Compression
```bash
docker exec -it deployment-backend-1 python Test/file_test.py \
  -i Test/small_files/sample.txt \
  -w 100 -min 500 -max 1000 \
  --log-level verbose
```

Parameters:
- `-i, --input`: Path to the file to compress (required)
- `-o, --output`: Output directory (default: `Output`)
- `-w, --window-size`: Context window size (default: 64)
- `-min, --min-chunk`: Minimum chunk size in bytes (default: 100)
- `-max, --max-chunk`: Maximum chunk size in bytes (default: 500)
- `--log-level`: Logging verbosity (choices: quiet, normal, verbose, debug)

### Batch Compression
```bash
docker exec -it deployment-backend-1 python Test/batch_test.py \
  -i Test/small_files \
  -w 100 -min 500 -max 1000 \
  --log-level normal
```

### Advanced Chunking Test
```bash
docker exec -it deployment-backend-1 python Test/chunk_test.py \
  -i Test/small_files/sample.txt \
  -m 100 -M 500 \
  --log-level debug
```

## Logging Levels

LLMPress supports different logging levels to control the verbosity of output:

| Level | Description |
|-------|-------------|
| `quiet` | Show only errors |
| `normal` | Show warnings and errors |
| `verbose` | Show info, warnings, and errors |
| `debug` | Show all messages including debug information |

Example:
```bash
docker exec -it deployment-backend-1 python Test/file_test.py -i Test/small_files/sample.txt --log-level verbose
```

## Scaling with Multiple Workers

LLMPress supports horizontal scaling with multiple worker instances:

```bash
docker compose --profile gpu up --scale llmpress-worker=3
```

## License
This project is licensed under the MIT License.
