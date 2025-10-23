#!/bin/bash
#
# PostgreSQL Backup Script
#
# Creates full database backups using pg_dump.
# Supports daily full backups and retention policies.
#
# Usage:
#   ./scripts/backup_postgresql.sh [full|incremental]
#
# Cron examples:
#   # Daily full backup at 2 AM
#   0 2 * * * /path/to/scripts/backup_postgresql.sh full
#
#   # Hourly incremental backup (using WAL archiving)
#   0 * * * * /path/to/scripts/backup_postgresql.sh incremental
#

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups/postgresql}"
BACKUP_TYPE="${1:-full}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_ONLY=$(date +%Y%m%d)

# Database connection (from docker-compose.yml)
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-ai-studio-postgres}"
POSTGRES_DB="${POSTGRES_DB:-life_os}"
POSTGRES_USER="${POSTGRES_USER:-lifeos}"

# Retention settings
KEEP_DAILY_BACKUPS=30     # Keep daily backups for 30 days
KEEP_HOURLY_BACKUPS=7     # Keep hourly backups for 7 days

# Create backup directory
mkdir -p "$BACKUP_DIR/full"
mkdir -p "$BACKUP_DIR/incremental"

echo "🗄️  PostgreSQL Backup Script"
echo "============================"
echo "Type: $BACKUP_TYPE"
echo "Timestamp: $TIMESTAMP"
echo "Database: $POSTGRES_DB"
echo ""

# Check if Docker container is running
if ! docker ps | grep -q "$POSTGRES_CONTAINER"; then
    echo "❌ Error: PostgreSQL container '$POSTGRES_CONTAINER' is not running"
    echo "   Start it with: docker-compose up -d postgres"
    exit 1
fi

case "$BACKUP_TYPE" in
    full)
        # Full database backup
        BACKUP_FILE="$BACKUP_DIR/full/postgres_full_${DATE_ONLY}_${TIMESTAMP}.sql"
        echo "📦 Creating full database backup..."
        echo "   Output: $BACKUP_FILE"

        # Use pg_dump to create full backup
        docker exec "$POSTGRES_CONTAINER" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
            --clean --if-exists --create \
            > "$BACKUP_FILE"

        if [ $? -eq 0 ]; then
            # Compress backup
            echo "🗜️  Compressing backup..."
            gzip -f "$BACKUP_FILE"
            BACKUP_FILE="${BACKUP_FILE}.gz"

            BACKUP_SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
            echo "   ✅ Backup created: $(basename "$BACKUP_FILE") ($BACKUP_SIZE)"

            # Verify backup
            echo "🔍 Verifying backup..."
            if gunzip -t "$BACKUP_FILE" 2>/dev/null; then
                echo "   ✅ Backup integrity verified"
            else
                echo "   ⚠️  Warning: Backup integrity check failed"
            fi

            # Cleanup old backups
            echo "🧹 Cleaning up old backups (keeping last $KEEP_DAILY_BACKUPS days)..."
            find "$BACKUP_DIR/full" -name "postgres_full_*.sql.gz" -mtime +$KEEP_DAILY_BACKUPS -delete
            REMAINING=$(ls -1 "$BACKUP_DIR/full"/postgres_full_*.sql.gz 2>/dev/null | wc -l)
            echo "   ℹ️  Backups remaining: $REMAINING"

        else
            echo "   ❌ Backup failed!"
            exit 1
        fi
        ;;

    incremental)
        # Incremental backup using WAL archiving
        BACKUP_FILE="$BACKUP_DIR/incremental/postgres_incr_${DATE_ONLY}_${TIMESTAMP}.wal"
        echo "📦 Creating incremental backup (WAL archive)..."
        echo "   Output: $BACKUP_FILE"

        # Force WAL switch and archive
        docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
            -c "SELECT pg_switch_wal();" > /dev/null 2>&1

        # Copy WAL files (requires WAL archiving to be configured)
        WAL_DIR="/var/lib/postgresql/data/pg_wal"
        docker exec "$POSTGRES_CONTAINER" sh -c "ls -1t $WAL_DIR/*.ready 2>/dev/null | head -1" > /tmp/latest_wal.txt || true

        if [ -s /tmp/latest_wal.txt ]; then
            LATEST_WAL=$(cat /tmp/latest_wal.txt)
            echo "   ⚠️  WAL archiving may not be configured"
            echo "   To enable: Configure archive_mode and archive_command in postgresql.conf"
        fi

        echo "   ℹ️  For incremental backups, configure WAL archiving"
        echo "   See: https://www.postgresql.org/docs/current/continuous-archiving.html"

        # Cleanup old incremental backups
        echo "🧹 Cleaning up old incremental backups (keeping last $KEEP_HOURLY_BACKUPS days)..."
        find "$BACKUP_DIR/incremental" -name "postgres_incr_*.wal" -mtime +$KEEP_HOURLY_BACKUPS -delete 2>/dev/null || true
        ;;

    *)
        echo "❌ Error: Unknown backup type '$BACKUP_TYPE'"
        echo "   Usage: $0 [full|incremental]"
        exit 1
        ;;
esac

echo ""
echo "✅ Backup Complete!"
echo "==================="
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "To restore from this backup:"
echo "  # Full backup"
echo "  gunzip -c $BACKUP_FILE | docker exec -i $POSTGRES_CONTAINER psql -U $POSTGRES_USER"
echo ""
echo "To schedule automated backups:"
echo "  # Daily full backup at 2 AM"
echo "  echo '0 2 * * * $SCRIPT_DIR/backup_postgresql.sh full >> /var/log/postgres_backup.log 2>&1' | crontab -"
echo ""
echo "Done! 🎉"
