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
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --extra-index-url https://download.pytorch.org/whl/cu118 -r requirements.txt

# Pre-download model to avoid first-request delays
RUN mkdir -p /root/.cache/huggingface/hub
RUN python3 -c "from transformers import GPT2LMHeadModel, GPT2Tokenizer; GPT2Tokenizer.from_pretrained('gpt2'); GPT2LMHeadModel.from_pretrained('gpt2')"

# Copy worker application files
COPY . .

# Copy and set the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Default command (will be passed to entrypoint)
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info", "--pool=solo"]