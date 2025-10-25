# Life-OS Backup & Disaster Recovery Plan

**Last Updated**: 2025-10-24
**System**: Mac Studio (single-host deployment)
**Total Data Size**: ~125GB (122GB Ollama models + 3GB application data)

---

## Current State Analysis

### Data Inventory

| Category | Path | Size | Criticality | Backup Priority |
|----------|------|------|-------------|-----------------|
| PostgreSQL DB | Docker volume `life-os_postgres_data` | 11MB | **CRITICAL** | P0 (Hourly) |
| Generated Images | `/output` | 1.7GB | HIGH | P1 (Daily) |
| Entity Previews | `/entity_previews` | 937MB | MEDIUM | P1 (Daily) |
| Presets | `/presets` | 141MB | HIGH | P1 (Daily) |
| User Data | `/data` | 17MB | HIGH | P1 (Daily) |
| Uploads | `/uploads` | 14MB | MEDIUM | P2 (Weekly) |
| Logs | `/logs` | 19MB | LOW | P3 (Monthly) |
| Ollama Models | Docker volume `life-os_ollama_models` | 122GB | MEDIUM | P2 (Weekly) |
| Redis Data | Docker volume `life-os_redis_data` | <100MB | LOW | P3 (Ephemeral) |
| Code | Git repository | ~50MB | **CRITICAL** | P0 (On commit) |

**Total Critical Data**: ~3GB (excluding Ollama models which can be re-downloaded)

### Existing Backup Infrastructure ✅

1. **PostgreSQL Backup Script** (`scripts/backup_postgres.sh`)
   - Status: ✅ Implemented
   - Frequency: ❌ Not automated (no cron)
   - Retention: 30 days
   - Compression: Yes (gzip)
   - Location: Local only (`backups/postgres/`)

2. **JSON Data Backup Script** (`scripts/backup_json_data.sh`)
   - Status: ✅ Implemented
   - Frequency: ❌ Not automated
   - Retention: 30 backups
   - Compression: Yes (tar.gz)
   - Location: Local only (`backups/json/`)

3. **Git Version Control**
   - Status: ✅ Active
   - Remote: GitHub (`staging` branch)
   - Frequency: Manual commits
   - Coverage: Code only (no data)

### Missing Protections ❌

- ❌ No automated backup scheduling
- ❌ No off-site/cloud backups
- ❌ No Docker volume backups (Ollama models)
- ❌ No full system backup (generated images, entity previews)
- ❌ No monitoring/alerts for backup failures
- ❌ No tested disaster recovery procedures
- ❌ No failover/high-availability setup

---

## Multi-Tier Backup Strategy

### Tier 1: Local Backups (Mac Studio)

**Purpose**: Fast recovery from software issues, accidental deletion
**Location**: `/Users/fancymatt/docker/life-os/backups/`
**Protects Against**: User error, software bugs, container corruption

**Schedule**:
- **Hourly**: PostgreSQL database (last 24 hours)
- **Daily**: Full application data (last 7 days)
- **Weekly**: Ollama models (last 4 weeks)

### Tier 2: Network Attached Storage (NAS)

**Purpose**: Protection from Mac Studio hardware failure
**Location**: Network share (external NAS or Time Machine)
**Protects Against**: Disk failure, hardware death, theft

**Schedule**:
- **Daily**: Sync critical data to NAS (2-4 AM)
- **Weekly**: Full system backup to NAS

**Recommended Setup**:
- Synology NAS, QNAP, or macOS Time Machine
- Automated rsync to network share

### Tier 3: Cloud Backup (Off-site)

**Purpose**: Protection from power outage, house fire, local disaster
**Location**: Cloud storage (S3, Backblaze B2, Google Cloud)
**Protects Against**: Power loss, physical disaster, regional outage

**Schedule**:
- **Daily**: Database + critical data to cloud
- **Weekly**: Full application data to cloud
- **Monthly**: Ollama models to cloud (optional - 122GB)

**Cost Estimate** (Backblaze B2):
- 3GB daily backups × 30 days = 90GB storage = $0.54/month
- 125GB full backup (monthly) = $0.75/month
- **Total**: ~$1-2/month

---

## Automated Backup Implementation

### 1. Master Backup Script

Create `scripts/backup_all.sh` (orchestrates all backups):

```bash
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

# 3. Backup Docker volumes (weekly only)
if [ "$(date +%u)" -eq 7 ] || [ "$FORCE_FULL" = "true" ]; then
    log "Step 3/5: Backing up Docker volumes (weekly)..."
    if "$SCRIPT_DIR/backup_docker_volumes.sh"; then
        log "✓ Docker volumes backup complete"
    else
        log "⚠ Docker volumes backup FAILED (non-critical)"
    fi
else
    log "Step 3/5: Skipping Docker volumes backup (not Sunday)"
fi

# 4. Sync to NAS (if tier=nas or tier=cloud)
if [ "$TIER" = "nas" ] || [ "$TIER" = "cloud" ]; then
    log "Step 4/5: Syncing to NAS..."
    if "$SCRIPT_DIR/sync_to_nas.sh"; then
        log "✓ NAS sync complete"
    else
        log "⚠ NAS sync FAILED (non-critical)"
    fi
else
    log "Step 4/5: Skipping NAS sync (tier=$TIER)"
fi

# 5. Upload to cloud (if tier=cloud)
if [ "$TIER" = "cloud" ]; then
    log "Step 5/5: Uploading to cloud storage..."
    if "$SCRIPT_DIR/upload_to_cloud.sh"; then
        log "✓ Cloud upload complete"
    else
        log "⚠ Cloud upload FAILED (non-critical)"
    fi
else
    log "Step 5/5: Skipping cloud upload (tier=$TIER)"
fi

log "========================================="
log "Backup completed successfully"
log "========================================="
```

### 2. Application Data Backup Script

Create `scripts/backup_app_data.sh`:

```bash
#!/bin/bash
# Backup all application data (images, presets, data, uploads)

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
        cp -r "$PROJECT_DIR/$dir" "$TEMP_DIR/"
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
EOF

# Compress
echo "🗜️  Compressing..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Retention: Keep last 7 daily backups
ls -1t "$BACKUP_DIR"/app_data_*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true

echo "✅ Application data backup complete: ${BACKUP_NAME}.tar.gz"
echo "   Size: $(du -sh "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)"
```

### 3. Docker Volumes Backup Script

Create `scripts/backup_docker_volumes.sh`:

```bash
#!/bin/bash
# Backup Docker volumes (Ollama models, PostgreSQL data, Redis data)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups/docker_volumes"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR"

echo "📦 Backing up Docker volumes..."

# Backup Ollama models (122GB - use docker export)
echo "  🤖 Backing up Ollama models (this may take a while)..."
docker run --rm \
    -v life-os_ollama_models:/source:ro \
    -v "$BACKUP_DIR":/backup \
    alpine \
    tar -czf "/backup/ollama_models_${TIMESTAMP}.tar.gz" -C /source .

# Backup PostgreSQL volume (alternative to pg_dump)
echo "  🗄️  Backing up PostgreSQL volume..."
docker run --rm \
    -v life-os_postgres_data:/source:ro \
    -v "$BACKUP_DIR":/backup \
    alpine \
    tar -czf "/backup/postgres_volume_${TIMESTAMP}.tar.gz" -C /source .

# Backup Redis volume (less critical)
echo "  🔴 Backing up Redis volume..."
docker run --rm \
    -v life-os_redis_data:/source:ro \
    -v "$BACKUP_DIR":/backup \
    alpine \
    tar -czf "/backup/redis_volume_${TIMESTAMP}.tar.gz" -C /source .

# Retention: Keep last 4 weekly backups
for volume in ollama_models postgres_volume redis_volume; do
    ls -1t "$BACKUP_DIR/${volume}_"*.tar.gz 2>/dev/null | tail -n +5 | xargs rm -f 2>/dev/null || true
done

echo "✅ Docker volumes backup complete"
```

### 4. NAS Sync Script

Create `scripts/sync_to_nas.sh`:

```bash
#!/bin/bash
# Sync backups to Network Attached Storage

set -euo pipefail

# Configuration (CUSTOMIZE THIS)
NAS_HOST="your-nas-hostname-or-ip"
NAS_USER="your-username"
NAS_PATH="/volume1/backups/life-os"  # Synology example
LOCAL_BACKUP_DIR="/Users/fancymatt/docker/life-os/backups"

# Alternative: Use macOS Time Machine destination
# NAS_PATH="/Volumes/TimeMachine/Backups.backupdb/$(hostname)"

echo "📡 Syncing to NAS..."

# Check if NAS is reachable
if ! ping -c 1 -t 2 "$NAS_HOST" > /dev/null 2>&1; then
    echo "⚠️  NAS not reachable: $NAS_HOST"
    exit 1
fi

# Rsync to NAS (preserves timestamps, compression during transfer)
rsync -avz --progress \
    --exclude="*.log" \
    "$LOCAL_BACKUP_DIR/" \
    "${NAS_USER}@${NAS_HOST}:${NAS_PATH}/"

echo "✅ NAS sync complete"
```

### 5. Cloud Upload Script

Create `scripts/upload_to_cloud.sh`:

```bash
#!/bin/bash
# Upload backups to cloud storage (Backblaze B2 example)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"

# Configuration (CUSTOMIZE THIS)
# Option 1: Backblaze B2
B2_BUCKET="life-os-backups"
B2_KEY_ID="${B2_APPLICATION_KEY_ID:-}"
B2_APP_KEY="${B2_APPLICATION_KEY:-}"

# Option 2: AWS S3
# S3_BUCKET="s3://life-os-backups"

# Option 3: Google Cloud Storage
# GCS_BUCKET="gs://life-os-backups"

echo "☁️  Uploading to cloud storage..."

# Check if b2 CLI is installed
if ! command -v b2 &> /dev/null; then
    echo "⚠️  Backblaze B2 CLI not installed"
    echo "   Install: brew install b2-tools"
    exit 1
fi

# Authenticate
if [ -z "$B2_KEY_ID" ] || [ -z "$B2_APP_KEY" ]; then
    echo "⚠️  B2 credentials not set"
    echo "   Set B2_APPLICATION_KEY_ID and B2_APPLICATION_KEY"
    exit 1
fi

b2 authorize-account "$B2_KEY_ID" "$B2_APP_KEY"

# Upload latest backups only (not entire backup directory)
LATEST_POSTGRES=$(ls -t "$BACKUP_DIR/postgres"/*.sql.gz 2>/dev/null | head -1)
LATEST_APP_DATA=$(ls -t "$BACKUP_DIR/app_data"/*.tar.gz 2>/dev/null | head -1)

if [ -n "$LATEST_POSTGRES" ]; then
    echo "  📤 Uploading PostgreSQL backup..."
    b2 upload-file "$B2_BUCKET" "$LATEST_POSTGRES" "postgres/$(basename "$LATEST_POSTGRES")"
fi

if [ -n "$LATEST_APP_DATA" ]; then
    echo "  📤 Uploading application data backup..."
    b2 upload-file "$B2_BUCKET" "$LATEST_APP_DATA" "app_data/$(basename "$LATEST_APP_DATA")"
fi

# Upload Ollama models monthly (optional - 122GB)
if [ "$(date +%d)" -eq 1 ]; then
    LATEST_OLLAMA=$(ls -t "$BACKUP_DIR/docker_volumes"/ollama_models_*.tar.gz 2>/dev/null | head -1)
    if [ -n "$LATEST_OLLAMA" ]; then
        echo "  📤 Uploading Ollama models (monthly)..."
        b2 upload-file --threads 4 "$B2_BUCKET" "$LATEST_OLLAMA" "ollama/$(basename "$LATEST_OLLAMA")"
    fi
fi

echo "✅ Cloud upload complete"
```

### 6. Automated Scheduling (cron)

Create `scripts/install_cron.sh`:

```bash
#!/bin/bash
# Install cron jobs for automated backups

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📅 Installing Life-OS backup cron jobs..."

# Create cron jobs
(crontab -l 2>/dev/null || true; cat <<EOF

# Life-OS Automated Backups
# -------------------------

# Hourly: PostgreSQL database (local only)
0 * * * * $SCRIPT_DIR/backup_postgres.sh 1 >> $SCRIPT_DIR/../logs/cron_backup.log 2>&1

# Daily 2 AM: Full application data + sync to NAS
0 2 * * * $SCRIPT_DIR/backup_all.sh nas >> $SCRIPT_DIR/../logs/cron_backup.log 2>&1

# Daily 3 AM: Upload to cloud storage
0 3 * * * $SCRIPT_DIR/upload_to_cloud.sh >> $SCRIPT_DIR/../logs/cron_backup.log 2>&1

# Weekly Sunday 4 AM: Full backup including Docker volumes
0 4 * * 0 FORCE_FULL=true $SCRIPT_DIR/backup_all.sh cloud >> $SCRIPT_DIR/../logs/cron_backup.log 2>&1

# Monthly cleanup: Delete backups older than 90 days
0 5 1 * * find $SCRIPT_DIR/../backups -type f -mtime +90 -delete >> $SCRIPT_DIR/../logs/cron_backup.log 2>&1

EOF
) | crontab -

echo "✅ Cron jobs installed"
echo ""
echo "Backup schedule:"
echo "  - Hourly: PostgreSQL database"
echo "  - Daily 2 AM: Application data + NAS sync"
echo "  - Daily 3 AM: Cloud upload"
echo "  - Weekly Sunday 4 AM: Full backup (includes Docker volumes)"
echo "  - Monthly: Cleanup old backups"
echo ""
echo "To view cron jobs: crontab -l"
echo "To remove cron jobs: crontab -r"
```

---

## Disaster Recovery Procedures

### Scenario 1: Power Outage (Mac Studio Down)

**Impact**: System offline, no data loss (containers stopped cleanly)
**RTO**: 5 minutes
**RPO**: 0 (no data loss if clean shutdown)

**Recovery Steps**:
1. Wait for power restoration
2. Start Docker containers: `docker-compose up -d`
3. Verify health: `docker ps` and check API at http://localhost:8000/health
4. Check logs: `docker logs ai-studio-api --tail 50`

**Prevention**:
- ✅ Configure Docker restart policy: `restart: unless-stopped` (already set)
- 💡 Consider UPS (Uninterruptible Power Supply) for Mac Studio

---

### Scenario 2: Database Corruption

**Impact**: PostgreSQL data corrupted or lost
**RTO**: 15 minutes
**RPO**: 1 hour (hourly backups)

**Recovery Steps**:

```bash
# 1. Stop containers
docker-compose down

# 2. Remove corrupted PostgreSQL volume
docker volume rm life-os_postgres_data

# 3. Recreate volume
docker volume create life-os_postgres_data

# 4. Start PostgreSQL container
docker-compose up -d postgres

# 5. Wait for PostgreSQL to initialize (30 seconds)
sleep 30

# 6. Restore from latest backup
LATEST_BACKUP=$(ls -t backups/postgres/*.sql.gz | head -1)
gunzip -c "$LATEST_BACKUP" | docker exec -i ai-studio-postgres psql -U lifeos -d lifeos

# 7. Start remaining containers
docker-compose up -d

# 8. Verify data integrity
docker exec ai-studio-postgres psql -U lifeos -d lifeos -c "SELECT COUNT(*) FROM characters;"
```

---

### Scenario 3: Mac Studio Hardware Failure

**Impact**: Total system loss, need to rebuild on new hardware
**RTO**: 2-4 hours
**RPO**: 24 hours (daily cloud backups)

**Recovery Steps**:

**Option A: Restore on New Mac**

```bash
# 1. Install Docker Desktop
# Download from https://www.docker.com/products/docker-desktop/

# 2. Clone repository
git clone https://github.com/fancymatt/life-os.git
cd life-os

# 3. Restore backups from cloud
# (Assuming Backblaze B2)
b2 authorize-account $B2_KEY_ID $B2_APP_KEY
b2 download-file-by-name life-os-backups postgres/life_os_backup_YYYYMMDD_HHMMSS.sql.gz backups/postgres/
b2 download-file-by-name life-os-backups app_data/app_data_YYYYMMDD_HHMMSS.tar.gz backups/app_data/

# 4. Extract application data
cd backups/app_data
tar -xzf app_data_YYYYMMDD_HHMMSS.tar.gz
cp -r app_data_YYYYMMDD_HHMMSS/output ../../
cp -r app_data_YYYYMMDD_HHMMSS/entity_previews ../../
cp -r app_data_YYYYMMDD_HHMMSS/presets ../../
cp -r app_data_YYYYMMDD_HHMMSS/data ../../
cd ../..

# 5. Start containers
docker-compose up -d postgres redis
sleep 30

# 6. Restore database
gunzip -c backups/postgres/life_os_backup_YYYYMMDD_HHMMSS.sql.gz | \
    docker exec -i ai-studio-postgres psql -U lifeos -d lifeos

# 7. Start remaining containers
docker-compose up -d

# 8. Re-download Ollama models (or restore from backup)
docker exec ai-studio-ollama ollama pull qwen2.5:72b-instruct
docker exec ai-studio-ollama ollama pull llama3.2-vision:90b
# ... other models

# 9. Verify system
curl http://localhost:8000/health
curl http://localhost:3000
```

**Option B: Restore on Cloud VPS (Temporary Failover)**

See "Cloud Failover Setup" section below.

---

### Scenario 4: Accidental Data Deletion

**Impact**: User deleted entities or files
**RTO**: 5 minutes
**RPO**: 1 hour (hourly PostgreSQL backups)

**Recovery Steps**:

```bash
# Option 1: Restore specific entity from database backup
LATEST_BACKUP=$(ls -t backups/postgres/*.sql.gz | head -1)
gunzip -c "$LATEST_BACKUP" > /tmp/restore.sql

# Extract specific table and restore
grep "COPY public.characters" /tmp/restore.sql | head -100 > /tmp/characters_restore.sql
docker exec -i ai-studio-postgres psql -U lifeos -d lifeos < /tmp/characters_restore.sql

# Option 2: Restore entire database (if above doesn't work)
# Use Scenario 2 procedure
```

---

### Scenario 5: Ransomware / Security Breach

**Impact**: System compromised, data encrypted
**RTO**: 4-8 hours
**RPO**: 24 hours (daily cloud backups)

**Recovery Steps**:

```bash
# 1. Disconnect from network immediately
sudo ifconfig en0 down

# 2. Take forensic snapshot (optional)
docker-compose down
sudo dd if=/dev/disk0 of=/Volumes/External/forensic_image.dmg bs=1m

# 3. Wipe system and reinstall macOS
# (Full system reinstall)

# 4. Restore from CLEAN cloud backups (not local - may be encrypted)
# Use "Option A: Restore on New Mac" from Scenario 3

# 5. Change all passwords and API keys
# - GitHub
# - Gemini API
# - OpenAI API
# - Database passwords
# - JWT secrets

# 6. Audit logs for breach timeline
grep -r "suspicious_activity" logs/
```

**Prevention**:
- 💡 Use macOS FileVault encryption
- 💡 Enable macOS Firewall
- 💡 Restrict Docker API access
- 💡 Keep cloud backups immutable (versioned)

---

## Cloud Failover Setup (High Availability)

### Option 1: DigitalOcean / Hetzner / Linode VPS

**When to use**: Mac Studio hardware failure, need immediate access during repair
**Cost**: $10-40/month (only enable when needed)
**Setup Time**: 30 minutes

**Pre-configuration** (do this NOW):

```bash
# 1. Create Docker Machine config for cloud VPS
# (Stored locally, ready to deploy when needed)

cat > scripts/deploy_to_cloud.sh <<'EOF'
#!/bin/bash
# Deploy Life-OS to cloud VPS for failover

set -euo pipefail

# Configuration
VPS_PROVIDER="digitalocean"  # or hetzner, linode, aws
VPS_SIZE="s-4vcpu-8gb"       # $40/month
VPS_REGION="nyc3"
VPS_NAME="life-os-failover"

echo "🚀 Deploying Life-OS to cloud VPS..."

# Create VPS (requires doctl, hcloud, or linode-cli)
if command -v doctl &> /dev/null; then
    echo "Creating DigitalOcean droplet..."
    doctl compute droplet create "$VPS_NAME" \
        --image docker-20-04 \
        --size "$VPS_SIZE" \
        --region "$VPS_REGION" \
        --ssh-keys $(doctl compute ssh-key list --format ID --no-header) \
        --wait

    VPS_IP=$(doctl compute droplet get "$VPS_NAME" --format PublicIPv4 --no-header)
else
    echo "⚠️  Cloud CLI not installed. Install: brew install doctl"
    exit 1
fi

echo "✅ VPS created: $VPS_IP"

# Wait for SSH
echo "Waiting for SSH..."
until ssh -o StrictHostKeyChecking=no root@$VPS_IP "echo SSH ready" 2>/dev/null; do
    sleep 5
done

# Deploy Life-OS
echo "Deploying Life-OS to VPS..."
scp -r . root@$VPS_IP:/root/life-os/
ssh root@$VPS_IP "cd /root/life-os && docker-compose up -d"

# Restore backups from cloud
ssh root@$VPS_IP "cd /root/life-os && ./scripts/restore_from_cloud.sh"

echo "========================================="
echo "✅ Life-OS deployed to cloud VPS"
echo "   URL: http://$VPS_IP:3000"
echo "   API: http://$VPS_IP:8000"
echo "========================================="
echo ""
echo "⚠️  REMEMBER: This is a temporary failover."
echo "   - Data is restored from latest cloud backup (up to 24 hours old)"
echo "   - New data created on VPS needs manual sync back to Mac Studio"
echo "   - Destroy VPS when Mac Studio is restored: doctl compute droplet delete $VPS_NAME"
EOF

chmod +x scripts/deploy_to_cloud.sh
```

**Activation** (when Mac Studio fails):

```bash
# Deploy to cloud VPS
./scripts/deploy_to_cloud.sh

# Access system at http://VPS_IP:3000
# Continue working while Mac Studio is repaired

# When Mac Studio is back online:
# 1. Backup data from VPS
ssh root@VPS_IP "cd /root/life-os && ./scripts/backup_all.sh cloud"

# 2. Download VPS backups to Mac Studio
scp -r root@VPS_IP:/root/life-os/backups/* backups/

# 3. Merge data (manual review recommended)
# 4. Destroy VPS
doctl compute droplet delete life-os-failover
```

### Option 2: Docker Swarm / Kubernetes (Future)

**When to use**: Need true high availability (99.9% uptime)
**Cost**: $100-200/month (3+ VPS instances)
**Complexity**: HIGH - requires significant DevOps work

**Current Status**: ❌ Not recommended for Phase 2
**Revisit**: Phase 5+ (if Life-OS becomes mission-critical)

---

## Monitoring & Alerts

### Backup Health Monitoring

Create `scripts/check_backup_health.sh`:

```bash
#!/bin/bash
# Check backup health and send alerts if stale

set -euo pipefail

PROJECT_DIR="/Users/fancymatt/docker/life-os"
ALERT_EMAIL="your-email@example.com"  # CUSTOMIZE THIS

# Check PostgreSQL backup age
LATEST_PG=$(ls -t "$PROJECT_DIR/backups/postgres"/*.sql.gz 2>/dev/null | head -1)
if [ -n "$LATEST_PG" ]; then
    PG_AGE_HOURS=$(( ($(date +%s) - $(stat -f %m "$LATEST_PG")) / 3600 ))
    echo "PostgreSQL backup age: $PG_AGE_HOURS hours"

    if [ $PG_AGE_HOURS -gt 2 ]; then
        echo "⚠️  PostgreSQL backup is stale! (>2 hours old)"
        # Send alert (requires mailx or similar)
        # echo "PostgreSQL backup is $PG_AGE_HOURS hours old" | mail -s "Life-OS Backup Alert" $ALERT_EMAIL
    fi
else
    echo "❌ No PostgreSQL backups found!"
fi

# Check application data backup age
LATEST_APP=$(ls -t "$PROJECT_DIR/backups/app_data"/*.tar.gz 2>/dev/null | head -1)
if [ -n "$LATEST_APP" ]; then
    APP_AGE_HOURS=$(( ($(date +%s) - $(stat -f %m "$LATEST_APP")) / 3600 ))
    echo "App data backup age: $APP_AGE_HOURS hours"

    if [ $APP_AGE_HOURS -gt 25 ]; then
        echo "⚠️  App data backup is stale! (>25 hours old)"
    fi
else
    echo "❌ No app data backups found!"
fi

# Check backup directory size
BACKUP_SIZE=$(du -sh "$PROJECT_DIR/backups" | cut -f1)
echo "Total backup size: $BACKUP_SIZE"

# Check Docker containers status
if ! docker ps --filter "name=ai-studio" --format '{{.Names}}' | grep -q "ai-studio-api"; then
    echo "❌ Life-OS containers not running!"
fi
```

Add to cron (hourly check):

```bash
0 * * * * /Users/fancymatt/docker/life-os/scripts/check_backup_health.sh >> /Users/fancymatt/docker/life-os/logs/backup_health.log 2>&1
```

---

## Quick Reference: Common Operations

### Create Manual Backup Now

```bash
cd /Users/fancymatt/docker/life-os
./scripts/backup_all.sh local
```

### Restore Database from Backup

```bash
# 1. Find backup
ls -lt backups/postgres/*.sql.gz | head -5

# 2. Restore
gunzip -c backups/postgres/life_os_backup_YYYYMMDD_HHMMSS.sql.gz | \
    docker exec -i ai-studio-postgres psql -U lifeos -d lifeos
```

### Test Restore Procedure (Monthly)

```bash
./scripts/test_backup_restore.sh
```

### Check Backup Status

```bash
./scripts/check_backup_health.sh
```

### View Backup Logs

```bash
tail -f logs/backup_*.log
tail -f logs/cron_backup.log
```

---

## Recommendations & Next Steps

### Immediate Actions (This Week)

1. ✅ **Create missing backup scripts** (app data, Docker volumes)
2. ✅ **Install automated cron jobs** (`scripts/install_cron.sh`)
3. ⚠️ **Test restore procedure** (to verify backups work)
4. 💡 **Set up NAS sync** (if you have a NAS)

### Short-term (This Month)

1. 💡 **Set up cloud backups** (Backblaze B2 - $2/month)
2. 💡 **Configure backup monitoring** (email alerts for stale backups)
3. 💡 **Document custom NAS/cloud credentials** (in `.env` file)
4. 💡 **Test cloud restore** (verify end-to-end recovery)

### Medium-term (This Quarter)

1. 💡 **Purchase UPS for Mac Studio** (prevent dirty shutdowns)
2. 💡 **Create cloud failover playbook** (DigitalOcean setup)
3. 💡 **Set up monitoring dashboard** (backup health, system uptime)

### Long-term (Phase 5+)

1. 💡 **Multi-region cloud deployment** (for true high availability)
2. 💡 **Automated failover** (DNS-based, health checks)
3. 💡 **Real-time database replication** (PostgreSQL streaming replication)

---

## Cost Summary

| Service | Monthly Cost | Purpose |
|---------|--------------|---------|
| **Local Backups** | $0 | Fast recovery |
| **NAS Storage** (optional) | $0 (if owned) | Hardware failure protection |
| **Backblaze B2 Cloud** | $1-2 | Off-site disaster recovery |
| **Cloud VPS Failover** (on-demand) | $0 (only when activated) | Temporary failover during repairs |
| **UPS** (one-time) | $200-400 | Power outage protection |
| **TOTAL (Ongoing)** | **$1-2/month** | Comprehensive protection |

---

## Testing Checklist

**Monthly Backup Verification**:

- [ ] Restore PostgreSQL from latest backup → Verify data integrity
- [ ] Extract app data backup → Verify files readable
- [ ] Check cloud backups → Verify upload succeeded
- [ ] Test NAS sync → Verify files transferred
- [ ] Review backup logs → Check for errors
- [ ] Verify backup retention → Old backups cleaned up
- [ ] Check backup storage usage → Ensure not full

**Quarterly Disaster Recovery Drill**:

- [ ] Simulate hardware failure → Restore on different machine
- [ ] Simulate database corruption → Full restore procedure
- [ ] Simulate ransomware → Restore from cloud backups only
- [ ] Time recovery procedures → Measure actual RTO
- [ ] Document lessons learned → Update procedures

---

## Conclusion

This backup and disaster recovery plan provides **multi-tier protection** for your Life-OS deployment:

1. **Hourly PostgreSQL backups** → Protect against data loss
2. **Daily application backups** → Protect against file corruption
3. **NAS sync** → Protect against hardware failure
4. **Cloud backups** → Protect against physical disaster
5. **Cloud failover** → Keep system running during Mac Studio downtime

**Total cost**: $1-2/month for comprehensive protection
**Recovery time**: 5 minutes (power outage) to 4 hours (hardware failure)

The system is designed to be **resilient** while remaining **cost-effective** for a single-user deployment.
