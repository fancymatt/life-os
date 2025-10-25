#!/bin/bash
#
# Install Cron Jobs for Automated Backups
# Sets up automated backup schedule for Life-OS
#
# Usage: ./install_cron.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📅 Installing Life-OS Backup Cron Jobs"
echo "========================================="
echo ""

# Check if scripts exist and are executable
for script in backup_all.sh backup_postgres.sh check_backup_health.sh; do
    if [ ! -x "$SCRIPT_DIR/$script" ]; then
        echo "❌ Error: $script not found or not executable"
        echo "   Run: chmod +x $SCRIPT_DIR/$script"
        exit 1
    fi
done

echo "✓ All backup scripts found and executable"
echo ""

# Show current crontab (if any)
echo "Current crontab (before changes):"
crontab -l 2>/dev/null || echo "  (none)"
echo ""

# Backup existing crontab
if crontab -l &>/dev/null; then
    BACKUP_FILE="$PROJECT_DIR/backups/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
    mkdir -p "$PROJECT_DIR/backups"
    crontab -l > "$BACKUP_FILE"
    echo "✓ Existing crontab backed up to: $BACKUP_FILE"
    echo ""
fi

# Create new crontab with Life-OS backup jobs
echo "Installing new cron jobs..."
(crontab -l 2>/dev/null | grep -v "Life-OS" || true; cat <<EOF

# ========================================
# Life-OS Automated Backups
# ========================================
# Installed: $(date)
# Docs: $PROJECT_DIR/docs/BACKUP_AND_DISASTER_RECOVERY.md

# Hourly: PostgreSQL database (local only)
# Keeps last 1 day of hourly backups
0 * * * * $SCRIPT_DIR/backup_postgres.sh 1 >> $PROJECT_DIR/logs/cron_backup.log 2>&1

# Daily 2 AM: Full application data + NAS sync
# Backs up images, presets, data, uploads
0 2 * * * $SCRIPT_DIR/backup_all.sh nas >> $PROJECT_DIR/logs/cron_backup.log 2>&1

# Weekly Sunday 4 AM: Full backup including Docker volumes
# Includes Ollama models (122GB - takes 10-30 minutes)
0 4 * * 0 FORCE_FULL=true $SCRIPT_DIR/backup_all.sh cloud >> $PROJECT_DIR/logs/cron_backup.log 2>&1

# Hourly: Check backup health
# Monitors backup freshness and container status
15 * * * * $SCRIPT_DIR/check_backup_health.sh >> $PROJECT_DIR/logs/backup_health.log 2>&1

# Monthly cleanup: Delete backups older than 90 days
# Prevents backup directory from growing indefinitely
0 5 1 * * find $PROJECT_DIR/backups -type f -mtime +90 -delete >> $PROJECT_DIR/logs/cron_backup.log 2>&1

# ========================================
EOF
) | crontab -

echo "✅ Cron jobs installed successfully!"
echo ""

echo "========================================="
echo "Backup Schedule:"
echo "========================================="
echo "  ⏱️  Hourly:   PostgreSQL database (keeps last 24 hours)"
echo "  📅 Daily 2AM: Application data + NAS sync"
echo "  📅 Weekly:    Full backup inc. Docker volumes (Sunday 4AM)"
echo "  🏥 Hourly:    Backup health check (:15 past hour)"
echo "  🧹 Monthly:   Cleanup old backups (>90 days)"
echo ""

echo "========================================="
echo "Installed Cron Jobs:"
echo "========================================="
crontab -l | grep -A 20 "Life-OS"
echo ""

echo "========================================="
echo "Useful Commands:"
echo "========================================="
echo "  View all cron jobs:     crontab -l"
echo "  Edit cron jobs:         crontab -e"
echo "  Remove all cron jobs:   crontab -r"
echo "  View backup logs:       tail -f $PROJECT_DIR/logs/cron_backup.log"
echo "  View health logs:       tail -f $PROJECT_DIR/logs/backup_health.log"
echo "  Manual backup:          $SCRIPT_DIR/backup_all.sh local"
echo ""

echo "⚠️  IMPORTANT NOTES:"
echo "  1. Cron jobs run in limited environment (PATH may differ)"
echo "  2. Make sure Docker is running before backups execute"
echo "  3. NAS sync and cloud upload require configuration (see docs)"
echo "  4. Test restore procedure monthly: $SCRIPT_DIR/test_backup_restore.sh"
echo ""

echo "✅ Setup complete!"
echo ""
