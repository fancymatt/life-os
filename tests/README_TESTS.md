# Job Queue System - Test Suite

Comprehensive test suite for verifying the job queue management system implementation.

## Test Components

### 1. Backend Python Tests (`test_job_queue_system.py`)

Automated Python test script that verifies:
- ✅ API health and connectivity
- ✅ Analyzer endpoints
- ✅ Job management endpoints
- ✅ Synchronous analysis workflow
- ✅ Asynchronous analysis with job queue
- ✅ Comprehensive analysis with selective analyzers
- ✅ Job cancellation
- ✅ Concurrent job execution

**Run the tests:**
```bash
# Make the script executable
chmod +x tests/test_job_queue_system.py

# Run all tests
python3 tests/test_job_queue_system.py
```

**Expected Output:**
```
==============================================================================
Job Queue System - Comprehensive Test Suite
==============================================================================

Testing: API Health Check
✓ API is healthy

Testing: List Analyzers
✓ Found 9 analyzers: outfit, comprehensive, visual-style, art-style, ...

... (more tests) ...

==============================================================================
Test Summary
==============================================================================
✓ Passed: 8
✗ Failed: 0
⚠ Warnings: 0

Success Rate: 100.0%
```

### 2. Frontend Integration Tests (`test_frontend_integration.html`)

Interactive browser-based test page for manual verification of:
- 🌐 API connectivity from browser
- 📊 Job queue operations
- 🔄 Server-Sent Events (SSE) streaming
- 🎯 Comprehensive analysis workflow

**Run the tests:**
```bash
# Open in browser (make sure Docker containers are running)
open tests/test_frontend_integration.html
# or
# Navigate to: file:///path/to/tests/test_frontend_integration.html
```

Click the test buttons to verify each feature. Results appear in real-time on the page.

## Prerequisites

Before running tests:

1. **Start Docker containers:**
   ```bash
   docker-compose up -d
   ```

2. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

   You should see:
   - `ai-studio-api` (running on port 8000)
   - `ai-studio-frontend` (running on port 80)

3. **Check API health:**
   ```bash
   curl http://localhost:8000/health
   ```

## Test Coverage

### Backend API Tests

| Test | Endpoint | Method | Verifies |
|------|----------|--------|----------|
| Health Check | `/health` | GET | API is running and healthy |
| List Analyzers | `/api/analyze/` | GET | All analyzers are registered |
| List Jobs | `/api/jobs` | GET | Job endpoint is accessible |
| Sync Analysis | `/api/analyze/outfit?async_mode=false` | POST | Blocking analysis works |
| Async Analysis | `/api/analyze/outfit?async_mode=true` | POST | Job queue creation |
| Get Job Status | `/api/jobs/{job_id}` | GET | Job status tracking |
| Cancel Job | `/api/jobs/{job_id}/cancel` | POST | Job cancellation |
| Delete Job | `/api/jobs/{job_id}` | DELETE | Job cleanup |
| Comprehensive | `/api/analyze/comprehensive` | POST | Multi-analyzer workflow |
| SSE Stream | `/api/jobs/stream` | GET | Real-time updates |

### Frontend Integration Tests

| Test | Component | Verifies |
|------|-----------|----------|
| API Health | JavaScript fetch | CORS and connectivity |
| List Analyzers | API call | Frontend can list tools |
| List Jobs | API call | Frontend can access jobs |
| Async Analysis | Job creation | Frontend can queue jobs |
| Job Polling | Status updates | Frontend can poll job status |
| Job Cancellation | Cancel operation | Frontend can cancel jobs |
| SSE Connection | EventSource | Real-time job updates |
| Comprehensive | Complex workflow | Multi-step analysis |

## Manual Testing Checklist

After running automated tests, manually verify the following in the browser:

### TaskManager UI

1. **Floating Button**
   - [ ] Button appears in bottom-right corner
   - [ ] Badge shows active job count
   - [ ] Button color changes based on job status (blue=running, green=completed, red=failed)
   - [ ] Button pulses when jobs are running

2. **Task Panel**
   - [ ] Panel slides in from bottom-right when button is clicked
   - [ ] Shows all active jobs
   - [ ] Jobs are grouped by status (Running → Queued → Completed → Failed)
   - [ ] Completed jobs auto-dismiss after 5 seconds

3. **Task Items**
   - [ ] Each task shows title, progress bar, and status icon
   - [ ] Running tasks show spinning icon and progress percentage
   - [ ] Progress bars animate smoothly
   - [ ] Cancel button works for running jobs
   - [ ] Dismiss button works for completed/failed jobs
   - [ ] Click to expand shows full details (error messages, results)

4. **Real-time Updates**
   - [ ] Task statuses update automatically via SSE
   - [ ] Progress bars update in real-time
   - [ ] New tasks appear immediately when created

### Analyzer Integration

1. **Individual Analyzers** (Outfit, Visual Style, etc.)
   - [ ] Upload image
   - [ ] Click "Analyze"
   - [ ] Modal closes immediately
   - [ ] Task appears in TaskManager
   - [ ] Progress updates in real-time
   - [ ] Task completes successfully
   - [ ] Preset is created in the list

2. **Comprehensive Analyzer**
   - [ ] Upload image
   - [ ] Select subset of analyses
   - [ ] Click "Run Selected Analyses"
   - [ ] Modal closes immediately
   - [ ] Parent task appears with child tasks
   - [ ] Each child task updates independently
   - [ ] Parent progress shows "X/Y complete"
   - [ ] All presets are created when complete

## Troubleshooting

### Tests Fail with Connection Error

**Problem:** `Connection refused` or `Failed to connect`

**Solution:**
```bash
# Check if containers are running
docker-compose ps

# Restart containers
docker-compose restart

# Check API logs
docker-compose logs api
```

### SSE Tests Fail

**Problem:** `SSE connection error` or timeouts

**Solution:**
1. Check nginx configuration allows SSE:
   ```nginx
   proxy_buffering off;
   proxy_cache off;
   proxy_set_header Connection '';
   ```

2. Verify SSE endpoint:
   ```bash
   curl -N http://localhost:8000/api/jobs/stream
   ```

### Jobs Never Complete

**Problem:** Jobs stuck in "running" or "queued" status

**Solution:**
```bash
# Check API logs for errors
docker-compose logs -f api

# Restart API container
docker-compose restart api
```

### Frontend Can't Connect to API

**Problem:** CORS errors or 404s

**Solution:**
1. Check nginx proxy configuration
2. Verify API is accessible:
   ```bash
   curl http://localhost:8000/health
   ```

## Performance Benchmarks

Expected performance on standard hardware:

| Operation | Expected Time | Notes |
|-----------|--------------|-------|
| Single Analysis | 3-5 seconds | Depends on image size and model |
| Comprehensive (2 analyses) | 8-12 seconds | Runs analyzers sequentially |
| Comprehensive (6 analyses) | 20-30 seconds | Full analysis suite |
| Job Queue Overhead | <100ms | Job creation and queueing |
| SSE Latency | <500ms | Real-time update delivery |
| Concurrent Jobs (3) | ~Same as single | Jobs run in parallel |

## Continuous Testing

### Watch Mode for Development

Monitor API logs while testing:
```bash
docker-compose logs -f api
```

### Automated Testing in CI/CD

Add to your CI pipeline:
```yaml
# .github/workflows/test.yml
- name: Run Job Queue Tests
  run: |
    docker-compose up -d
    sleep 10  # Wait for services
    python3 tests/test_job_queue_system.py
    docker-compose down
```

## Test Data Cleanup

After testing, clean up test data:

```bash
# Remove test presets
rm -rf presets/outfits/*.json
rm -rf presets/visual_styles/*.json

# Remove test cache
rm -rf cache/*

# Remove preview images
rm -rf presets/*/*.png

# Restart containers to reset state
docker-compose restart
```

## Reporting Issues

If tests fail, include:
1. Test output (full log)
2. Docker logs: `docker-compose logs api`
3. Browser console errors (for frontend tests)
4. System info (OS, Docker version)
5. Test image used (if custom)

## Next Steps

After all tests pass:
1. ✅ Test with real images
2. ✅ Monitor performance under load
3. ✅ Test concurrent user scenarios
4. ✅ Verify cleanup and memory usage
5. ✅ Test error recovery and edge cases
