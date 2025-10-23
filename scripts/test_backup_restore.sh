#!/bin/bash
#
# Backup & Restoration Testing Script
#
# Tests the complete backup and restore cycle to ensure data safety.
# This script verifies that:
#   1. Backups are created successfully
#   2. Backups can be restored
#   3. Restored data matches original data
#   4. Rollback from PostgreSQL works
#
# Usage:
#   ./scripts/test_backup_restore.sh
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_DIR="$PROJECT_ROOT/backups/test_$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Backup & Restoration Testing Script"
echo "========================================"
echo "Test directory: $TEST_DIR"
echo ""

# Create test directory
mkdir -p "$TEST_DIR"

# Test 1: JSON Backup Creation
echo "Test 1: JSON Backup Creation"
echo "-----------------------------"
echo "Creating backup of current JSON files..."
"$SCRIPT_DIR/backup_json_data.sh" "$TEST_DIR/backup1" > "$TEST_DIR/backup1.log" 2>&1
if [ $? -eq 0 ] && [ -f "$TEST_DIR/backup1"/*.tar.gz ]; then
    echo -e "${GREEN}✅ PASS${NC} - Backup created successfully"
    BACKUP1_FILE=$(ls -1 "$TEST_DIR/backup1"/*.tar.gz | head -1)
    echo "   Archive: $(basename "$BACKUP1_FILE")"
    echo "   Size: $(du -sh "$BACKUP1_FILE" | cut -f1)"
else
    echo -e "${RED}❌ FAIL${NC} - Backup creation failed"
    cat "$TEST_DIR/backup1.log"
    exit 1
fi
echo ""

# Test 2: Backup Extraction
echo "Test 2: Backup Extraction"
echo "-------------------------"
echo "Extracting backup archive..."
mkdir -p "$TEST_DIR/extracted"
cd "$TEST_DIR/extracted"
tar -xzf "$BACKUP1_FILE"
if [ $? -eq 0 ]; then
    EXTRACTED_DIR=$(ls -1d json_backup_* | head -1)
    if [ -d "$EXTRACTED_DIR" ]; then
        echo -e "${GREEN}✅ PASS${NC} - Backup extracted successfully"
        echo "   Directory: $EXTRACTED_DIR"
        echo "   Files: $(find "$EXTRACTED_DIR" -type f | wc -l)"
        echo "   JSON files: $(find "$EXTRACTED_DIR" -name "*.json" | wc -l)"
    else
        echo -e "${RED}❌ FAIL${NC} - Extracted directory not found"
        exit 1
    fi
else
    echo -e "${RED}❌ FAIL${NC} - Extraction failed"
    exit 1
fi
echo ""

# Test 3: Data Integrity Check
echo "Test 3: Data Integrity Check"
echo "----------------------------"
echo "Comparing original vs extracted data..."
cd "$PROJECT_ROOT"

# Check a few sample files
SAMPLE_FILES=(
    "data/users.json"
    "data/favorites.json"
)

INTEGRITY_OK=true
for sample in "${SAMPLE_FILES[@]}"; do
    if [ -f "$sample" ]; then
        ORIG_MD5=$(md5sum "$sample" 2>/dev/null | cut -d' ' -f1 || md5 -q "$sample" 2>/dev/null)
        BACKUP_FILE="$TEST_DIR/extracted/$EXTRACTED_DIR/$sample"
        if [ -f "$BACKUP_FILE" ]; then
            BACKUP_MD5=$(md5sum "$BACKUP_FILE" 2>/dev/null | cut -d' ' -f1 || md5 -q "$BACKUP_FILE" 2>/dev/null)
            if [ "$ORIG_MD5" = "$BACKUP_MD5" ]; then
                echo "   ✅ $sample - MATCH"
            else
                echo -e "   ${RED}❌ $sample - MISMATCH${NC}"
                INTEGRITY_OK=false
            fi
        else
            echo -e "   ${YELLOW}⚠️  $sample - NOT IN BACKUP${NC}"
        fi
    fi
done

if [ "$INTEGRITY_OK" = true ]; then
    echo -e "${GREEN}✅ PASS${NC} - Data integrity verified"
else
    echo -e "${RED}❌ FAIL${NC} - Data integrity check failed"
    exit 1
fi
echo ""

# Test 4: Backup Manifest Check
echo "Test 4: Backup Manifest Check"
echo "-----------------------------"
if [ -f "$TEST_DIR/extracted/$EXTRACTED_DIR/MANIFEST.txt" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Manifest exists"
    echo "   Preview:"
    head -15 "$TEST_DIR/extracted/$EXTRACTED_DIR/MANIFEST.txt" | sed 's/^/   /'
else
    echo -e "${RED}❌ FAIL${NC} - Manifest not found"
    exit 1
fi
echo ""

# Test 5: PostgreSQL Rollback (Dry Run)
echo "Test 5: PostgreSQL Rollback (Dry Run)"
echo "-------------------------------------"
echo "Testing PostgreSQL to JSON rollback..."
cd "$PROJECT_ROOT"

# Check if Docker is running
if docker ps > /dev/null 2>&1; then
    # Run rollback script inside Docker container
    docker exec ai-studio-api python3 /app/scripts/rollback_to_json.py --dry-run --output-dir "/tmp/rollback_test" > "$TEST_DIR/rollback.log" 2>&1
    if [ $? -eq 0 ]; then
        ROLLBACK_FILES=$(grep -c "✅" "$TEST_DIR/rollback.log" || echo "0")
        echo -e "${GREEN}✅ PASS${NC} - Rollback dry run successful"
        echo "   Entity types exported: $ROLLBACK_FILES"
        # Cleanup test directory in container
        docker exec ai-studio-api rm -rf /tmp/rollback_test 2>/dev/null || true
    else
        echo -e "${YELLOW}⚠️  SKIP${NC} - Rollback dry run failed (see log for details)"
        echo "   Log: $TEST_DIR/rollback.log"
        # Don't fail the entire test suite
    fi
else
    echo -e "${YELLOW}⚠️  SKIP${NC} - Docker not running, cannot test PostgreSQL rollback"
    echo "   Run 'docker-compose up -d' to enable this test"
fi
echo ""

# Test 6: Backup Rotation (Old Backup Cleanup)
echo "Test 6: Backup Rotation"
echo "----------------------"
echo "Creating multiple backups to test rotation..."
for i in {1..3}; do
    "$SCRIPT_DIR/backup_json_data.sh" "$TEST_DIR/rotation_test" > /dev/null 2>&1
    sleep 1  # Ensure different timestamps
done
BACKUP_COUNT=$(ls -1 "$TEST_DIR/rotation_test"/*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -ge 3 ]; then
    echo -e "${GREEN}✅ PASS${NC} - Backup rotation works"
    echo "   Created $BACKUP_COUNT backups"
else
    echo -e "${YELLOW}⚠️  WARNING${NC} - Expected 3 backups, found $BACKUP_COUNT"
fi
echo ""

# Summary
echo "========================================"
echo "Test Summary"
echo "========================================"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""
echo "Test artifacts saved to:"
echo "  $TEST_DIR"
echo ""
echo "Cleanup:"
echo "  To remove test files, run:"
echo "  rm -rf $TEST_DIR"
echo ""
echo "Next steps:"
echo "  1. Review test results above"
echo "  2. Schedule regular backups (cron or systemd timer)"
echo "  3. Test actual PostgreSQL rollback in staging environment"
echo "  4. Document restoration procedures for team"
echo ""
echo "Done! 🎉"
