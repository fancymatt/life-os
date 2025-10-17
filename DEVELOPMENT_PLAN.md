# Life-OS Development Plan
**Last Updated**: 2025-10-16 (End of Day)
**Status**: Stable foundation with good patterns established
**Next Focus**: Testing infrastructure & local LLM integration

---

## Today's Accomplishments ✅

### What We Built (2025-10-16)
1. **Story Preset Modal System**
   - Reusable modal component for story themes, audiences, prose styles
   - Complete field templates matching existing presets
   - Proper error handling and loading states

2. **Tool Configuration System**
   - All 9 analyzer tools now have configuration UI
   - Model selection, temperature control, prompt editing
   - Test functionality for all analyzers
   - Template override system (data/tool_configs/)

3. **Backend Async Refactoring**
   - All analyzer tools have async `aanalyze()` methods
   - Synchronous wrappers using `asyncio.run()`
   - Template override support via `_load_template()`
   - Support for both Pydantic models and plain dicts in PresetManager

4. **UX Improvements**
   - Fixed browser back button navigation in entity detail views
   - Alphabetized all sidebar sections
   - Moved Story Generator to Applications section
   - Trailing slash fixes for API consistency

---

## Current State Assessment

### Strengths 💪
- ✅ **Solid Architecture**: Entity-based design with URL routing
- ✅ **Good Patterns**: Character + Tool + Workflow system works well
- ✅ **Async Throughout**: Backend properly async now
- ✅ **Consistent UI**: Story preset modal matches character modal pattern
- ✅ **Multi-Provider LLM**: LiteLLM routing working smoothly
- ✅ **Configuration**: Tools configurable without code changes

### Code Quality Concerns 🔴

#### High Priority (Address Tomorrow)
1. **No Frontend Tests** (0% coverage)
   - Critical paths untested (story workflow, character import, image generation)
   - No smoke tests to catch regressions
   - Manual testing is fragile and time-consuming

2. **Large Frontend Components** (Still exist)
   - `Composer.jsx` - 910 lines (needs refactoring)
   - `OutfitAnalyzer.jsx` - 702 lines (duplicate with GenericAnalyzer)
   - `GenericAnalyzer.jsx` - 586 lines (85% duplicate)
   - These are maintainability risks

3. **Missing Backend Tests for New Features**
   - Story preset creation (no tests)
   - Tool configuration API (no tests)
   - Analyzer async methods (no tests)

#### Medium Priority
1. **Performance Not Validated**
   - No tests for large datasets (200+ entities)
   - No performance benchmarks
   - Unknown scaling limits

2. **Error Handling Gaps**
   - Some error paths not tested
   - User-facing error messages could be clearer
   - No structured error logging

#### Low Priority
1. **Code Duplication** (OutfitAnalyzer vs GenericAnalyzer)
2. **Bundle Size** (not measured or optimized)
3. **No CI/CD** (manual testing only)

---

## Immediate Priorities (Tomorrow - 2025-10-17)

### Priority 1: Testing Infrastructure 🧪
**Goal**: Catch regressions before they reach production
**Effort**: 6-8 hours
**Impact**: High - prevents bugs, enables confident changes

#### Backend Tests (3-4 hours)
```bash
# Test structure
tests/
├── unit/                     # Existing tests (mostly passing)
├── integration/
│   ├── test_story_presets.py      # NEW - Story preset CRUD
│   ├── test_tool_configs.py       # NEW - Tool configuration API
│   ├── test_analyzer_async.py     # NEW - Async analyzer methods
│   └── test_trailing_slash.py     # NEW - API route consistency
└── smoke/
    └── test_critical_paths.py     # NEW - Quick sanity checks
```

**Tasks**:
- [ ] Create `tests/integration/test_story_presets.py`
  - Test create/read/update/delete for story themes
  - Test validation of field structures
  - Test error cases (missing fields, invalid category)

- [ ] Create `tests/integration/test_tool_configs.py`
  - Test GET /tools, GET /tools/{tool_name}
  - Test PUT /tools/{tool_name} (model, temperature, template)
  - Test POST /tools/{tool_name}/test

- [ ] Create `tests/smoke/test_critical_paths.py`
  - Test all main routes return 200 OK
  - Test character import from subject
  - Test story workflow end-to-end (fast, mocked LLM)

- [ ] Run and fix existing tests
  ```bash
  docker-compose run --rm api pytest tests/ -v
  ```

#### Frontend Tests (3-4 hours)
```bash
# Set up Vitest
npm install -D vitest @testing-library/react @testing-library/jest-dom \
  @testing-library/user-event jsdom

# Test structure
frontend/src/
├── __tests__/
│   ├── components/
│   │   ├── StoryPresetModal.test.jsx    # NEW
│   │   └── EntityBrowser.test.jsx       # NEW
│   └── integration/
│       └── story-workflow.test.jsx      # NEW
└── vitest.config.js                     # NEW
```

**Tasks**:
- [ ] Set up Vitest + React Testing Library
- [ ] Write `StoryPresetModal.test.jsx`
  - Renders without crashing
  - Shows error when name is empty
  - Calls API correctly on submit

- [ ] Write `EntityBrowser.test.jsx`
  - Renders list of entities
  - Switches to detail view on click
  - Browser back button works

- [ ] Add npm script: `"test": "vitest"`

**Success Criteria**:
- ✅ Backend tests pass: `pytest tests/ -v`
- ✅ Frontend tests pass: `npm test`
- ✅ Smoke tests catch broken routes
- ✅ Can run tests in CI (future)

---

### Priority 2: Local LLM Integration (llama.cpp) 🤖
**Goal**: Run local models as alternative to cloud APIs
**Effort**: 8-10 hours
**Impact**: High - cost savings, privacy, offline capability

#### Research & Planning (1 hour)
- [ ] Review llama.cpp documentation
- [ ] Choose Python binding: llama-cpp-python vs llama.cpp directly
- [ ] Decide on model format (GGUF recommended)
- [ ] Plan model storage (data/models/ directory)

#### Backend Implementation (5-6 hours)

**File**: `ai_tools/shared/providers/local_llm_provider.py` (NEW)
```python
"""
Local LLM Provider using llama.cpp

Provides local inference as an alternative to cloud APIs.
Compatible with LLMRouter interface.
"""

class LocalLLMProvider:
    """Wrapper for local llama.cpp models"""

    def __init__(self, model_path: Path, n_ctx: int = 2048):
        """Initialize local model"""
        pass

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text completion"""
        pass

    async def agenerate(self, prompt: str, max_tokens: int = 500) -> str:
        """Async generation"""
        pass

    def supports_images(self) -> bool:
        """Check if model supports vision"""
        return False  # Start with text-only
```

**File**: `api/routes/local_models.py` (NEW)
```python
"""
Local Model Management API

Download, list, delete local models.
"""

@router.get("/local-models")
async def list_local_models():
    """List downloaded models"""
    pass

@router.post("/local-models/download")
async def download_model(url: str):
    """Download model from HuggingFace"""
    pass

@router.delete("/local-models/{model_id}")
async def delete_model(model_id: str):
    """Delete local model"""
    pass
```

**Integration with LLMRouter**:
```python
# In router.py, update __init__
def __init__(self, model: Optional[str] = None):
    # Detect local:// prefix
    if model and model.startswith("local://"):
        self.provider = "local"
        self.local_model = LocalLLMProvider(model[8:])
    else:
        self.provider = "cloud"
```

**Tasks**:
- [ ] Add `llama-cpp-python` to requirements.txt
- [ ] Create `LocalLLMProvider` class
- [ ] Add local model detection to `LLMRouter`
- [ ] Create `/api/local-models` routes
- [ ] Test with a small model (e.g., TinyLlama 1.1B)

#### Frontend UI (2-3 hours)

**File**: `frontend/src/pages/LocalModelsPage.jsx` (NEW)
```jsx
/**
 * Local Models Management
 *
 * Download and manage local LLMs for offline use.
 */
function LocalModelsPage() {
  // Model catalog (HuggingFace GGUF models)
  const catalog = [
    {
      id: 'tinyllama-1.1b',
      name: 'TinyLlama 1.1B',
      size: '637 MB',
      url: 'https://huggingface.co/...',
      recommended: true,
      capabilities: ['text']
    },
    {
      id: 'phi-2-2.7b',
      name: 'Phi-2 2.7B',
      size: '1.6 GB',
      url: 'https://huggingface.co/...',
      capabilities: ['text', 'code']
    }
  ]

  return (
    <div>
      <h1>Local Models</h1>
      <ModelCatalog catalog={catalog} />
      <InstalledModels />
    </div>
  )
}
```

**Tasks**:
- [ ] Create `LocalModelsPage.jsx`
- [ ] Add route to `App.jsx`: `/local-models`
- [ ] Add to sidebar under "System"
- [ ] Show model download progress
- [ ] Add local models to tool config dropdowns (prefix: `local://`)

**Success Criteria**:
- ✅ Can download TinyLlama 1.1B model
- ✅ Can select local model in tool configuration
- ✅ Analyzers work with local model
- ✅ Performance is acceptable (< 5s for analysis)
- ✅ Clear indication when using local vs cloud

---

## Testing Strategy

### Test Pyramid
```
           /\
          /  \    E2E Tests (5%)
         /____\   - Story workflow end-to-end
        /      \
       / Integration (20%)
      /   Tests    \
     /              \
    /  Unit Tests    \  (75%)
   /   (Fast, Many)  \
  /____________________\
```

### Critical Paths to Test
1. **Story Workflow**: Planner → Writer → Illustrator
2. **Character Creation**: From subject image + appearance analysis
3. **Tool Configuration**: Save/load model settings
4. **Image Generation**: Modular generator with presets
5. **Entity CRUD**: Create/read/update/delete for all entity types

### Test Data Strategy
```
tests/fixtures/
├── images/
│   ├── test_portrait.jpg (small, 100KB)
│   └── test_scene.jpg
├── data/
│   ├── test_character.json
│   ├── test_story_theme.json
│   └── test_tool_config.json
└── mocks/
    └── mock_llm_responses.json
```

### Running Tests
```bash
# Backend
docker-compose run --rm api pytest tests/ -v
docker-compose run --rm api pytest tests/smoke/ -v  # Fast sanity check

# Frontend
cd frontend && npm test
cd frontend && npm run test:ui  # Interactive mode

# All tests
./scripts/run_all_tests.sh  # NEW script
```

---

## llama.cpp Integration Details

### Why llama.cpp?
- ✅ Fast inference (C++ core)
- ✅ GGUF format (widely supported)
- ✅ Python bindings available
- ✅ CPU and GPU support
- ✅ Active development

### Recommended Starter Models
1. **TinyLlama 1.1B** (637 MB)
   - Fast, good for testing
   - Use case: Quick analysis, tagging

2. **Phi-2 2.7B** (1.6 GB)
   - Better quality, still fast
   - Use case: Story themes, summaries

3. **LLaMA 2 7B** (4.0 GB)
   - High quality
   - Use case: Story writing, detailed analysis

### Performance Expectations
| Model | Size | Speed (CPU) | Quality | Use Case |
|-------|------|------------|---------|----------|
| TinyLlama 1.1B | 637 MB | ~5 tok/s | Basic | Testing, tags |
| Phi-2 2.7B | 1.6 GB | ~3 tok/s | Good | Themes, summaries |
| LLaMA 2 7B | 4.0 GB | ~1 tok/s | High | Story writing |

### Integration Points
```python
# Tool configuration UI
{
  "tool_name": "story_planner",
  "model": "local://phi-2-2.7b",  # Local model
  "temperature": 0.7
}

# vs

{
  "tool_name": "story_illustrator",
  "model": "gemini/gemini-2.0-flash-exp",  # Cloud model
  "temperature": 0.7
}
```

### Fallback Strategy
- Primary: Cloud (Gemini/OpenAI)
- Fallback: Local (if configured)
- User can choose per-tool

---

## Code Quality Improvements

### Refactoring Targets (Post-Testing)

#### 1. Frontend Component Cleanup
**File**: `Composer.jsx` (910 lines)
```
Current:
  Composer.jsx (910 lines)

Refactor to:
  Composer.jsx (300 lines)
    ├── ComposerHeader.jsx
    ├── PresetSelector.jsx
    ├── PresetLibrary.jsx
    └── ComposerCanvas.jsx
```

**File**: `OutfitAnalyzer.jsx` + `GenericAnalyzer.jsx`
```
Current:
  OutfitAnalyzer.jsx (702 lines)
  GenericAnalyzer.jsx (586 lines)  # 85% duplicate

Refactor to:
  AnalyzerPage.jsx (400 lines)  # Unified component
    ├── AnalyzerUpload.jsx
    ├── AnalyzerResults.jsx
    └── PresetActions.jsx
```

#### 2. Shared Component Library
Create `frontend/src/components/shared/`:
- `Modal.jsx` - Reusable modal wrapper
- `FormField.jsx` - Consistent form inputs
- `LoadingSpinner.jsx` - Loading states
- `ErrorMessage.jsx` - Error display
- `ConfirmDialog.jsx` - Confirmation prompts

#### 3. API Client Standardization
**File**: `frontend/src/api/client.js`
```javascript
// Add consistent error handling
api.interceptors.response.use(
  response => response,
  error => {
    // Log errors with context
    console.error('[API Error]', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data
    })
    throw error
  }
)
```

---

## Updated Roadmap

### Phase 1.6: Testing & Local LLMs (Week of 2025-10-17)
**Goal**: Stable foundation with tests and local inference

#### Week 1: Testing Infrastructure
- [ ] Set up Vitest for frontend (Day 1)
- [ ] Write critical path tests (Day 1-2)
- [ ] Write integration tests for new features (Day 2-3)
- [ ] Add smoke tests (Day 3)
- [ ] Fix any bugs found by tests (Day 3-4)
- [ ] Document testing practices (Day 4)

#### Week 2: Local LLM Integration
- [ ] Research llama.cpp + Python bindings (Day 1)
- [ ] Implement LocalLLMProvider (Day 1-2)
- [ ] Create local model management API (Day 2-3)
- [ ] Build Local Models UI (Day 3)
- [ ] Test with TinyLlama (Day 3-4)
- [ ] Test with larger model (Phi-2) (Day 4)
- [ ] Performance benchmarks (Day 4)
- [ ] Documentation (Day 5)

### Phase 1.7: Code Quality & Performance (Week of 2025-10-24)
**Goal**: Clean, maintainable codebase

#### Week 3: Refactoring
- [ ] Refactor Composer.jsx
- [ ] Unify OutfitAnalyzer + GenericAnalyzer
- [ ] Extract shared components
- [ ] Add PropTypes or TypeScript

#### Week 4: Performance
- [ ] Add pagination to entity browser
- [ ] Implement image lazy loading
- [ ] Add React memoization
- [ ] Bundle size optimization

### Phase 2: Workflow Enhancements (TBD)
- Multi-model workflows (mix local + cloud)
- Workflow templates (save/load)
- Conditional branching
- Error recovery

### Phase 3: Advanced Features (TBD)
- Plugin architecture
- Agent framework
- Cross-domain context
- Permission system

---

## Risk Assessment

### Current Risks

#### High Risk 🔴
1. **No Tests** - Regressions will happen
   - Mitigation: Testing infrastructure (Priority 1)

2. **Large Components** - Hard to maintain/test
   - Mitigation: Refactoring (Phase 1.7)

#### Medium Risk 🟡
1. **Performance Unknowns** - Scaling limits unclear
   - Mitigation: Benchmarking, pagination

2. **Local LLM Quality** - May not match cloud models
   - Mitigation: User choice, clear expectations

#### Low Risk 🟢
1. **Code Duplication** - Technical debt
2. **Bundle Size** - Could be optimized

### Mitigation Strategy
1. **Test First** - Prevent regressions
2. **Incremental** - Small, tested changes
3. **Fallback** - Always have cloud option
4. **Monitor** - Track performance, errors

---

## Success Metrics

### Phase 1.6 Complete When:
- [ ] Backend test coverage > 60%
- [ ] Frontend test coverage > 30%
- [ ] All critical paths tested
- [ ] Local LLM working with ≥1 model
- [ ] Tool configs support local models
- [ ] Zero regressions in manual testing

### Quality Targets:
- Test execution time < 30 seconds (smoke tests)
- Test execution time < 5 minutes (full suite)
- Local model inference < 10 seconds (TinyLlama)
- Zero failing tests in main branch

---

## Development Principles (Updated)

1. **Test-Driven Stability**
   - Write tests for new features
   - Run tests before committing
   - Fix failing tests immediately

2. **Local-First Option**
   - Support local LLMs where possible
   - Clear performance expectations
   - Cloud fallback always available

3. **Incremental Improvements**
   - Small, tested changes
   - One thing at a time
   - Commit working code

4. **User Choice**
   - Local vs cloud per tool
   - Configure, don't hard-code
   - Sensible defaults

5. **Maintain Momentum**
   - Don't let tests block features
   - Refactor with working tests
   - Document learnings

---

## Next Steps (Tomorrow Morning)

1. **Review this plan** ☕
   - Confirm priorities
   - Adjust timeline if needed

2. **Set up testing** (Morning)
   - Install Vitest
   - Write first smoke test
   - Run existing backend tests

3. **Research llama.cpp** (Afternoon)
   - Read docs
   - Choose Python binding
   - Download test model

4. **Start implementation** (Afternoon)
   - Create LocalLLMProvider skeleton
   - Test basic inference
   - Document findings

---

**End of Development Plan - Focus on testing & local LLMs next**
