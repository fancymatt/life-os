#!/bin/bash
# Docker Entrypoint Script
# Runs startup tasks and starts the API server

set -e

echo "🚀 Starting AI-Studio API..."

# Run preview generation in background (non-blocking)
if [ -f "/app/scripts/startup_generate_previews.py" ]; then
    echo "🔍 Checking for missing preview images (background task)..."
    python /app/scripts/startup_generate_previews.py > /dev/null 2>&1 &
fi

# Start the API server
echo "✅ Starting FastAPI server..."
exec python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
