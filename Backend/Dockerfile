FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app:/app/AI

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY Backend/requirements.txt .
RUN pip install -r requirements.txt

# Create necessary directories
RUN mkdir -p Output/Compressed Output/Results Output/Debug

# Use a simple shell command to keep the container running
CMD ["sh", "-c", "echo 'Backend container running. Use \"docker compose exec backend python <script.py>\" to run tests.' && tail -f /dev/null"]

