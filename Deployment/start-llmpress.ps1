# PowerShell script to start LLMPress with GPU support

Write-Host "Starting LLMPress with GPU support..." -ForegroundColor Green

# Change to the deployment directory (where docker-compose.yml is located)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptPath
Write-Host "Changed to directory: $scriptPath" -ForegroundColor Cyan

# Use .env file for LLMPRESS_ROOT (preferred) or set a default
if (-not $env:LLMPRESS_ROOT) {
    # Relative path from Deployment directory
    $aiPath = Join-Path -Path (Split-Path -Parent $scriptPath) -ChildPath "AI"
    if (Test-Path $aiPath) {
        $env:LLMPRESS_ROOT = $aiPath
        Write-Host "Set LLMPRESS_ROOT to: $env:LLMPRESS_ROOT" -ForegroundColor Yellow
    } else {
        Write-Host "WARNING: AI directory not found at $aiPath" -ForegroundColor Red
    }
}

# Check if nvidia-smi is available (basic GPU check)
Write-Host "Checking for NVIDIA GPU..." -ForegroundColor Cyan
$nvidiaSmiAvailable = $false
try {
    $nvidiaSmiOutput = nvidia-smi
    $nvidiaSmiAvailable = $true
    Write-Host "NVIDIA GPU detected!" -ForegroundColor Green
    Write-Host "GPU Information:" -ForegroundColor Cyan
    $nvidiaSmiOutput | Select-Object -First 10 | ForEach-Object { Write-Host "  $_" }
} catch {
    Write-Host "WARNING: NVIDIA GPU not detected or drivers not installed!" -ForegroundColor Red
    Write-Host "GPU acceleration will not be available." -ForegroundColor Red
    
    $continue = Read-Host "Continue without GPU support? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Exiting..." -ForegroundColor Red
        exit 1
    }
}

# Check if NVIDIA Docker runtime is available
Write-Host "Checking NVIDIA Docker runtime..." -ForegroundColor Cyan
$testContainer = "nvidia-docker-test"
try {
    docker run --rm --name $testContainer --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
    Write-Host "NVIDIA Docker runtime is working correctly!" -ForegroundColor Green
} catch {
    Write-Host "WARNING: NVIDIA Docker runtime test failed!" -ForegroundColor Red
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "1. NVIDIA Container Toolkit not installed" -ForegroundColor Yellow
    Write-Host "2. Docker service not configured for NVIDIA runtime" -ForegroundColor Yellow
    Write-Host "3. Docker daemon not restarted after configuration" -ForegroundColor Yellow
    
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Exiting..." -ForegroundColor Red
        exit 1
    }
}

# Run Docker Compose with GPU profile
Write-Host "Starting Docker Compose with GPU profile..." -ForegroundColor Cyan
Write-Host "Command: docker compose --profile gpu up --build" -ForegroundColor Gray
docker compose --profile gpu up --build

# To run in detached mode, uncomment the line below:
# docker compose --profile gpu up --build -d