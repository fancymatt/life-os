# PostgreSQL Backup and Restore Guide

## Overview

This directory contains scripts for backing up and restoring the Life-OS PostgreSQL database.

## Backup Script

### Usage

```bash
# Run backup with default 30-day retention
./scripts/backup_postgres.sh

# Run backup with custom retention (7 days)
./scripts/backup_postgres.sh 7
```

### What It Does

1. Creates a full database dump using `pg_dump`
2. Compresses the backup with gzip (saves ~75% space)
3. Deletes backups older than retention period
4. Logs all operations to `logs/backups.log`

### Backup Location

Backups are stored in: `backups/postgres/`

Format: `life_os_backup_YYYYMMDD_HHMMSS.sql.gz`

### Automated Backups (Cron)

Add to crontab for automated backups:

```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily backup at 2 AM (30-day retention)
0 2 * * * /path/to/life-os/scripts/backup_postgres.sh

# Hourly backup during work hours (7-day retention)
0 9-17 * * * /path/to/life-os/scripts/backup_postgres.sh 7
```

## Restore from Backup

### Stop the API (to prevent conflicts)

```bash
docker-compose stop api
```

### Restore Database

```bash
# List available backups
ls -lh backups/postgres/

# Restore from specific backup
gunzip -c backups/postgres/life_os_backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i ai-studio-postgres psql -U lifeos -d lifeos

# OR restore from uncompressed backup
docker exec -i ai-studio-postgres psql -U lifeos -d lifeos < backups/postgres/backup.sql
```

### Restart the API

```bash
docker-compose start api
```

### Verify Restoration

```bash
# Check database tables
docker exec ai-studio-postgres psql -U lifeos -d lifeos -c "\dt"

# Check row counts
docker exec ai-studio-postgres psql -U lifeos -d lifeos -c "
  SELECT
    schemaname,
    tablename,
    n_live_tup as row_count
  FROM pg_stat_user_tables
  ORDER BY n_live_tup DESC;
"
```

## Point-in-Time Recovery (PITR)

For point-in-time recovery, you would need to:

1. Enable WAL archiving in PostgreSQL
2. Store WAL files externally
3. Use `pg_restore` with point-in-time options

This is a more advanced setup and is not currently configured.

## Backup Best Practices

### Retention Strategy

- **Hourly backups**: 7-day retention (for recent changes)
- **Daily backups**: 30-day retention (for monthly recovery)
- **Monthly backups**: Keep manually (for long-term archival)

### Testing Backups

Test restoration quarterly to ensure backups work:

```bash
# 1. Create test database
docker exec ai-studio-postgres psql -U lifeos -c "CREATE DATABASE lifeos_test;"

# 2. Restore to test database
gunzip -c backups/postgres/latest_backup.sql.gz | \
  docker exec -i ai-studio-postgres psql -U lifeos -d lifeos_test

# 3. Verify data
docker exec ai-studio-postgres psql -U lifeos -d lifeos_test -c "\dt"

# 4. Drop test database
docker exec ai-studio-postgres psql -U lifeos -c "DROP DATABASE lifeos_test;"
```

### Monitoring

- Check `logs/backups.log` for backup status
- Monitor backup directory size: `du -sh backups/postgres/`
- Set up alerts if backups fail (check log for ERROR)

## Troubleshooting

### Backup fails with "connection refused"

```bash
# Check if postgres container is running
docker ps | grep postgres

# If not running, start it
docker-compose up -d postgres
```

### Backup fails with "role does not exist"

```bash
# Verify database credentials in docker-compose.yml
grep -A 5 "postgres:" docker-compose.yml

# Update backup script if credentials changed
```

### Restore fails with permission errors

```bash
# Ensure you're running restore from project root
cd /path/to/life-os
./scripts/restore_postgres.sh
```

### Disk space issues

```bash
# Check backup directory size
du -sh backups/postgres/

# Manually delete old backups if needed
rm backups/postgres/life_os_backup_2024*.sql.gz

# Or reduce retention period
./scripts/backup_postgres.sh 7  # Only keep 7 days
```

## Security Notes

- **Backups are NOT encrypted** - Protect backup directory permissions
- **Backups contain all data** - Including passwords (hashed)
- **External storage** - Consider copying backups to S3/external drive
- **Access control** - Restrict backup directory to authorized users only

## Future Improvements

- [ ] Encrypt backups (GPG or AES-256)
- [ ] Upload to external storage (S3, external drive)
- [ ] Implement incremental backups (WAL archiving)
- [ ] Point-in-time recovery (PITR)
- [ ] Automated backup verification
- [ ] Backup monitoring dashboard
- [ ] Email notifications on backup failure
