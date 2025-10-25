# Deployment Strategy

**Last Updated**: 2025-10-23
**Status**: Staging/Production separation implemented

---

## Overview

Life-OS uses a **staging → production** deployment workflow with automated CI/CD and manual promotion to production.

```
Development (local) → Staging (staging branch) → Production (main branch)
```

---

## Branch Strategy

### Branches

1. **`main`** - Production branch (deployed to os.fcy.sh)
   - Protected: Requires PR reviews
   - Only accepts merges from `staging`
   - Tagged releases (v1.0.0, v1.1.0, etc.)

2. **`staging`** - Staging branch (deployed to staging.os.fcy.sh)
   - Default development target
   - Automatically deployed on push
   - Integration testing happens here

3. **`feature/*`** - Feature branches (optional)
   - Branch from `staging`
   - Merge back to `staging` via PR
   - Short-lived (delete after merge)

### Branch Protection Rules

**Production (`main`)**:
- ✅ Require pull request reviews (1 approval)
- ✅ Require status checks to pass (CI tests)
- ✅ No direct pushes (including admins)
- ✅ Require linear history (rebase or squash merge)
- ✅ Require conversation resolution before merging

**Staging (`staging`)**:
- ✅ Require status checks to pass (CI tests)
- ⚠️ Direct pushes allowed (for rapid iteration)
- ✅ Automatically deploy on push

---

## Deployment Workflow

### Daily Development

```bash
# Work on staging branch
git checkout staging
git pull origin staging

# Make changes
# ... edit files ...

# Commit and push (triggers staging deployment)
git add .
git commit -m "feat: add new feature"
git push origin staging

# Verify on staging.os.fcy.sh
```

### Deploying to Production

```bash
# 1. Ensure staging is stable and tested
# 2. Create PR from staging to main
gh pr create --base main --head staging --title "Release v1.1.0" --body "

## Changes in this release
- Feature 1
- Feature 2
- Bug fix 3

## Testing
- ✅ Tested on staging.os.fcy.sh
- ✅ All CI tests passing
- ✅ No breaking changes

"

# 3. Review and approve PR (GitHub web UI)
# 4. Merge PR (squash or rebase merge)
# 5. Tag release
git checkout main
git pull origin main
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0

# 6. Production deploys automatically (or manually if configured)
```

### Hotfixes (Emergency Production Fixes)

```bash
# 1. Branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. Make minimal fix
# ... fix bug ...

# 3. Commit
git add .
git commit -m "fix: critical bug in production"

# 4. PR to main (expedited review)
gh pr create --base main --head hotfix/critical-bug --title "Hotfix: Critical Bug" --label "hotfix"

# 5. After merging to main, also merge to staging
git checkout staging
git merge main  # Or cherry-pick the hotfix commit
git push origin staging
```

---

## Environment Configuration

### Environment Files

**Local Development** (`.env.local`):
```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/life_os_dev
REDIS_URL=redis://localhost:6379/0

# API Keys (development keys)
GEMINI_API_KEY=your_dev_gemini_key
OPENAI_API_KEY=your_dev_openai_key

# Auth
REQUIRE_AUTH=false
JWT_SECRET_KEY=dev_secret_key_insecure

# Environment
ENVIRONMENT=development
DEBUG=true
```

**Staging** (`.env.staging` - on server):
```bash
# Database (separate staging database)
DATABASE_URL=postgresql+asyncpg://postgres:secure_password@db.fcy.sh:5432/life_os_staging
REDIS_URL=redis://redis.fcy.sh:6379/1

# API Keys (production keys, but tracked separately)
GEMINI_API_KEY=production_gemini_key
OPENAI_API_KEY=production_openai_key

# Auth
REQUIRE_AUTH=true
JWT_SECRET_KEY=staging_secure_secret_key

# Environment
ENVIRONMENT=staging
DEBUG=false
BASE_URL=https://staging.os.fcy.sh
```

**Production** (`.env.production` - on server):
```bash
# Database (production database with backups)
DATABASE_URL=postgresql+asyncpg://postgres:very_secure_password@db.fcy.sh:5432/life_os_production
REDIS_URL=redis://redis.fcy.sh:6379/0

# API Keys
GEMINI_API_KEY=production_gemini_key
OPENAI_API_KEY=production_openai_key

# Auth
REQUIRE_AUTH=true
JWT_SECRET_KEY=production_super_secure_secret_key

# Environment
ENVIRONMENT=production
DEBUG=false
BASE_URL=https://os.fcy.sh

# Monitoring
SENTRY_DSN=your_sentry_dsn  # Error tracking
```

### Docker Compose Variants

**Development** (`docker-compose.yml`):
- Used for local development
- Includes hot-reload, debug tools
- Mounts source code as volumes
- Uses local ports (3000, 8000, 5432)

**Staging** (`docker-compose.staging.yml`):
- Production-like environment
- No hot-reload (builds static assets)
- Uses staging environment variables
- Connected to staging database

**Production** (`docker-compose.production.yml`):
- Optimized for performance
- Health checks and restart policies
- Resource limits configured
- Connected to production database
- Logging to external services

---

## Database Strategy

### Three Separate Databases

1. **Development** (`life_os_dev`) - Local PostgreSQL
   - Frequent schema changes
   - Test data
   - Can be reset/wiped freely

2. **Staging** (`life_os_staging`) - Remote PostgreSQL
   - Mirrors production schema
   - Realistic test data
   - Reset weekly/monthly

3. **Production** (`life_os_production`) - Remote PostgreSQL
   - Real user data
   - Daily backups (retain 30 days)
   - Point-in-time recovery enabled
   - Never directly modified

### Database Migrations

```bash
# Development: Create new migration
alembic revision --autogenerate -m "add user preferences table"
alembic upgrade head

# Test migration locally
# ... verify changes ...

# Push to staging
git push origin staging

# On staging server, run migrations automatically (via CI/CD)
# Or manually:
docker exec ai-studio-api alembic upgrade head

# Verify on staging.os.fcy.sh
# ... test thoroughly ...

# Promote to production (via PR main ← staging)
# On production server, run migrations (manual approval required)
docker exec ai-studio-api alembic upgrade head
```

---

## CI/CD Pipelines

### Staging Pipeline (Automatic)

**Trigger**: Push to `staging` branch

**Steps**:
1. Run all tests (backend + frontend)
2. Build Docker images
3. Push images to registry (optional)
4. SSH to staging server
5. Pull latest code
6. Run database migrations (if any)
7. Restart containers (`docker-compose up -d --build`)
8. Run smoke tests
9. Notify on Slack/Discord (optional)

**Workflow File**: `.github/workflows/deploy-staging.yml`

### Production Pipeline (Manual Approval)

**Trigger**: Merge to `main` branch

**Steps**:
1. Run all tests (backend + frontend)
2. Build Docker images (tagged with version)
3. Push images to registry
4. **Manual approval required** (GitHub Environments)
5. SSH to production server
6. Create backup (database + files)
7. Pull latest code
8. Run database migrations (manual confirmation)
9. Restart containers (blue-green or rolling)
10. Run smoke tests
11. Rollback if smoke tests fail
12. Notify on Slack/Discord

**Workflow File**: `.github/workflows/deploy-production.yml`

---

## Rollback Procedures

### Staging Rollback (Fast)

```bash
# Option 1: Revert commit
git checkout staging
git revert HEAD
git push origin staging
# Staging auto-deploys

# Option 2: Reset to previous commit
git reset --hard HEAD~1
git push origin staging --force
```

### Production Rollback (Careful)

```bash
# 1. Identify last good version
git log --oneline main

# 2. Create rollback PR
git checkout main
git revert <bad_commit_sha>
git checkout -b rollback/v1.0.9
git push origin rollback/v1.0.9

# 3. Fast-track PR review and merge

# Or emergency rollback:
# 1. On production server, checkout previous tag
git fetch --tags
git checkout v1.0.9
docker-compose down
docker-compose up -d --build

# 2. Restore database if needed (from backup)
./scripts/restore_postgresql_backup.sh backup_20251023_120000.sql.gz
```

---

## Monitoring & Alerts

### Staging
- Error tracking: Basic logging to files
- Uptime monitoring: Simple health checks
- Performance: No tracking (not critical)

### Production
- **Error Tracking**: Sentry (optional)
- **Uptime Monitoring**: UptimeRobot or StatusCake
- **Performance**: Application metrics (Prometheus + Grafana, Phase 2.2)
- **Alerts**: Email/Slack on errors >10/min or downtime >5min

---

## Testing Strategy

### Development (Local)
- Run tests before committing
- Use `pytest tests/` for backend
- Use `npm test` for frontend

### Staging (Automated)
- CI runs all tests on push
- Manual exploratory testing
- Integration testing with real services
- Performance testing (optional)

### Production (Pre-Deployment)
- Staging must be stable for 24+ hours
- All CI tests passing
- Manual smoke test checklist completed
- No open critical bugs

---

## Security Considerations

### Secrets Management

**Never commit**:
- `.env.staging`
- `.env.production`
- API keys
- Database passwords
- JWT secrets

**Use**:
- GitHub Secrets for CI/CD
- Environment variables on servers
- Secrets management service (AWS Secrets Manager, Vault) - optional

### Access Control

**Staging**:
- Password-protected (optional)
- IP whitelist (optional)
- Same auth as production (REQUIRE_AUTH=true)

**Production**:
- Rate limiting enabled (Phase 2.3)
- HTTPS only (enforce via nginx)
- Regular security audits

---

## Deployment Checklist

### Before Deploying to Staging

- [ ] All tests passing locally
- [ ] No console errors in browser
- [ ] Database migrations tested locally
- [ ] Commit messages follow convention
- [ ] No secrets in code

### Before Deploying to Production

- [ ] Staging stable for 24+ hours
- [ ] All CI tests passing
- [ ] Database migration plan documented
- [ ] Rollback plan documented
- [ ] Stakeholders notified (if user-facing changes)
- [ ] Backup created (database + files)
- [ ] Smoke test checklist prepared

### Post-Deployment

- [ ] Smoke tests pass (critical paths work)
- [ ] Error monitoring shows no spikes
- [ ] Performance acceptable (response times normal)
- [ ] Database migrations completed successfully
- [ ] Rollback plan available (if needed)

---

## Quick Reference

### Common Commands

```bash
# Check current branch
git branch

# Switch to staging
git checkout staging

# Switch to production (read-only, no direct edits!)
git checkout main

# Create feature branch
git checkout staging
git checkout -b feature/my-feature

# Deploy to staging (push to staging branch)
git push origin staging

# Deploy to production (PR staging → main)
gh pr create --base main --head staging

# Check deployment status
docker ps
docker logs ai-studio-api --tail 100
docker logs ai-studio-frontend --tail 100

# Run migrations
docker exec ai-studio-api alembic upgrade head

# Restart services
docker-compose restart api frontend

# View live logs
docker-compose logs -f api frontend
```

### URLs

- **Local Development**: http://localhost:3000
- **Staging**: https://staging.os.fcy.sh
- **Production**: https://os.fcy.sh

### Support

- **Documentation**: This file (docs/guides/deployment.md)
- **Runbook**: ROADMAP.md (project status)
- **Issues**: GitHub Issues
- **Emergencies**: Rollback procedures above

---

## Next Steps

After implementing this deployment strategy:

1. **Create staging branch**:
   ```bash
   git checkout -b staging
   git push origin staging
   ```

2. **Set up branch protection rules** (GitHub Settings → Branches)

3. **Create staging deployment workflow** (`.github/workflows/deploy-staging.yml`)

4. **Set up staging server** (if not already exists)

5. **Test deployment workflow** (push to staging, verify auto-deploy)

6. **Document server setup** (if manual deployment)

---

## Version History

- **v3.0** (2025-10-23): Initial deployment strategy documentation
