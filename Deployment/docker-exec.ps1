# Script to execute commands in Docker containers
param (
    [Parameter(Mandatory=$true)]
    [string]$Service,

    [Parameter(Mandatory=$true)]
    [string]$Command,

    [Parameter(Mandatory=$false, ValueFromRemainingArguments=$true)]
    [string[]]$CommandArgs
)

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
