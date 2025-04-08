# Docker Scripts for LLMPress

This document explains how to use the simplified Docker scripts for building and controlling the LLMPress containers.

## Scripts

### build-docker.ps1

Builds all Docker containers defined in the `docker-compose.yml` file.

```powershell
.\build-docker.ps1
```

### docker-control.ps1

Controls the Docker containers with start, stop, and restart actions. Also allows scaling the number of workers and backends.

```powershell
# Start containers with default configuration (1 worker, 1 backend)
.\docker-control.ps1 -Action start

# Start containers with custom scaling (2 workers, 1 backend)
.\docker-control.ps1 -Action start -Workers 2 -Backends 1

# Start containers with custom scaling (1 worker, 2 backends)
.\docker-control.ps1 -Action start -Workers 1 -Backends 2

# Stop all containers
.\docker-control.ps1 -Action stop

# Restart containers with custom scaling
.\docker-control.ps1 -Action restart -Workers 3 -Backends 2
```

#### Parameters

- `-Action`: Required. Specifies the action to perform: "start", "stop", or "restart".
- `-Workers`: Optional. Number of worker containers to run (default: 1).
- `-Backends`: Optional. Number of backend containers to run (default: 1).

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

## Running Tests

To run tests in the backend container:

```powershell
# Start the containers first
.\docker-control.ps1 -Action start

# Run a test using the docker-run.ps1 script
.\docker-run.ps1 backend python Test/encoder_decoder_test.py

# Run batch test using the docker-run.ps1 script
.\docker-run.ps1 backend python Test/batch_test.py -i Test/small_files/ -m gpt2
```

## Cleaning Up

You can safely remove the old scripts in this directory:
- llmpress-build.bat
- llmpress-start.bat
- llmpress-stop.bat
- start-llmpress.ps1
- docker-exec.ps1 (replaced by docker-run.ps1)

These have been replaced by the new, simplified scripts.
