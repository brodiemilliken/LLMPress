# Script to control Docker containers
param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [int]$Workers = 1,
    
    [Parameter(Mandatory=$false)]
    [int]$Backends = 1
)

# Set the current directory to the script's directory
Set-Location $PSScriptRoot

# Define actions
switch ($Action) {
    "start" {
        Write-Host "Starting Docker containers with $Workers worker(s) and $Backends backend(s)..." -ForegroundColor Cyan
        
        # Set environment variables for scaling
        $env:WORKER_SCALE = $Workers
        $env:BACKEND_SCALE = $Backends
        
        # Start containers
        docker compose up -d
        
        Write-Host "Containers started successfully." -ForegroundColor Green
    }
    "stop" {
        Write-Host "Stopping Docker containers..." -ForegroundColor Cyan
        docker compose down
        Write-Host "Containers stopped successfully." -ForegroundColor Green
    }
    "restart" {
        Write-Host "Restarting Docker containers with $Workers worker(s) and $Backends backend(s)..." -ForegroundColor Cyan
        
        # Set environment variables for scaling
        $env:WORKER_SCALE = $Workers
        $env:BACKEND_SCALE = $Backends
        
        # Restart containers
        docker compose down
        docker compose up -d
        
        Write-Host "Containers restarted successfully." -ForegroundColor Green
    }
    "status" {
        Write-Host "Checking Docker container status..." -ForegroundColor Cyan
        docker compose ps
    }
}
