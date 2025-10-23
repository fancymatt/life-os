# Backup & Recovery Guide

**Last Updated**: 2025-10-23
**Version**: 1.0

---

## Overview

This guide documents all backup and recovery procedures for Life-OS. With the completion of Phase 1.1 (Database Migration Safety Features), we now have comprehensive backup and rollback capabilities.

**Key Safety Features**:
- ✅ JSON data backups (automated)
- ✅ PostgreSQL backups (daily full backups)
- ✅ Rollback script (PostgreSQL → JSON)
- ✅ Backup testing suite
- ✅ Feature flags system for gradual rollout
- ⚠️ Point-in-time recovery (WAL archiving configuration documented, needs setup)

---

## Backup Types

### 1. JSON Data Backup

Backs up all JSON files (data/, presets/, configs/) to compressed archives.

**Location**: `backups/json/`
**Retention**: 30 backups (auto-cleanup)
**Frequency**: On-demand or scheduled

**Create Backup**:
```bash
./scripts/backup_json_data.sh
```

**Output**:
- Timestamped tar.gz archive (e.g., `json_backup_20251023_071327.tar.gz`)
- Backup manifest with checksums
- Automatic cleanup of old backups

**Restore from Backup**:
```bash
cd backups/json
tar -xzf json_backup_YYYYMMDD_HHMMSS.tar.gz
cp -r json_backup_YYYYMMDD_HHMMSS/data /path/to/project/
cp -r json_backup_YYYYMMDD_HHMMSS/presets /path/to/project/
cp -r json_backup_YYYYMMDD_HHMMSS/configs /path/to/project/
```

### 2. PostgreSQL Full Backup

Creates full database dump using `pg_dump`.

**Location**: `backups/postgresql/full/`
**Retention**: 30 days
**Frequency**: Daily at 2 AM (recommended)

**Create Backup**:
```bash
./scripts/backup_postgresql.sh full
```

**Output**:
- Compressed SQL dump (e.g., `postgres_full_20251023_071500.sql.gz`)
- Includes schema and data
- Automatic verification and cleanup

**Restore from Backup**:
```bash
# Decompress and restore
gunzip -c backups/postgresql/full/postgres_full_*.sql.gz | \
  docker exec -i ai-studio-postgres psql -U lifeos -d life_os
```

### 3. PostgreSQL to JSON Rollback

Exports all entities from PostgreSQL back to JSON files.

**Use Case**: Migration failure, need to revert to JSON-based storage

**Create Rollback** (Dry Run):
```bash
docker exec ai-studio-api python3 /app/scripts/rollback_to_json.py --dry-run
```

**Create Rollback** (Actual):
```bash
# Backup current JSON files first
./scripts/backup_json_data.sh

# Export from PostgreSQL
docker exec ai-studio-api python3 /app/scripts/rollback_to_json.py --backup-first
```

**Entities Exported**:
- Characters
- Clothing Items
- Outfits
- Compositions
- Board Games
- Favorites

### 4. Point-in-Time Recovery (WAL Archiving)

**Status**: ⚠️ Needs Configuration

Enables restore to any point in time using Write-Ahead Log (WAL) archiving.

**Setup Required**:
1. Configure `postgresql.conf`:
   ```ini
   wal_level = replica
   archive_mode = on
   archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
   ```

2. Create WAL archive directory:
   ```bash
   docker exec ai-studio-postgres mkdir -p /var/lib/postgresql/wal_archive
   ```

3. Restart PostgreSQL:
   ```bash
   docker-compose restart postgres
   ```

**Restore to Point-in-Time**:
```bash
# 1. Restore base backup
gunzip -c backups/postgresql/full/postgres_full_*.sql.gz | \
  docker exec -i ai-studio-postgres psql -U lifeos -d life_os

# 2. Create recovery.conf
docker exec ai-studio-postgres bash -c "cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'
recovery_target_time = '2025-10-23 12:00:00'
EOF"

# 3. Restart PostgreSQL
docker-compose restart postgres
```

---

## Automated Backups

### Schedule with Cron

**Daily JSON Backup** (2 AM):
```bash
0 2 * * * /path/to/life-os/scripts/backup_json_data.sh >> /var/log/json_backup.log 2>&1
```

**Daily PostgreSQL Backup** (3 AM):
```bash
0 3 * * * /path/to/life-os/scripts/backup_postgresql.sh full >> /var/log/postgres_backup.log 2>&1
```

**Weekly Backup Test** (Sunday 4 AM):
```bash
0 4 * * 0 /path/to/life-os/scripts/test_backup_restore.sh >> /var/log/backup_test.log 2>&1
```

### Schedule with systemd Timers

Create `/etc/systemd/system/lifeos-backup.service`:
```ini
[Unit]
Description=Life-OS JSON Backup
After=network.target

[Service]
Type=oneshot
User=fancymatt
WorkingDirectory=/path/to/life-os
ExecStart=/path/to/life-os/scripts/backup_json_data.sh
```

Create `/etc/systemd/system/lifeos-backup.timer`:
```ini
[Unit]
Description=Daily Life-OS Backup

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable lifeos-backup.timer
sudo systemctl start lifeos-backup.timer
```

---

## Backup Testing

### Automated Test Suite

Run comprehensive backup/restore tests:

```bash
./scripts/test_backup_restore.sh
```

**Tests Performed**:
1. ✅ JSON backup creation
2. ✅ Backup extraction
3. ✅ Data integrity check (MD5 checksums)
4. ✅ Backup manifest verification
5. ✅ PostgreSQL rollback dry run
6. ✅ Backup rotation (old backup cleanup)

**Test Results**:
- Saved to `backups/test_YYYYMMDD_HHMMSS/`
- Includes logs and extracted files
- Auto-cleanup with instructions

### Manual Verification

**Quarterly Restoration Drill** (Recommended):

1. **Create test database**:
   ```bash
   docker exec ai-studio-postgres createdb -U lifeos life_os_test
   ```

2. **Restore latest backup**:
   ```bash
   gunzip -c backups/postgresql/full/postgres_full_*.sql.gz | \
     docker exec -i ai-studio-postgres psql -U lifeos -d life_os_test
   ```

3. **Verify data**:
   ```bash
   docker exec ai-studio-postgres psql -U lifeos -d life_os_test -c "SELECT COUNT(*) FROM characters;"
   docker exec ai-studio-postgres psql -U lifeos -d life_os_test -c "SELECT COUNT(*) FROM clothing_items;"
   ```

4. **Cleanup**:
   ```bash
   docker exec ai-studio-postgres dropdb -U lifeos life_os_test
   ```

---

## Feature Flags System

Control database migration rollout using feature flags.

### Check Feature Flags

```bash
docker exec ai-studio-api python3 /app/scripts/manage_feature_flags.py list
```

### Enable/Disable Features

```bash
# Enable PostgreSQL backend
docker exec ai-studio-api python3 /app/scripts/manage_feature_flags.py set use_postgresql_backend true

# Disable PostgreSQL backend (rollback to JSON)
docker exec ai-studio-api python3 /app/scripts/manage_feature_flags.py set use_postgresql_backend false
```

### Gradual Rollout

**10% Rollout** (test with 10% of requests):
```bash
docker exec ai-studio-api python3 /app/scripts/manage_feature_flags.py set use_postgresql_backend 10%
```

**50% Rollout** (half of requests):
```bash
docker exec ai-studio-api python3 /app/scripts/manage_feature_flags.py set use_postgresql_backend 50%
```

**100% Rollout** (all requests):
```bash
docker exec ai-studio-api python3 /app/scripts/manage_feature_flags.py set use_postgresql_backend 100%
```

Or fully enable:
```bash
docker exec ai-studio-api python3 /app/scripts/manage_feature_flags.py set use_postgresql_backend true
```

### User-Specific Overrides

Enable for specific user (testing):
```bash
docker exec ai-studio-api python3 /app/scripts/manage_feature_flags.py set-user use_postgresql_backend user123 true
```

---

## Disaster Recovery Procedures

### Scenario 1: PostgreSQL Corruption

**Symptoms**: Database won't start, data corruption errors

**Recovery**:
1. Stop the application:
   ```bash
   docker-compose down
   ```

2. Restore from latest backup:
   ```bash
   # Start only PostgreSQL
   docker-compose up -d postgres

   # Restore backup
   gunzip -c backups/postgresql/full/postgres_full_*.sql.gz | \
     docker exec -i ai-studio-postgres psql -U lifeos -d life_os
   ```

3. Verify restoration:
   ```bash
   docker exec ai-studio-postgres psql -U lifeos -d life_os -c "\dt"
   ```

4. Restart application:
   ```bash
   docker-compose up -d
   ```

**Recovery Time Objective (RTO)**: <1 hour
**Recovery Point Objective (RPO)**: Last backup (daily = 24 hours max data loss)

### Scenario 2: Database Migration Failure

**Symptoms**: Migration errors, data inconsistencies

**Recovery**:
1. Create backup of current state:
   ```bash
   ./scripts/backup_postgresql.sh full
   ./scripts/backup_json_data.sh
   ```

2. Disable PostgreSQL backend via feature flag:
   ```bash
   docker exec ai-studio-api python3 /app/scripts/manage_feature_flags.py set use_postgresql_backend false
   ```

3. Rollback to JSON files:
   ```bash
   docker exec ai-studio-api python3 /app/scripts/rollback_to_json.py --backup-first
   ```

4. Restart application:
   ```bash
   docker-compose restart api
   ```

**RTO**: <30 minutes
**RPO**: Last sync to PostgreSQL

### Scenario 3: Accidental Data Deletion

**Symptoms**: User reports missing data

**Recovery (if within 24 hours)**:
1. Restore from yesterday's backup to test database:
   ```bash
   docker exec ai-studio-postgres createdb -U lifeos life_os_restore
   gunzip -c backups/postgresql/full/postgres_full_$(date -d yesterday +%Y%m%d)_*.sql.gz | \
     docker exec -i ai-studio-postgres psql -U lifeos -d life_os_restore
   ```

2. Export deleted entity:
   ```bash
   docker exec ai-studio-postgres psql -U lifeos -d life_os_restore \
     -c "SELECT * FROM characters WHERE character_id = 'xxx';" -o /tmp/deleted_character.sql
   ```

3. Import to production:
   ```bash
   # Manual import or use rollback script with --entity-type flag
   ```

**RTO**: <1 hour
**RPO**: Last backup (24 hours)

### Scenario 4: Complete System Failure

**Symptoms**: Server crash, data center failure

**Recovery** (requires off-site backups):
1. Set up new server
2. Clone repository
3. Copy backups from off-site storage
4. Restore PostgreSQL:
   ```bash
   docker-compose up -d postgres
   gunzip -c backups/postgresql/full/postgres_full_*.sql.gz | \
     docker exec -i ai-studio-postgres psql -U lifeos -d life_os
   ```
5. Restore JSON files:
   ```bash
   tar -xzf backups/json/json_backup_*.tar.gz
   cp -r json_backup_*/data ./
   cp -r json_backup_*/presets ./
   ```
6. Start application:
   ```bash
   docker-compose up -d
   ```

**RTO**: <4 hours
**RPO**: Last backup sync to off-site storage

---

## Backup Monitoring

### Check Backup Status

```bash
# List recent JSON backups
ls -lht backups/json/*.tar.gz | head -5

# List recent PostgreSQL backups
ls -lht backups/postgresql/full/*.sql.gz | head -5

# Check backup sizes
du -sh backups/json/
du -sh backups/postgresql/
```

### Alerts (Recommended)

Set up alerts for:
- Backup job failures
- Backup size anomalies (too large/small)
- Missing backups (check daily)
- Disk space warnings

**Example Monitoring Script**:
```bash
#!/bin/bash
# Check if backup ran in last 25 hours
LATEST_BACKUP=$(find backups/postgresql/full -name "*.sql.gz" -mtime -1 | wc -l)
if [ "$LATEST_BACKUP" -eq 0 ]; then
    echo "WARNING: No PostgreSQL backup in last 24 hours!"
    # Send alert (email, Slack, PagerDuty, etc.)
fi
```

---

## Best Practices

### DO:
- ✅ Test backups regularly (monthly minimum)
- ✅ Keep backups off-site (cloud storage, external drive)
- ✅ Verify backup integrity (checksums, test restores)
- ✅ Document recovery procedures
- ✅ Practice disaster recovery drills
- ✅ Monitor backup job success/failure
- ✅ Use feature flags for gradual rollout
- ✅ Keep multiple backup versions

### DON'T:
- ❌ Assume backups work without testing
- ❌ Store backups only on the same server
- ❌ Delete old backups without retention policy
- ❌ Skip verification steps
- ❌ Modify production data without backup first
- ❌ Use production database for testing
- ❌ Run untested recovery procedures during outage

---

## Troubleshooting

### Backup Script Fails

**Check**:
- Docker containers running: `docker ps`
- Disk space available: `df -h`
- Permissions on backup directory: `ls -la backups/`
- PostgreSQL container name matches: `docker ps | grep postgres`

### Restore Fails

**Common Issues**:
- Database already exists: Drop and recreate
- Permission denied: Check user/role permissions
- Incompatible PostgreSQL version: Verify versions match
- Corrupted backup: Try previous backup

### Feature Flags Not Working

**Check**:
- Redis running: `docker ps | grep redis`
- Feature flag service imported: Check application logs
- Correct flag name: List all flags with `manage_feature_flags.py list`

---

## Maintenance Schedule

| Task | Frequency | Script | Time |
|------|-----------|--------|------|
| JSON Backup | Daily | `backup_json_data.sh` | 2 AM |
| PostgreSQL Backup | Daily | `backup_postgresql.sh full` | 3 AM |
| Backup Testing | Weekly | `test_backup_restore.sh` | Sunday 4 AM |
| Restore Drill | Quarterly | Manual | Scheduled |
| Cleanup Old Backups | Daily | Auto (in backup scripts) | After backup |
| Off-site Sync | Daily | rsync/rclone (TBD) | 5 AM |

---

## Scripts Reference

| Script | Purpose | Location |
|--------|---------|----------|
| `backup_json_data.sh` | Backup JSON files | `scripts/` |
| `backup_postgresql.sh` | Backup PostgreSQL | `scripts/` |
| `rollback_to_json.py` | PostgreSQL → JSON | `scripts/` |
| `test_backup_restore.sh` | Test backup/restore | `scripts/` |
| `manage_feature_flags.py` | Manage feature flags | `scripts/` |

---

## Compliance & Auditing

### Audit Trail

All backup operations create logs with:
- Timestamp
- User who initiated
- Backup type and size
- Success/failure status
- File locations

### Data Retention

- **JSON Backups**: 30 days
- **PostgreSQL Full**: 30 days
- **PostgreSQL Incremental**: 7 days
- **Audit Logs**: 90 days

### Security

- Backups stored with restricted permissions (chmod 600)
- Encrypted backups recommended for off-site storage
- Access controls for backup restoration
- Audit all restore operations

---

## Future Enhancements

Planned improvements (Phase 2.4):

- [ ] Automated off-site backup sync (S3, GCS, Azure Blob)
- [ ] Encrypted backups
- [ ] Real-time replication (streaming replication)
- [ ] Backup monitoring dashboard
- [ ] Automated alerts (Slack, email, PagerDuty)
- [ ] Multi-region backups
- [ ] Backup compression optimization
- [ ] Incremental PostgreSQL backups (WAL-E, pgBackRest)

---

## See Also

- `ROADMAP.md` - Phase 1.1 Database Migration Safety Features
- `API_ARCHITECTURE.md` - Database architecture
- `docker-compose.yml` - PostgreSQL configuration
- PostgreSQL Documentation: https://www.postgresql.org/docs/current/backup.html

---

**Questions?** Contact the team or file an issue in the repository.
