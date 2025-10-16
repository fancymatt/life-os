# Life-OS - Claude AI Assistant Context

**Last Updated**: 2025-10-15
**Current Sprint**: Sprint 4 (Performance & Architecture Foundations)

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
1. **OPTIMIZATION_ROADMAP.md** - Complete 4-phase development plan with current status
2. **SPRINT_3.md** - Recently completed features (reference for patterns)
3. **README.md** - Setup instructions and feature overview
4. **API_ARCHITECTURE.md** - Backend architecture details

### For Understanding the Codebase
1. **Directory Structure** (see below)
2. **Key Technologies** (see below)
3. **Current Blockers & Progress** (see OPTIMIZATION_ROADMAP.md)

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
- **LLM Routing**: LiteLLM (multi-provider support: Gemini, OpenAI, Claude)
- **Job Queue**: Redis (with in-memory fallback)
- **Authentication**: JWT (python-jose)
- **File I/O**: aiofiles (async file operations)
- **Image Processing**: Pillow

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

### Active Work (Week 1-2, Sprint 4)
1. **Story Generation Workflow Prototype** 🚧 IN PROGRESS
   - Multi-agent workflow: Story Planner → Story Writer → Image Illustrator
   - Tests workflow orchestration architecture
   - Validates Phase 2 extensibility needs

2. **Performance Quick Wins**
   - ✅ Async file I/O (routes completed)
   - ✅ Cache-Control headers for static files
   - 🔴 BLOCKED: GZIP compression (import issue)
   - 📋 TODO: React optimizations (useMemo/useCallback)
   - 📋 TODO: Batch preset loading endpoint

### Known Issues & Blockers

**🔴 Critical Blockers**:
- **GZIP Compression**: `ImportError: cannot import name 'GZIPMiddleware'`
  - Current FastAPI/Starlette version compatibility issue
  - Needs research for correct import path
  - Impact: Would reduce bandwidth by 60-80%

**⚠️ Technical Debt**:
- **Code Duplication**: OutfitAnalyzer.jsx and GenericAnalyzer.jsx are 85% identical (~500 duplicate lines)
- **Large Components**: Composer.jsx (855 lines), OutfitAnalyzer.jsx (702 lines) need refactoring
- **No Frontend Tests**: 0% test coverage for React components
- **Synchronous File I/O**: Still present in api/services/*.py files

**📊 Performance Opportunities**:
- Sequential preset loading (8 API calls on page load → should be 1)
- No React memoization (causes unnecessary re-renders)
- No search debouncing (triggers on every keystroke)
- No request batching or rate limiting

---

## Coding Standards & Patterns

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
# Redis (job queue)
docker exec -it ai-studio-redis redis-cli

# Data files
ls data/users.json              # User accounts
ls data/favorites/              # User favorites (per user)
ls data/compositions/           # Saved compositions (per user)
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

## Future Architecture (Phases 2-4)

### Phase 2: Extensibility (4-5 weeks)
**Goal**: Plugin architecture for domain expansion

**New Components**:
- `api/core/plugin_interface.py` - Base plugin class
- `api/core/plugin_manager.py` - Plugin discovery & lifecycle
- `api/core/workflow_engine.py` - Multi-step workflow orchestration
- `api/core/context_manager.py` - Cross-domain memory & preferences
- `api/core/providers/` - Provider abstraction (local LLMs, ComfyUI, MCP)
- `plugins/` - Domain-specific plugins

**Example Plugin Structure**:
```
plugins/image_generation/
├── plugin.py           # BasePlugin implementation
├── config.yaml         # Plugin configuration
└── README.md          # Plugin documentation
```

### Phase 3: Agent Framework (3-4 weeks)
**Goal**: Autonomous agents with safety

**New Components**:
- `api/core/agents/` - Agent implementations
- `api/core/task_planner.py` - Goal decomposition
- `api/core/permission_manager.py` - Safety & permissions
- `api/core/learning_system.py` - Preference learning

### Phase 4: Domain Expansion (12-15 weeks)
**Goal**: Add new domains

**New Plugins**:
- `plugins/video_generation/` - Sora integration
- `plugins/code_management/` - Claude Code integration
- `plugins/home_automation/` - Home Assistant integration
- `plugins/life_planning/` - Calendar, tasks, habits
- `plugins/educational_content/` - Video scripts, lessons
- `plugins/board_game_tools/` - Game analysis, teaching guides
- `plugins/mcp_integration/` - MCP server connections

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
- `SPRINT_3.md` - Recently completed features
- `API_QUICKSTART.md` - API usage examples
- `README.md` - High-level overview

### For Architecture
- `API_ARCHITECTURE.md` - Backend design
- `OPTIMIZATION_ROADMAP.md` - Development plan
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
1. Check `OPTIMIZATION_ROADMAP.md` for known blockers
2. Check `API_ARCHITECTURE.md` for design decisions
3. Check existing code for similar patterns
4. Ask the user for clarification

### If You Find Issues
1. Document in `OPTIMIZATION_ROADMAP.md` (Blockers section)
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

**Remember**: Life-OS is evolving into a multi-domain AI platform. Always consider how your changes will support the plugin architecture and workflow orchestration planned for Phase 2.

**Current Priority**: Build story generation workflow to validate architectural needs, then continue Phase 1 optimizations.
