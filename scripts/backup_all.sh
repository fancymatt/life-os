#!/bin/bash
#
# Master Backup Script for Life-OS
# Orchestrates database, data, and Docker volume backups
#
# Usage:
#   ./backup_all.sh [tier]
#     tier: local | nas | cloud (default: local)

set -euo pipefail

# Configuration
TIER="${1:-local}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$PROJECT_DIR/logs/backup_${TIMESTAMP}.log"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "Starting Life-OS Backup (Tier: $TIER)"
log "========================================="

# 1. Backup PostgreSQL database
log "Step 1/5: Backing up PostgreSQL database..."
if "$SCRIPT_DIR/backup_postgres.sh" 7; then
    log "✓ PostgreSQL backup complete"
else
    log "✗ PostgreSQL backup FAILED"
    exit 1
fi

# 2. Backup application data
log "Step 2/5: Backing up application data..."
if "$SCRIPT_DIR/backup_app_data.sh"; then
    log "✓ Application data backup complete"
else
    log "✗ Application data backup FAILED"
    exit 1
fi

# 3. Backup Docker volumes (weekly only, or if FORCE_FULL=true)
if [ "$(date +%u)" -eq 7 ] || [ "${FORCE_FULL:-false}" = "true" ]; then
    log "Step 3/5: Backing up Docker volumes (weekly)..."
    if "$SCRIPT_DIR/backup_docker_volumes.sh"; then
        log "✓ Docker volumes backup complete"
    else
        log "⚠ Docker volumes backup FAILED (non-critical)"
    fi
else
    log "Step 3/5: Skipping Docker volumes backup (not Sunday, use FORCE_FULL=true to override)"
fi

# 4. Sync to NAS (if tier=nas or tier=cloud)
if [ "$TIER" = "nas" ] || [ "$TIER" = "cloud" ]; then
    if [ -f "$SCRIPT_DIR/sync_to_nas.sh" ]; then
        log "Step 4/5: Syncing to NAS..."
        if "$SCRIPT_DIR/sync_to_nas.sh"; then
            log "✓ NAS sync complete"
        else
            log "⚠ NAS sync FAILED (non-critical)"
        fi
    else
        log "Step 4/5: Skipping NAS sync (sync_to_nas.sh not configured)"
    fi
else
    log "Step 4/5: Skipping NAS sync (tier=$TIER)"
fi

# 5. Upload to cloud (if tier=cloud)
if [ "$TIER" = "cloud" ]; then
    if [ -f "$SCRIPT_DIR/upload_to_cloud.sh" ]; then
        log "Step 5/5: Uploading to cloud storage..."
        if "$SCRIPT_DIR/upload_to_cloud.sh"; then
            log "✓ Cloud upload complete"
        else
            log "⚠ Cloud upload FAILED (non-critical)"
        fi
    else
        log "Step 5/5: Skipping cloud upload (upload_to_cloud.sh not configured)"
    fi
else
    log "Step 5/5: Skipping cloud upload (tier=$TIER)"
fi

log "========================================="
log "Backup completed successfully"
log "Backup log: $LOG_FILE"
log "========================================="
