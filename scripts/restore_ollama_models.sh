#!/bin/bash
#
# Restore Ollama Models from Manifest
# Re-downloads all models listed in the manifest
#
# Usage: ./restore_ollama_models.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MANIFEST_FILE="$PROJECT_DIR/data/ollama_models_manifest.txt"

echo "🔄 Restoring Ollama models from manifest..."
echo ""

# Check if manifest exists
if [ ! -f "$MANIFEST_FILE" ]; then
    echo "❌ Manifest not found: $MANIFEST_FILE"
    echo "   Run: ./scripts/save_ollama_manifest.sh"
    exit 1
fi

# Check if Ollama container is running
if ! docker ps --filter "name=ai-studio-ollama" --format '{{.Names}}' | grep -q "ai-studio-ollama"; then
    echo "⚠️  Ollama container is not running"
    echo "   Start with: docker-compose up -d ollama"
    exit 1
fi

# Extract model names from manifest (skip header lines and parse model names)
echo "📋 Models to restore:"
MODELS=$(grep -v '^#' "$MANIFEST_FILE" | grep -v '^NAME' | awk '{print $1}' | grep -v '^$')

if [ -z "$MODELS" ]; then
    echo "⚠️  No models found in manifest"
    exit 1
fi

echo "$MODELS"
echo ""

# Ask for confirmation
echo "⚠️  This will download all models listed above."
echo "   Estimated time: 30-60 minutes"
echo "   Estimated size: ~122GB"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

# Download each model
COUNT=0
TOTAL=$(echo "$MODELS" | wc -l)

for model in $MODELS; do
    COUNT=$((COUNT + 1))
    echo ""
    echo "[$COUNT/$TOTAL] Pulling $model..."
    docker exec ai-studio-ollama ollama pull "$model"
done

echo ""
echo "========================================="
echo "✅ All models restored successfully"
echo "========================================="
echo ""
docker exec ai-studio-ollama ollama list
