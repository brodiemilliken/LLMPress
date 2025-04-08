# Script to run commands in Docker containers
# This script uses a different approach to handle command arguments

# Get the service name (first argument)
$Service = $args[0]

# Get the command (second argument)
$Command = $args[1]

# Get all remaining arguments (third argument onwards)
$CommandArgs = $args[2..$args.Length]

# Check if required arguments are provided
if (-not $Service -or -not $Command) {
    Write-Host "Error: Service and Command are required." -ForegroundColor Red
    Write-Host "Usage: .\docker-run.ps1 <service> <command> [args...]" -ForegroundColor Yellow
    Write-Host "Example: .\docker-run.ps1 backend python Test/batch_test.py -i Test/small_files/ -m gpt2" -ForegroundColor Yellow
    exit 1
}

# Execute the command in the specified service
Write-Host "Executing command in $Service container..." -ForegroundColor Cyan

# Build the full command with arguments
$fullCommand = @("compose", "exec", $Service, $Command)
if ($CommandArgs) {
    $fullCommand += $CommandArgs
}

# Show the command being executed
Write-Host "Running: docker $($fullCommand -join ' ')" -ForegroundColor DarkGray

# Execute the command
& docker $fullCommand

Write-Host "Command execution completed." -ForegroundColor Green
