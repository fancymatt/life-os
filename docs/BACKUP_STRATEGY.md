# Backup Strategy (Synology Drive + GitHub)

**Last Updated**: 2025-10-24
**System**: Mac Studio with Synology Drive

---

## Overview

Life-OS uses a **minimal backup strategy** leveraging existing infrastructure:

1. **Files** → Synology Drive (real-time sync to NAS + cloud)
2. **Database** → Daily PostgreSQL dumps (files synced by Synology Drive)
3. **Code** → GitHub (git commits and pushes)
4. **Ollama Models** → Manifest only (re-download on restore)

---

## What Gets Backed Up

### Automatically (Synology Drive)

Synology Drive continuously backs up these directories:

| Directory | Size | Contents | Backup Location |
|-----------|------|----------|-----------------|
| `/output` | 1.7GB | Generated images | Synology NAS + Cloud |
| `/entity_previews` | 937MB | Entity preview images | Synology NAS + Cloud |
| `/presets` | 141MB | Preset JSON files | Synology NAS + Cloud |
| `/data` | 17MB | User data, configs | Synology NAS + Cloud |
| `/uploads` | 14MB | Uploaded files | Synology NAS + Cloud |
| `/backups/postgres` | ~500KB | Database dumps | Synology NAS + Cloud |

**Total**: ~2.9GB of critical data backed up in real-time

### Daily Automated (Cron)

**PostgreSQL Database Dumps**:
- Runs daily at 3 AM via cron
- Creates `.sql.gz` file in `backups/postgres/`
- Keeps 7 days of local backups
- Synology Drive syncs dump files to NAS + cloud

**Ollama Model Manifest**:
- Saved to `data/ollama_models_manifest.txt`
- Lists all installed models
- Used to re-download models after disaster (don't backup 122GB)

### Manual (Git)

**Code Repository**:
- Commit changes regularly
- Push to GitHub: `git push origin staging`
- GitHub serves as off-site code backup

---

## What's NOT Backed Up

**Ollama Models** (122GB):
- Re-downloadable from Ollama registry
- Manifest file documents what to re-download
- Recovery time: 30-60 minutes

**Redis Cache**:
- Ephemeral data (job queue state)
- Rebuilt automatically on container start

**Docker Images**:
- Re-pullable from Docker Hub
- Defined in docker-compose.yml

---

## Setup Instructions

### 1. Enable Daily Database Backups

Add one cron job for daily PostgreSQL dumps:

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 3 AM):
0 3 * * * /Users/fancymatt/docker/life-os/scripts/backup_postgres.sh 7 >> /Users/fancymatt/docker/life-os/logs/postgres_backup.log 2>&1
```

Verify cron job is installed:
```bash
crontab -l | grep backup_postgres
```

### 2. Verify Synology Drive Sync

Ensure Synology Drive is watching these directories:
```bash
/Users/fancymatt/docker/life-os/output
/Users/fancymatt/docker/life-os/entity_previews
/Users/fancymatt/docker/life-os/presets
/Users/fancymatt/docker/life-os/data
/Users/fancymatt/docker/life-os/backups
```

Check sync status in Synology Drive app.

### 3. Generate Ollama Manifest (One-Time)

```bash
# Save current models to manifest
./scripts/save_ollama_manifest.sh
```

This creates `data/ollama_models_manifest.txt` (which Synology Drive backs up).

### 4. Git Best Practices

After completing work:
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: description of changes"

# Push to GitHub (off-site backup)
git push origin staging
```

**Commit frequency**: After completing features, fixing bugs, or making significant changes.

---

## Disaster Recovery

### Scenario: Mac Studio Hardware Failure

**Recovery Steps** (Total time: 1-2 hours):

#### 1. Set Up New Mac or Cloud VPS (15 min)

```bash
# Install Docker Desktop (macOS)
# Download from: https://www.docker.com/products/docker-desktop/

# Or use cloud VPS
# See cloud failover section below
```

#### 2. Restore Code from GitHub (2 min)

```bash
git clone https://github.com/fancymatt/life-os.git
cd life-os
```

#### 3. Restore Files from Synology Drive (5-10 min)

```bash
# Option A: Mount Synology share
# Option B: Download from Synology cloud
# Option C: Copy from local Synology Drive sync folder

# Restore directories
cp -r /path/to/synology/backup/output ./output
cp -r /path/to/synology/backup/entity_previews ./entity_previews
cp -r /path/to/synology/backup/presets ./presets
cp -r /path/to/synology/backup/data ./data
cp -r /path/to/synology/backup/backups ./backups
```

#### 4. Start Containers (2 min)

```bash
# Start PostgreSQL first
docker-compose up -d postgres redis

# Wait for PostgreSQL to initialize
sleep 30
```

#### 5. Restore Database (2 min)

```bash
# Find latest database dump
ls -lt backups/postgres/*.sql.gz | head -1

# Restore database
gunzip -c backups/postgres/life_os_backup_YYYYMMDD_HHMMSS.sql.gz | \
    docker exec -i ai-studio-postgres psql -U lifeos -d lifeos

# Verify restoration
docker exec ai-studio-postgres psql -U lifeos -d lifeos -c "SELECT COUNT(*) FROM characters;"
```

#### 6. Restore Ollama Models (30-60 min)

```bash
# Start Ollama container
docker-compose up -d ollama

# Wait for Ollama to initialize
sleep 10

# Restore all models from manifest
./scripts/restore_ollama_models.sh
```

#### 7. Start Remaining Containers (1 min)

```bash
docker-compose up -d
```

#### 8. Verify System (2 min)

```bash
# Check all containers running
docker ps

# Test API
curl http://localhost:8000/health

# Test frontend
open http://localhost:3000
```

**Total RTO**: 1-2 hours (mostly waiting for Ollama model downloads)
**Data Loss**: Up to 24 hours (since last database dump)

---

## Cloud Failover (Emergency Access During Mac Studio Downtime)

If your Mac Studio is unavailable and you need immediate access, deploy to a cloud VPS:

### Quick Deploy to DigitalOcean

```bash
# Prerequisites: Install doctl
brew install doctl
doctl auth init

# Create VPS ($40/month, 4 vCPU, 8GB RAM)
doctl compute droplet create life-os-failover \
    --image docker-20-04 \
    --size s-4vcpu-8gb \
    --region nyc3 \
    --ssh-keys $(doctl compute ssh-key list --format ID --no-header) \
    --wait

# Get IP address
VPS_IP=$(doctl compute droplet get life-os-failover --format PublicIPv4 --no-header)
echo "VPS IP: $VPS_IP"

# Wait for SSH
until ssh root@$VPS_IP "echo ready" 2>/dev/null; do sleep 5; done

# Deploy code
git clone https://github.com/fancymatt/life-os.git
scp -r life-os root@$VPS_IP:/root/

# Deploy from Synology backups
scp -r /path/to/synology/backups/* root@$VPS_IP:/root/life-os/backups/

# Start system on VPS
ssh root@$VPS_IP "cd /root/life-os && docker-compose up -d"

# Access at http://$VPS_IP:3000
```

**When Mac Studio is restored**:
```bash
# Destroy VPS to stop charges
doctl compute droplet delete life-os-failover
```

---

## Monitoring

### Check Backup Health

```bash
# View recent database backups
ls -lht backups/postgres/*.sql.gz | head -5

# Check last backup time
ls -lt backups/postgres/*.sql.gz | head -1

# View backup logs
tail -50 logs/postgres_backup.log

# Verify Synology Drive sync status
# (Check Synology Drive app)
```

### Monthly Verification

Once per month, verify backups are working:

```bash
# 1. Check database backup exists and is recent
ls -lh backups/postgres/*.sql.gz | head -1

# 2. Test database restore (in test database)
docker-compose exec postgres createdb -U lifeos test_restore
gunzip -c backups/postgres/$(ls -t backups/postgres/*.sql.gz | head -1) | \
    docker exec -i ai-studio-postgres psql -U lifeos -d test_restore

# 3. Verify Synology Drive has latest files
# Check Synology web interface or app

# 4. Verify GitHub has latest code
git log -5
git remote -v
```

---

## Backup Scripts

All scripts located in `scripts/`:

### Active Scripts

- **`backup_postgres.sh`** - PostgreSQL database dumps
  - Usage: `./scripts/backup_postgres.sh [retention_days]`
  - Scheduled: Daily at 3 AM via cron

- **`save_ollama_manifest.sh`** - Save list of installed Ollama models
  - Usage: `./scripts/save_ollama_manifest.sh`
  - Run after installing/updating models

- **`restore_ollama_models.sh`** - Re-download all models from manifest
  - Usage: `./scripts/restore_ollama_models.sh`
  - Run during disaster recovery

### Monitoring Scripts

- **`check_backup_health.sh`** - Verify backup freshness
  - Usage: `./scripts/check_backup_health.sh`
  - Optional: Add to hourly cron for monitoring

---

## Quick Reference

### Daily Workflow

```bash
# Make changes to code
# ...

# Commit and push to GitHub
git add .
git commit -m "feat: description"
git push origin staging

# Files automatically synced by Synology Drive
# Database automatically backed up at 3 AM
```

### After Installing New Ollama Model

```bash
# Update manifest
./scripts/save_ollama_manifest.sh
```

### Manual Database Backup (Before Risky Operation)

```bash
# Create backup now
./scripts/backup_postgres.sh

# Or create named backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec ai-studio-postgres pg_dump -U lifeos -d lifeos --clean --if-exists | \
    gzip > backups/postgres/manual_backup_${TIMESTAMP}.sql.gz
```

---

## Summary

**Backup Coverage**:
- ✅ All application data (Synology Drive - real-time)
- ✅ Database (Daily dumps via cron)
- ✅ Code (GitHub - manual push)
- ✅ Ollama models (Manifest for re-download)

**Setup Required**:
1. Add one cron job for database dumps (see Setup Instructions)
2. Verify Synology Drive sync is active
3. Generate Ollama manifest once

**Recovery Time**:
- Power outage: 5 minutes (Docker restart)
- Hardware failure: 1-2 hours (mostly Ollama downloads)
- Data loss: Up to 24 hours (last database dump)

**Cost**: $0/month (uses existing Synology Drive + GitHub)

---

## Files to Ensure Are Backed Up by Synology

Critical files that MUST be in Synology Drive sync:

```
/Users/fancymatt/docker/life-os/
├── output/                          # 1.7GB - Generated images
├── entity_previews/                 # 937MB - Entity previews
├── presets/                         # 141MB - Preset files
├── data/                            # 17MB - User data, configs
│   └── ollama_models_manifest.txt   # Model list (CRITICAL)
├── uploads/                         # 14MB - Uploaded files
└── backups/postgres/                # ~500KB - Database dumps (CRITICAL)
```

Verify these are synced in Synology Drive app.
