#!/bin/bash
#
# JSON Data Backup Script
#
# Creates timestamped backups of all JSON data files before database migration.
# Useful for rollback if PostgreSQL migration fails.
#
# Usage:
#   ./scripts/backup_json_data.sh
#   ./scripts/backup_json_data.sh /path/to/custom/backup/dir
#

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${1:-$PROJECT_ROOT/backups/json}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="json_backup_${TIMESTAMP}"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_PATH"

echo "📦 JSON Data Backup Script"
echo "=========================="
echo "Timestamp: $TIMESTAMP"
echo "Backup directory: $BACKUP_PATH"
echo ""

# Backup data/ directory (all JSON files)
echo "📁 Backing up data/ directory..."
if [ -d "$PROJECT_ROOT/data" ]; then
    cp -r "$PROJECT_ROOT/data" "$BACKUP_PATH/"
    DATA_COUNT=$(find "$BACKUP_PATH/data" -type f -name "*.json" | wc -l)
    DATA_SIZE=$(du -sh "$BACKUP_PATH/data" | cut -f1)
    echo "   ✅ Backed up $DATA_COUNT JSON files ($DATA_SIZE)"
else
    echo "   ⚠️  data/ directory not found"
fi

# Backup presets/ directory (all preset JSON files)
echo "📁 Backing up presets/ directory..."
if [ -d "$PROJECT_ROOT/presets" ]; then
    cp -r "$PROJECT_ROOT/presets" "$BACKUP_PATH/"
    PRESET_COUNT=$(find "$BACKUP_PATH/presets" -type f -name "*.json" | wc -l)
    PRESET_SIZE=$(du -sh "$BACKUP_PATH/presets" | cut -f1)
    echo "   ✅ Backed up $PRESET_COUNT preset files ($PRESET_SIZE)"
else
    echo "   ⚠️  presets/ directory not found"
fi

# Backup configs/ directory (YAML configs)
echo "📁 Backing up configs/ directory..."
if [ -d "$PROJECT_ROOT/configs" ]; then
    cp -r "$PROJECT_ROOT/configs" "$BACKUP_PATH/"
    CONFIG_SIZE=$(du -sh "$BACKUP_PATH/configs" | cut -f1)
    echo "   ✅ Backed up configs ($CONFIG_SIZE)"
else
    echo "   ⚠️  configs/ directory not found"
fi

# Create backup manifest
echo "📝 Creating backup manifest..."
cat > "$BACKUP_PATH/MANIFEST.txt" <<EOF
JSON Data Backup Manifest
=========================
Timestamp: $TIMESTAMP
Backup Date: $(date)
Hostname: $(hostname)
User: $(whoami)

Directory Structure:
$(tree -L 2 "$BACKUP_PATH" 2>/dev/null || find "$BACKUP_PATH" -maxdepth 2 -type d)

File Counts:
- JSON files in data/: $(find "$BACKUP_PATH/data" -type f -name "*.json" 2>/dev/null | wc -l)
- JSON files in presets/: $(find "$BACKUP_PATH/presets" -type f -name "*.json" 2>/dev/null | wc -l)
- Total JSON files: $(find "$BACKUP_PATH" -type f -name "*.json" 2>/dev/null | wc -l)

Sizes:
- data/: $(du -sh "$BACKUP_PATH/data" 2>/dev/null | cut -f1 || echo "N/A")
- presets/: $(du -sh "$BACKUP_PATH/presets" 2>/dev/null | cut -f1 || echo "N/A")
- Total: $(du -sh "$BACKUP_PATH" | cut -f1)

MD5 Checksums:
$(find "$BACKUP_PATH" -type f -name "*.json" -exec md5sum {} \; 2>/dev/null | sort || echo "md5sum not available")
EOF
echo "   ✅ Manifest created: $BACKUP_PATH/MANIFEST.txt"

# Compress backup
echo "🗜️  Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
ARCHIVE_SIZE=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)
echo "   ✅ Archive created: ${BACKUP_NAME}.tar.gz ($ARCHIVE_SIZE)"

# Remove uncompressed backup
rm -rf "$BACKUP_NAME"

# Summary
echo ""
echo "✅ Backup Complete!"
echo "=========================="
echo "Archive: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "Size: $ARCHIVE_SIZE"
echo ""
echo "To restore from this backup:"
echo "  cd $BACKUP_DIR"
echo "  tar -xzf ${BACKUP_NAME}.tar.gz"
echo "  cp -r ${BACKUP_NAME}/data $PROJECT_ROOT/"
echo "  cp -r ${BACKUP_NAME}/presets $PROJECT_ROOT/"
echo "  cp -r ${BACKUP_NAME}/configs $PROJECT_ROOT/"
echo ""

# List recent backups
echo "Recent backups:"
ls -lht "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -5 || echo "  (none)"
echo ""

# Cleanup old backups (keep last 30)
echo "🧹 Cleaning up old backups (keeping last 30)..."
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 30 ]; then
    ls -1t "$BACKUP_DIR"/*.tar.gz | tail -n +31 | xargs rm -f
    echo "   ✅ Removed $((BACKUP_COUNT - 30)) old backups"
else
    echo "   ℹ️  No cleanup needed ($BACKUP_COUNT backups)"
fi

echo ""
echo "Done! 🎉"
