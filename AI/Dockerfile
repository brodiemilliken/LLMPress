FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.9 \
    python3-pip \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --extra-index-url https://download.pytorch.org/whl/cu118 -r requirements.txt

# Copy AI module files
COPY . .

# Default command
CMD ["python3", "-c", "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"]