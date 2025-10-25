#!/bin/bash
#
# Save Ollama Model Manifest
# Creates a list of installed Ollama models for recovery purposes
#
# Usage: ./save_ollama_manifest.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MANIFEST_FILE="$PROJECT_DIR/data/ollama_models_manifest.txt"

echo "📋 Saving Ollama model manifest..."

# Check if Ollama container is running
if ! docker ps --filter "name=ai-studio-ollama" --format '{{.Names}}' | grep -q "ai-studio-ollama"; then
    echo "⚠️  Ollama container is not running"
    exit 1
fi

# Get list of installed models
echo "# Ollama Models Manifest" > "$MANIFEST_FILE"
echo "# Generated: $(date)" >> "$MANIFEST_FILE"
echo "# Hostname: $(hostname)" >> "$MANIFEST_FILE"
echo "#" >> "$MANIFEST_FILE"
echo "# To restore models after disaster:" >> "$MANIFEST_FILE"
echo "#   docker exec ai-studio-ollama ollama pull <model-name>" >> "$MANIFEST_FILE"
echo "" >> "$MANIFEST_FILE"

docker exec ai-studio-ollama ollama list >> "$MANIFEST_FILE"

echo "✅ Manifest saved to: $MANIFEST_FILE"
echo ""
echo "Installed models:"
docker exec ai-studio-ollama ollama list
echo ""
echo "To restore all models, run:"
echo "  ./scripts/restore_ollama_models.sh"
