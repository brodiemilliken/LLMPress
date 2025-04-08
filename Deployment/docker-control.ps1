# Script to control Docker containers for LLMPress with scaling options
param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [int]$Workers = 1,
    
    [Parameter(Mandatory=$false)]
    [int]$Backends = 1
)

# Validate parameters
if ($Workers -lt 1) {
    Write-Host "Error: Number of workers must be at least 1" -ForegroundColor Red
    exit 1
}

if ($Backends -lt 1) {
    Write-Host "Error: Number of backends must be at least 1" -ForegroundColor Red
    exit 1
}

switch ($Action) {
    "start" {
        Write-Host "Starting Docker containers..." -ForegroundColor Cyan
        Write-Host "Configuration: $Workers worker(s), $Backends backend(s)" -ForegroundColor Cyan
        
        # Start the containers
        docker compose up -d
        
        # Scale the services if needed
        if ($Workers -gt 1 -or $Backends -gt 1) {
            Write-Host "Scaling services..." -ForegroundColor Cyan
            docker compose up -d --scale llmpress-worker=$Workers --scale backend=$Backends
        }
        
        Write-Host "Containers started." -ForegroundColor Green
        
        # Display running containers
        Write-Host "`nRunning containers:" -ForegroundColor Cyan
        docker compose ps
    }
    "stop" {
        Write-Host "Stopping Docker containers..." -ForegroundColor Cyan
        docker compose down
        Write-Host "Containers stopped." -ForegroundColor Green
    }
    "restart" {
        Write-Host "Restarting Docker containers..." -ForegroundColor Cyan
        Write-Host "Configuration: $Workers worker(s), $Backends backend(s)" -ForegroundColor Cyan
        
        # Stop all containers
        docker compose down
        
        # Start the containers
        docker compose up -d
        
        # Scale the services if needed
        if ($Workers -gt 1 -or $Backends -gt 1) {
            Write-Host "Scaling services..." -ForegroundColor Cyan
            docker compose up -d --scale llmpress-worker=$Workers --scale backend=$Backends
        }
        
        Write-Host "Containers restarted." -ForegroundColor Green
        
        # Display running containers
        Write-Host "`nRunning containers:" -ForegroundColor Cyan
        docker compose ps
    }
}
