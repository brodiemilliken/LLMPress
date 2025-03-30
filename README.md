# LLMPress

LLMPress is a tool for compressing files and folders using advanced language models. It supports single-file and folder-based compression workflows, and can scale to multiple workers for efficient processing.

## Features
- Compress a single file or an entire folder of files.
- Specify context window size (`--k`) and model (`--model`) for compression.
- Debug mode to save token information for analysis.
- Scalable architecture with support for multiple workers using Docker Compose.

## Usage

### Single File Compression
Run the following command to compress a single file:
```bash
python compress.py --input <path_to_file> --output <output_directory> --k <context_window_size> --model <model_name> --debug
```
- `--input` (`-i`): Path to the file to compress (required).
- `--output` (`-o`): Output directory for results (default: `Output`).
- `--k`: Context window size (default: `64`).
- `--model`: Model name to use (default: `gpt2`).
- `--debug` (`-d`): Enable debug mode to save token information.

### Folder Compression
Run the following command to compress all files in a folder:
```bash
python compress_folder.py --input <input_directory> --output <output_directory> --k <context_window_size> --model <model_name> --debug
```
- `--input` (`-i`): Input directory with files to compress (required).
- `--output` (`-o`): Output directory for results (default: `Output`).
- `--k`: Context window size (default: `64`).
- `--model`: Model name to use (default: `gpt2`).
- `--debug` (`-d`): Enable debug mode to save token information.

### Scaling with Multiple Workers or Multiple Backends
LLMPress supports scaling to multiple workers for parallel processing. Use Docker Compose to spin up multiple workers:
```bash
docker compose --profile gpu up --scale backend=2 --scale llmpress-worker=1
```
- `--scale llmpress-worker=3`: Spins up 3 workers for parallel processing. Adjust the number as needed.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/LLMPress.git
   cd LLMPress
   ```
2. Build the Docker image (this will install all dependencies):
   ```bash
   docker compose build
   ```

### Notes
- Ensure you have Docker and Docker Compose installed for scaling workers.
- GPU support requires CUDA-compatible hardware and drivers.
- If you are developing locally without Docker, you can install dependencies manually:
   ```bash
   pip install -r requirements.txt
   ```

## License
This project is licensed under the MIT License.
