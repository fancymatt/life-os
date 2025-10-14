#!/bin/bash
# AI-Studio API Startup Script

set -e

echo "🚀 Starting AI-Studio API..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env with your API keys:"
    echo "  GEMINI_API_KEY=your_key_here"
    echo "  OPENAI_API_KEY=your_key_here (optional)"
    exit 1
fi

# Load environment
export $(cat .env | xargs)

# Check if running in Docker
if [ -n "$DOCKER_ENV" ]; then
    echo "📦 Running in Docker container"
else
    echo "💻 Running locally"

    # Create necessary directories
    mkdir -p presets output cache uploads

    # Check if dependencies are installed
    if ! python3 -c "import fastapi" 2>/dev/null; then
        echo "📦 Installing dependencies..."

        # Use pip3 if pip is not available
        if command -v pip &> /dev/null; then
            pip install -r requirements.txt
        elif command -v pip3 &> /dev/null; then
            pip3 install -r requirements.txt
        else
            echo "❌ Error: pip or pip3 not found"
            echo "Please install dependencies manually:"
            echo "  pip3 install -r requirements.txt"
            exit 1
        fi
    fi
fi

# Start the API
echo "✅ Starting FastAPI server on http://localhost:8000"
echo "📚 API documentation: http://localhost:8000/docs"
echo ""

python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
