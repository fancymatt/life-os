# Life-OS Optimization & Expansion Roadmap

**Vision**: Transform Life-OS from a specialized image generation platform into a comprehensive personal AI assistant capable of autonomous task execution across multiple domains.

**Timeline**: 4 phases over 6-8 months
**Total Effort**: ~600-800 hours
**Priority**: Foundation → Extensibility → Agent Framework → Domain Expansion

**Last Updated**: 2025-10-15
**Current Phase**: Phase 1 (Week 1 - Quick Wins) + Story Workflow Prototype ⏳
**Overall Progress**: 8/100+ tasks completed (~8%)

---

## Current Status & Recent Progress

### ✅ Completed (2025-10-15)

**Phase 1 Quick Wins**:
- **Cache-Control Headers** - Static files now cached (1hr for images, 30min for uploads)
- **Async File I/O** - Replaced synchronous file operations with aiofiles in routes
  - `api/routes/compositions.py` (3 operations)
  - `api/routes/analyzers.py` (3 operations)
- **API Performance**: ~20-35% improvement from file I/O and caching optimizations

**Story Workflow Prototype** (Completed in 1 session!):
- ✅ **Workflow Engine** - Simple sequential workflow executor
- ✅ **Agent Base Class** - Interface for all workflow agents
- ✅ **Story Planner Agent** - Generates structured outlines with scenes
- ✅ **Story Writer Agent** - Writes full narrative with prose styles
- ✅ **Story Illustrator Agent** - Generates scene illustrations
- ✅ **API Endpoints** - REST API for workflow execution
- ✅ **Design Documentation** - Complete architecture documented

**Key Files Added**:
- `api/core/simple_workflow.py` - Workflow orchestration
- `api/core/simple_agent.py` - Agent interface
- `api/agents/` - Story generation agents (3 agents)
- `api/routes/workflows.py` - Workflow API endpoints
- `workflows/STORY_WORKFLOW_DESIGN.md` - Architecture documentation

### 🚧 In Progress
- Testing story workflow end-to-end
- Documenting learnings for Phase 2 architecture

### 🔴 Blocked
- **GZIP Compression** - Import issue with FastAPI/Starlette version
  - **Issue**: `ImportError: cannot import name 'GZIPMiddleware'`
  - **Action Required**: Research correct import for current FastAPI version
  - **Impact**: Would provide 60-80% bandwidth reduction
  - **Priority**: Medium (will revisit after workflow prototype)

### 📋 Next Up
1. Build story workflow prototype (validates architecture)
2. Frontend React optimizations (useMemo/useCallback)
3. Batch preset loading endpoint (8x faster load)
4. Parallel generation with asyncio.gather (3-4x faster batches)

---

## Platform Vision & Expansion Goals

### Current State (Sprint 3)
- Image analysis & generation (8 analyzers, 6 generators)
- Preset composition with mobile UI
- Job queue with real-time tracking
- Multi-provider LLM routing (Gemini, OpenAI, Claude)

### Target State (12-18 months)

**Domain Expansion**:
1. **Video Generation** (Sora) - Apply presets to video subjects
2. **Board Game Analysis** - Teaching guides, rule references
3. **Educational Content** - Video script generation
4. **Code Management** - Integration with Claude Code, autonomous refactoring
5. **Life Planning** - Calendar, tasks, productivity automation
6. **Home Automation** - Home Assistant integration
7. **World Interaction** - MCP servers, real-time information

**Architectural Requirements**:
- **Modularity**: Plug-and-play domain modules
- **Extensibility**: Add new tools without modifying core
- **Orchestration**: Chain multiple AI operations into workflows
- **Autonomy**: Semi-autonomous agents that proactively suggest/execute tasks
- **Security**: Granular permissions for real-world actions (home control, code execution)
- **Performance**: Handle 10+ concurrent multi-step workflows
- **Context**: Persistent cross-domain memory and preferences

---

## Phase 1: Critical Foundations (Sprint 4)
**Duration**: 3-4 weeks
**Effort**: 100-120 hours
**Goal**: Fix critical issues, establish performance baseline, enable safe refactoring

### Week 1: Performance Quick Wins (15-20 hours)

#### PF-1: Backend Response Optimization
**Priority**: 🔴 Critical
**Effort**: 4-6 hours
**Impact**: 60-80% bandwidth reduction, 25-50% faster file I/O

**Tasks**:
- [🔴 BLOCKED] Add GZIPMiddleware to FastAPI (api/main.py)
  - **Blocker**: ImportError with current FastAPI/Starlette version
  - **Will revisit**: After researching correct import path
- [✅ DONE] Replace synchronous file I/O with aiofiles
  - Files: ✅ api/routes/compositions.py, ✅ api/routes/analyzers.py
  - Remaining: api/services/preset_service.py, api/services/favorites_service.py
- [✅ DONE] Add Cache-Control headers to static files
  - Implemented custom `CachedStaticFiles` class with configurable max-age
  - Output: 3600s, Uploads: 1800s, Subjects: 3600s
- [ ] Implement parallel generation with asyncio.gather()
  - File: api/routes/generators.py:108-157
  - Replace sequential loop with `await asyncio.gather(*tasks)`

**Success Metrics**:
- API response size reduced by 60-80%
- File write operations don't block event loop
- Batch generation 3-4x faster

---

#### PF-2: Frontend React Optimization
**Priority**: 🔴 Critical
**Effort**: 8-10 hours
**Impact**: 15-30% render performance, 20-40% fewer API calls

**Tasks**:
- [ ] Add useMemo/useCallback to Composer.jsx
  ```jsx
  // Lines 175-238: Memoize generateImage function
  const generateImage = useCallback(async (presetsToApply) => {
    // ... implementation
  }, [subject, appliedPresets, generationHistory])

  // Lines 284-298: Memoize addPreset
  const addPreset = useCallback(async (preset) => {
    // ... implementation
  }, [appliedPresets, subject, mobileTab])

  // Lines 558-570: Memoize filteredPresets
  const filteredPresets = useMemo(() => {
    return presets[activeCategory]?.filter(p =>
      p.display_name?.toLowerCase().includes(searchQuery.toLowerCase())
    ) || []
  }, [presets, activeCategory, searchQuery])
  ```

- [ ] Create debouncing utility hook
  ```jsx
  // frontend/src/hooks/useDebounce.js
  export function useDebounce(value, delay = 300) {
    const [debouncedValue, setDebouncedValue] = useState(value)
    useEffect(() => {
      const timer = setTimeout(() => setDebouncedValue(value), delay)
      return () => clearTimeout(timer)
    }, [value, delay])
    return debouncedValue
  }
  ```

- [ ] Apply debouncing to search inputs
  - File: frontend/src/Composer.jsx:501
  - File: frontend/src/OutfitAnalyzer.jsx (search functionality)
  - File: frontend/src/GenericAnalyzer.jsx (search functionality)

- [ ] Implement LRU cache for generation history
  ```jsx
  // Limit to 50 most recent items
  const MAX_HISTORY = 50
  const addToHistory = useCallback((item) => {
    setGenerationHistory(prev => {
      const updated = [item, ...prev.filter(h => h.cacheKey !== item.cacheKey)]
      return updated.slice(0, MAX_HISTORY)
    })
  }, [])
  ```

**Success Metrics**:
- React DevTools Profiler shows 15-30% fewer renders
- Search input triggers API calls only after 300ms pause
- Memory usage stable during long sessions

---

#### PF-3: API Optimization
**Priority**: 🟠 High
**Effort**: 3-4 hours
**Impact**: 8x faster initial load

**Tasks**:
- [ ] Create batch preset loading endpoint
  ```python
  # api/routes/presets.py
  @router.get("/batch", response_model=Dict[str, List[PresetMetadata]])
  async def get_all_presets():
      """Get all presets across all categories in single request"""
      preset_service = PresetService()
      result = {}
      for category in preset_service.get_categories():
          result[category] = preset_service.list_presets(category)
      return result
  ```

- [ ] Update Composer.jsx to use batch endpoint
  ```jsx
  // Replace lines 44-61 (8 sequential calls)
  const fetchAllPresets = async () => {
    const response = await api.get('/presets/batch')
    setPresets(response.data)
  }
  ```

- [ ] Add pagination to job listing
  ```python
  @router.get("/", response_model=List[JobMetadata])
  async def list_jobs(skip: int = 0, limit: int = 50):
      # Prevent loading thousands of jobs at once
  ```

**Success Metrics**:
- Initial preset load: 8 requests → 1 request
- Load time reduced by ~7x (assuming 100ms per request)

---

### Week 2: Testing Infrastructure (25-30 hours)

#### PF-4: Frontend Testing Setup
**Priority**: 🔴 Critical (enables safe refactoring)
**Effort**: 20-25 hours
**Impact**: Prevents regressions, enables confident refactoring

**Tasks**:
- [ ] Install testing dependencies
  ```bash
  cd frontend
  npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest @vitest/ui jsdom
  ```

- [ ] Create Vitest configuration
  ```javascript
  // frontend/vitest.config.js
  import { defineConfig } from 'vitest/config'
  import react from '@vitejs/plugin-react'

  export default defineConfig({
    plugins: [react()],
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './src/test/setup.js',
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'html'],
        exclude: ['node_modules/', 'src/test/']
      }
    }
  })
  ```

- [ ] Create test utilities
  ```jsx
  // frontend/src/test/setup.js
  import '@testing-library/jest-dom'
  import { vi } from 'vitest'

  // Mock API client
  vi.mock('../api/client', () => ({
    default: {
      get: vi.fn(),
      post: vi.fn(),
      delete: vi.fn()
    }
  }))
  ```

- [ ] Write core Composer.jsx tests (70%+ coverage target)
  ```jsx
  // frontend/src/Composer.test.jsx
  describe('Composer', () => {
    describe('Preset Application', () => {
      test('adds outfit preset to applied list', async () => { ... })
      test('replaces non-outfit presets', async () => { ... })
      test('caches generation results', async () => { ... })
    })

    describe('Mobile Navigation', () => {
      test('switches to canvas tab when applying preset on mobile', () => { ... })
      test('shows badge count on applied tab', () => { ... })
    })

    describe('Composition Management', () => {
      test('saves composition with current presets', async () => { ... })
      test('loads composition and applies presets', async () => { ... })
    })
  })
  ```

- [ ] Write tests for OutfitAnalyzer.jsx (60%+ coverage)
- [ ] Write tests for ModularGenerator.jsx (60%+ coverage)
- [ ] Add npm script: `"test": "vitest", "test:ui": "vitest --ui", "test:coverage": "vitest --coverage"`

**Success Metrics**:
- Frontend test coverage ≥70%
- All tests pass in CI
- Tests run in <10 seconds

---

#### PF-5: Backend Route Testing
**Priority**: 🟠 High
**Effort**: 5-8 hours
**Impact**: Catch API regressions

**Tasks**:
- [ ] Create API test fixtures
  ```python
  # tests/fixtures/api_fixtures.py
  import pytest
  from fastapi.testclient import TestClient
  from api.main import app

  @pytest.fixture
  def client():
      return TestClient(app)

  @pytest.fixture
  def auth_headers(client):
      response = client.post("/auth/login", json={
          "username": "test_user",
          "password": "test_password"
      })
      token = response.json()["access_token"]
      return {"Authorization": f"Bearer {token}"}
  ```

- [ ] Write tests for critical routes
  ```python
  # tests/api/test_presets_routes.py
  def test_batch_preset_loading(client, auth_headers):
      response = client.get("/api/presets/batch", headers=auth_headers)
      assert response.status_code == 200
      data = response.json()
      assert "outfits" in data
      assert "visual_styles" in data
      assert len(data.keys()) == 8  # All categories

  # tests/api/test_generators_routes.py
  def test_modular_generation_with_invalid_subject(client, auth_headers):
      response = client.post("/api/generate/modular",
          json={"subject_image": "nonexistent.png", "presets": []},
          headers=auth_headers)
      assert response.status_code == 404
      assert "not found" in response.json()["detail"].lower()

  # tests/api/test_compositions_routes.py
  def test_save_and_load_composition(client, auth_headers):
      # Save
      save_response = client.post("/api/compositions/save",
          json={"name": "Test Comp", "subject": "test.png", "presets": [...]},
          headers=auth_headers)
      assert save_response.status_code == 200

      # Load
      comp_id = save_response.json()["composition_id"]
      load_response = client.get(f"/api/compositions/{comp_id}", headers=auth_headers)
      assert load_response.status_code == 200
      assert load_response.json()["name"] == "Test Comp"
  ```

- [ ] Add tests for error cases (404, 400, 401)
- [ ] Target: 80%+ coverage for api/routes/

**Success Metrics**:
- Backend API route coverage ≥80%
- All error cases tested
- Tests independent (can run in any order)

---

### Week 3-4: Code Quality & Refactoring (60-70 hours)

#### PF-6: Extract Shared Component Logic
**Priority**: 🔴 Critical (reduces technical debt)
**Effort**: 12-16 hours
**Impact**: Eliminates 500+ duplicate lines

**Tasks**:
- [ ] Create shared analyzer hook
  ```jsx
  // frontend/src/hooks/useAnalyzer.js
  export function useAnalyzer(config) {
    const { analyzerType, category } = config

    const [file, setFile] = useState(null)
    const [analyzing, setAnalyzing] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)

    const handleDrag = useCallback((e) => {
      e.preventDefault()
      e.stopPropagation()
    }, [])

    const handleDrop = useCallback(async (e) => {
      e.preventDefault()
      e.stopPropagation()
      const files = e.dataTransfer.files
      if (files.length > 0) await handleFile(files[0])
    }, [])

    const handleFileInput = useCallback(async (e) => {
      if (e.target.files.length > 0) await handleFile(e.target.files[0])
    }, [])

    const handleFile = useCallback(async (file) => {
      if (!file.type.startsWith('image/')) {
        setError('Please upload an image file')
        return
      }
      setFile(file)
      setError(null)
    }, [])

    const analyzeImage = useCallback(async () => {
      if (!file) return

      setAnalyzing(true)
      setError(null)

      try {
        const reader = new FileReader()
        reader.onloadend = async () => {
          const base64Data = reader.result.split(',')[1]
          const response = await api.post(`/analyze/${analyzerType}`, {
            image: { image_data: base64Data }
          })
          setResult(response.data.result)
          setAnalyzing(false)
        }
        reader.onerror = () => {
          setError('Failed to read image file')
          setAnalyzing(false)
        }
        reader.readAsDataURL(file)
      } catch (err) {
        setError(err.response?.data?.detail || err.message)
        setAnalyzing(false)
      }
    }, [file, analyzerType])

    return {
      file,
      analyzing,
      result,
      error,
      handleDrag,
      handleDrop,
      handleFileInput,
      analyzeImage,
      reset: () => {
        setFile(null)
        setResult(null)
        setError(null)
      }
    }
  }
  ```

- [ ] Create shared preset management hook
  ```jsx
  // frontend/src/hooks/usePresetManager.js
  export function usePresetManager(category) {
    const [presets, setPresets] = useState([])
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)

    const loadPresets = useCallback(async () => {
      setLoading(true)
      try {
        const response = await api.get(`/presets/${category}`)
        setPresets(response.data)
      } catch (err) {
        console.error('Failed to load presets:', err)
      } finally {
        setLoading(false)
      }
    }, [category])

    const savePreset = useCallback(async (presetData) => {
      setSaving(true)
      try {
        await api.post(`/presets/${category}`, presetData)
        await loadPresets() // Refresh
        return true
      } catch (err) {
        console.error('Failed to save preset:', err)
        return false
      } finally {
        setSaving(false)
      }
    }, [category, loadPresets])

    const deletePreset = useCallback(async (presetId) => {
      try {
        await api.delete(`/presets/${category}/${presetId}`)
        await loadPresets()
        return true
      } catch (err) {
        console.error('Failed to delete preset:', err)
        return false
      }
    }, [category, loadPresets])

    useEffect(() => {
      loadPresets()
    }, [loadPresets])

    return {
      presets,
      loading,
      saving,
      savePreset,
      deletePreset,
      refresh: loadPresets
    }
  }
  ```

- [ ] Create shared polling utility
  ```jsx
  // frontend/src/hooks/usePolling.js
  export function usePolling(options = {}) {
    const { maxAttempts = 20, interval = 1000 } = options

    const poll = useCallback(async (fn, shouldContinue) => {
      for (let attempt = 0; attempt < maxAttempts; attempt++) {
        try {
          const result = await fn(attempt)
          if (!shouldContinue(result)) return result
        } catch (err) {
          if (attempt === maxAttempts - 1) throw err
        }
        await new Promise(resolve => setTimeout(resolve, interval))
      }
      throw new Error(`Polling timeout after ${maxAttempts} attempts`)
    }, [maxAttempts, interval])

    return { poll }
  }
  ```

- [ ] Refactor OutfitAnalyzer.jsx to use hooks
  ```jsx
  // Reduce from 702 lines to ~400 lines
  function OutfitAnalyzer() {
    const analyzer = useAnalyzer({ analyzerType: 'outfit', category: 'outfits' })
    const presetManager = usePresetManager('outfits')
    const { poll } = usePolling({ maxAttempts: 20, interval: 1000 })

    // Component-specific logic only
    // ...
  }
  ```

- [ ] Refactor GenericAnalyzer.jsx to use hooks (reduce from 580 to ~350 lines)
- [ ] Refactor ComprehensiveAnalyzer.jsx to use hooks

**Success Metrics**:
- Codebase reduction: 500+ duplicate lines eliminated
- Component files <400 lines each
- All analyzer tests still pass
- No regressions in functionality

---

#### PF-7: Refactor Composer.jsx
**Priority**: 🟠 High
**Effort**: 20-25 hours
**Impact**: Better maintainability, easier to add video generation later

**Tasks**:
- [ ] Extract sub-components
  ```jsx
  // frontend/src/components/composer/ComposerLibrary.jsx
  export function ComposerLibrary({
    categories,
    presets,
    activeCategory,
    onSelectCategory,
    onApplyPreset,
    favorites,
    onToggleFavorite,
    searchQuery,
    onSearchChange
  }) {
    // Lines 493-609 from Composer.jsx
    return (
      <div className="composer-sidebar">
        <CategoryTabs ... />
        <SearchBar ... />
        <PresetGrid ... />
      </div>
    )
  }

  // frontend/src/components/composer/ComposerCanvas.jsx
  export function ComposerCanvas({
    subject,
    subjects,
    onSubjectChange,
    generatedImage,
    generating,
    onDownload
  }) {
    // Lines 611-698 from Composer.jsx
    return (
      <div className="composer-canvas">
        <SubjectSelector ... />
        <ImagePreview ... />
        {generatedImage && <DownloadButton ... />}
      </div>
    )
  }

  // frontend/src/components/composer/AppliedPresets.jsx
  export function AppliedPresets({
    appliedPresets,
    onRemovePreset,
    compositions,
    onSaveComposition,
    onLoadComposition,
    onDeleteComposition
  }) {
    // Lines 700-852 from Composer.jsx
    return (
      <div className="composer-applied">
        <AppliedPresetsList ... />
        <CompositionManager ... />
      </div>
    )
  }
  ```

- [ ] Use useReducer for complex state
  ```jsx
  // frontend/src/reducers/composerReducer.js
  const initialState = {
    subject: 'jenny.png',
    subjects: [],
    categories: [],
    presets: {},
    appliedPresets: [],
    generatedImage: null,
    generating: false,
    favorites: [],
    compositions: [],
    ui: {
      activeCategory: null,
      searchQuery: '',
      mobileTab: 'canvas',
      showSaveDialog: false,
      showCompositions: false
    },
    cache: {
      generationHistory: []
    }
  }

  function composerReducer(state, action) {
    switch (action.type) {
      case 'SET_SUBJECT':
        return { ...state, subject: action.payload }
      case 'ADD_PRESET':
        return {
          ...state,
          appliedPresets: addPresetLogic(state.appliedPresets, action.payload)
        }
      case 'REMOVE_PRESET':
        return {
          ...state,
          appliedPresets: state.appliedPresets.filter(p => p.preset_id !== action.payload)
        }
      case 'SET_GENERATED_IMAGE':
        return { ...state, generatedImage: action.payload, generating: false }
      case 'START_GENERATION':
        return { ...state, generating: true }
      // ... etc
      default:
        return state
    }
  }

  // In Composer.jsx
  function Composer() {
    const [state, dispatch] = useReducer(composerReducer, initialState)
    // Much cleaner!
  }
  ```

- [ ] Extract generation logic into custom hook
  ```jsx
  // frontend/src/hooks/useImageGeneration.js
  export function useImageGeneration() {
    const [cache, setCache] = useState([])
    const { poll } = usePolling()

    const generateImage = useCallback(async (subject, presets) => {
      // Check cache
      const cacheKey = buildCacheKey(subject, presets)
      const cached = cache.find(c => c.cacheKey === cacheKey)
      if (cached) return cached.imageUrl

      // Generate
      const response = await api.post('/generate/modular', {
        subject_image: subject,
        presets: presets
      })

      // Poll for completion
      const result = await poll(
        async () => {
          const job = await api.get(`/jobs/${response.data.job_id}`)
          return job.data
        },
        (job) => job.status === 'pending' || job.status === 'running'
      )

      const imageUrl = result.result.output_url

      // Update cache
      setCache(prev => [{
        cacheKey,
        subject,
        presets: presets.map(p => p.preset_id),
        imageUrl,
        timestamp: Date.now()
      }, ...prev].slice(0, 50)) // LRU

      return imageUrl
    }, [cache, poll])

    return { generateImage, cache }
  }
  ```

- [ ] Refactor Composer.jsx to use extracted components
  ```jsx
  // Reduce from 855 lines to ~200 lines
  function Composer() {
    const [state, dispatch] = useReducer(composerReducer, initialState)
    const { generateImage } = useImageGeneration()
    const { favorites, toggleFavorite } = useFavorites()
    const { compositions, saveComposition, loadComposition } = useCompositions()

    // Only orchestration logic remains
    const handleApplyPreset = async (preset) => {
      dispatch({ type: 'ADD_PRESET', payload: preset })
      const imageUrl = await generateImage(state.subject, [...state.appliedPresets, preset])
      dispatch({ type: 'SET_GENERATED_IMAGE', payload: imageUrl })
    }

    return (
      <div className="composer">
        <ComposerLibrary
          categories={state.categories}
          presets={state.presets}
          activeCategory={state.ui.activeCategory}
          onSelectCategory={(cat) => dispatch({ type: 'SET_ACTIVE_CATEGORY', payload: cat })}
          onApplyPreset={handleApplyPreset}
          favorites={favorites}
          onToggleFavorite={toggleFavorite}
          searchQuery={state.ui.searchQuery}
          onSearchChange={(q) => dispatch({ type: 'SET_SEARCH_QUERY', payload: q })}
        />
        <ComposerCanvas
          subject={state.subject}
          subjects={state.subjects}
          onSubjectChange={(s) => dispatch({ type: 'SET_SUBJECT', payload: s })}
          generatedImage={state.generatedImage}
          generating={state.generating}
        />
        <AppliedPresets
          appliedPresets={state.appliedPresets}
          onRemovePreset={(id) => dispatch({ type: 'REMOVE_PRESET', payload: id })}
          compositions={compositions}
          onSaveComposition={saveComposition}
          onLoadComposition={loadComposition}
        />
        <MobileTabNavigation ... />
      </div>
    )
  }
  ```

**Success Metrics**:
- Composer.jsx reduced from 855 to <250 lines
- 5+ reusable components extracted
- State management centralized in reducer
- All tests pass after refactoring

---

#### PF-8: Standardize Error Handling
**Priority**: 🟡 Medium
**Effort**: 6-8 hours
**Impact**: Consistent UX, easier debugging

**Tasks**:
- [ ] Create ErrorContext for frontend
  ```jsx
  // frontend/src/contexts/ErrorContext.jsx
  import { createContext, useContext, useState, useCallback } from 'react'

  const ErrorContext = createContext()

  export function ErrorProvider({ children }) {
    const [error, setError] = useState(null)

    const showError = useCallback((message, options = {}) => {
      const { duration = 5000, type = 'error' } = options
      setError({ message, type, timestamp: Date.now() })

      if (duration > 0) {
        setTimeout(() => setError(null), duration)
      }
    }, [])

    const clearError = useCallback(() => setError(null), [])

    return (
      <ErrorContext.Provider value={{ error, showError, clearError }}>
        {children}
        {error && (
          <div className={`error-toast error-${error.type}`}>
            <span>{error.message}</span>
            <button onClick={clearError}>×</button>
          </div>
        )}
      </ErrorContext.Provider>
    )
  }

  export const useError = () => {
    const context = useContext(ErrorContext)
    if (!context) throw new Error('useError must be used within ErrorProvider')
    return context
  }
  ```

- [ ] Replace all alert() and console.error() with useError()
  ```jsx
  // Before
  catch (err) {
    alert('Failed to generate image: ' + err.message)
  }

  // After
  const { showError } = useError()
  catch (err) {
    showError(`Failed to generate image: ${err.response?.data?.detail || err.message}`)
  }
  ```

- [ ] Create standardized error response schema for backend
  ```python
  # api/models/responses.py
  class ErrorDetail(BaseModel):
      message: str
      error_code: str
      details: Optional[Dict[str, Any]] = None
      timestamp: datetime = Field(default_factory=datetime.now)

  class ErrorResponse(BaseModel):
      status: str = "error"
      error: ErrorDetail
  ```

- [ ] Create error handler decorator
  ```python
  # api/utils/error_handlers.py
  def handle_api_errors(response_model=None):
      def decorator(func):
          @wraps(func)
          async def wrapper(*args, **kwargs):
              try:
                  return await func(*args, **kwargs)
              except HTTPException:
                  raise
              except FileNotFoundError as e:
                  raise HTTPException(status_code=404, detail=str(e))
              except ValueError as e:
                  raise HTTPException(status_code=400, detail=str(e))
              except Exception as e:
                  logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                  if response_model:
                      return response_model(status="error", error=str(e))
                  raise HTTPException(status_code=500, detail="Internal server error")
          return wrapper
      return decorator
  ```

**Success Metrics**:
- All errors shown in consistent UI toast
- No alert() calls remaining
- Backend errors include error codes
- Error context logged properly

---

#### PF-9: Create Shared CSS Library
**Priority**: 🟢 Low
**Effort**: 3-4 hours
**Impact**: 30% CSS reduction

**Tasks**:
- [ ] Extract common styles
  ```css
  /* frontend/src/styles/common.css */

  /* Modals */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    max-width: 500px;
    width: 90%;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  }

  /* Forms */
  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-label {
    display: block;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #374151;
  }

  .form-input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 1rem;
  }

  /* Buttons */
  .button-group {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: #3b82f6;
    color: white;
  }

  .btn-secondary {
    background: #6b7280;
    color: white;
  }

  /* Loading states */
  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e5e7eb;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Messages */
  .error-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #ef4444;
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    z-index: 2000;
    animation: slideIn 0.3s ease-out;
  }

  @keyframes slideIn {
    from { transform: translateX(400px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  ```

- [ ] Import in all component CSS files
- [ ] Remove duplicate styles from component files

**Success Metrics**:
- Total CSS reduced by ~30%
- Consistent styling across components

---

### Week 4: Job Queue & Cleanup (10-15 hours)

#### PF-10: Job Queue Optimization
**Priority**: 🟡 Medium
**Effort**: 4-6 hours
**Impact**: Prevents memory leaks

**Tasks**:
- [ ] Add job cleanup scheduler
  ```python
  # api/services/job_cleanup.py
  import asyncio
  from datetime import datetime, timedelta
  from api.services.job_queue import get_job_queue_manager

  async def cleanup_old_jobs():
      """Remove completed jobs older than 24 hours"""
      while True:
          await asyncio.sleep(3600)  # Run every hour

          manager = get_job_queue_manager()
          cutoff = datetime.now() - timedelta(hours=24)

          all_jobs = manager.list_jobs()
          for job in all_jobs:
              if job.status in ['completed', 'failed', 'cancelled']:
                  if job.updated_at < cutoff:
                      manager._storage.delete_job(job.job_id)
                      logger.info(f"Cleaned up old job: {job.job_id}")

  # Start in api/main.py
  @app.on_event("startup")
  async def startup_event():
      asyncio.create_task(cleanup_old_jobs())
  ```

- [ ] Add job archive endpoint
  ```python
  @router.post("/{job_id}/archive")
  async def archive_job(job_id: str):
      """Archive completed job to file storage"""
      manager = get_job_queue_manager()
      job = manager.get_job(job_id)

      if job.status not in ['completed', 'failed']:
          raise HTTPException(400, "Can only archive completed/failed jobs")

      archive_path = settings.base_dir / "data" / "job_archives" / f"{job_id}.json"
      archive_path.parent.mkdir(parents=True, exist_ok=True)

      async with aiofiles.open(archive_path, 'w') as f:
          await f.write(job.json(indent=2))

      manager._storage.delete_job(job_id)
      return {"message": "Job archived"}
  ```

- [ ] Add configuration for retention policy
  ```python
  # api/config.py
  job_retention_hours: int = 24
  job_archive_enabled: bool = True
  max_concurrent_jobs: int = 10
  ```

**Success Metrics**:
- Memory usage stable over 24+ hours
- Old jobs auto-cleanup
- Job archive searchable

---

#### PF-11: Request Validation & Rate Limiting
**Priority**: 🟡 Medium
**Effort**: 4-6 hours
**Impact**: Prevents abuse, resource exhaustion

**Tasks**:
- [ ] Add request size validation
  ```python
  # api/dependencies/validation.py
  from fastapi import Request, HTTPException

  async def validate_request_size(request: Request, max_size_mb: int = 10):
      content_length = request.headers.get('content-length')
      if content_length and int(content_length) > max_size_mb * 1024 * 1024:
          raise HTTPException(413, f"Request too large (max {max_size_mb}MB)")

  # Use in routes
  @router.post("/upload", dependencies=[Depends(lambda r: validate_request_size(r, 10))])
  async def upload_file(...):
      ...
  ```

- [ ] Add rate limiting middleware
  ```python
  # api/middleware/rate_limit.py
  from fastapi import Request
  from starlette.middleware.base import BaseHTTPMiddleware
  from datetime import datetime, timedelta
  import asyncio

  class RateLimitMiddleware(BaseHTTPMiddleware):
      def __init__(self, app, requests_per_minute: int = 60):
          super().__init__(app)
          self.requests_per_minute = requests_per_minute
          self.request_counts = {}
          asyncio.create_task(self.cleanup_loop())

      async def dispatch(self, request: Request, call_next):
          client_ip = request.client.host
          now = datetime.now()

          # Get request count for this IP
          if client_ip not in self.request_counts:
              self.request_counts[client_ip] = []

          # Remove old requests
          self.request_counts[client_ip] = [
              ts for ts in self.request_counts[client_ip]
              if now - ts < timedelta(minutes=1)
          ]

          # Check limit
          if len(self.request_counts[client_ip]) >= self.requests_per_minute:
              return JSONResponse(
                  status_code=429,
                  content={"detail": "Rate limit exceeded"}
              )

          self.request_counts[client_ip].append(now)
          return await call_next(request)

      async def cleanup_loop(self):
          while True:
              await asyncio.sleep(300)  # Every 5 minutes
              now = datetime.now()
              for ip in list(self.request_counts.keys()):
                  self.request_counts[ip] = [
                      ts for ts in self.request_counts[ip]
                      if now - ts < timedelta(minutes=1)
                  ]
                  if not self.request_counts[ip]:
                      del self.request_counts[ip]

  # Add to main.py
  app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
  ```

- [ ] Add concurrent job limit
  ```python
  # api/services/job_queue.py
  def create_job(self, ...):
      running_jobs = len([j for j in self.list_jobs() if j.status == 'running'])
      if running_jobs >= settings.max_concurrent_jobs:
          raise ValueError(f"Too many concurrent jobs (max {settings.max_concurrent_jobs})")
      # ... create job
  ```

**Success Metrics**:
- API can't be overwhelmed by rapid requests
- Large uploads rejected
- Max 10 concurrent jobs enforced

---

#### PF-12: Documentation
**Priority**: 🟢 Low
**Effort**: 2-3 hours
**Impact**: Easier onboarding

**Tasks**:
- [ ] Add JSDoc to custom hooks
- [ ] Add API endpoint examples to docstrings
- [ ] Update README with testing instructions
- [ ] Create CONTRIBUTING.md with code standards

**Success Metrics**:
- All public functions documented
- New developers can run tests

---

## Phase 1 Summary

**Total Effort**: 100-120 hours (3-4 weeks)
**Impact**:
- ✅ 40-60% performance improvement
- ✅ 70%+ test coverage
- ✅ 500+ duplicate lines eliminated
- ✅ Memory leaks prevented
- ✅ Codebase ready for Phase 2 refactoring

**Deliverables**:
- [ ] All critical performance optimizations
- [ ] Frontend testing infrastructure with 70%+ coverage
- [ ] Backend route tests with 80%+ coverage
- [ ] Shared component library (hooks, CSS)
- [ ] Refactored Composer.jsx (<250 lines)
- [ ] Error handling standardized
- [ ] Job cleanup automated
- [ ] Rate limiting enabled

---

## Phase 2: Extensibility Architecture (Sprint 5)
**Duration**: 4-5 weeks
**Effort**: 150-180 hours
**Goal**: Create plugin architecture for domain expansion

### Overview

Phase 2 transforms Life-OS from a specialized image platform into a **modular AI platform** that can support multiple domains (video, board games, code, home automation) without modifying core infrastructure.

**Key Architectural Changes**:
1. **Plugin System** - Load domain modules dynamically
2. **Workflow Engine** - Chain AI operations across domains
3. **Context Management** - Persistent cross-domain memory
4. **Provider Abstraction** - Support local LLMs, ComfyUI, MCP servers
5. **Permission System** - Granular control for autonomous actions

---

### EA-1: Plugin Architecture Foundation
**Priority**: 🔴 Critical
**Effort**: 30-35 hours
**Impact**: Enables domain expansion without core changes

**Tasks**:

#### 1. Define Plugin Interface
```python
# api/core/plugin_interface.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class PluginMetadata(BaseModel):
    plugin_id: str
    name: str
    version: str
    domain: str  # 'image', 'video', 'boardgame', 'code', 'home', etc.
    capabilities: List[str]  # ['analyze', 'generate', 'transform']
    dependencies: List[str] = []
    author: str
    description: str

class ToolDefinition(BaseModel):
    tool_id: str
    tool_type: str  # 'analyzer', 'generator', 'transformer'
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    parameters: Dict[str, Any] = {}
    requires_auth: bool = False
    estimated_cost: float = 0.0

class BasePlugin(ABC):
    """Base class for all Life-OS plugins"""

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass

    @abstractmethod
    def get_tools(self) -> List[ToolDefinition]:
        """Return list of tools provided by this plugin"""
        pass

    @abstractmethod
    async def execute_tool(
        self,
        tool_id: str,
        inputs: Dict[str, Any],
        context: Optional['ExecutionContext'] = None
    ) -> Dict[str, Any]:
        """Execute a specific tool"""
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin with configuration"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass

class ExecutionContext(BaseModel):
    """Context passed to tool execution"""
    user_id: Optional[str] = None
    session_id: str
    workflow_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
```

#### 2. Create Plugin Manager
```python
# api/core/plugin_manager.py
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Optional
from api.core.plugin_interface import BasePlugin, PluginMetadata, ToolDefinition

class PluginManager:
    """Manages plugin lifecycle and discovery"""

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._tool_registry: Dict[str, tuple[str, str]] = {}  # tool_id -> (plugin_id, tool_id)
        self._initialized = False

    async def discover_plugins(self, plugin_dirs: List[Path]) -> None:
        """Discover and load plugins from directories"""
        for plugin_dir in plugin_dirs:
            if not plugin_dir.exists():
                continue

            for plugin_path in plugin_dir.iterdir():
                if plugin_path.is_dir() and (plugin_path / "plugin.py").exists():
                    await self._load_plugin(plugin_path)

    async def _load_plugin(self, plugin_path: Path) -> None:
        """Load a single plugin"""
        try:
            # Import plugin module
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_path.name}",
                plugin_path / "plugin.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin class
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, BasePlugin) and
                    obj is not BasePlugin):

                    # Instantiate plugin
                    plugin_instance = obj()
                    metadata = plugin_instance.get_metadata()

                    # Initialize
                    config = self._load_plugin_config(plugin_path)
                    if await plugin_instance.initialize(config):
                        self._plugins[metadata.plugin_id] = plugin_instance

                        # Register tools
                        for tool in plugin_instance.get_tools():
                            self._tool_registry[tool.tool_id] = (metadata.plugin_id, tool.tool_id)

                        logger.info(f"Loaded plugin: {metadata.name} v{metadata.version}")
                    break

        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_path}: {e}")

    def _load_plugin_config(self, plugin_path: Path) -> Dict[str, Any]:
        """Load plugin configuration"""
        config_file = plugin_path / "config.yaml"
        if config_file.exists():
            import yaml
            with open(config_file) as f:
                return yaml.safe_load(f)
        return {}

    async def execute_tool(
        self,
        tool_id: str,
        inputs: Dict[str, Any],
        context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """Execute a tool by ID"""
        if tool_id not in self._tool_registry:
            raise ValueError(f"Tool not found: {tool_id}")

        plugin_id, _ = self._tool_registry[tool_id]
        plugin = self._plugins[plugin_id]

        return await plugin.execute_tool(tool_id, inputs, context)

    def list_plugins(self) -> List[PluginMetadata]:
        """List all loaded plugins"""
        return [p.get_metadata() for p in self._plugins.values()]

    def list_tools(self, domain: Optional[str] = None) -> List[ToolDefinition]:
        """List all tools, optionally filtered by domain"""
        tools = []
        for plugin in self._plugins.values():
            metadata = plugin.get_metadata()
            if domain is None or metadata.domain == domain:
                tools.extend(plugin.get_tools())
        return tools

    async def cleanup(self):
        """Cleanup all plugins"""
        for plugin in self._plugins.values():
            await plugin.cleanup()

# Global singleton
_plugin_manager: Optional[PluginManager] = None

def get_plugin_manager() -> PluginManager:
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
```

#### 3. Migrate Existing Image Tools to Plugin
```python
# plugins/image_generation/plugin.py
from api.core.plugin_interface import BasePlugin, PluginMetadata, ToolDefinition, ExecutionContext
from api.services import AnalyzerService, GeneratorService, PresetService

class ImageGenerationPlugin(BasePlugin):
    """Plugin for image analysis and generation"""

    def __init__(self):
        self.analyzer_service = None
        self.generator_service = None
        self.preset_service = None

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="image_generation",
            name="Image Generation & Analysis",
            version="1.0.0",
            domain="image",
            capabilities=["analyze", "generate", "preset_management"],
            author="Life-OS Team",
            description="Comprehensive image analysis and generation using AI"
        )

    def get_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                tool_id="analyze_outfit",
                tool_type="analyzer",
                input_schema={"image": "string|file"},
                output_schema={"outfit_details": "object"},
                parameters={"async_mode": {"type": "boolean", "default": False}}
            ),
            ToolDefinition(
                tool_id="generate_modular_image",
                tool_type="generator",
                input_schema={
                    "subject_image": "string",
                    "presets": "array"
                },
                output_schema={"output_url": "string"},
                estimated_cost=0.05
            ),
            # ... all other tools
        ]

    async def execute_tool(
        self,
        tool_id: str,
        inputs: Dict[str, Any],
        context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """Execute image tool"""
        if tool_id.startswith("analyze_"):
            analyzer_name = tool_id.replace("analyze_", "")
            return await self._execute_analyzer(analyzer_name, inputs, context)
        elif tool_id.startswith("generate_"):
            generator_name = tool_id.replace("generate_", "")
            return await self._execute_generator(generator_name, inputs, context)
        else:
            raise ValueError(f"Unknown tool: {tool_id}")

    async def _execute_analyzer(self, analyzer_name: str, inputs: Dict, context: ExecutionContext):
        result = self.analyzer_service.analyze(
            analyzer_name=analyzer_name,
            image_input=inputs["image"],
            async_mode=inputs.get("async_mode", False)
        )
        return {"result": result}

    async def _execute_generator(self, generator_name: str, inputs: Dict, context: ExecutionContext):
        result = self.generator_service.generate(
            generator_name=generator_name,
            **inputs
        )
        return {"result": result}

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize services"""
        self.analyzer_service = AnalyzerService()
        self.generator_service = GeneratorService()
        self.preset_service = PresetService()
        return True

    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass
```

#### 4. Create Plugin Discovery Route
```python
# api/routes/plugins.py
from fastapi import APIRouter, HTTPException
from api.core.plugin_manager import get_plugin_manager
from api.core.plugin_interface import PluginMetadata, ToolDefinition, ExecutionContext

router = APIRouter()

@router.get("/", response_model=List[PluginMetadata])
async def list_plugins(domain: Optional[str] = None):
    """List all loaded plugins"""
    manager = get_plugin_manager()
    plugins = manager.list_plugins()

    if domain:
        plugins = [p for p in plugins if p.domain == domain]

    return plugins

@router.get("/{plugin_id}/tools", response_model=List[ToolDefinition])
async def list_plugin_tools(plugin_id: str):
    """List tools provided by a specific plugin"""
    manager = get_plugin_manager()
    plugins = manager.list_plugins()
    plugin = next((p for p in plugins if p.plugin_id == plugin_id), None)

    if not plugin:
        raise HTTPException(404, f"Plugin not found: {plugin_id}")

    return manager._plugins[plugin_id].get_tools()

@router.post("/execute")
async def execute_tool(
    tool_id: str,
    inputs: Dict[str, Any],
    session_id: str,
    user_id: Optional[str] = None
):
    """Execute a tool from any plugin"""
    manager = get_plugin_manager()

    context = ExecutionContext(
        user_id=user_id,
        session_id=session_id
    )

    result = await manager.execute_tool(tool_id, inputs, context)
    return result

# Add to main.py
app.include_router(plugins.router, prefix="/plugins", tags=["plugins"])

@app.on_event("startup")
async def load_plugins():
    manager = get_plugin_manager()
    await manager.discover_plugins([
        settings.base_dir / "plugins",
        settings.base_dir / "plugins/community"  # For third-party plugins
    ])
```

**Success Metrics**:
- Existing image tools work through plugin system
- Plugin discovery automatic on startup
- New plugins can be added without code changes

---

### EA-2: Workflow Engine
**Priority**: 🔴 Critical
**Effort**: 40-45 hours
**Impact**: Enable multi-step AI operations

**Purpose**: Chain multiple AI tools together (e.g., analyze image → generate script → create video)

#### 1. Define Workflow Schema
```python
# api/core/workflow_engine.py
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field
from datetime import datetime

class StepType(str, Enum):
    TOOL_EXECUTION = "tool_execution"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    PARALLEL = "parallel"
    TRANSFORM = "transform"

class WorkflowStep(BaseModel):
    step_id: str
    step_type: StepType
    tool_id: Optional[str] = None  # For tool_execution
    inputs: Dict[str, Any] = {}
    outputs: List[str] = []  # Variable names to store outputs
    condition: Optional[str] = None  # For conditional steps
    on_error: str = "fail"  # "fail", "continue", "retry"
    retry_count: int = 0
    depends_on: List[str] = []  # Step IDs that must complete first

class WorkflowDefinition(BaseModel):
    workflow_id: str
    name: str
    description: str
    version: str
    author: str
    domain: str
    steps: List[WorkflowStep]
    inputs: Dict[str, Any] = {}  # Expected workflow inputs
    outputs: List[str] = []  # Final workflow outputs
    metadata: Dict[str, Any] = {}

class WorkflowExecution(BaseModel):
    execution_id: str
    workflow_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_step: Optional[str] = None
    variables: Dict[str, Any] = {}  # Workflow variable context
    step_results: Dict[str, Any] = {}  # Results from each step
    error: Optional[str] = None
```

#### 2. Create Workflow Engine
```python
# api/core/workflow_engine.py (continued)
import asyncio
from api.core.plugin_manager import get_plugin_manager, ExecutionContext

class WorkflowEngine:
    """Executes multi-step AI workflows"""

    def __init__(self):
        self.plugin_manager = get_plugin_manager()
        self.executions: Dict[str, WorkflowExecution] = {}

    async def execute_workflow(
        self,
        workflow: WorkflowDefinition,
        inputs: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> WorkflowExecution:
        """Execute a workflow"""
        execution_id = f"wf_{uuid.uuid4().hex[:12]}"

        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow.workflow_id,
            status="running",
            started_at=datetime.now(),
            variables=inputs.copy()
        )

        self.executions[execution_id] = execution

        try:
            # Build dependency graph
            dep_graph = self._build_dependency_graph(workflow.steps)

            # Execute steps in topological order
            for step in self._topological_sort(dep_graph):
                execution.current_step = step.step_id

                # Execute step
                result = await self._execute_step(step, execution, user_id)

                # Store results
                execution.step_results[step.step_id] = result

                # Update variables
                for i, output_var in enumerate(step.outputs):
                    if isinstance(result, dict) and output_var in result:
                        execution.variables[output_var] = result[output_var]
                    elif isinstance(result, list) and i < len(result):
                        execution.variables[output_var] = result[i]
                    else:
                        execution.variables[output_var] = result

            execution.status = "completed"
            execution.completed_at = datetime.now()

        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            execution.completed_at = datetime.now()
            logger.error(f"Workflow {workflow.workflow_id} failed: {e}", exc_info=True)

        return execution

    async def _execute_step(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
        user_id: Optional[str]
    ) -> Any:
        """Execute a single workflow step"""
        if step.step_type == StepType.TOOL_EXECUTION:
            return await self._execute_tool_step(step, execution, user_id)
        elif step.step_type == StepType.CONDITIONAL:
            return await self._execute_conditional_step(step, execution, user_id)
        elif step.step_type == StepType.PARALLEL:
            return await self._execute_parallel_step(step, execution, user_id)
        elif step.step_type == StepType.TRANSFORM:
            return self._execute_transform_step(step, execution)
        else:
            raise ValueError(f"Unsupported step type: {step.step_type}")

    async def _execute_tool_step(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
        user_id: Optional[str]
    ) -> Any:
        """Execute a tool from a plugin"""
        # Resolve input variables
        resolved_inputs = self._resolve_variables(step.inputs, execution.variables)

        context = ExecutionContext(
            user_id=user_id,
            session_id=execution.execution_id,
            workflow_id=execution.workflow_id,
            parent_task_id=step.step_id
        )

        # Execute with retry logic
        for attempt in range(step.retry_count + 1):
            try:
                result = await self.plugin_manager.execute_tool(
                    step.tool_id,
                    resolved_inputs,
                    context
                )
                return result
            except Exception as e:
                if attempt == step.retry_count:
                    if step.on_error == "continue":
                        logger.warning(f"Step {step.step_id} failed but continuing: {e}")
                        return None
                    else:
                        raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def _execute_parallel_step(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
        user_id: Optional[str]
    ) -> List[Any]:
        """Execute multiple tools in parallel"""
        tasks = []
        for tool_config in step.inputs.get("parallel_tools", []):
            tool_step = WorkflowStep(
                step_id=f"{step.step_id}_{tool_config['tool_id']}",
                step_type=StepType.TOOL_EXECUTION,
                tool_id=tool_config["tool_id"],
                inputs=tool_config.get("inputs", {}),
                on_error=step.on_error
            )
            tasks.append(self._execute_tool_step(tool_step, execution, user_id))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    def _execute_transform_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Execute a data transformation"""
        transform_fn = step.inputs.get("transform")
        input_var = step.inputs.get("input")

        if not transform_fn or not input_var:
            raise ValueError("Transform step requires 'transform' and 'input'")

        input_value = execution.variables.get(input_var)

        # Simple expression evaluation (can be extended with safe_eval)
        if transform_fn.startswith("lambda"):
            fn = eval(transform_fn)
            return fn(input_value)
        else:
            # Predefined transformations
            transformations = {
                "to_list": lambda x: [x] if not isinstance(x, list) else x,
                "flatten": lambda x: [item for sublist in x for item in sublist],
                "join": lambda x: "\n".join(x) if isinstance(x, list) else str(x)
            }
            if transform_fn in transformations:
                return transformations[transform_fn](input_value)
            else:
                raise ValueError(f"Unknown transformation: {transform_fn}")

    def _resolve_variables(self, inputs: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve variable references in inputs"""
        resolved = {}
        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("$"):
                var_name = value[1:]
                resolved[key] = variables.get(var_name, value)
            else:
                resolved[key] = value
        return resolved

    def _build_dependency_graph(self, steps: List[WorkflowStep]) -> Dict[str, List[str]]:
        """Build dependency graph for steps"""
        graph = {step.step_id: step.depends_on for step in steps}
        return graph

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[WorkflowStep]:
        """Sort steps by dependencies (topological sort)"""
        # Simple implementation - can be improved
        visited = set()
        result = []

        def visit(node):
            if node in visited:
                return
            visited.add(node)
            for dep in graph.get(node, []):
                visit(dep)
            result.append(node)

        for node in graph:
            visit(node)

        return result

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        return self.executions.get(execution_id)

# Global singleton
_workflow_engine: Optional[WorkflowEngine] = None

def get_workflow_engine() -> WorkflowEngine:
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine
```

#### 3. Create Workflow Storage
```python
# api/services/workflow_service.py
from pathlib import Path
import aiofiles
import json
from typing import List
from api.core.workflow_engine import WorkflowDefinition

class WorkflowService:
    """Manage workflow definitions"""

    def __init__(self):
        self.workflow_dir = settings.base_dir / "workflows"
        self.workflow_dir.mkdir(parents=True, exist_ok=True)

    async def save_workflow(self, workflow: WorkflowDefinition) -> None:
        """Save workflow definition"""
        workflow_file = self.workflow_dir / f"{workflow.workflow_id}.json"
        async with aiofiles.open(workflow_file, 'w') as f:
            await f.write(workflow.json(indent=2))

    async def load_workflow(self, workflow_id: str) -> WorkflowDefinition:
        """Load workflow definition"""
        workflow_file = self.workflow_dir / f"{workflow_id}.json"
        if not workflow_file.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_id}")

        async with aiofiles.open(workflow_file, 'r') as f:
            data = await f.read()
            return WorkflowDefinition.parse_raw(data)

    async def list_workflows(self, domain: Optional[str] = None) -> List[WorkflowDefinition]:
        """List all workflows"""
        workflows = []
        for workflow_file in self.workflow_dir.glob("*.json"):
            async with aiofiles.open(workflow_file, 'r') as f:
                data = await f.read()
                workflow = WorkflowDefinition.parse_raw(data)
                if domain is None or workflow.domain == domain:
                    workflows.append(workflow)
        return workflows
```

#### 4. Create Workflow API Routes
```python
# api/routes/workflows.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.core.workflow_engine import WorkflowDefinition, WorkflowExecution, get_workflow_engine
from api.services.workflow_service import WorkflowService

router = APIRouter()

@router.post("/", response_model=WorkflowDefinition)
async def create_workflow(workflow: WorkflowDefinition):
    """Create a new workflow"""
    service = WorkflowService()
    await service.save_workflow(workflow)
    return workflow

@router.get("/", response_model=List[WorkflowDefinition])
async def list_workflows(domain: Optional[str] = None):
    """List all workflows"""
    service = WorkflowService()
    return await service.list_workflows(domain)

@router.get("/{workflow_id}", response_model=WorkflowDefinition)
async def get_workflow(workflow_id: str):
    """Get workflow by ID"""
    service = WorkflowService()
    return await service.load_workflow(workflow_id)

@router.post("/{workflow_id}/execute", response_model=WorkflowExecution)
async def execute_workflow(
    workflow_id: str,
    inputs: Dict[str, Any],
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = None
):
    """Execute a workflow"""
    service = WorkflowService()
    workflow = await service.load_workflow(workflow_id)

    engine = get_workflow_engine()

    # Execute in background
    execution = await engine.execute_workflow(workflow, inputs, user_id)

    return execution

@router.get("/executions/{execution_id}", response_model=WorkflowExecution)
async def get_execution_status(execution_id: str):
    """Get workflow execution status"""
    engine = get_workflow_engine()
    execution = engine.get_execution(execution_id)

    if not execution:
        raise HTTPException(404, "Execution not found")

    return execution

# Add to main.py
app.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
```

#### 5. Create Example Workflows
```yaml
# workflows/image_to_video_script.json
{
  "workflow_id": "image_to_video_script",
  "name": "Image to Video Script",
  "description": "Analyze image, extract key features, generate video script",
  "version": "1.0.0",
  "author": "Life-OS",
  "domain": "content_creation",
  "inputs": {
    "image": "Image file or URL to analyze",
    "target_audience": "Target audience for the video (e.g., 'beginners', 'experts')",
    "duration": "Target video duration in seconds"
  },
  "outputs": ["script", "scene_descriptions", "visual_suggestions"],
  "steps": [
    {
      "step_id": "analyze_visual_style",
      "step_type": "tool_execution",
      "tool_id": "analyze_visual_style",
      "inputs": {
        "image": "$image"
      },
      "outputs": ["visual_style"],
      "on_error": "fail"
    },
    {
      "step_id": "analyze_outfit",
      "step_type": "tool_execution",
      "tool_id": "analyze_outfit",
      "inputs": {
        "image": "$image"
      },
      "outputs": ["outfit_details"],
      "on_error": "continue"
    },
    {
      "step_id": "generate_script",
      "step_type": "tool_execution",
      "tool_id": "generate_video_script",
      "inputs": {
        "visual_style": "$visual_style",
        "outfit_details": "$outfit_details",
        "target_audience": "$target_audience",
        "duration": "$duration"
      },
      "outputs": ["script", "scene_descriptions"],
      "depends_on": ["analyze_visual_style", "analyze_outfit"]
    },
    {
      "step_id": "suggest_visuals",
      "step_type": "tool_execution",
      "tool_id": "suggest_video_visuals",
      "inputs": {
        "scene_descriptions": "$scene_descriptions",
        "original_style": "$visual_style"
      },
      "outputs": ["visual_suggestions"],
      "depends_on": ["generate_script"]
    }
  ]
}
```

**Success Metrics**:
- Workflows can chain 5+ steps
- Parallel execution works
- Error handling (retry, continue, fail) tested
- Example workflows run successfully

---

### EA-3: Context Management System
**Priority**: 🟠 High
**Effort**: 25-30 hours
**Impact**: Enable cross-domain memory and preferences

**Purpose**: Remember user preferences, conversation history, and context across domains

#### 1. Define Context Schema
```python
# api/core/context_manager.py
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

class ContextScope(str, Enum):
    SESSION = "session"  # Single conversation/interaction
    TASK = "task"  # Multi-step task
    DOMAIN = "domain"  # Specific domain (image, video, etc.)
    USER = "user"  # User-wide preferences
    GLOBAL = "global"  # Cross-user (e.g., system settings)

class ContextEntry(BaseModel):
    key: str
    value: Any
    scope: ContextScope
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class UserContext(BaseModel):
    user_id: str
    contexts: Dict[str, ContextEntry] = {}  # key -> entry
    preferences: Dict[str, Any] = {}
    recent_activities: List[Dict[str, Any]] = []
    domain_state: Dict[str, Any] = {}  # domain -> state
```

#### 2. Create Context Manager
```python
# api/core/context_manager.py (continued)
import aiofiles
import json
from pathlib import Path

class ContextManager:
    """Manages user context and memory across sessions"""

    def __init__(self):
        self.context_dir = settings.base_dir / "data" / "contexts"
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, UserContext] = {}

    async def get_context(
        self,
        user_id: str,
        key: str,
        scope: ContextScope = ContextScope.USER
    ) -> Optional[Any]:
        """Get a context value"""
        user_context = await self._load_user_context(user_id)

        entry = user_context.contexts.get(f"{scope}:{key}")
        if not entry:
            return None

        # Check expiration
        if entry.expires_at and datetime.now() > entry.expires_at:
            del user_context.contexts[f"{scope}:{key}"]
            await self._save_user_context(user_context)
            return None

        return entry.value

    async def set_context(
        self,
        user_id: str,
        key: str,
        value: Any,
        scope: ContextScope = ContextScope.USER,
        ttl_seconds: Optional[int] = None,
        metadata: Dict[str, Any] = {}
    ) -> None:
        """Set a context value"""
        user_context = await self._load_user_context(user_id)

        expires_at = None
        if ttl_seconds:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

        entry = ContextEntry(
            key=key,
            value=value,
            scope=scope,
            expires_at=expires_at,
            metadata=metadata
        )

        user_context.contexts[f"{scope}:{key}"] = entry
        await self._save_user_context(user_context)

    async def get_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        """Get user preference"""
        user_context = await self._load_user_context(user_id)
        return user_context.preferences.get(key, default)

    async def set_preference(self, user_id: str, key: str, value: Any) -> None:
        """Set user preference"""
        user_context = await self._load_user_context(user_id)
        user_context.preferences[key] = value
        await self._save_user_context(user_context)

    async def add_activity(
        self,
        user_id: str,
        activity_type: str,
        data: Dict[str, Any],
        max_activities: int = 100
    ) -> None:
        """Record user activity"""
        user_context = await self._load_user_context(user_id)

        activity = {
            "type": activity_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        user_context.recent_activities.insert(0, activity)
        user_context.recent_activities = user_context.recent_activities[:max_activities]

        await self._save_user_context(user_context)

    async def get_recent_activities(
        self,
        user_id: str,
        activity_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent activities"""
        user_context = await self._load_user_context(user_id)

        activities = user_context.recent_activities
        if activity_type:
            activities = [a for a in activities if a["type"] == activity_type]

        return activities[:limit]

    async def get_domain_state(self, user_id: str, domain: str) -> Dict[str, Any]:
        """Get domain-specific state"""
        user_context = await self._load_user_context(user_id)
        return user_context.domain_state.get(domain, {})

    async def update_domain_state(
        self,
        user_id: str,
        domain: str,
        state_updates: Dict[str, Any]
    ) -> None:
        """Update domain state"""
        user_context = await self._load_user_context(user_id)

        if domain not in user_context.domain_state:
            user_context.domain_state[domain] = {}

        user_context.domain_state[domain].update(state_updates)
        await self._save_user_context(user_context)

    async def _load_user_context(self, user_id: str) -> UserContext:
        """Load user context from cache or disk"""
        if user_id in self.memory_cache:
            return self.memory_cache[user_id]

        context_file = self.context_dir / f"{user_id}.json"

        if context_file.exists():
            async with aiofiles.open(context_file, 'r') as f:
                data = await f.read()
                user_context = UserContext.parse_raw(data)
        else:
            user_context = UserContext(user_id=user_id)

        self.memory_cache[user_id] = user_context
        return user_context

    async def _save_user_context(self, user_context: UserContext) -> None:
        """Save user context to disk"""
        context_file = self.context_dir / f"{user_context.user_id}.json"

        async with aiofiles.open(context_file, 'w') as f:
            await f.write(user_context.json(indent=2))

    async def cleanup_expired(self) -> int:
        """Remove expired context entries"""
        count = 0
        for user_id in self.memory_cache:
            user_context = self.memory_cache[user_id]
            now = datetime.now()

            expired_keys = [
                key for key, entry in user_context.contexts.items()
                if entry.expires_at and now > entry.expires_at
            ]

            for key in expired_keys:
                del user_context.contexts[key]
                count += 1

            if expired_keys:
                await self._save_user_context(user_context)

        return count

# Global singleton
_context_manager: Optional[ContextManager] = None

def get_context_manager() -> ContextManager:
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
```

#### 3. Create Context API
```python
# api/routes/context.py
from fastapi import APIRouter, Depends
from api.core.context_manager import get_context_manager, ContextScope
from api.dependencies.auth import get_current_active_user
from api.models.auth import User

router = APIRouter()

@router.get("/preferences")
async def get_all_preferences(current_user: User = Depends(get_current_active_user)):
    """Get all user preferences"""
    manager = get_context_manager()
    user_context = await manager._load_user_context(current_user.username)
    return user_context.preferences

@router.put("/preferences/{key}")
async def set_preference(
    key: str,
    value: Any,
    current_user: User = Depends(get_current_active_user)
):
    """Set a user preference"""
    manager = get_context_manager()
    await manager.set_preference(current_user.username, key, value)
    return {"message": "Preference updated"}

@router.get("/activity")
async def get_recent_activity(
    activity_type: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """Get recent activity"""
    manager = get_context_manager()
    activities = await manager.get_recent_activities(
        current_user.username,
        activity_type,
        limit
    )
    return activities

@router.get("/domain/{domain}/state")
async def get_domain_state(
    domain: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get domain-specific state"""
    manager = get_context_manager()
    state = await manager.get_domain_state(current_user.username, domain)
    return state

@router.put("/domain/{domain}/state")
async def update_domain_state(
    domain: str,
    state_updates: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Update domain state"""
    manager = get_context_manager()
    await manager.update_domain_state(current_user.username, domain, state_updates)
    return {"message": "Domain state updated"}

# Add to main.py
app.include_router(context.router, prefix="/context", tags=["context"])

@app.on_event("startup")
async def cleanup_context():
    """Cleanup expired context entries hourly"""
    async def cleanup_loop():
        while True:
            await asyncio.sleep(3600)
            manager = get_context_manager()
            count = await manager.cleanup_expired()
            logger.info(f"Cleaned up {count} expired context entries")

    asyncio.create_task(cleanup_loop())
```

**Success Metrics**:
- User preferences persist across sessions
- Recent activities tracked (limit 100)
- Domain state isolated and queryable
- Expired contexts auto-cleanup

---

### EA-4: Provider Abstraction Layer
**Priority**: 🟠 High
**Effort**: 20-25 hours
**Impact**: Support local LLMs, ComfyUI, MCP servers

**Purpose**: Abstract away provider differences (OpenAI, Gemini, local LLMs, ComfyUI, MCP)

#### 1. Define Provider Interface
```python
# api/core/providers/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ProviderCapability(str, Enum):
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    VIDEO_GENERATION = "video_generation"
    STRUCTURED_OUTPUT = "structured_output"
    FUNCTION_CALLING = "function_calling"

class ProviderConfig(BaseModel):
    provider_id: str
    provider_type: str  # 'openai', 'gemini', 'local_llm', 'comfyui', 'mcp'
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    capabilities: List[ProviderCapability]
    config: Dict[str, Any] = {}

class BaseProvider(ABC):
    """Base class for all AI providers"""

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text completion"""
        pass

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """Generate image, returns URL or base64"""
        pass

    @abstractmethod
    async def analyze_image(
        self,
        image_input: Any,
        prompt: str,
        **kwargs
    ) -> str:
        """Analyze image with prompt"""
        pass

    @abstractmethod
    def supports(self, capability: ProviderCapability) -> bool:
        """Check if provider supports capability"""
        pass
```

#### 2. Create ComfyUI Provider
```python
# api/core/providers/comfyui_provider.py
import aiohttp
from api.core.providers.base import BaseProvider, ProviderCapability

class ComfyUIProvider(BaseProvider):
    """Provider for ComfyUI API"""

    def __init__(self, config: ProviderConfig):
        self.endpoint = config.endpoint or "http://localhost:8188"
        self.capabilities = config.capabilities

    async def generate_image(self, prompt: str, **kwargs) -> str:
        """Generate image using ComfyUI workflow"""
        workflow = kwargs.get("workflow", "default")

        # Load workflow definition
        workflow_data = await self._load_workflow(workflow)

        # Update prompt in workflow
        workflow_data = self._update_workflow_prompt(workflow_data, prompt, kwargs)

        # Submit to ComfyUI
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/prompt",
                json={"prompt": workflow_data}
            ) as response:
                result = await response.json()
                prompt_id = result["prompt_id"]

            # Poll for completion
            image_url = await self._wait_for_completion(session, prompt_id)
            return image_url

    async def analyze_image(self, image_input: Any, prompt: str, **kwargs) -> str:
        """ComfyUI doesn't support image analysis natively"""
        raise NotImplementedError("ComfyUI does not support image analysis")

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """ComfyUI doesn't support text generation natively"""
        raise NotImplementedError("ComfyUI does not support text generation")

    def supports(self, capability: ProviderCapability) -> bool:
        return capability in self.capabilities

    async def _load_workflow(self, workflow_name: str) -> Dict:
        """Load ComfyUI workflow definition"""
        workflow_file = settings.base_dir / "comfyui_workflows" / f"{workflow_name}.json"
        async with aiofiles.open(workflow_file, 'r') as f:
            data = await f.read()
            return json.loads(data)

    def _update_workflow_prompt(self, workflow: Dict, prompt: str, params: Dict) -> Dict:
        """Update workflow with prompt and parameters"""
        # Find text nodes and update
        for node_id, node in workflow.items():
            if node.get("class_type") == "CLIPTextEncode":
                node["inputs"]["text"] = prompt

            # Update other parameters from kwargs
            for key, value in params.items():
                if key in node.get("inputs", {}):
                    node["inputs"][key] = value

        return workflow

    async def _wait_for_completion(self, session: aiohttp.ClientSession, prompt_id: str) -> str:
        """Poll ComfyUI for completion"""
        import asyncio

        for _ in range(60):  # 60 seconds timeout
            await asyncio.sleep(1)

            async with session.get(f"{self.endpoint}/history/{prompt_id}") as response:
                history = await response.json()

                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_output in outputs.values():
                        if "images" in node_output:
                            filename = node_output["images"][0]["filename"]
                            return f"{self.endpoint}/view?filename={filename}"

        raise TimeoutError("ComfyUI generation timeout")
```

#### 3. Create Local LLM Provider
```python
# api/core/providers/local_llm_provider.py
import aiohttp
from api.core.providers.base import BaseProvider, ProviderCapability

class LocalLLMProvider(BaseProvider):
    """Provider for local LLMs via Ollama or LM Studio API"""

    def __init__(self, config: ProviderConfig):
        self.endpoint = config.endpoint or "http://localhost:11434"  # Ollama default
        self.model = config.model or "llama2"
        self.capabilities = config.capabilities

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using local LLM"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            **kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/api/chat",
                json=payload
            ) as response:
                result = await response.json()
                return result["message"]["content"]

    async def generate_image(self, prompt: str, **kwargs) -> str:
        """Most local LLMs don't support image generation"""
        raise NotImplementedError("Local LLM does not support image generation")

    async def analyze_image(self, image_input: Any, prompt: str, **kwargs) -> str:
        """Analyze image using vision-capable local LLM (e.g., LLaVA)"""
        # Encode image to base64
        if isinstance(image_input, str) and image_input.startswith("http"):
            # Download image
            async with aiohttp.ClientSession() as session:
                async with session.get(image_input) as response:
                    image_data = await response.read()
        else:
            image_data = image_input

        import base64
        image_base64 = base64.b64encode(image_data).decode()

        payload = {
            "model": self.model,  # Should be vision model like llava
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }
            ],
            "stream": False
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/api/chat",
                json=payload
            ) as response:
                result = await response.json()
                return result["message"]["content"]

    def supports(self, capability: ProviderCapability) -> bool:
        return capability in self.capabilities
```

#### 4. Create MCP Provider
```python
# api/core/providers/mcp_provider.py
from mcp import Client
from api.core.providers.base import BaseProvider, ProviderCapability

class MCPProvider(BaseProvider):
    """Provider for MCP (Model Context Protocol) servers"""

    def __init__(self, config: ProviderConfig):
        self.endpoint = config.endpoint
        self.capabilities = config.capabilities
        self.client = None

    async def initialize(self):
        """Connect to MCP server"""
        self.client = await Client.connect(self.endpoint)

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Execute MCP tool for text generation"""
        if not self.client:
            await self.initialize()

        result = await self.client.call_tool(
            "generate_text",
            arguments={
                "prompt": prompt,
                "system_prompt": system_prompt,
                **kwargs
            }
        )
        return result["text"]

    async def generate_image(self, prompt: str, **kwargs) -> str:
        """Execute MCP tool for image generation"""
        if not self.client:
            await self.initialize()

        result = await self.client.call_tool(
            "generate_image",
            arguments={"prompt": prompt, **kwargs}
        )
        return result["image_url"]

    async def analyze_image(self, image_input: Any, prompt: str, **kwargs) -> str:
        """Execute MCP tool for image analysis"""
        if not self.client:
            await self.initialize()

        result = await self.client.call_tool(
            "analyze_image",
            arguments={
                "image": image_input,
                "prompt": prompt,
                **kwargs
            }
        )
        return result["analysis"]

    def supports(self, capability: ProviderCapability) -> bool:
        return capability in self.capabilities

    async def list_available_tools(self) -> List[str]:
        """List tools available on MCP server"""
        if not self.client:
            await self.initialize()

        tools = await self.client.list_tools()
        return [tool.name for tool in tools]
```

#### 5. Create Provider Registry
```python
# api/core/providers/registry.py
from typing import Dict, List, Optional
from api.core.providers.base import BaseProvider, ProviderConfig, ProviderCapability
from api.core.providers.comfyui_provider import ComfyUIProvider
from api.core.providers.local_llm_provider import LocalLLMProvider
from api.core.providers.mcp_provider import MCPProvider

class ProviderRegistry:
    """Manages AI provider registration and selection"""

    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self.provider_configs: Dict[str, ProviderConfig] = {}

    async def register_provider(self, config: ProviderConfig) -> None:
        """Register a new provider"""
        provider_class = {
            "comfyui": ComfyUIProvider,
            "local_llm": LocalLLMProvider,
            "mcp": MCPProvider,
            # ... existing providers (OpenAI, Gemini, etc.)
        }.get(config.provider_type)

        if not provider_class:
            raise ValueError(f"Unknown provider type: {config.provider_type}")

        provider = provider_class(config)

        if hasattr(provider, 'initialize'):
            await provider.initialize()

        self.providers[config.provider_id] = provider
        self.provider_configs[config.provider_id] = config

    def get_provider(self, provider_id: str) -> Optional[BaseProvider]:
        """Get provider by ID"""
        return self.providers.get(provider_id)

    def get_providers_by_capability(
        self,
        capability: ProviderCapability
    ) -> List[BaseProvider]:
        """Get all providers supporting a capability"""
        return [
            provider for provider in self.providers.values()
            if provider.supports(capability)
        ]

    def list_providers(self) -> List[ProviderConfig]:
        """List all registered providers"""
        return list(self.provider_configs.values())

    async def auto_select_provider(
        self,
        capability: ProviderCapability,
        preferences: Dict[str, Any] = {}
    ) -> Optional[BaseProvider]:
        """Automatically select best provider for capability"""
        providers = self.get_providers_by_capability(capability)

        if not providers:
            return None

        # Simple selection (can be enhanced with cost, speed, quality ranking)
        prefer_local = preferences.get("prefer_local", False)

        if prefer_local:
            local_providers = [p for p in providers if isinstance(p, (LocalLLMProvider, ComfyUIProvider))]
            if local_providers:
                return local_providers[0]

        return providers[0]

# Global singleton
_provider_registry: Optional[ProviderRegistry] = None

def get_provider_registry() -> ProviderRegistry:
    global _provider_registry
    if _provider_registry is None:
        _provider_registry = ProviderRegistry()
    return _provider_registry
```

#### 6. Update Router to Use Provider Registry
```python
# ai_tools/shared/router.py - Add provider registry integration
from api.core.providers.registry import get_provider_registry, ProviderCapability

class LLMRouter:
    # ... existing code ...

    async def call_with_provider_fallback(
        self,
        prompt: str,
        capability: ProviderCapability,
        **kwargs
    ) -> str:
        """Call provider with automatic fallback"""
        registry = get_provider_registry()

        # Get user preferences
        context_manager = get_context_manager()
        user_id = kwargs.get("user_id")
        preferences = {}
        if user_id:
            preferences = await context_manager.get_preference(user_id, "provider_preferences", {})

        # Try to get preferred provider
        provider = await registry.auto_select_provider(capability, preferences)

        if not provider:
            raise ValueError(f"No provider available for {capability}")

        try:
            if capability == ProviderCapability.TEXT_GENERATION:
                return await provider.generate_text(prompt, **kwargs)
            elif capability == ProviderCapability.IMAGE_GENERATION:
                return await provider.generate_image(prompt, **kwargs)
            elif capability == ProviderCapability.IMAGE_ANALYSIS:
                return await provider.analyze_image(kwargs.get("image"), prompt, **kwargs)
        except Exception as e:
            logger.error(f"Provider {provider.config.provider_id} failed: {e}")

            # Try fallback providers
            fallback_providers = registry.get_providers_by_capability(capability)
            for fallback in fallback_providers:
                if fallback == provider:
                    continue
                try:
                    logger.info(f"Trying fallback provider: {fallback.config.provider_id}")
                    if capability == ProviderCapability.TEXT_GENERATION:
                        return await fallback.generate_text(prompt, **kwargs)
                    # ... other capabilities
                except Exception as fallback_error:
                    logger.error(f"Fallback provider {fallback.config.provider_id} failed: {fallback_error}")
                    continue

            raise ValueError(f"All providers failed for {capability}")
```

**Success Metrics**:
- ComfyUI workflows execute successfully
- Local LLMs (Ollama) work for text generation
- MCP servers integrate properly
- Provider fallback works when primary fails
- User can set provider preferences

---

### EA-5: Permission & Safety System
**Priority**: 🟡 Medium
**Effort**: 15-20 hours
**Impact**: Enable safe autonomous actions (critical for home automation)

**Purpose**: Prevent autonomous agents from executing dangerous actions without approval

#### 1. Define Permission Schema
```python
# api/core/permissions.py
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PermissionLevel(str, Enum):
    NO_PERMISSION = "none"
    VIEW_ONLY = "view"
    SUGGEST = "suggest"  # Can suggest but needs approval
    EXECUTE_SAFE = "execute_safe"  # Can execute pre-approved safe actions
    EXECUTE_ALL = "execute_all"  # Full execution (dangerous!)

class ActionCategory(str, Enum):
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    GENERATE_CONTENT = "generate_content"
    EXTERNAL_API_CALL = "external_api"
    HOME_CONTROL = "home_control"
    CODE_EXECUTION = "code_execution"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"

class Permission(BaseModel):
    user_id: str
    domain: str  # 'image', 'video', 'home', 'code', etc.
    action_category: ActionCategory
    permission_level: PermissionLevel
    restrictions: Dict[str, Any] = {}  # Additional restrictions
    require_approval: bool = True
    approved_actions: List[str] = []  # Pre-approved specific actions

class ActionRequest(BaseModel):
    action_id: str
    domain: str
    category: ActionCategory
    description: str
    parameters: Dict[str, Any]
    risk_level: str  # 'low', 'medium', 'high'
    reversible: bool
    estimated_cost: float = 0.0

class ActionApproval(BaseModel):
    approval_id: str
    action_request: ActionRequest
    user_id: str
    status: str  # 'pending', 'approved', 'rejected'
    created_at: datetime
    approved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
```

#### 2. Create Permission Manager
```python
# api/core/permission_manager.py
class PermissionManager:
    """Manages permissions and action approvals"""

    def __init__(self):
        self.permissions: Dict[str, List[Permission]] = {}  # user_id -> permissions
        self.pending_approvals: Dict[str, ActionApproval] = {}

    async def check_permission(
        self,
        user_id: str,
        action: ActionRequest
    ) -> tuple[bool, Optional[str]]:
        """Check if user has permission for action"""
        # Get user permissions
        user_perms = self.permissions.get(user_id, [])

        # Find matching permission
        perm = next((
            p for p in user_perms
            if p.domain == action.domain and p.action_category == action.category
        ), None)

        if not perm:
            return False, "No permission defined for this action"

        # Check permission level
        if perm.permission_level == PermissionLevel.NO_PERMISSION:
            return False, "Action not permitted"

        if perm.permission_level == PermissionLevel.VIEW_ONLY:
            if action.category in [ActionCategory.WRITE_DATA, ActionCategory.HOME_CONTROL]:
                return False, "View-only permission"

        # Check if action is pre-approved
        if action.action_id in perm.approved_actions:
            return True, "Pre-approved action"

        # Check if high-risk action
        if action.risk_level == "high":
            if perm.permission_level != PermissionLevel.EXECUTE_ALL:
                return False, "High-risk action requires explicit approval"

        # Check if approval required
        if perm.require_approval and perm.permission_level != PermissionLevel.EXECUTE_ALL:
            # Create approval request
            approval = await self.request_approval(user_id, action)
            return False, f"Approval required (approval_id: {approval.approval_id})"

        # Check restrictions
        for restriction_key, restriction_value in perm.restrictions.items():
            if restriction_key in action.parameters:
                if action.parameters[restriction_key] != restriction_value:
                    return False, f"Restriction violation: {restriction_key}"

        return True, None

    async def request_approval(
        self,
        user_id: str,
        action: ActionRequest,
        ttl_seconds: int = 3600
    ) -> ActionApproval:
        """Request user approval for action"""
        approval_id = f"approval_{uuid.uuid4().hex[:12]}"

        approval = ActionApproval(
            approval_id=approval_id,
            action_request=action,
            user_id=user_id,
            status="pending",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=ttl_seconds)
        )

        self.pending_approvals[approval_id] = approval

        # Send notification to user (webhook, email, etc.)
        await self._notify_user_approval_needed(user_id, approval)

        return approval

    async def approve_action(self, approval_id: str) -> bool:
        """Approve pending action"""
        approval = self.pending_approvals.get(approval_id)

        if not approval:
            raise ValueError("Approval not found")

        if approval.status != "pending":
            raise ValueError(f"Approval already {approval.status}")

        if approval.expires_at and datetime.now() > approval.expires_at:
            approval.status = "expired"
            raise ValueError("Approval expired")

        approval.status = "approved"
        approval.approved_at = datetime.now()

        return True

    async def reject_action(self, approval_id: str) -> bool:
        """Reject pending action"""
        approval = self.pending_approvals.get(approval_id)

        if not approval:
            raise ValueError("Approval not found")

        approval.status = "rejected"
        return True

    async def get_pending_approvals(self, user_id: str) -> List[ActionApproval]:
        """Get user's pending approvals"""
        return [
            a for a in self.pending_approvals.values()
            if a.user_id == user_id and a.status == "pending"
        ]

    async def set_permission(self, permission: Permission) -> None:
        """Set user permission"""
        if permission.user_id not in self.permissions:
            self.permissions[permission.user_id] = []

        # Remove existing permission for same domain/category
        self.permissions[permission.user_id] = [
            p for p in self.permissions[permission.user_id]
            if not (p.domain == permission.domain and p.action_category == permission.action_category)
        ]

        self.permissions[permission.user_id].append(permission)

    async def _notify_user_approval_needed(self, user_id: str, approval: ActionApproval):
        """Notify user that approval is needed"""
        # Could send email, push notification, etc.
        logger.info(f"Approval needed for user {user_id}: {approval.action_request.description}")

        # Store in context for UI to display
        context_manager = get_context_manager()
        await context_manager.set_context(
            user_id,
            f"pending_approval_{approval.approval_id}",
            approval.dict(),
            scope=ContextScope.USER,
            ttl_seconds=3600
        )

# Global singleton
_permission_manager: Optional[PermissionManager] = None

def get_permission_manager() -> PermissionManager:
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager
```

#### 3. Create Permission API
```python
# api/routes/permissions.py
from fastapi import APIRouter, Depends, HTTPException
from api.core.permission_manager import get_permission_manager, Permission, ActionApproval
from api.dependencies.auth import get_current_active_user

router = APIRouter()

@router.post("/set")
async def set_permission(
    permission: Permission,
    current_user: User = Depends(get_current_active_user)
):
    """Set permission for user (admin only in production)"""
    # In production, add admin check here
    manager = get_permission_manager()
    await manager.set_permission(permission)
    return {"message": "Permission set"}

@router.get("/approvals")
async def get_pending_approvals(
    current_user: User = Depends(get_current_active_user)
):
    """Get pending action approvals"""
    manager = get_permission_manager()
    approvals = await manager.get_pending_approvals(current_user.username)
    return approvals

@router.post("/approvals/{approval_id}/approve")
async def approve_action(
    approval_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Approve pending action"""
    manager = get_permission_manager()
    await manager.approve_action(approval_id)
    return {"message": "Action approved"}

@router.post("/approvals/{approval_id}/reject")
async def reject_action(
    approval_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Reject pending action"""
    manager = get_permission_manager()
    await manager.reject_action(approval_id)
    return {"message": "Action rejected"}

# Add to main.py
app.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
```

**Success Metrics**:
- High-risk actions require approval
- Approval UI shows pending actions
- Pre-approved actions execute immediately
- Permission levels enforced correctly

---

## Phase 2 Summary

**Total Effort**: 150-180 hours (4-5 weeks)
**Impact**:
- ✅ Plugin architecture enables domain expansion
- ✅ Workflow engine supports multi-step AI operations
- ✅ Context management for cross-domain memory
- ✅ Provider abstraction for local LLMs, ComfyUI, MCP
- ✅ Permission system for safe autonomous actions

**Deliverables**:
- [ ] Plugin system with image generation migrated
- [ ] Workflow engine with 5+ example workflows
- [ ] Context manager with preferences & activity tracking
- [ ] ComfyUI, Local LLM, and MCP providers working
- [ ] Permission system with approval flow
- [ ] Documentation for creating plugins

---

## Phase 3: Agent Framework (Sprint 6)
**Duration**: 3-4 weeks
**Effort**: 120-150 hours
**Goal**: Enable semi-autonomous agents

### Overview

Phase 3 introduces autonomous agents that can:
- Proactively suggest tasks
- Execute multi-step workflows
- Learn from user feedback
- Operate with safety constraints

**Key Components**:
1. **Agent Core** - Decision-making logic
2. **Task Planner** - Break goals into executable steps
3. **Learning System** - Improve from user interactions
4. **Safety Monitor** - Prevent unsafe actions

### AF-1: Agent Core Architecture
**Priority**: 🔴 Critical
**Effort**: 35-40 hours

**Tasks**:
- [ ] Define agent interface
- [ ] Create agent registry
- [ ] Implement agent lifecycle (init, run, pause, stop)
- [ ] Create agent state persistence
- [ ] Build agent communication protocol

**Example Agent**:
```python
class ProactiveImageAgent(BaseAgent):
    """Agent that suggests images based on user preferences"""

    async def run(self):
        # Analyze recent user activity
        recent = await self.context.get_recent_activities(limit=50)

        # Find patterns (favorite styles, subjects)
        patterns = self.analyze_patterns(recent)

        # Suggest new combinations
        suggestions = await self.generate_suggestions(patterns)

        # Request approval
        for suggestion in suggestions:
            await self.request_approval(suggestion)
```

### AF-2: Task Planner
**Priority**: 🔴 Critical
**Effort**: 30-35 hours

**Tasks**:
- [ ] Goal decomposition (break "make a video" into steps)
- [ ] Task dependency resolution
- [ ] Resource estimation (time, cost)
- [ ] Alternative path generation (if step fails, try different approach)

### AF-3: Learning System
**Priority**: 🟠 High
**Effort**: 25-30 hours

**Tasks**:
- [ ] Feedback collection (user approves/rejects agent suggestions)
- [ ] Preference learning (what styles does user like?)
- [ ] Habit detection (user always generates images on Monday morning)
- [ ] Recommendation engine

### AF-4: Safety Monitor
**Priority**: 🔴 Critical
**Effort**: 20-25 hours

**Tasks**:
- [ ] Action risk classification
- [ ] Anomaly detection (agent behaving unexpectedly)
- [ ] Rate limiting (agent can't make 1000 API calls)
- [ ] Rollback mechanism (undo agent actions)
- [ ] Emergency stop button

### AF-5: Agent UI
**Priority**: 🟠 High
**Effort**: 10-15 hours

**Tasks**:
- [ ] Agent dashboard (status, recent actions)
- [ ] Approval queue UI
- [ ] Agent configuration UI
- [ ] Activity timeline

## Phase 3 Summary

**Total Effort**: 120-150 hours (3-4 weeks)
**Deliverables**:
- [ ] 3-5 functional agents (image suggestions, code refactoring, content ideas)
- [ ] Task planner for multi-step goals
- [ ] Learning system that improves with feedback
- [ ] Safety monitoring dashboard
- [ ] Agent management UI

---

## Phase 4: Domain Expansion (Sprint 7+)
**Duration**: Ongoing (12+ weeks)
**Effort**: 400-500 hours
**Goal**: Add new domains

### New Domains Implementation

#### Domain 1: Video Generation (Sora)
**Priority**: 🔴 Critical
**Effort**: 60-80 hours

**Plugin**: `video_generation`

**Tools**:
- `analyze_video` - Extract scenes, styles
- `generate_video_sora` - Create video with Sora
- `apply_preset_to_video` - Use existing image presets on video
- `video_script_generator` - Generate scripts for videos

**Workflows**:
- Image → Video (apply same style to video generation)
- Script → Video (generate video from script)
- Video Remix (analyze existing video, create variation)

**Estimated Timeline**: 3-4 weeks

---

#### Domain 2: Board Game Analysis
**Priority**: 🟡 Medium
**Effort**: 40-50 hours

**Plugin**: `board_game_tools`

**Tools**:
- `analyze_game_state` - Analyze board photo to understand state
- `generate_teaching_guide` - Create step-by-step tutorial
- `generate_reference_card` - Quick reference for rules
- `suggest_next_move` - Suggest optimal play

**Data Requirements**:
- Game rule databases
- OCR for board recognition
- Game state representation

**Estimated Timeline**: 2-3 weeks

---

#### Domain 3: Educational Content
**Priority**: 🟠 High
**Effort**: 50-60 hours

**Plugin**: `educational_content`

**Tools**:
- `generate_video_script` - Create teaching scripts
- `create_lesson_plan` - Multi-part lesson planning
- `generate_quiz` - Create assessments
- `summarize_topic` - News/topic summaries

**Workflows**:
- Topic → Lesson Plan → Scripts → Videos
- News Summary → Teaching Points → Quiz

**Estimated Timeline**: 2-3 weeks

---

#### Domain 4: Code Management (Claude Code Integration)
**Priority**: 🔴 Critical
**Effort**: 70-90 hours

**Plugin**: `code_management`

**Tools**:
- `analyze_codebase` - Understand code structure
- `plan_refactoring` - Identify improvement tasks
- `generate_tests` - Auto-generate test cases
- `code_review` - Automated code review
- `execute_code_task` - Integrate with Claude Code API

**Integration**:
- Connect to Claude Code via API
- Manage task queues
- Track refactoring progress
- Automated PR creation

**Estimated Timeline**: 4-5 weeks

---

#### Domain 5: Life Planning
**Priority**: 🟠 High
**Effort**: 60-70 hours

**Plugin**: `life_planning`

**Tools**:
- `calendar_manager` - Schedule optimization
- `task_prioritizer` - Eisenhower matrix automation
- `goal_tracker` - Long-term goal decomposition
- `habit_builder` - Habit formation suggestions

**Integrations**:
- Google Calendar
- Todoist/similar
- Apple Reminders

**Estimated Timeline**: 3-4 weeks

---

#### Domain 6: Home Automation (Home Assistant)
**Priority**: 🔴 Critical (requires safety!)
**Effort**: 80-100 hours

**Plugin**: `home_automation`

**Tools**:
- `get_device_status` - Query Home Assistant
- `control_device` - Send commands (with approval!)
- `create_automation` - Generate HA automations
- `analyze_energy` - Energy usage insights
- `scene_suggester` - Suggest lighting/climate scenes

**Safety Requirements**:
- All control actions require approval (unless pre-approved)
- Rate limiting (max 10 commands/hour)
- Audit log of all actions
- Emergency override

**Integration**:
- Home Assistant REST API
- WebSocket for real-time updates
- Event subscriptions

**Estimated Timeline**: 4-5 weeks

---

#### Domain 7: MCP Server Integration
**Priority**: 🟠 High
**Effort**: 40-50 hours

**Plugin**: `mcp_integration`

**Tools**:
- Dynamic tool discovery from MCP servers
- Generic tool execution wrapper
- Multi-server orchestration

**MCP Servers to Support**:
- Web search
- Weather
- News
- File system
- Database
- Browser automation

**Estimated Timeline**: 2-3 weeks

---

## Phase 4 Summary

**Total Effort**: 400-500 hours (12-15 weeks)
**Timeline**: Domains added incrementally

**Prioritization**:
1. **Week 1-4**: Video Generation (Sora) - extends current image work
2. **Week 5-8**: Code Management (Claude Code) - meta capability
3. **Week 9-12**: Home Automation - high-value daily use
4. **Week 13-16**: Life Planning + Educational Content
5. **Week 17-20**: Board Games + MCP Integration

---

## Implementation Strategy

### Recommended Order

**Sprint 4** (Weeks 1-4): Phase 1 - Critical Foundations
- Performance optimizations
- Testing infrastructure
- Code refactoring

**Sprint 5** (Weeks 5-9): Phase 2 - Extensibility
- Plugin architecture
- Workflow engine
- Context management
- Provider abstraction

**Sprint 6** (Weeks 10-13): Phase 3 - Agents
- Agent framework
- Task planner
- Learning system
- Safety monitoring

**Sprint 7+** (Weeks 14-30): Phase 4 - Domain Expansion
- Video generation
- Code management
- Home automation
- Life planning
- Educational content
- Board games
- MCP integration

---

## Success Metrics

### Phase 1 Success Criteria
- [ ] Test coverage ≥70% (frontend), ≥80% (backend)
- [ ] Performance improvement 40-60%
- [ ] Codebase reduced by 500+ duplicate lines
- [ ] All Quick Wins completed

### Phase 2 Success Criteria
- [ ] 1+ plugin successfully added without core changes
- [ ] 3+ workflows executing successfully
- [ ] User preferences persist across sessions
- [ ] Local LLM integration working

### Phase 3 Success Criteria
- [ ] 3+ agents running autonomously
- [ ] Task planner handles 5-step workflows
- [ ] Safety monitor prevents 100% of dangerous actions
- [ ] Agent suggestions have >50% user approval rate

### Phase 4 Success Criteria
- [ ] 5+ domains operational
- [ ] Cross-domain workflows work (e.g., Image → Video)
- [ ] Home automation safe and reliable
- [ ] Code management reduces manual work by 40%

---

## Resource Requirements

### Development Team
- **Phase 1**: 1 full-time developer (3-4 weeks)
- **Phase 2**: 1-2 developers (4-5 weeks)
- **Phase 3**: 1-2 developers (3-4 weeks)
- **Phase 4**: 2-3 developers (12-15 weeks)

### Infrastructure
- **Current**: Docker Compose, Redis, PostgreSQL (optional)
- **Added in Phase 2**: Local LLM server (Ollama), ComfyUI server
- **Added in Phase 3**: Agent monitoring dashboard
- **Added in Phase 4**: Home Assistant, MCP servers

### Budget (API Costs)
- **Phase 1-3**: ~$100-200/month (mostly testing)
- **Phase 4**: $300-500/month (video generation, multiple domains)

---

## Risk Mitigation

### High Risks

**Risk 1: Agent Safety**
- **Mitigation**: Comprehensive permission system, approval flow, audit logs
- **Testing**: Simulate dangerous scenarios, ensure all blocked

**Risk 2: Performance Degradation**
- **Mitigation**: Phase 1 optimizations first, load testing
- **Monitoring**: Track response times, set alerts

**Risk 3: Scope Creep**
- **Mitigation**: Strict phase boundaries, feature freeze during phases
- **Review**: Weekly scope review

**Risk 4: API Cost Explosion**
- **Mitigation**: Cost tracking per tool, rate limiting, budget alerts
- **Fallback**: Local LLM options for high-volume tasks

---

## Next Steps

Would you like me to:

1. **Start Phase 1 immediately** (performance quick wins)?
2. **Create detailed specification** for a specific phase?
3. **Build a prototype** of plugin architecture or workflow engine?
4. **Design specific domain plugin** (e.g., video generation)?
5. **Create project management board** with all tasks?

Let me know where you'd like to begin, and I'll dive in!
