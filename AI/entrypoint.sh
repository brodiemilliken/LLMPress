#!/bin/bash
set -e

echo "Initializing CUDA environment in main process..."
# Use python3.9 explicitly and avoid f-strings for compatibility
python3 -c "import torch; print('CUDA available:', torch.cuda.is_available())"


# Execute the command
exec "$@"