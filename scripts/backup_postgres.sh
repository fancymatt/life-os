#!/bin/bash
# PostgreSQL Backup Script
# Creates timestamped full backups of the Life-OS database
#
# Usage: ./backup_postgres.sh [retention_days]
#   retention_days: Number of days to keep backups (default: 30)
#
# Schedule with cron:
#   Daily: 0 2 * * * /path/to/backup_postgres.sh
#   Hourly: 0 * * * * /path/to/backup_postgres.sh 7

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups/postgres"
RETENTION_DAYS="${1:-30}"  # Default 30 days retention
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/life_os_backup_$TIMESTAMP.sql"
LOG_FILE="$PROJECT_DIR/logs/backups.log"

# Database connection (from docker-compose.yml)
DB_CONTAINER="ai-studio-postgres"
DB_NAME="lifeos"
DB_USER="lifeos"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$PROJECT_DIR/logs"

log "========================================="
log "Starting PostgreSQL backup"
log "Backup file: $BACKUP_FILE"

# Check if docker is running
if ! docker ps > /dev/null 2>&1; then
    error_exit "Docker is not running"
fi

# Check if postgres container is running
if ! docker ps --filter "name=$DB_CONTAINER" --format '{{.Names}}' | grep -q "$DB_CONTAINER"; then
    error_exit "PostgreSQL container '$DB_CONTAINER' is not running"
fi

# Perform backup using pg_dump
echo -e "${YELLOW}Creating database backup...${NC}"
log "Running pg_dump..."

if docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" --clean --if-exists > "$BACKUP_FILE"; then
    # Get backup file size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✓ Backup created successfully${NC}"
    log "Backup created: $BACKUP_FILE (Size: $BACKUP_SIZE)"

    # Compress backup (optional, saves space)
    echo -e "${YELLOW}Compressing backup...${NC}"
    if gzip "$BACKUP_FILE"; then
        COMPRESSED_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
        echo -e "${GREEN}✓ Backup compressed${NC}"
        log "Backup compressed: ${BACKUP_FILE}.gz (Size: $COMPRESSED_SIZE)"
    else
        echo -e "${YELLOW}⚠ Compression failed, keeping uncompressed backup${NC}"
        log "WARNING: Compression failed"
    fi
else
    error_exit "pg_dump failed"
fi

# Cleanup old backups (retention policy)
echo -e "${YELLOW}Cleaning up old backups (keeping last $RETENTION_DAYS days)...${NC}"
log "Applying retention policy: $RETENTION_DAYS days"

DELETED_COUNT=0
while IFS= read -r -d '' old_backup; do
    rm "$old_backup"
    DELETED_COUNT=$((DELETED_COUNT + 1))
    log "Deleted old backup: $(basename "$old_backup")"
done < <(find "$BACKUP_DIR" -name "life_os_backup_*.sql.gz" -type f -mtime +"$RETENTION_DAYS" -print0)

if [ $DELETED_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓ Deleted $DELETED_COUNT old backup(s)${NC}"
    log "Deleted $DELETED_COUNT old backups"
else
    echo -e "${GREEN}✓ No old backups to delete${NC}"
    log "No old backups to delete"
fi

# Count total backups
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "life_os_backup_*.sql.gz" -type f | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Backup completed successfully${NC}"
echo -e "${GREEN}Total backups: $TOTAL_BACKUPS (Total size: $TOTAL_SIZE)${NC}"
echo -e "${GREEN}=========================================${NC}"

log "Backup completed successfully (Total backups: $TOTAL_BACKUPS, Total size: $TOTAL_SIZE)"
log "========================================="

exit 0
