# Local Deployment Script for Never-Be-Alone (PowerShell)
# Runs the orchestrator locally with gunicorn

Write-Host "========================================"
Write-Host "Never-Be-Alone Local Server"
Write-Host "========================================"

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "ERROR: .env file not found!"
    Write-Host "Please create a .env file with your API keys"
    exit 1
}

# Load environment variables from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

# Set port
$PORT = if ($env:PORT) { $env:PORT } else { "8080" }

Write-Host "Starting server on port $PORT..."
Write-Host ""
Write-Host "Endpoints:"
Write-Host "  - GET  http://localhost:$PORT/health"
Write-Host "  - POST http://localhost:$PORT/orchestrate"
Write-Host ""
Write-Host "Press Ctrl+C to stop"
Write-Host "========================================"

# Run with gunicorn
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 300 main:app
