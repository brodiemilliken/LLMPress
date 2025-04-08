# LLMPress Deployment

This directory contains scripts and configuration files for deploying and managing LLMPress.

## Prerequisites

- Docker and Docker Compose
- PowerShell (for Windows users)

## Quick Start

1. Start the containers:
```powershell
.\docker-control.ps1 -Action start
```

2. Run a test:
```powershell
.\docker-run.ps1 backend python Test/batch_test.py -i Test/small_files/ -m gpt2
```

3. Stop the containers:
```powershell
.\docker-control.ps1 -Action stop
```

## Available Scripts

### docker-control.ps1

Controls Docker containers (start, stop, restart, status).

```powershell
# Start containers with default scaling (1 worker, 1 backend)
.\docker-control.ps1 -Action start

# Start containers with custom scaling
.\docker-control.ps1 -Action start -Workers 2 -Backends 1

# Stop all containers
.\docker-control.ps1 -Action stop

# Restart containers
.\docker-control.ps1 -Action restart

# Check container status
.\docker-control.ps1 -Action status
```

#### Parameters

- `-Action`: Required. The action to perform (start, stop, restart, status).
- `-Workers`: Optional. The number of worker containers to start (default: 1).
- `-Backends`: Optional. The number of backend containers to start (default: 1).

### docker-run.ps1

Executes commands in Docker containers. This is especially useful for running tests or other commands in the backend container.

```powershell
# Run a test in the backend container
.\docker-run.ps1 backend python Test/encoder_decoder_test.py

# Run batch test in the backend container
.\docker-run.ps1 backend python Test/batch_test.py -i Test/small_files/ -m gpt2

# Run a command in the redis container
.\docker-run.ps1 redis redis-cli ping
```

#### Parameters

- `<service>`: The service to run the command in (e.g., "backend", "redis", "llmpress-worker").
- `<command>`: The main command to execute in the container.
- `[args...]`: Any additional arguments to pass to the command.

### docker-exec.ps1

Alternative script for executing commands in Docker containers with named parameters.

```powershell
# Run a test in the backend container
.\docker-exec.ps1 -Service backend -Command python -Args Test/encoder_decoder_test.py

# Run a command in the redis container
.\docker-exec.ps1 -Service redis -Command redis-cli -Args ping
```

#### Parameters

- `-Service`: Required. The service to run the command in (e.g., "backend", "redis", "llmpress-worker").
- `-Command`: Required. The main command to execute in the container.
- `-Args`: Optional. Additional arguments to pass to the command.

## Running Tests

You can run tests in the backend container using the docker-run.ps1 script:

```powershell
# Start the containers first
.\docker-control.ps1 -Action start

# Run a test using the docker-run.ps1 script
.\docker-run.ps1 backend python Test/encoder_decoder_test.py

# Run batch test using the docker-run.ps1 script
.\docker-run.ps1 backend python Test/batch_test.py -i Test/small_files/ -m gpt2
```

## Configuration

The `.env` file contains environment variables used by Docker Compose. You can modify this file to change the configuration.

## Troubleshooting

If you encounter issues with the Docker containers, try the following:

1. Check the container logs:
```powershell
docker compose logs
```

2. Restart the containers:
```powershell
.\docker-control.ps1 -Action restart
```

3. Rebuild the containers:
```powershell
docker compose build --no-cache
```
