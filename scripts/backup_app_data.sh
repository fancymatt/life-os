#!/bin/bash
#
# Application Data Backup Script
# Backs up generated images, entity previews, presets, user data, and uploads
#
# Usage: ./backup_app_data.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups/app_data"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="app_data_${TIMESTAMP}"

mkdir -p "$BACKUP_DIR"

echo "📦 Backing up application data..."

# Create temporary backup directory
TEMP_DIR="$BACKUP_DIR/$BACKUP_NAME"
mkdir -p "$TEMP_DIR"

# Backup critical directories
for dir in output entity_previews presets data uploads; do
    if [ -d "$PROJECT_DIR/$dir" ]; then
        echo "  📁 Backing up $dir..."
        SIZE=$(du -sh "$PROJECT_DIR/$dir" | cut -f1)
        cp -r "$PROJECT_DIR/$dir" "$TEMP_DIR/"
        echo "     Size: $SIZE"
    else
        echo "  ⚠️  Directory not found: $dir"
    fi
done

# Create manifest
cat > "$TEMP_DIR/MANIFEST.txt" <<EOF
Application Data Backup
=======================
Timestamp: $TIMESTAMP
Date: $(date)
Hostname: $(hostname)

Included Directories:
- output/ (generated images)
- entity_previews/ (entity previews)
- presets/ (preset JSON files)
- data/ (user data)
- uploads/ (uploaded files)

Total Size: $(du -sh "$TEMP_DIR" | cut -f1)

File Counts:
- Generated images: $(find "$TEMP_DIR/output" -type f 2>/dev/null | wc -l)
- Entity previews: $(find "$TEMP_DIR/entity_previews" -type f 2>/dev/null | wc -l)
- Preset files: $(find "$TEMP_DIR/presets" -name "*.json" 2>/dev/null | wc -l)
- Data files: $(find "$TEMP_DIR/data" -type f 2>/dev/null | wc -l)
- Uploads: $(find "$TEMP_DIR/uploads" -type f 2>/dev/null | wc -l)
EOF

# Compress
echo "🗜️  Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME" 2>/dev/null
ARCHIVE_SIZE=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)

# Remove uncompressed backup
rm -rf "$BACKUP_NAME"

echo "✅ Application data backup complete!"
echo "   Archive: ${BACKUP_NAME}.tar.gz"
echo "   Size: $ARCHIVE_SIZE"

# Retention: Keep last 7 daily backups
echo "🧹 Cleaning up old backups (keeping last 7)..."
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/app_data_*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 7 ]; then
    ls -1t "$BACKUP_DIR"/app_data_*.tar.gz | tail -n +8 | xargs rm -f
    DELETED=$((BACKUP_COUNT - 7))
    echo "   Deleted $DELETED old backup(s)"
else
    echo "   No cleanup needed ($BACKUP_COUNT backups)"
fi

# Show recent backups
echo ""
echo "Recent backups:"
ls -lht "$BACKUP_DIR"/app_data_*.tar.gz 2>/dev/null | head -3 || echo "  (none)"
echo ""

exit 0
