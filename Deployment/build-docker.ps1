# Simple script to build Docker containers for LLMPress
Write-Host "Building Docker containers..." -ForegroundColor Cyan

# Build the Docker containers
docker compose build

Write-Host "Build completed." -ForegroundColor Green
