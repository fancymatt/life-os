# lifeOS v2.5.1 (110) - Claude AI Assistant Context

**Last Updated**: 2025-10-23
**Current Phase**: Phase 2 - User Experience & Core Features (see ROADMAP.md)

---

## Versioning Rules

**Format**: `vMajor.Minor.Patch (Build)` (e.g., v2.5.1 (100))

**Version Components**:
- **Major**: Phase number (e.g., 2 for Phase 2)
- **Minor**: Section within phase (e.g., 2.5 for Phase 2.5 Tagging System)
- **Patch**: Increments with significant updates (features, major fixes)
- **Build**: Increments with EVERY commit/push (tracks all changes)

**Versioning Rules**:
1. **On Phase Section Completion**: Version becomes `vPhase.Section.0 (Build+1)`
   - Example: Complete Phase 2.6 → version becomes `v2.6.0 (105)`
   - Build number always increments

2. **On Significant Update**: Patch version increments, build increments
   - Example: Major bug fix → `v2.5.1 (100)` → `v2.5.2 (101)`
   - Significant: Features, major fixes, important refactors

3. **On Any Commit**: Build number increments (even if version stays same)
   - Example: Documentation update → `v2.5.1 (100)` → `v2.5.1 (101)`
   - Minor fixes, docs, config changes
   - Build tracks ALL changes

4. **During Development**: Version stays at `vX.Y.0` until feature complete
   - Example: Working on Phase 2.6 → version is `v2.6.0` but build increments
   - Each commit: `v2.6.0 (102)`, `v2.6.0 (103)`, etc.
   - Once complete and pushed → becomes `v2.6.0 (final_build)`

**Current Version**: v2.5.1 (110)
- Phase: 2.5 (Tagging System) - IN DEVELOPMENT
- Build 110: Create tag API routes and Pydantic models

**Version History**:
- v2.5.1 (110) - Create tag API routes (11 endpoints) and Pydantic request/response models
- v2.5.1 (109) - Fix version downgrade error, commit TagService for tag business logic
- v2.5.1 (108) - Create TagRepository for tag database operations
- v2.5.1 (107) - Create Alembic migration for tags and entity_tags tables
- v2.5.1 (106) - Run Alembic migration to create tags tables
- v2.5.1 (105) - Add Tag and EntityTag SQLAlchemy models
- v2.5.1 (104) - Start Phase 2.5 Tagging System implementation
- v2.5.1 (103) - Made version number smaller in UI header
- v2.5.1 (102) - Version number moved to document headers
- v2.5.1 (101) - Build number tracking added to versioning system
- v2.5.1 (100) - Add versioning system with build numbers
- v2.5.0 - Phase 2.4 (UI Theme System) complete
- v2.4.0 - Phase 2.3 (Database Persistence) complete
- v2.3.0 - Phase 2.2 (Mobile Responsiveness) complete
- v2.2.0 - Phase 2.1 (Complete Archive System) complete

---

## Quick Start for AI Assistants

If you're Claude Code or another AI assistant working on this project, here's what you need to know:

### What is Life-OS?

Life-OS is evolving from a specialized **AI image generation platform** into a **comprehensive personal AI assistant** capable of autonomous task execution across multiple domains (video, code, home automation, life planning, etc.).

**Current State** (Sprint 3 Complete):
- 8 image analyzers (outfit, style, hair, makeup, expression, accessories, etc.)
- 6 image generators (modular, style transfer, art style, etc.)
- Preset composition system with drag-and-drop UI
- Mobile-responsive interface
- Job queue with real-time progress tracking
- Favorites and composition management

**Vision** (12-18 months):
- Multi-domain AI platform (video, board games, education, code, home automation)
- Autonomous agents that proactively suggest and execute tasks
- Workflow orchestration (chain multiple AI operations)
- Safe execution with permission system
- Cross-domain context and memory

---

## Essential Documentation

### For Development Work
1. **ROADMAP.md** - Complete 6-phase development plan with priorities
2. **DESIGN_PATTERNS.md** - Best practices guide using Character + Appearance Analyzer as gold standard
3. **README.md** - Setup instructions and feature overview
4. **API_ARCHITECTURE.md** - Backend architecture details

### For Understanding the Codebase
1. **Directory Structure** (see below)
2. **Key Technologies** (see below)
3. **Current Phase & Priorities** (see ROADMAP.md)

---

## Project Structure

```
life-os/
├── api/                          # FastAPI backend (Python 3.9)
│   ├── routes/                   # API endpoints
│   │   ├── analyzers.py         # Image analysis endpoints
│   │   ├── generators.py        # Image generation endpoints
│   │   ├── presets.py           # Preset CRUD
│   │   ├── jobs.py              # Job queue & progress
│   │   ├── auth.py              # JWT authentication
│   │   ├── favorites.py         # User favorites
│   │   └── compositions.py      # Saved preset combinations
│   ├── services/                # Business logic layer
│   │   ├── analyzer_service.py  # Wraps AI analyzers
│   │   ├── generator_service.py # Wraps AI generators
│   │   ├── preset_service.py    # Preset management
│   │   ├── job_queue.py         # Background job management
│   │   └── auth_service.py      # User authentication
│   ├── models/                  # Pydantic schemas
│   ├── dependencies/            # FastAPI dependencies
│   └── main.py                  # Application entry point
│
├── ai_tools/                    # AI tool implementations
│   ├── shared/                  # Shared utilities
│   │   ├── router.py           # LLM router (LiteLLM wrapper) - 964 lines, COMPLEX
│   │   ├── preset.py           # Preset file I/O - 533 lines
│   │   ├── cache.py            # File-based caching - 486 lines
│   │   └── visualizer.py       # Preview image generation - 432 lines
│   ├── outfit_analyzer/        # Example analyzer tool
│   ├── modular_image_generator/ # Main image generator - 602 lines, COMPLEX
│   └── [21 other tools]/       # Analyzers and generators
│
├── frontend/                    # React + Vite (Node 18)
│   ├── src/
│   │   ├── Composer.jsx        # Main preset composition UI - 855 lines, NEEDS REFACTORING
│   │   ├── OutfitAnalyzer.jsx  # Outfit analysis UI - 702 lines
│   │   ├── GenericAnalyzer.jsx # Generic analyzer UI - 580 lines (85% duplicate with OutfitAnalyzer)
│   │   ├── ModularGenerator.jsx # Multi-preset generator - 377 lines
│   │   ├── TaskManager.jsx     # Job progress tracking - 336 lines
│   │   ├── Gallery.jsx         # Image gallery - 195 lines
│   │   └── App.jsx             # Main router - 190 lines
│   └── nginx.conf              # Nginx config for production

├── workflows/                   # 🚧 NEW - Multi-step AI workflows (to be built)
├── plugins/                     # 🚧 NEW - Domain plugins (to be built)
├── configs/                     # Configuration files
│   └── models.yaml             # LLM model configuration
├── presets/                     # User-created presets (8 categories)
├── output/                      # Generated images
├── subjects/                    # Subject images for composition
├── data/                        # Persistent data (users, favorites, compositions)
└── docker-compose.yml          # Multi-container orchestration
```

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+ (async Python web framework)
- **Database**: PostgreSQL 15 with asyncpg (SQLAlchemy 2.0 async ORM)
- **LLM Routing**: LiteLLM (multi-provider support: Gemini, OpenAI, Claude)
- **Job Queue**: Redis (with in-memory fallback)
- **Authentication**: JWT (python-jose)
- **File I/O**: aiofiles (async file operations)
- **Image Processing**: Pillow

### 🚨 CRITICAL: Database Architecture

**WE USE POSTGRESQL, NOT JSON FILES OR SQLITE**

```
┌─────────────────────────────────────────────────────────┐
│ ACTIVE DATABASE: PostgreSQL                            │
│ - Host: ai-studio-postgres (Docker container)          │
│ - Database: lifeos                                      │
│ - User: lifeos                                          │
│ - Connection: postgresql+asyncpg://lifeos:password@... │
│ - Tables: characters, clothing_items, outfits, stories │
│           images, users, favorites, etc.                │
└─────────────────────────────────────────────────────────┘
```

**How to Query the Database:**
```bash
# ✅ CORRECT - Query PostgreSQL
docker exec ai-studio-postgres psql -U lifeos -d lifeos -c "SELECT COUNT(*) FROM clothing_items;"

# ✅ CORRECT - Query via Python
docker exec ai-studio-api python3 -c "
import asyncio
from api.database import get_session
from sqlalchemy import text

async def count_items():
    async with get_session() as db:
        result = await db.execute(text('SELECT COUNT(*) FROM clothing_items'))
        print(result.scalar())

asyncio.run(count_items())
"

# ❌ WRONG - Don't query SQLite (doesn't exist)
# ❌ WRONG - Don't read JSON files (old/deprecated data)
```

**Where Data is Stored:**
- **Database records**: PostgreSQL tables (characters, clothing_items, etc.)
- **Generated images**: `output/` directory (PNG files)
- **Uploaded images**: `uploads/` directory
- **Presets**: `presets/` directory (JSON files - still used for presets only)
- **Cache**: `cache/` directory (temporary analysis results)

**Old JSON files in `data/` are DEPRECATED:**
- `data/characters/*.json` - OLD (now in PostgreSQL `characters` table)
- `data/clothing_items/*.json` - OLD (now in PostgreSQL `clothing_items` table)
- These files are no longer used and have been deleted to prevent confusion

### Frontend
- **Framework**: React 18.2
- **Build Tool**: Vite 5.0
- **State Management**: Context API (AuthContext), useState/useReducer
- **HTTP Client**: Axios with JWT interceptors
- **Styling**: Vanilla CSS (component-scoped)
- **Server**: Nginx (production)

### Infrastructure
- **Containerization**: Docker Compose (Redis, API, Frontend)
- **Python Version**: 3.9-slim
- **Node Version**: 18-alpine

### AI Providers
- **Gemini 2.0/2.5 Flash**: Primary (image analysis & generation)
- **OpenAI DALL-E 3**: Image generation
- **OpenAI Sora**: Video generation (planned)
- **Local LLMs**: Planned (Ollama integration)
- **ComfyUI**: Planned (custom workflows)

---

## Current Development Focus

### Phase 1: Foundation & Critical Fixes (4-6 weeks)

**See ROADMAP.md for complete details**

**Priority 1: Database Migration** (2-3 weeks)
- Migrate from JSON files to PostgreSQL
- Add Alembic for migrations
- Update service layer to async ORM

**Priority 2: Performance Optimizations** (1-2 weeks)
- Backend pagination for all list endpoints
- Redis-based response caching
- Virtual scrolling for large entity lists

**Priority 3: Code Quality** (1 week)
- Structured logging infrastructure
- Standardized error handling
- Component refactoring (Composer.jsx, unify analyzers)

### Known Issues

**See ROADMAP.md Phase 1 for complete list**

**Critical**:
- JSON file storage doesn't scale (Phase 1.1 - Database Migration)
- No pagination causes slow loads with 200+ entities (Phase 1.2)
- 10 failing smoke tests need auth fixtures (Phase 1.4)

**Technical Debt**:
- Component duplication: OutfitAnalyzer + GenericAnalyzer (~500 lines)
- Large components: Composer.jsx (910 lines) needs splitting
- Zero frontend tests (Phase 1.4)

**Performance**:
- No response caching (Phase 1.2)
- No virtual scrolling for large lists (Phase 1.2)
- No search debouncing

---

## Coding Standards & Patterns

### 🚨 CRITICAL: Logging Standards (NEVER USE print())

**MANDATORY**: This codebase uses structured logging. **NEVER** add `print()` statements.

We have cleaned up print statements MULTIPLE times. Do not reintroduce them.

#### ✅ CORRECT - Use structured logging:
```python
from api.logging_config import get_logger

logger = get_logger(__name__)

# Success/Info messages
logger.info(f"Created character: {character_id}")
logger.info(f"Processing {count} items", extra={'extra_fields': {'count': count}})

# Warnings
logger.warning(f"Failed to load config: {error}")
logger.warning("API rate limit approaching")

# Errors
logger.error(f"Database connection failed: {error}")
logger.error("Image generation timed out", extra={'extra_fields': {'timeout': 30}})
```

#### ❌ WRONG - Never use print():
```python
# ❌ NEVER DO THIS
print("Created character")
print(f"Processing {count} items")
print(f"Error: {error}")
```

#### Why This Matters:
- **Structured logs** → Searchable JSON with timestamps, request IDs, and context
- **print() statements** → Unstructured text that's hard to search and analyze
- **Production debugging** → Logs go to files and aggregation systems, not stdout
- **Performance** → print() can block I/O and slow down async operations

#### If You Need to Debug:
```python
# ✅ Use logger.debug for temporary debugging
logger.debug(f"Variable value: {variable}")

# ✅ Use logging context for structured data
logger.info("Task completed", extra={'extra_fields': {
    'duration_ms': duration,
    'item_count': len(items),
    'status': 'success'
}})
```

#### Enforcement:
- A pre-commit hook will be added to reject any new `print()` statements
- Use `scripts/replace_print_with_logging.py` if you accidentally add prints
- Code reviews will flag any print() statements

---

### Backend Patterns
```python
# Use async file I/O
import aiofiles
async with aiofiles.open(file_path, 'w') as f:
    await f.write(json.dumps(data, indent=2))

# Route pattern with error handling
@router.post("/endpoint")
async def endpoint_name(
    request: RequestModel,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Endpoint description

    Args:
        request: Request description
    """
    try:
        # Business logic via service layer
        result = service.method(request)
        return ResponseModel(status="completed", result=result)
    except Exception as e:
        return ResponseModel(status="failed", error=str(e))
```

### Frontend Patterns
```jsx
// Component structure
function ComponentName() {
  // State hooks
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  // Custom hooks
  const { user } = useAuth()

  // Effects
  useEffect(() => {
    fetchData()
  }, [dependency])

  // Event handlers
  const handleAction = useCallback(async () => {
    // Implementation
  }, [dependencies])

  // Render
  return (
    <div className="component-name">
      {/* JSX */}
    </div>
  )
}
```

### File Organization
- **Backend**: Service layer handles business logic, routes handle HTTP concerns
- **Frontend**: Component-scoped CSS, one component per file
- **Presets**: JSON files in `/presets/{category}/{preset_id}.json`
- **Data**: Per-user directories in `/data/{type}/{username}/`

---

## API Conventions & Critical Patterns

### FastAPI Trailing Slash Requirements ⚠️

**CRITICAL**: FastAPI is strict about trailing slashes. This has caused multiple bugs. Follow these rules:

#### Backend Route Definitions
```python
# ✅ CORRECT - Be consistent with trailing slashes
@router.get("/characters/", response_model=CharacterListResponse)
@router.post("/characters/", response_model=CharacterInfo)
@router.get("/presets/{category}/", response_model=PresetList)

# Also valid - just be consistent
@router.post("/from-subject", response_model=Response)  # No slash
```

#### Frontend API Calls
```javascript
// ✅ CRITICAL - Frontend calls MUST exactly match backend route definitions

// If backend has trailing slash:
@router.get("/characters/", ...)
await api.get('/characters/')  // ✅ Must include slash

// If backend has NO trailing slash:
@router.post("/from-subject", ...)
await api.post('/characters/from-subject')  // ✅ Must NOT include slash

// ❌ WRONG - Mismatched slashes cause 307 redirects
@router.get("/characters/", ...)
await api.get('/characters')  // ❌ Missing slash

@router.post("/from-subject", ...)
await api.post('/characters/from-subject/')  // ❌ Extra slash causes POST to fail
```

#### Route Ordering (CRITICAL)
```python
# ✅ CORRECT - Specific routes BEFORE parameterized routes
@router.post("/characters/from-subject/", ...)  # Line 133
@router.get("/{character_id}", ...)             # Line 242

# ❌ WRONG - Parameterized route matches everything
@router.get("/{character_id}", ...)             # Will match "from-subject"
@router.post("/characters/from-subject/", ...)  # Never reached!
```

#### Why This Matters
- **307 Redirect**: Missing trailing slash → FastAPI redirects → Extra network round-trip
- **405 Method Not Allowed**: Route ordering issue → Wrong handler called
- **Inconsistent Behavior**: Some endpoints work, others fail mysteriously

#### Common Symptoms
- "Network Error" in frontend
- 307 redirects in API logs
- 405 Method Not Allowed errors
- "Failed to import any characters"

#### Debugging Steps
1. Check API logs: `docker logs ai-studio-api --tail 50`
2. Look for 307 Temporary Redirect or 405 Method Not Allowed
3. If 307 redirect: Check if frontend call matches backend route exactly (slash/no-slash)
4. If 405 error: Check route ordering (specific before parameterized)
5. Fix the mismatch and restart: `docker-compose restart api frontend`

---

## 🚨 Common Pitfalls & Preventative Measures

These are recurring issues that have caused debugging headaches. **Prevention is critical for maintainability.**

### Issue 1: File Path Mismatches (Container vs Host)

**Problem**: Files saved with wrong paths cause "file not found" errors.
- Config saves `/uploads/image.png` but actual path is `/app/uploads/image.png`
- Visualizer can't find reference images → falls back to different model
- No clear error message → silent failure

**Solution**: Use `api/utils/file_paths.py` utilities:
```python
from api.utils.file_paths import (
    normalize_container_path,     # Fix paths to work in container
    validate_file_exists,          # Check existence with helpful errors
    ensure_app_prefix,             # Add /app prefix for internal use
    fix_upload_path                # Quick fix for uploads
)

# ✅ CORRECT - Validate with auto-normalization
try:
    valid_path = validate_file_exists(
        user_provided_path,
        description="Reference image",
        auto_normalize=True  # Will try /app prefix if needed
    )
except FilePathError as e:
    logger.error(f"File validation failed: {e}")
    # Error includes: parent directory check, normalized path suggestion,
    # similar files in directory

# ✅ CORRECT - Normalize before saving to database
reference_image_path = ensure_app_prefix(uploaded_file_path)
config = service.update_config(reference_image_path=reference_image_path)
```

**When to use**:
- Before passing file paths to image generation APIs
- When saving uploaded file paths to database/configs
- When loading reference images or subject images
- Anytime you see "file not found" errors in logs

**Error symptoms**:
- Gemini falls back to DALL-E unexpectedly
- "No reference image found" warnings in logs
- Generated images don't match reference style

---

### Issue 2: Cache Invalidation Pattern Bugs

**Problem**: Cache keys don't match invalidation patterns.
- Pattern: `cache:/api/visualization-configs/*`
- Actual keys: `cache:/visualization-configs/abc123`
- Mismatch → caches never cleared → stale data persists

**Solution**: Pattern must match actual cache key structure:
```python
# ✅ CORRECT - Pattern matches actual keys
# Actual key: cache:/visualization-configs/abc123
# Pattern: cache:/visualization-configs*
pattern = f"{self.prefix}/{endpoint_path}*"  # NO /api/ prefix

# ❌ WRONG - Pattern doesn't match
pattern = f"{self.prefix}/api/{endpoint_path}*"  # Has /api/ prefix
```

**Verification**:
```python
# In cache_service.py - Add logging to see actual patterns
logger.info(f"Invalidating pattern: {pattern}")
await self.delete_pattern(pattern)

# Check Redis to see actual keys
docker exec ai-studio-redis redis-cli KEYS "cache:*"
```

**When cache seems broken**:
1. Check logs for "Invalidating pattern" messages
2. Check Redis for actual key format: `docker exec ai-studio-redis redis-cli KEYS "cache:*"`
3. Verify pattern in `cache_service.py` matches actual keys
4. Test invalidation manually: `await cache_service.invalidate_entity_type("entity_type")`

**Error symptoms**:
- Save succeeds but refresh shows old data
- Clearing field doesn't persist after page reload
- Cache hits show stale data in logs

---

### Issue 3: Frontend Not Using Server Response

**Problem**: Frontend updates UI with local state instead of server response.
```javascript
// ❌ WRONG - Uses local editedData
const response = await api.save(entity, editedData)
setEntity({ ...entity, data: editedData })  // Local state!

// ✅ CORRECT - Uses server response
const response = await api.save(entity, editedData)
setEntity({ ...entity, data: response })  // Server response!
```

**Why this matters**:
- Server may transform data (validation, normalization)
- Server may add computed fields
- Server is source of truth, not frontend

**Solution**: Always use API response as source of truth:
```javascript
// EntityBrowser.jsx handleSave pattern
const response = await config.saveEntity(selectedEntity, {
  data: editedData,
  title: editedTitle
})

// CRITICAL: Use response from server
const savedData = response
const savedTitle = response.display_name || response.title || editedTitle

// Update UI with server data
setEditedData(JSON.parse(JSON.stringify(savedData)))
setEditedTitle(savedTitle)
```

**Error symptoms**:
- Save shows success but data doesn't update
- Refresh shows different data than what was displayed
- Setting values works but clearing doesn't

---

### Issue 4: Conflicting Prompt Details

**Problem**: Entity specs contain detailed descriptions that conflict with custom visualization styles.
- Expression spec: "vibrant red lipstick", "dark eyeliner"
- User instruction: "NO COLOR, black ink manga style"
- Model receives conflicting instructions → ignores user preference

**Solution**: Simplify descriptions when custom viz config exists:
```python
# ✅ CORRECT - Detect conflict and simplify
if has_reference and additional_instructions and spec_type == "expressions":
    # Use simplified description that focuses on structure, not styling
    subject_description = self._extract_simplified_expression_description(spec)
else:
    # Use full description with all details
    subject_description = self._extract_subject_description(spec_type, spec)
```

**Prompt structure priority**:
```python
# Put user instructions FIRST (highest priority)
prompt = f"""
🎨 CRITICAL REQUIREMENTS (HIGHEST PRIORITY):
{user_instructions}

📋 SUBJECT/EXPRESSION TO PORTRAY:
{simplified_subject_description}

IMPORTANT: CRITICAL REQUIREMENTS override any styling details in subject description.
"""
```

**When to use**:
- Custom visualization configs with reference images
- User provides specific style instructions (manga, sketch, 3D render)
- Any case where spec details might conflict with desired output style

**Error symptoms**:
- Generated image has colors when user said "NO COLOR"
- Style doesn't match reference image
- User instructions seem ignored

---

### Prevention Strategies

**1. Add Validation at Boundaries**
```python
# At API entry points
@router.post("/upload")
async def upload_file(file: UploadFile):
    file_path = await save_upload(file)
    # ✅ Normalize before saving
    normalized_path = ensure_app_prefix(file_path)
    config.update(reference_image_path=normalized_path)
```

**2. Add Helpful Error Messages**
```python
# ✅ CORRECT - Detailed error with suggestions
try:
    validate_file_exists(path, "Reference image")
except FilePathError as e:
    logger.error(f"Validation failed: {e}")
    # Error includes: normalized path suggestion, similar files, parent dir check
```

**3. Add Tests for Common Issues**
```python
# tests/test_file_paths.py
def test_normalize_upload_path():
    assert normalize_container_path("/uploads/img.png") == Path("/app/uploads/img.png")

# tests/test_cache_invalidation.py
async def test_invalidate_pattern_matches_keys():
    await cache.set("/viz-configs/abc", "data")
    await cache.invalidate_entity_type("viz_configs")
    assert await cache.get("/viz-configs/abc") is None
```

**4. Document in Code**
```python
# ✅ Add docstrings explaining WHY
def normalize_container_path(path):
    """
    Normalize to /app prefix for Docker container.

    Common issue: Paths saved as "/uploads/file.png" but actual container
    path is "/app/uploads/file.png". This causes file-not-found errors.
    """
```

**5. Use Logging to Surface Issues Early**
```python
# Log when falling back or using workarounds
logger.warning(f"Reference image not found at {path}, falling back to DALL-E")
logger.warning(f"Cache pattern {pattern} found {count} keys to invalidate")
```

---

## Common Tasks

### Running the Application
```bash
# Start all containers
docker-compose up -d

# View logs
docker logs ai-studio-api --tail 50
docker logs ai-studio-frontend --tail 50

# Rebuild after changes
docker-compose up -d --build api       # API only
docker-compose up -d --build frontend  # Frontend only
docker-compose up -d --build          # All containers
```

### Making Changes
```bash
# Backend changes
# 1. Edit files in api/
# 2. Rebuild: docker-compose up -d --build api
# 3. Check logs: docker logs ai-studio-api

# Frontend changes
# 1. Edit files in frontend/src/
# 2. Rebuild: docker-compose up -d --build frontend
# 3. Browser auto-refreshes (Vite HMR)

# Configuration changes
# Edit configs/models.yaml for LLM routing
# Edit docker-compose.yml for container settings
```

### Testing
```bash
# Backend tests (93% passing)
docker-compose run --rm api pytest tests/unit/ -v

# Frontend tests (NOT IMPLEMENTED YET)
# TODO: Set up Vitest + React Testing Library
```

### Database Operations
```bash
# PostgreSQL (main database)
docker exec ai-studio-postgres psql -U lifeos -d lifeos

# Common queries
docker exec ai-studio-postgres psql -U lifeos -d lifeos -c "\dt"  # List tables
docker exec ai-studio-postgres psql -U lifeos -d lifeos -c "SELECT COUNT(*) FROM clothing_items;"
docker exec ai-studio-postgres psql -U lifeos -d lifeos -c "SELECT * FROM characters LIMIT 5;"

# Redis (job queue)
docker exec -it ai-studio-redis redis-cli

# Static files (NOT in database)
ls presets/                     # Preset JSON files (still file-based)
ls output/                      # Generated images
ls uploads/                     # Uploaded images
```

---

## Architecture Decisions

### Why Service Layer Pattern?
- **Separation of Concerns**: Routes handle HTTP, services handle business logic
- **Testability**: Services can be tested independently
- **Reusability**: Services used by routes and background tasks

### Why LiteLLM Router?
- **Multi-Provider**: Switch between Gemini, OpenAI, Claude without code changes
- **Cost Optimization**: Route to cheaper models when possible
- **Fallback**: Auto-fallback if primary provider fails
- **Structured Output**: Pydantic model validation

### Why Job Queue?
- **Long-Running Tasks**: Image generation can take 30+ seconds
- **Progress Tracking**: Real-time progress updates via SSE
- **Error Recovery**: Retry failed jobs
- **Background Processing**: Don't block API responses

### Why Per-User Data?
- **Multi-Tenancy**: Support multiple users
- **Privacy**: Isolate user data
- **Scalability**: Easy to shard by user

---

## Future Architecture

**See ROADMAP.md for complete 6-phase plan**

### Phase 2: Board Game Assistant (3-4 weeks)
- Rules Gatherer (BGG integration)
- Document RAG Preparer (Docling + ChromaDB)
- Document Q&A system (semantic search + citations)
- Tool configuration UI

### Phase 3: Local LLMs & Performance (2-3 weeks)
- llama-cpp-python integration
- Local model management
- Rate limiting & monitoring

### Phase 4: Extensibility & Workflows (4-6 weeks)
- Plugin architecture
- Advanced workflow engine
- Context management system

### Phase 5: Agent Framework (5-6 weeks)
- Semi-autonomous agents
- Task planning & decomposition
- Safety & permissions system

### Phase 6: Domain Expansion (Ongoing)
- Video generation (Sora)
- Code management
- Life planning
- Home automation
- Educational content
- Board games (full suite)

---

## Design Philosophy

### UI/UX Principles
- **Mobile-First**: Works on phones without sacrificing desktop UX
- **Progressive Disclosure**: Hide complexity, reveal as needed
- **Real-Time Feedback**: Show progress, don't leave users waiting
- **Undo/Redo**: Support reversible actions
- **Component Reusability**: Build once, use everywhere

### Code Principles
- **DRY** (Don't Repeat Yourself): Eliminate code duplication
- **SOLID**: Single responsibility, open/closed, etc.
- **Async by Default**: Use async/await for I/O operations
- **Type Safety**: Pydantic models for validation
- **Error Handling**: Always handle errors gracefully

### AI Principles
- **Safety First**: Permission system for autonomous actions
- **Explainability**: Show reasoning, not just results
- **Cost Awareness**: Track and optimize API costs
- **Fallback Strategies**: Always have a backup plan
- **Human-in-the-Loop**: Request approval for risky actions

---

## Important Files to Reference

### For Code Patterns
- `api/routes/compositions.py` - Clean async route with aiofiles
- `api/services/job_queue.py` - Job management patterns
- `frontend/src/Composer.jsx` - Complex React component (needs refactoring)
- `ai_tools/modular_image_generator/tool.py` - Complex AI tool implementation

### For Understanding Features
- `README.md` - High-level overview and feature documentation
- `API_QUICKSTART.md` - API usage examples
- `DESIGN_PATTERNS.md` - Development patterns and best practices

### For Architecture
- `API_ARCHITECTURE.md` - Backend design
- `ROADMAP.md` - Development plan (Phases 1-6)
- `configs/models.yaml` - LLM configuration

---

## Git Workflow

### Commit Message Format
```
<type>: <short description>

<optional detailed description>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**: feat, fix, refactor, docs, test, perf, chore

### Branch Strategy
- `main` - Production-ready code
- Feature branches for major work (optional)
- Direct commits to main for small changes (current workflow)

### When to Commit
- After completing a logical unit of work
- Before switching to a different task
- After fixing a bug
- After completing a feature
- Before making potentially breaking changes

---

## Getting Help

### If You're Stuck
1. Check `ROADMAP.md` for known issues and priorities
2. Check `API_ARCHITECTURE.md` for design decisions
3. Check `DESIGN_PATTERNS.md` for established patterns
4. Ask the user for clarification

### If You Find Issues
1. Document in comments or create GitHub issue
2. Update TODO tasks with blocker status
3. Provide workaround if possible
4. Suggest next steps

### If You Make Architectural Decisions
1. Document reasoning in code comments
2. Update relevant .md files
3. Create example usage
4. Consider future implications

---

## Quick Reference

### Environment Variables
```bash
# Required
GEMINI_API_KEY=<your-key>
OPENAI_API_KEY=<your-key>

# Optional
REQUIRE_AUTH=true                    # Enable JWT authentication
JWT_SECRET_KEY=<random-string>       # Production: use secure key
REDIS_URL=redis://redis:6379/0       # Job queue storage
```

### API Endpoints
```
# Analysis
POST /api/analyze/{analyzer_name}   # Analyze image
GET  /api/analyze/subjects           # List subject images
POST /api/analyze/upload             # Upload image

# Generation
POST /api/generate/{generator_name}  # Generate image
POST /api/generate/modular          # Modular generation (main)

# Presets
GET  /api/presets/{category}        # List presets
POST /api/presets/{category}        # Create preset
GET  /api/presets/{category}/{id}/preview  # Get preview image

# Jobs
GET  /api/jobs                      # List jobs
GET  /api/jobs/{id}                 # Get job status
GET  /api/jobs/stream               # SSE progress stream

# User
POST /api/auth/login                # Login
GET  /api/favorites                 # Get favorites
POST /api/favorites/{item_id}       # Add favorite
GET  /api/compositions              # List saved compositions
POST /api/compositions/save         # Save composition
```

### File Paths
```
/app/                               # Container root
/app/presets/{category}/{id}.json   # Preset files
/app/output/{filename}.png          # Generated images
/app/subjects/{filename}.png        # Subject images
/app/data/users.json                # User accounts
/app/data/favorites/{username}.json # User favorites
/app/data/compositions/{username}/  # User compositions
/app/cache/{category}/{hash}.json   # Cached analysis results
```

---

## Tips for AI Assistants

### When Making Changes
1. **Read before editing**: Always read files before modifying
2. **Test incrementally**: Make small changes, test, commit
3. **Update documentation**: Keep .md files current
4. **Follow patterns**: Use existing code as reference
5. **Think about scale**: Consider future plugin architecture

### When Adding Features
1. **Check roadmap**: Align with planned architecture
2. **Consider Phase 2**: Will this need to work with plugins?
3. **Think workflows**: Could this be part of a multi-step workflow?
4. **Add tests**: Write tests for new functionality
5. **Document**: Update relevant .md files

### When Refactoring
1. **Start small**: Refactor one file at a time
2. **Test continuously**: Ensure no regressions
3. **Extract patterns**: Look for reusable components
4. **Document decisions**: Explain why, not just what
5. **Update roadmap**: Mark completed refactoring tasks

### When Debugging
1. **Check logs**: `docker logs ai-studio-api --tail 100`
2. **Test endpoints**: Use FastAPI /docs for interactive testing
3. **Verify files**: Check data files exist and have correct permissions
4. **Check imports**: Verify all dependencies installed
5. **Review recent changes**: Look at git diff

---

**Remember**: Life-OS is evolving into a multi-domain AI platform. Always consider how your changes will support future extensibility.

**Current Priority**: Phase 1 Foundation - Database migration, performance optimizations, code quality improvements. See ROADMAP.md for complete plan.

---

## 🚨 CRITICAL: Mandatory Development Workflow

### Deployment Pipeline (MEMORIZE THIS)

**Backend Changes (Python/API)**:
```bash
# 1. Edit files in api/ or ai_tools/
# 2. Rebuild API container
docker-compose up -d --build api
# 3. Check logs for errors
docker logs ai-studio-api --tail 50
# 4. Changes are IMMEDIATELY live (no browser refresh needed for API)
```

**Frontend Changes (React/JavaScript)**:
```bash
# 1. Edit files in frontend/src/
# 2. Rebuild frontend container (REQUIRED - Vite builds static bundle)
docker-compose up -d --build frontend
# 3. Check build succeeded
docker logs ai-studio-frontend --tail 20
# 4. Hard refresh browser (Cmd+Shift+R) to clear cache
# 5. Verify bundle hash changed in Network tab: index-XXXXXXXX.js
```

**Config Changes (YAML/JSON)**:
```bash
# configs/models.yaml → Restart API
docker-compose restart api

# configs/agent_configs/ → Restart API (loaded at runtime)
docker-compose restart api

# frontend/vite.config.js → Rebuild frontend
docker-compose up -d --build frontend
```

**What File is Actually Being Used?**
- ALWAYS check `App.jsx` imports to see which component renders for a route
- Example: `/entities/stories` route uses `StoriesEntity.jsx`, NOT `StoriesPage.jsx`
- If unsure, grep for the component: `grep -r "ComponentName" src/`

### Critical System Knowledge (DO NOT FORGET)

#### Gemini Image Generation Models
```yaml
# ✅ CORRECT - Use these exact model names
gemini/gemini-2.5-flash-image    # Image generation (NEW dedicated model)
gemini/gemini-2.0-flash-exp      # Text/analysis (multimodal)

# ❌ WRONG - These don't exist
gemini/gemini-2.5-flash-latest   # No image generation support
gemini-2.5-flash-image           # Missing "gemini/" prefix for router
```

**How Gemini Routing Works**:
1. LiteLLM expects: `gemini/model-name` (prefix for routing)
2. `ai_tools/shared/router.py` strips the `gemini/` prefix before calling Gemini API
3. Gemini API receives: `model-name` (no prefix)

**Gemini Image Generation Requirements** (ai_tools/shared/router.py:458-663):
```python
# 1. Header-based authentication (NOT query parameter)
headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": api_key  # NOT in URL
}

# 2. responseModalities parameter (REQUIRED for image output)
"generationConfig": {
    "responseModalities": ["image"]  # Must specify image output
}

# 3. Request format
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

#### Tools/Entities/Workflows Architecture

**CRITICAL PRINCIPLE**: Tools must work standalone AND in workflows

```
┌─────────────────────────────────────────────────────────────┐
│ Entity (Data + Self-Description)                            │
│ - Defines properties (name, description, prompt_guidance)   │
│ - Stored in: data/{entity_type}/*.json                      │
│ - Examples: Characters, Visual Styles, Story Themes         │
└─────────────────────────────────────────────────────────────┘
                           ↓ used by
┌─────────────────────────────────────────────────────────────┐
│ Tool (Prompting Logic + Model Config)                       │
│ - Describes HOW to use entities in prompts                  │
│ - Configurable: model, temperature, system prompt           │
│ - Stored in: ai_tools/{tool_name}/tool.py                   │
│ - Examples: story_illustrator, outfit_analyzer              │
│ - MUST have standalone API endpoint: /api/tools/{tool}      │
└─────────────────────────────────────────────────────────────┘
                           ↓ orchestrated by
┌─────────────────────────────────────────────────────────────┐
│ Workflow (Multi-Tool Coordination)                          │
│ - Chains multiple tools together                            │
│ - Passes data between tools                                 │
│ - Uses SAME tool code as standalone endpoints               │
│ - Stored in: api/routes/workflows.py                        │
│ - Examples: Story workflow (planner→writer→illustrator)     │
└─────────────────────────────────────────────────────────────┘
```

**❌ ANTI-PATTERNS (DO NOT DO THIS)**:
1. Creating workflow-specific prompting logic that bypasses tools
2. Making a tool that only works in workflows (not standalone)
3. Duplicating prompting logic between tool and workflow
4. Creating a job system that bypasses the existing job queue

**✅ CORRECT PATTERN**:
1. Tool works perfectly standalone: `/api/tools/story-illustrator`
2. Workflow calls the same tool code with same parameters
3. Results are identical whether called standalone or in workflow
4. Refining the tool improves both standalone AND workflow results

### Mandatory Commit/Push Workflow

**WHEN TO COMMIT** (Do this automatically, don't wait for user):
- ✅ After completing a feature (working end-to-end)
- ✅ After fixing a bug (verified fixed)
- ✅ After major refactoring (tests pass)
- ✅ Before switching to a different task
- ❌ NOT after every file edit (too granular)

**COMMIT CHECKLIST**:
```bash
# 1. Check what changed
git status
git diff --stat

# 2. Stage relevant files only (don't commit data files)
git add path/to/file.py path/to/another.jsx

# 3. Commit with descriptive message
git commit -m "type: description

Details...

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 4. PUSH IMMEDIATELY (don't forget this!)
git push origin main
```

**FILES TO NEVER COMMIT**:
- `data/users.json` (user accounts - contains passwords)
- `data/characters/*_ref.png` (temporary reference images)
- `data/characters/*.json` (unless new template/example)
- `output/` (generated images)
- `cache/` (temporary cache files)
- `.env` (secrets)

### Testing Requirements

**BEFORE asking user to test**:
```bash
# 1. Backend: Check logs for errors
docker logs ai-studio-api --tail 100

# 2. Frontend: Verify build succeeded and bundle hash changed
docker logs ai-studio-frontend --tail 20
# Look for: "✓ built in XXXms" and "index-XXXXXXXX.js"

# 3. API: Test endpoint with curl or /docs
curl -X POST http://localhost:8000/api/workflows/story

# 4. Frontend: Check browser console for errors
# Open browser DevTools → Console tab

# 5. If any errors: FIX THEM FIRST before asking user
```

**Tests to Write** (Priority Order):
1. **Critical Path Tests** (story workflow, character import, image generation)
2. **API Endpoint Tests** (all /api/ routes return 200 or expected error)
3. **Frontend Component Tests** (pages render without crashing)
4. **Integration Tests** (workflow end-to-end)

**Setting Up Tests**:
```bash
# Backend (pytest)
pip install pytest pytest-asyncio httpx
pytest tests/ -v

# Frontend (Vitest)
npm install -D vitest @testing-library/react @testing-library/jest-dom
npm run test
```

### Error Rate Reduction Strategies

**1. Document learnings in code** (not just claude.md):
```python
# ✅ CORRECT - Document critical details
async def generate_image(model: str, prompt: str):
    """Generate image using Gemini 2.5 Flash Image model.

    CRITICAL:
    - Model must be 'gemini/gemini-2.5-flash-image' (with prefix)
    - Prefix is stripped before calling Gemini API (see router.py:612)
    - Must use header auth, not query param (router.py:458)
    - Must include responseModalities: ["image"] (router.py:656)
    """
    pass
```

**2. Add validation to prevent mistakes**:
```python
# ✅ Add checks for common mistakes
def validate_gemini_model(model: str):
    valid_models = [
        "gemini/gemini-2.5-flash-image",
        "gemini/gemini-2.0-flash-exp"
    ]
    if model not in valid_models:
        raise ValueError(f"Invalid model: {model}. Use {valid_models}")
```

**3. Create smoke tests** (quick checks that basics work):
```python
# tests/smoke_test.py - Run before asking user to test
def test_all_pages_load():
    """Verify all routes return 200 OK"""
    pages = ["/", "/entities/stories", "/entities/characters", "/workflows/story"]
    for page in pages:
        response = client.get(page)
        assert response.status_code == 200, f"{page} failed"
```

**4. Use the TODO tool** to track progress:
- Always use TodoWrite when working on multi-step tasks
- Mark tasks in_progress BEFORE starting work
- Mark completed IMMEDIATELY after finishing
- One task in_progress at a time

---

## Summary: Required Development Discipline

**Every work session MUST include**:
1. ✅ Clear understanding of deployment pipeline for changes
2. ✅ Testing changes locally before asking user
3. ✅ Committing logical units of work
4. ✅ Pushing commits to remote immediately
5. ✅ Following tools/entities/workflows architecture
6. ✅ Documenting critical learnings in code comments
7. ✅ Using TodoWrite for multi-step tasks

**Red Flags That Indicate Sloppy Work**:
- 🚩 Asking user "can you test this?" without checking logs first
- 🚩 Editing a file that isn't actually being used (check imports!)
- 🚩 Forgetting model names you've used multiple times
- 🚩 Creating workflow-specific code instead of reusable tools
- 🚩 Not committing for multiple work sessions
- 🚩 Restarting services randomly hoping it fixes things
