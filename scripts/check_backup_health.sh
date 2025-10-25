#!/bin/bash
#
# Backup Health Check Script
# Monitors backup freshness and sends alerts if backups are stale
#
# Usage: ./check_backup_health.sh

set -euo pipefail

PROJECT_DIR="/Users/fancymatt/docker/life-os"
ALERT_EMAIL="${BACKUP_ALERT_EMAIL:-}"  # Set in environment or .env

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🏥 Life-OS Backup Health Check"
echo "$(date)"
echo "========================================="
echo ""

# Check PostgreSQL backup age
echo "📊 PostgreSQL Database Backups:"
LATEST_PG=$(ls -t "$PROJECT_DIR/backups/postgres"/*.sql.gz 2>/dev/null | head -1)
if [ -n "$LATEST_PG" ]; then
    PG_AGE_HOURS=$(( ($(date +%s) - $(stat -f %m "$LATEST_PG")) / 3600 ))
    PG_SIZE=$(du -sh "$LATEST_PG" | cut -f1)
    echo "   Latest backup: $(basename "$LATEST_PG")"
    echo "   Age: $PG_AGE_HOURS hours"
    echo "   Size: $PG_SIZE"

    if [ $PG_AGE_HOURS -gt 2 ]; then
        echo -e "   ${YELLOW}⚠️  WARNING: PostgreSQL backup is stale (>2 hours old)${NC}"
        if [ -n "$ALERT_EMAIL" ]; then
            echo "PostgreSQL backup is $PG_AGE_HOURS hours old" | \
                mail -s "Life-OS Backup Alert: Stale PostgreSQL Backup" "$ALERT_EMAIL" 2>/dev/null || true
        fi
    else
        echo -e "   ${GREEN}✓ Fresh backup${NC}"
    fi
else
    echo -e "   ${RED}❌ No PostgreSQL backups found!${NC}"
fi
echo ""

# Check application data backup age
echo "📁 Application Data Backups:"
LATEST_APP=$(ls -t "$PROJECT_DIR/backups/app_data"/*.tar.gz 2>/dev/null | head -1)
if [ -n "$LATEST_APP" ]; then
    APP_AGE_HOURS=$(( ($(date +%s) - $(stat -f %m "$LATEST_APP")) / 3600 ))
    APP_SIZE=$(du -sh "$LATEST_APP" | cut -f1)
    echo "   Latest backup: $(basename "$LATEST_APP")"
    echo "   Age: $APP_AGE_HOURS hours"
    echo "   Size: $APP_SIZE"

    if [ $APP_AGE_HOURS -gt 25 ]; then
        echo -e "   ${YELLOW}⚠️  WARNING: App data backup is stale (>25 hours old)${NC}"
    else
        echo -e "   ${GREEN}✓ Fresh backup${NC}"
    fi
else
    echo -e "   ${RED}❌ No app data backups found!${NC}"
fi
echo ""

# Check Docker volume backups (weekly, so less critical)
echo "🐳 Docker Volume Backups:"
LATEST_OLLAMA=$(ls -t "$PROJECT_DIR/backups/docker_volumes"/ollama_models_*.tar.gz 2>/dev/null | head -1)
if [ -n "$LATEST_OLLAMA" ]; then
    OLLAMA_AGE_DAYS=$(( ($(date +%s) - $(stat -f %m "$LATEST_OLLAMA")) / 86400 ))
    OLLAMA_SIZE=$(du -sh "$LATEST_OLLAMA" | cut -f1)
    echo "   Latest Ollama backup: $(basename "$LATEST_OLLAMA")"
    echo "   Age: $OLLAMA_AGE_DAYS days"
    echo "   Size: $OLLAMA_SIZE"

    if [ $OLLAMA_AGE_DAYS -gt 8 ]; then
        echo -e "   ${YELLOW}⚠️  WARNING: Ollama backup is stale (>8 days old)${NC}"
    else
        echo -e "   ${GREEN}✓ Fresh backup${NC}"
    fi
else
    echo "   ℹ️  No Ollama volume backups found (expected weekly)"
fi
echo ""

# Check total backup directory size
echo "💾 Backup Storage Usage:"
BACKUP_SIZE=$(du -sh "$PROJECT_DIR/backups" | cut -f1)
echo "   Total backup size: $BACKUP_SIZE"
echo ""

# Check Docker containers status
echo "🐋 Docker Containers:"
if docker ps --filter "name=ai-studio" --format '{{.Names}}: {{.Status}}' 2>/dev/null | grep -q "ai-studio-api"; then
    echo -e "   ${GREEN}✓ Life-OS containers running${NC}"
    docker ps --filter "name=ai-studio" --format '   - {{.Names}}: {{.Status}}'
else
    echo -e "   ${RED}❌ Life-OS containers NOT running!${NC}"
    echo "   Stopped containers:"
    docker ps -a --filter "name=ai-studio" --format '   - {{.Names}}: {{.Status}}'
fi
echo ""

# Show recent backup activity
echo "📋 Recent Backup Activity:"
if [ -f "$PROJECT_DIR/logs/backups.log" ]; then
    echo "   Last 5 backup operations:"
    grep "Backup completed successfully" "$PROJECT_DIR/logs/backups.log" 2>/dev/null | tail -5 | sed 's/^/   /'
else
    echo "   ⚠️  No backup log found"
fi
echo ""

echo "========================================="
echo "Health check complete"
echo ""
