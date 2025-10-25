# Life-OS - AI Assistant Development Guide

**Last Updated**: 2025-10-24

## What is Life-OS?

Multi-domain AI platform for image generation, analysis, and workflow orchestration. Built with FastAPI (Python), React (Vite), PostgreSQL, and Redis.

**Find detailed documentation in:**
- **README.md** - Setup, features, architecture overview
- **ROADMAP.md** - Development phases and priorities
- **docs/guides/design-patterns.md** - Best practices and code patterns
- **docs/guides/api-reference.md** - Backend architecture details
- **ai_tools/README_TOOL_DEVELOPMENT.md** - AI tool checklist

---

## Core Architecture Principles

### Tools/Entities/Workflows (CRITICAL)

**Tools must work standalone AND in workflows** - never create workflow-only code.

```
Entity (Data + Self-Description)
  ↓ used by
Tool (Prompting Logic + Model Config)
  - MUST have standalone API endpoint: /api/tools/{tool}
  ↓ orchestrated by
Workflow (Multi-Tool Coordination)
  - Uses SAME tool code as standalone
```

**✅ Correct**: Tool works standalone, workflow calls same code
**❌ Wrong**: Workflow-specific prompting logic that bypasses tools

### Database: PostgreSQL (NOT JSON files)

```bash
# ✅ Query database
docker exec ai-studio-postgres psql -U lifeos -d lifeos -c "SELECT COUNT(*) FROM clothing_items;"

# ❌ Don't read JSON files (deprecated)
# data/characters/*.json - OLD, migrated to PostgreSQL
```

**Data storage:**
- Database records → PostgreSQL (characters, clothing_items, outfits, stories)
- Generated images → `output/` directory
- Presets → `presets/` directory (JSON files, still used)
- Cache → `cache/` directory (temporary)

### Service Layer Pattern

- **Routes** (`api/routes/`) - Handle HTTP concerns (validation, auth)
- **Services** (`api/services/`) - Handle business logic
- **Models** (`api/models/`) - Pydantic schemas for validation

---

## Development Workflow

### Deployment Pipeline

**Backend changes** (Python/API):
```bash
# 1. Edit files in api/ or ai_tools/
# 2. Rebuild API + workers (BOTH required)
docker-compose up -d --build api
docker-compose up -d --build rq-worker
docker-compose up -d --scale rq-worker=4

# 3. Check logs
docker logs ai-studio-api --tail 50
docker logs life-os-rq-worker-1 --tail 20
```

**Frontend changes** (React):
```bash
# 1. Edit files in frontend/src/
# 2. Rebuild frontend (Vite bundles static files)
docker-compose up -d --build frontend

# 3. Check build succeeded
docker logs ai-studio-frontend --tail 20

# 4. Hard refresh browser (Cmd+Shift+R)
```

**Config changes**:
```bash
# configs/models.yaml → Restart API
docker-compose restart api

# frontend/vite.config.js → Rebuild frontend
docker-compose up -d --build frontend
```

### Testing Before Asking User

```bash
# 1. Check logs for errors
docker logs ai-studio-api --tail 100

# 2. Verify build succeeded
docker logs ai-studio-frontend --tail 20

# 3. Test endpoint
curl -X POST http://localhost:8000/api/workflows/story

# 4. Check browser console (DevTools → Console)

# 5. Fix errors BEFORE asking user to test
```

### Git Workflow

**When to commit:**
- ✅ After completing a feature (working end-to-end)
- ✅ After fixing a bug (verified fixed)
- ✅ Before switching tasks
- ❌ NOT after every file edit

**Files to NEVER commit:**
- `data/users.json` (passwords)
- `output/` (generated images)
- `cache/` (temporary files)
- `.env` (secrets)

---

## Coding Standards

### Logging (MANDATORY)

**NEVER use print() statements** - use structured logging.

```python
from api.logging_config import get_logger
logger = get_logger(__name__)

# ✅ Correct
logger.info(f"Created character: {character_id}")
logger.warning(f"Failed to load config: {error}")
logger.error("Database connection failed", extra={'extra_fields': {'timeout': 30}})

# ❌ Wrong
print("Created character")  # NEVER DO THIS
```

### Backend Patterns

```python
# Async file I/O
import aiofiles
async with aiofiles.open(file_path, 'w') as f:
    await f.write(json.dumps(data, indent=2))

# Route with error handling
@router.post("/endpoint")
async def endpoint_name(
    request: RequestModel,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Endpoint description"""
    try:
        result = service.method(request)
        return ResponseModel(status="completed", result=result)
    except Exception as e:
        logger.error(f"Endpoint failed: {e}")
        return ResponseModel(status="failed", error=str(e))
```

### Frontend Patterns

```jsx
function ComponentName() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchData()
  }, [dependency])

  const handleAction = useCallback(async () => {
    // Implementation
  }, [dependencies])

  return <div className="component-name">{/* JSX */}</div>
}
```

---

## Common Pitfalls (CRITICAL)

### 1. RQ Worker Code Not Updating

**Problem**: Workers load code at startup, don't auto-reload after changes.

**Solution**: ALWAYS rebuild workers after API changes.

```bash
# ✅ Correct - rebuild both
docker-compose up -d --build api
docker-compose up -d --build rq-worker
docker-compose up -d --scale rq-worker=4

# ❌ Wrong - only rebuild API
docker-compose up -d --build api  # Workers still have old code!
```

**Symptoms:**
- Jobs show "completed" but no files updated
- No application logs (only RQ framework logs)
- Works directly via API but not via workers

**Rule**: If you rebuild API, rebuild workers too.

### 2. FastAPI Trailing Slash Issues

**Problem**: Frontend/backend slash mismatch causes 307 redirects or 405 errors.

```python
# Backend route
@router.get("/characters/", ...)

# ✅ Frontend must match exactly
await api.get('/characters/')  # Include slash

# ❌ Wrong
await api.get('/characters')  # Missing slash → 307 redirect
```

**Route ordering matters:**
```python
# ✅ Specific routes BEFORE parameterized
@router.post("/characters/from-subject/", ...)  # Specific
@router.get("/{character_id}", ...)             # Parameterized

# ❌ Wrong - parameterized route matches everything
@router.get("/{character_id}", ...)             # Matches "from-subject"
@router.post("/characters/from-subject/", ...)  # Never reached!
```

**Debugging:**
```bash
docker logs ai-studio-api --tail 50
# Look for: 307 Temporary Redirect or 405 Method Not Allowed
```

### 3. File Path Mismatches (Container vs Host)

**Problem**: Paths saved as `/uploads/file.png` but actual path is `/app/uploads/file.png`.

**Solution**: Use `api/utils/file_paths.py` utilities.

```python
from api.utils.file_paths import (
    validate_file_exists,
    ensure_app_prefix,
    normalize_container_path
)

# ✅ Validate with auto-normalization
valid_path = validate_file_exists(
    user_path,
    description="Reference image",
    auto_normalize=True  # Tries /app prefix if needed
)

# ✅ Normalize before saving to database
reference_path = ensure_app_prefix(uploaded_file_path)
```

**Symptoms:**
- "File not found" errors
- Gemini falls back to DALL-E unexpectedly
- Generated images don't match reference style

### 4. Cache Invalidation Pattern Bugs

**Problem**: Pattern doesn't match actual cache keys.

```python
# Actual keys: cache:/visualization-configs/abc123
# Pattern must match:

# ✅ Correct
pattern = f"{self.prefix}/{endpoint_path}*"  # NO /api/ prefix

# ❌ Wrong
pattern = f"{self.prefix}/api/{endpoint_path}*"  # Doesn't match
```

**Debug cache issues:**
```bash
# Check actual keys in Redis
docker exec ai-studio-redis redis-cli KEYS "cache:*"
```

**Symptoms:**
- Save succeeds but refresh shows old data
- Clearing field doesn't persist

### 5. Frontend Not Using Server Response

**Problem**: UI updates with local state instead of server response.

```javascript
// ❌ Wrong - uses local state
const response = await api.save(entity, editedData)
setEntity({ ...entity, data: editedData })  // Local state!

// ✅ Correct - uses server response
const response = await api.save(entity, editedData)
setEntity({ ...entity, data: response })  // Server is source of truth
```

**Why**: Server may transform data, add computed fields, validate.

### 6. Conflicting Prompt Details

**Problem**: Entity specs conflict with custom visualization styles.

```python
# Expression spec: "vibrant red lipstick, dark eyeliner"
# User instruction: "NO COLOR, black ink manga style"
# → Model receives conflicting instructions

# ✅ Solution: Simplify when custom viz exists
if has_reference and additional_instructions:
    subject_description = self._extract_simplified_description(spec)

# Put user instructions FIRST (highest priority)
prompt = f"""
🎨 CRITICAL REQUIREMENTS (HIGHEST PRIORITY):
{user_instructions}

📋 SUBJECT TO PORTRAY:
{simplified_subject_description}

IMPORTANT: CRITICAL REQUIREMENTS override any styling details.
"""
```

---

## Critical System Knowledge

### Gemini Image Generation

```yaml
# ✅ Correct model names
gemini/gemini-2.5-flash-image    # Image generation (dedicated model)
gemini/gemini-2.0-flash-exp      # Text/analysis (multimodal)

# ❌ Wrong
gemini/gemini-2.5-flash-latest   # No image generation
gemini-2.5-flash-image           # Missing prefix
```

**How routing works:**
1. LiteLLM expects: `gemini/model-name` (with prefix)
2. `ai_tools/shared/router.py` strips prefix before calling API
3. Gemini API receives: `model-name` (no prefix)

**Image generation requirements** (router.py:458-663):
- Header auth (NOT query param)
- `responseModalities: ["image"]` (required)

### AI Tool Creation Checklist

**Every AI tool MUST have:**
1. ✅ `ai_tools/{tool_name}/{tool.py,template.md,README.md}`
2. ✅ Add to `configs/models.yaml` defaults
3. ✅ Add route to `frontend/src/App.jsx`
4. ✅ Add sidebar link to `Sidebar.jsx`
5. ✅ Add test UI to `ToolConfigPage.jsx`
6. ✅ Rebuild API + frontend

See `ai_tools/README_TOOL_DEVELOPMENT.md` for details.

---

## Quick Commands

```bash
# Start/stop
docker-compose up -d
docker-compose down

# Logs
docker logs ai-studio-api --tail 50
docker logs ai-studio-frontend --tail 50
docker logs life-os-rq-worker-1 --tail 20

# Database
docker exec ai-studio-postgres psql -U lifeos -d lifeos
docker exec ai-studio-postgres psql -U lifeos -d lifeos -c "\dt"

# Redis
docker exec -it ai-studio-redis redis-cli
KEYS "cache:*"

# Tests
docker-compose run --rm api pytest tests/unit/ -v
```

---

## Red Flags (Sloppy Work Indicators)

- 🚩 Asking user to test without checking logs first
- 🚩 Editing a file that isn't actually being used (check imports!)
- 🚩 Forgetting to rebuild RQ workers after API changes
- 🚩 Creating workflow-specific code instead of reusable tools
- 🚩 Not committing for multiple work sessions
- 🚩 Using print() instead of logger

---

## When Stuck

1. Check logs: `docker logs ai-studio-api --tail 100`
2. Check ROADMAP.md for known issues
3. Check docs/guides/design-patterns.md for established patterns
4. Check FastAPI docs: http://localhost:8000/docs
5. Ask user for clarification

---

**Remember**: Life-OS is a multi-domain platform. Consider extensibility in all changes. See ROADMAP.md for current priorities.
