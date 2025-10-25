# Preset Entity Standardization Pattern

**Last Updated**: 2025-10-23
**Status**: Reference Implementation Complete (Hair Styles)

---

## Overview

All preset-based entities related to image generation should provide a **consistent, unified experience**. This document defines the standard pattern implemented for Hair Styles that should be replicated across all other preset entities.

### Target Entities

All of these should work identically:
- ✅ **Hair Styles** (reference implementation)
- 🔲 Accessories
- 🔲 Art Styles
- 🔲 Clothing Items (partial - has preview generation but missing test images)
- 🔲 Expressions
- 🔲 Hair Colors
- 🔲 Makeup
- 🔲 Visual Styles
- 🔲 Characters (special case - has different structure but should support same operations)

---

## Required Features

Every preset entity must support:

1. **Preview Generation** - Generate a standalone visualization of the preset
2. **Test Image Generation** - Apply the preset to a reference subject (jenny.png)
3. **Visualization Config Assignment** - Custom visualization templates
4. **Gallery Tab** - View all generated images using this preset
5. **Consistent UI** - Same layout, buttons, and interaction patterns

---

## Architecture Pattern

### 1. Backend: API Endpoints

**Location**: `api/routes/presets.py`

All entities use the same preset routes:

```python
# Get preview image
@router.get("/{category}/{preset_id}/preview")
async def get_preset_preview(category: str, preset_id: str)

# Generate/regenerate preview
@router.post("/{category}/{preset_id}/generate-preview")
async def generate_preset_preview(
    category: str,
    preset_id: str,
    background_tasks: BackgroundTasks
)

# Generate test image with jenny.png
@router.post("/{category}/{preset_id}/generate-test-image")
async def generate_test_image(
    category: str,
    preset_id: str,
    background_tasks: BackgroundTasks
)
```

### 2. Backend: Background Task Functions

**CRITICAL**: Background task functions must be defined at **module level**, not nested inside endpoints.

```python
# ✅ CORRECT - Module level function
async def run_preview_generation_job(job_id: str, category: str, preset_id: str):
    """Background task to generate preview and update job"""
    from ai_tools.shared.visualizer import PresetVisualizer
    from api.services.job_queue import get_job_queue_manager
    import asyncio
    import traceback

    try:
        job_manager = get_job_queue_manager()
        job_manager.start_job(job_id)
        job_manager.update_progress(job_id, 0.1, "Loading preset data...")

        # Convert preset dict to Pydantic spec
        preset_data = preset_service.get_preset(category, preset_id)
        if '_metadata' in preset_data:
            del preset_data['_metadata']

        # Map category to spec class
        spec = get_spec_for_category(category, preset_data)

        job_manager.update_progress(job_id, 0.3, "Generating preview image...")

        # Get correct output directory from preset manager
        preset_dir = preset_service.preset_manager._get_preset_dir(category)

        # Generate preview image
        visualizer = PresetVisualizer()
        output_path = await asyncio.to_thread(
            visualizer.visualize,
            category,
            spec,
            str(preset_dir),
            preset_id,
            "standard"
        )

        job_manager.complete_job(job_id, {"output_path": str(output_path)})
        logger.info(f"✅ Preview generated: {output_path}")

    except Exception as e:
        logger.error(f"❌ Preview generation failed: {e}")
        get_job_queue_manager().fail_job(job_id, str(e))

# ❌ WRONG - Nested function inside endpoint
@router.post("/{category}/{preset_id}/generate-preview")
async def generate_preset_preview(...):
    async def generate_preview_task():  # ❌ This won't execute properly!
        ...
```

**Why**: FastAPI's BackgroundTasks scheduler requires functions at module level to execute properly. Nested functions may be queued but never run.

### 3. Backend: JobQueueManager Methods

Use the correct JobQueueManager methods:

```python
# ✅ CORRECT
job_manager.start_job(job_id)
job_manager.update_progress(job_id, 0.5, "Progress message...")
job_manager.complete_job(job_id, result_dict)
job_manager.fail_job(job_id, error_message)

# ❌ WRONG
job_manager.update_job(job_id, status="running")  # Method doesn't exist!
```

### 4. Backend: Directory Structure

**CRITICAL**: Preview images must be saved in the same directory as preset JSON files.

```python
# ✅ CORRECT - Use preset_manager to get directory
preset_dir = preset_service.preset_manager._get_preset_dir(category)
# Returns: /app/presets/{category}/

# ❌ WRONG - Hardcoded output directory
output_dir = f"output/{category}"
# PresetManager won't find the image!
```

**Directory structure**:
```
presets/
  hair_styles/
    {preset_id}.json              # Preset data
    {preset_id}_preview.png       # Preview image (generated)
  accessories/
    {preset_id}.json
    {preset_id}_preview.png
  ...
```

### 5. Frontend: Preview Component Pattern

**Location**: `frontend/src/components/entities/configs/presetsConfig.jsx`

```javascript
function EntityPreview({ entity, onUpdate }) {
  const [generatingJobId, setGeneratingJobId] = useState(null)
  const [jobProgress, setJobProgress] = useState(null)
  const [trackingPresetId, setTrackingPresetId] = useState(null)

  // Reset state if entity changes (prevent overlay on wrong entity)
  useEffect(() => {
    if (trackingPresetId && trackingPresetId !== entity.presetId) {
      setGeneratingJobId(null)
      setJobProgress(null)
      setTrackingPresetId(null)
    }
  }, [entity.presetId, trackingPresetId])

  // Poll for job status
  useEffect(() => {
    if (!generatingJobId) return

    const pollInterval = setInterval(async () => {
      try {
        const response = await api.get(`/jobs/${generatingJobId}`)
        const job = response.data
        setJobProgress(job.progress)

        if (job.status === 'completed') {
          setGeneratingJobId(null)
          setJobProgress(null)
          setTrackingPresetId(null)
          if (onUpdate) onUpdate()  // Refresh preview image
        } else if (job.status === 'failed') {
          setGeneratingJobId(null)
          setJobProgress(null)
          setTrackingPresetId(null)
        }
      } catch (error) {
        console.error('Failed to poll job status:', error)
        setGeneratingJobId(null)
        setJobProgress(null)
        setTrackingPresetId(null)
      }
    }, 1000)

    return () => clearInterval(pollInterval)
  }, [generatingJobId, onUpdate])

  const handleGeneratePreview = async (e) => {
    const button = e.currentTarget
    const originalText = button.textContent

    try {
      button.disabled = true
      button.textContent = '⏳ Queueing...'

      const response = await api.post(`/presets/{category}/${entity.presetId}/generate-preview`)
      const jobId = response.data.job_id

      button.textContent = '✅ Queued!'

      setTimeout(() => {
        setGeneratingJobId(jobId)
        setTrackingPresetId(entity.presetId)  // Track THIS specific entity
        button.textContent = originalText
        button.disabled = false
      }, 500)
    } catch (error) {
      console.error('Failed to queue preview generation:', error)
      button.textContent = '❌ Failed'
      setTimeout(() => {
        button.textContent = originalText
        button.disabled = false
      }, 2000)
    }
  }

  return (
    <div style={{ padding: '1rem' }}>
      {/* Preview Image Container */}
      <div style={{ position: 'relative', marginBottom: '1rem' }}>
        <div style={{
          borderRadius: '8px',
          overflow: 'hidden',
          background: 'rgba(0, 0, 0, 0.3)',
          minHeight: '300px',  // Reserve space for preview
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <LazyImage
            src={`/api/presets/{category}/${entity.presetId}/preview?t=${Date.now()}`}
            alt={entity.title}
            style={{ width: '100%', height: 'auto', display: 'block' }}
            onError={(e) => {
              e.target.style.display = 'none'
              const placeholder = document.createElement('div')
              placeholder.style.cssText = 'font-size: 4rem; color: rgba(255, 255, 255, 0.3);'
              placeholder.textContent = '{icon}'
              e.target.parentElement.appendChild(placeholder)
            }}
          />
        </div>

        {/* Loading Overlay (only show for THIS entity) */}
        {generatingJobId && trackingPresetId === entity.presetId && (
          <div style={{
            position: 'absolute',
            top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            borderRadius: '8px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            minHeight: '300px'
          }}>
            <div style={{ fontSize: '3rem', animation: 'spin 2s linear infinite' }}>
              🎨
            </div>
            <div style={{ color: 'white', fontSize: '0.95rem' }}>
              Generating preview...
            </div>
            {jobProgress !== null && (
              <div style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.85rem' }}>
                {Math.round(jobProgress * 100)}%
              </div>
            )}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <button onClick={handleGeneratePreview} style={{...}}>
        🎨 Generate Preview
      </button>
      <button onClick={handleCreateTestImage} style={{...}}>
        🎨 Create Test Image
      </button>
    </div>
  )
}
```

**Key Points**:
- **Track specific entity**: Use `trackingPresetId` to prevent loading overlay appearing on all entities after refresh
- **Reserve space**: Use `minHeight: '300px'` to prevent layout shift when overlay appears
- **Poll every second**: Check job status every 1000ms
- **Refresh on complete**: Call `onUpdate()` to trigger preview image reload

### 6. Frontend: Entity Configuration

```javascript
export const {category}Config = {
  ...createPresetConfig({
    entityType: '{entity_type}',
    title: '{Title}',
    icon: '{emoji}',
    category: '{category}',
    analyzerPath: '{analyzer-path}'
  }),
  enableGallery: true,  // Enable Gallery tab
  renderPreview: (entity, onUpdate) => <EntityPreview entity={entity} onUpdate={onUpdate} />
}
```

---

## Database Session Handling (CRITICAL)

**Context**: Entities that create database records (like clothing items from outfit analyzer) need proper database session management.

### The Problem

When analyzer tools (like `OutfitAnalyzer`) are created without a database session, they may fall back to old file-based storage instead of using PostgreSQL.

**Bug Example** (October 2025 - Outfit Analyzer):
```python
# ❌ WRONG - AnalyzerService creates OutfitAnalyzer without session
class AnalyzerService:
    def _get_analyzer(self, analyzer_name: str):
        if analyzer_name == "outfit":
            return OutfitAnalyzer(auto_visualize=auto_visualize)
            # No db_session parameter passed!
```

**Result**:
- Outfit analyzer fell back to `ClothingItemsService()` (file-based)
- New items saved to JSON files (which were deleted during migration)
- Items never appeared in PostgreSQL database
- User reported: "I ran outfit analysis but don't see any clothing items"

### The Solution

Analyzer tools should create their own database session when one isn't provided:

```python
# ✅ CORRECT - Analyzer creates session when needed
class OutfitAnalyzer:
    def __init__(
        self,
        db_session = None,
        user_id: Optional[int] = None,
        auto_visualize: bool = True
    ):
        self.db_session = db_session
        self.user_id = user_id
        self.owns_session = (db_session is None)

        if db_session is not None:
            # Use provided session
            from api.services.clothing_items_service_db import ClothingItemServiceDB
            self.clothing_service = ClothingItemServiceDB(db_session, user_id=user_id)
            self.use_db = True
        else:
            # Create session on-the-fly during analysis
            logger.info("Initialized without db_session - will create sessions as needed")
            self.clothing_service = None  # Created per-analysis
            self.use_db = True  # Use database by default, NOT files
```

**During analysis** (create session when needed):

```python
async def aanalyze(self, image_path: Path):
    # Perform analysis...
    analysis = await self.router.acall_structured(...)

    # Save items to database
    created_items = []

    if self.clothing_service is None:
        # Create our own session
        from api.database import get_session
        from api.services.clothing_items_service_db import ClothingItemServiceDB

        async with get_session() as session:
            service = ClothingItemServiceDB(session, user_id=self.user_id)

            for item_data in analysis.clothing_items:
                item_dict = await service.create_clothing_item(
                    category=item_data["category"],
                    item=item_data["item"],
                    # ... other fields
                )
                created_items.append(item_dict)
    else:
        # Use existing service (session provided to __init__)
        for item_data in analysis.clothing_items:
            item_dict = await self.clothing_service.create_clothing_item(...)
            created_items.append(item_dict)

    return {"clothing_items": created_items}
```

### When to Use This Pattern

Use this pattern when your analyzer/tool:
- ✅ Creates database records (clothing items, characters, etc.)
- ✅ May be called from AnalyzerService (without session)
- ✅ May be called from API routes (with session)
- ✅ Needs to work in both contexts

### Testing Checklist

When migrating an entity to PostgreSQL:

- [ ] **Test without session**: Verify analyzer creates its own session
- [ ] **Test with session**: Verify analyzer uses provided session
- [ ] **Test from AnalyzerService**: Verify items saved to PostgreSQL (not files)
- [ ] **Test from API route**: Verify items saved correctly
- [ ] **Check database**: `SELECT COUNT(*) FROM {table}` should increase after analysis
- [ ] **Check file system**: Old JSON files should NOT be created
- [ ] **Check logs**: Should see "will create sessions as needed" or session creation

### Migration Checklist for Other Entities

When migrating characters, visual styles, etc. to PostgreSQL:

1. **Update analyzer tool**:
   - Accept optional `db_session` parameter
   - Create session if not provided
   - Use `get_session()` context manager
   - Fall back to database, NOT files

2. **Update service layer**:
   - Create `{entity}_service_db.py` with SQLAlchemy ORM
   - Keep old `{entity}_service.py` temporarily for migration scripts
   - Use async database operations

3. **Test thoroughly**:
   - Run analysis without session (from AnalyzerService)
   - Run analysis with session (from API route)
   - Verify database records created
   - Verify NO file-based records created

4. **Update documentation**:
   - Add note to docs/guides/preset-entity-pattern.md
   - Update docs/guides/api-reference.md
   - Document in claude.md

---

## Common Mistakes & Fixes

### Mistake 1: Nested Background Task Functions
```python
# ❌ WRONG
@router.post("/generate")
async def endpoint():
    async def background_task():  # Won't execute!
        ...
    background_tasks.add_task(background_task)
```

**Fix**: Move function to module level
```python
# ✅ CORRECT
async def background_task_function(job_id, category, preset_id):
    ...

@router.post("/generate")
async def endpoint():
    background_tasks.add_task(background_task_function, job_id, category, preset_id)
```

### Mistake 2: Wrong Output Directory
```python
# ❌ WRONG
output_path = f"output/{category}/{preset_id}_preview.png"
```

**Fix**: Use preset manager
```python
# ✅ CORRECT
preset_dir = preset_service.preset_manager._get_preset_dir(category)
output_path = preset_dir / f"{preset_id}_preview.png"
```

### Mistake 3: Wrong JobQueueManager Methods
```python
# ❌ WRONG
job_manager.update_job(job_id, status="running", progress=50)
```

**Fix**: Use specific methods
```python
# ✅ CORRECT
job_manager.start_job(job_id)
job_manager.update_progress(job_id, 0.5, "Halfway done...")
job_manager.complete_job(job_id, result)
job_manager.fail_job(job_id, error_message)
```

### Mistake 4: Loading Overlay on All Entities
```javascript
// ❌ WRONG - Shows overlay on all entities
{generatingJobId && (
  <div>Loading...</div>
)}
```

**Fix**: Track specific entity
```javascript
// ✅ CORRECT - Only show on tracked entity
{generatingJobId && trackingPresetId === entity.presetId && (
  <div>Loading...</div>
)}
```

### Mistake 5: Class/Method Name Errors
```python
# ❌ WRONG
from ai_tools.shared.visualizer import Visualizer  # Class doesn't exist
visualizer.generate_preset_visualization()  # Method doesn't exist
```

**Fix**: Use correct names
```python
# ✅ CORRECT
from ai_tools.shared.visualizer import PresetVisualizer
visualizer.visualize(category, spec, output_dir, preset_id, quality)
```

### Mistake 6: Analyzer Creates Entities Without Database Session
```python
# ❌ WRONG - Analyzer falls back to file-based storage
class OutfitAnalyzer:
    def __init__(self):
        self.clothing_service = ClothingItemsService()  # File-based!
```

**Fix**: Create database session when needed (see **Database Session Handling** section above)
```python
# ✅ CORRECT - Use database by default
class OutfitAnalyzer:
    def __init__(self, db_session=None, user_id=None):
        if db_session is not None:
            self.clothing_service = ClothingItemServiceDB(db_session, user_id)
        else:
            self.clothing_service = None  # Create session during analysis

    async def aanalyze(self, image_path):
        if self.clothing_service is None:
            async with get_session() as session:
                service = ClothingItemServiceDB(session, self.user_id)
                # Use service to save items
```

**Impact**: Without this fix, items are saved to JSON files (deleted) instead of PostgreSQL database. See full solution in "Database Session Handling" section.

---

## Implementation Checklist

When adding preview/test generation to a new entity:

### Backend
- [ ] Add category to `category_param_map` in `run_test_generation_job()`
- [ ] Add category to spec mapping in `run_preview_generation_job()`
- [ ] Verify visualizer supports this category in `ai_tools/shared/visualizer.py`
- [ ] Test endpoint: `POST /presets/{category}/{preset_id}/generate-preview`
- [ ] Test endpoint: `POST /presets/{category}/{preset_id}/generate-test-image`
- [ ] Verify images save to `presets/{category}/`
- [ ] Verify preview endpoint serves images: `GET /presets/{category}/{preset_id}/preview`

### Frontend
- [ ] Create `EntityPreview` component in `presetsConfig.jsx`
- [ ] Add `enableGallery: true` to entity config
- [ ] Add `renderPreview` to entity config
- [ ] Test "Generate Preview" button
- [ ] Test "Create Test Image" button
- [ ] Verify loading overlay only appears on correct entity
- [ ] Verify preview image displays after generation completes
- [ ] Test Gallery tab shows generated images

### Testing
- [ ] Generate preview for 2-3 different presets
- [ ] Verify all preview images appear in entity list
- [ ] Verify detail view shows preview
- [ ] Generate test image and check `output/test_generations/{category}/`
- [ ] Refresh page and verify preview images persist
- [ ] Open multiple entities and verify loading overlays don't cross-contaminate

---

## File Structure Reference

```
life-os/
├── api/
│   └── routes/
│       └── presets.py                    # Unified endpoints for all presets
│           ├── run_preview_generation_job()  # Module-level background task
│           ├── run_test_generation_job()     # Module-level background task
│           ├── @router.post("/{category}/{preset_id}/generate-preview")
│           └── @router.post("/{category}/{preset_id}/generate-test-image")
│
├── ai_tools/
│   └── shared/
│       ├── visualizer.py                 # PresetVisualizer class
│       │   └── visualize()               # Main visualization method
│       └── preset.py                     # PresetManager class
│           ├── _get_preset_dir()         # Get directory for category
│           └── get_preview_image_path()  # Get preview image path
│
├── frontend/
│   └── src/
│       └── components/
│           └── entities/
│               └── configs/
│                   └── presetsConfig.jsx     # All preset entity configs
│                       ├── HairStylePreview  # Reference implementation
│                       ├── AccessoriesPreview (TODO)
│                       ├── ArtStylesPreview (TODO)
│                       └── ...
│
└── presets/
    ├── hair_styles/
    │   ├── {preset_id}.json              # Preset data
    │   └── {preset_id}_preview.png       # Preview image
    ├── accessories/
    ├── art_styles/
    └── ...
```

---

## Performance Considerations

- **Preview Generation**: ~20-30 seconds (Gemini 2.5 Flash Image)
- **Test Image Generation**: ~10-20 seconds (depends on complexity)
- **Job Polling**: 1 second intervals (acceptable for < 30 second tasks)
- **Image Size**: Preview images are 1024x1024 PNG (~1-2MB each)

---

## Future Enhancements

Potential improvements to this pattern:

1. **Batch Preview Generation**: Generate previews for all presets without previews
2. **Preview Quality Options**: Allow "standard" vs "hd" quality
3. **Custom Visualization Configs**: Per-preset visualization templates
4. **Preview Caching**: Regenerate only when preset changes
5. **Background Preview Generation**: Auto-generate on preset creation
6. **Preview Variants**: Multiple preview styles (icon, card, detail)

---

## See Also

- `docs/guides/api-reference.md` - Overall backend architecture
- `ROADMAP.md` - Development roadmap
- `ai_tools/shared/visualizer.py` - PresetVisualizer implementation
- `frontend/src/components/entities/configs/clothingItemsConfig.jsx` - Similar pattern for clothing items
