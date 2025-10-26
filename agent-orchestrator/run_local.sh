#!/bin/bash
# Local Deployment Script for Never-Be-Alone
# Runs the orchestrator locally with gunicorn

echo "========================================"
echo "Never-Be-Alone Local Server"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create a .env file with your API keys"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Set port
PORT=${PORT:-8080}

echo "Starting server on port $PORT..."
echo ""
echo "Endpoints:"
echo "  - GET  http://localhost:$PORT/health"
echo "  - POST http://localhost:$PORT/orchestrate"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"

# Run with gunicorn
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 300 main:app
