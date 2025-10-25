#!/bin/bash
#
# Docker Volumes Backup Script
# Backs up Docker volumes (Ollama models, PostgreSQL data, Redis data)
#
# Usage: ./backup_docker_volumes.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups/docker_volumes"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR"

echo "📦 Backing up Docker volumes..."
echo ""

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    exit 1
fi

# Backup Ollama models (122GB - this will take a while)
echo "🤖 Backing up Ollama models..."
echo "   ⚠️  This may take 10-30 minutes (122GB of data)..."
if docker run --rm \
    -v life-os_ollama_models:/source:ro \
    -v "$BACKUP_DIR":/backup \
    alpine \
    tar -czf "/backup/ollama_models_${TIMESTAMP}.tar.gz" -C /source . 2>/dev/null; then
    OLLAMA_SIZE=$(du -sh "$BACKUP_DIR/ollama_models_${TIMESTAMP}.tar.gz" | cut -f1)
    echo "   ✅ Ollama models backed up (Size: $OLLAMA_SIZE)"
else
    echo "   ⚠️  Ollama models backup failed"
fi
echo ""

# Backup PostgreSQL volume (alternative to pg_dump)
echo "🗄️  Backing up PostgreSQL volume..."
if docker run --rm \
    -v life-os_postgres_data:/source:ro \
    -v "$BACKUP_DIR":/backup \
    alpine \
    tar -czf "/backup/postgres_volume_${TIMESTAMP}.tar.gz" -C /source . 2>/dev/null; then
    PG_SIZE=$(du -sh "$BACKUP_DIR/postgres_volume_${TIMESTAMP}.tar.gz" | cut -f1)
    echo "   ✅ PostgreSQL volume backed up (Size: $PG_SIZE)"
else
    echo "   ⚠️  PostgreSQL volume backup failed"
fi
echo ""

# Backup Redis volume (less critical - cache data)
echo "🔴 Backing up Redis volume..."
if docker run --rm \
    -v life-os_redis_data:/source:ro \
    -v "$BACKUP_DIR":/backup \
    alpine \
    tar -czf "/backup/redis_volume_${TIMESTAMP}.tar.gz" -C /source . 2>/dev/null; then
    REDIS_SIZE=$(du -sh "$BACKUP_DIR/redis_volume_${TIMESTAMP}.tar.gz" | cut -f1)
    echo "   ✅ Redis volume backed up (Size: $REDIS_SIZE)"
else
    echo "   ⚠️  Redis volume backup failed"
fi
echo ""

# Retention: Keep last 4 weekly backups for each volume
echo "🧹 Cleaning up old volume backups (keeping last 4)..."
for volume in ollama_models postgres_volume redis_volume; do
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR/${volume}_"*.tar.gz 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 4 ]; then
        ls -1t "$BACKUP_DIR/${volume}_"*.tar.gz | tail -n +5 | xargs rm -f
        DELETED=$((BACKUP_COUNT - 4))
        echo "   Deleted $DELETED old ${volume} backup(s)"
    fi
done
echo ""

# Summary
echo "========================================="
echo "✅ Docker volumes backup complete"
echo "========================================="
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Recent volume backups:"
ls -lht "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -5 || echo "  (none)"
echo ""

exit 0
