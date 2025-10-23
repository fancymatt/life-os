#!/bin/bash
# Docker Entrypoint Script
# Runs startup tasks and starts the API server

set -e

echo "🚀 Starting AI-Studio API..."

# Preview generation removed - was causing OOM issues on startup
# Use POST /api/clothing-items/batch-generate-previews endpoint instead

# Start the API server
echo "✅ Starting FastAPI server..."
exec python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
