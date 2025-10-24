# Entity Preview Migration Plan

**Last Updated**: 2025-10-24 (Updated with Phase 0-1 completion)
**Goal**: Apply EntityPreviewImage component to all entities and complete ROADMAP 2.14 migration
**Duration**: 4-6 weeks (Phases 0-1 complete, ~2-4 weeks remaining)

---

## ✅ Completion Status

### Phase 0: Image Optimization System - **100% COMPLETE** ✅
- ✅ **0.2**: Preview generation jobs create optimized versions automatically
  - Clothing items: `api/workers/jobs.py` lines 74-122
  - Preset entities: `api/routes/tools.py` lines 91-115
  - Both use ImageOptimizer to create small/medium/large versions
- ✅ **0.3**: Frontend size selection (EntityPreviewImage with `getSizedImageUrl`)
- ✅ **0.4**: On-demand optimization system (`/entity-previews/optimize` + job)
- ✅ Discovery: API endpoint vs filesystem paths limitation documented

### Phase 1: EntityPreviewImage Rollout - **100% COMPLETE** ✅
- ✅ **1.1**: Characters Entity (already had EntityPreviewImage)
- ✅ **1.2**: Visualization Configs Entity (already had EntityPreviewImage)
- ✅ **1.3**: Images Entity (added EntityPreviewImage with `fullWidthDetail`)
- ✅ **1.4**: All 8 preset configs refactored (outfits, hair_styles, hair_colors, visual_styles, art_styles, accessories, expressions, makeup)
- ✅ **1.5**: Job naming standards enforced (preset preview generation)
- ✅ Deleted ~300 lines of manual job polling code
- ✅ All entities now use SSE-based automatic job tracking

### Phase 2: Outfit Previews & LLM Job Audit - **50% COMPLETE**
- ✅ **2.1**: Outfit preview generation - ALREADY COMPLETE
  - Discovered during Phase 1: Outfits are a preset entity
  - Already use `/api/presets/outfits/{id}/preview` endpoint
  - Preview generation works via `run_preset_preview_generation_job`
- ⏳ **2.2**: LLM job audit - TODO (next priority)

### Key Discoveries & Learnings

**1. API Endpoint Limitation**:
- **Problem**: Preset entities serve images via API endpoints (`/api/presets/{category}/{id}/preview`)
- **Impact**: Can't transform API URLs to size variants like filesystem paths
- **Current State**: All sizes (small/medium/large) load same full image for preset entities
- **Solution**: Phase 4 database migration will move preview images to `entity_previews/` directory with filesystem paths
- **Workaround**: Added API endpoint detection in EntityPreviewImage to skip optimization attempts

**2. EntityPreviewImage Component Success**:
- Eliminated ~300 lines of custom job polling code
- SSE-based job tracking works flawlessly (no manual polling needed)
- Auto-detects jobs even if triggered externally
- Stand-in icons work perfectly for entities without previews

**3. Job Naming Standards Enforced**:
- All jobs now follow: `"Create Preview Image ({model_name})"` / `"{Entity Type}: {entity_name}"`
- Established pattern in `clothing_items.py` lines 740-769
- Applied to `presets.py` lines 349-413
- Must fetch entity name from database (never use UUIDs in description)

**4. On-Demand Optimization Works**:
- EntityPreviewImage detects missing sized versions and triggers `/entity-previews/optimize`
- Optimization jobs tracked via SSE
- Only runs when needed (not on every page load)

---

## 📊 Visualization Configs Investigation - SOLVED

**Issue**: User created visualization configs yesterday, but they're not showing in UI today.

**Findings**:
- ✅ **9 configs exist in database** (verified via PostgreSQL)
- ✅ **API endpoint works** (`/visualization-configs/`)
- ⚠️ **Auth requirement**: Endpoint requires authentication
- 🔍 **Likely cause**: Frontend authentication issue or cache problem

**Configs in database**:
1. Hair Color Closeup (hair_color)
2. Facial Expression Drawing Manga (expression)
3. Hair Style on Mannequin (hair_style)
4. Inventory Item (clothing_item)
5. Lifestyle Shot (outfit)
6. Full Body Pose (character)
7. Flat Lay Style (clothing_item)
8. Full Body Display - Default (outfit)
9. Portrait Style - Default (character)

**Solution**: Check frontend authentication headers and clear browser cache.

---

## 📊 Current State Analysis (Post-Phase 1)

### Entity Preview Status Matrix

| Entity Type | EntityPreviewImage | Preview Generation | Storage Location | Status |
|-------------|-------------------|-------------------|-----------------|---------|
| **clothing_items** | ✅ | ✅ (RQ job) | entity_previews/clothing_items/ | **COMPLETE** |
| **characters** | ✅ | ✅ (has reference_image_path) | data/characters/*_ref.png | **COMPLETE** ✅ |
| **visualization_configs** | ✅ | ✅ (has reference_image_path) | data/visualization_configs/*_ref.png | **COMPLETE** ✅ |
| **images** | ✅ | N/A (already images) | output/ → entity_previews/images/ | **COMPLETE** ✅ |
| **outfits** (entity) | ✅ | ✅ (API endpoint) | /api/presets/outfits/{id}/preview | **COMPLETE** ✅ |
| **hair_styles** (entity) | ✅ | ✅ (API endpoint) | /api/presets/hair_styles/{id}/preview | **COMPLETE** ✅ |
| **hair_colors** (entity) | ✅ | ✅ (API endpoint) | /api/presets/hair_colors/{id}/preview | **COMPLETE** ✅ |
| **expressions** (entity) | ✅ | ✅ (API endpoint) | /api/presets/expressions/{id}/preview | **COMPLETE** ✅ |
| **makeup** (entity) | ✅ | ✅ (API endpoint) | /api/presets/makeup/{id}/preview | **COMPLETE** ✅ |
| **accessories** (entity) | ✅ | ✅ (API endpoint) | /api/presets/accessories/{id}/preview | **COMPLETE** ✅ |
| **visual_styles** (entity) | ✅ | ✅ (API endpoint) | /api/presets/visual_styles/{id}/preview | **COMPLETE** ✅ |
| **art_styles** (entity) | ✅ | ✅ (API endpoint) | /api/presets/art_styles/{id}/preview | **COMPLETE** ✅ |
| **stories** | ❌ | N/A (has illustrations) | output/workflows/story/ | **No preview needed** |
| **board_games** | ❌ | ❌ | N/A | **Low priority** |
| **story_themes** (text) | N/A | N/A | presets/story_themes/ | **Text only** |
| **story_prose_styles** (text) | N/A | N/A | presets/story_prose_styles/ | **Text only** |
| **story_audiences** (text) | N/A | N/A | presets/story_audiences/ | **Text only** |

### Key Findings (Updated)

1. ✅ **13 entity types** now have complete EntityPreviewImage + SSE job tracking
2. ✅ **All preset entities** (8 categories) use EntityPreviewImage with API endpoints
3. ⚠️ **API endpoint limitation**: Preset entities can't use optimized sizes until Phase 4 migration
4. ✅ **Job naming standards** enforced across all preview generation endpoints
5. ✅ **SSE-based job tracking** eliminates need for manual polling (saved ~300 lines of code)
6. ⏳ **Phase 4 needed**: Migrate preset entities to database for optimized image support
7. ⏳ **Phase 2 still TODO**: LLM job audit to ensure all tool endpoints spawn jobs

---

## 📋 Job Naming Standard (Established Phase 0)

**CRITICAL**: All jobs created from here on must follow this standard for consistency and usability.

### Title Format
```
"{Action} {Object} ({Context})"
```

**Examples:**
- `"Create Preview Image (gemini-2.5-flash-image)"` - Shows what model is being used
- `"Generate Preview Image (medium)"` - Shows what size variant
- `"Analyze Outfit (gemini-2.0-flash-exp)"` - For analysis jobs
- `"Generate Story (claude-3-5-sonnet)"` - For workflow jobs

**Rules:**
- Action verb: Create, Generate, Analyze, Process, etc.
- Object: What's being created/analyzed
- Context in parentheses: Model name, size, or other relevant detail
- **Strip `"gemini/"` prefix** from model names for cleaner display (e.g., use `"gemini-2.5-flash-image"` not `"gemini/gemini-2.5-flash-image"`)

### Description Format
```
"{Entity Type}: {human_readable_name}"
```

**Examples:**
- `"Clothing Item: ruched neck tub scarf"`
- `"Character: Jenny"`
- `"Outfit: Summer Beach Day"`
- `"Hair Style: Messy Bun"`

**Rules:**
- Entity type in title case (e.g., "Clothing Item" not "clothing_item")
- **Fetch actual entity name from database** (never use UUIDs in description)
- For batch operations: `"Batch: 15 clothing items"`

### Implementation Pattern

```python
# Get entity info for better job title/description
service = EntityServiceDB(db, user_id=None)
entity = await service.get_entity(entity_id)

if not entity:
    raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

# Get visualization config to determine model
from api.services.visualization_config_service_db import VisualizationConfigServiceDB
config_service = VisualizationConfigServiceDB(db, user_id=None)
config_dict = await config_service.get_default_config("entity_type")

# Extract model name (or use default)
model_name = "gemini-2.5-flash-image"  # default
if config_dict and 'model' in config_dict:
    model_name = config_dict['model']
    # Strip "gemini/" prefix if present for cleaner display
    if model_name.startswith("gemini/"):
        model_name = model_name[len("gemini/"):]

# Create job with descriptive title and description
job_id = get_job_queue_manager().create_job(
    job_type=JobType.GENERATE_IMAGE,
    title=f"Create Preview Image ({model_name})",
    description=f"Entity Type: {entity['name']}",
    metadata={
        'entity_type': 'entity_type',
        'entity_id': entity_id
    }
)
```

**Reference Implementation**: See `api/routes/clothing_items.py` lines 740-769 for complete example.

---

## 🎯 Implementation Plan (5 Phases)

### **Phase 0: Image Optimization System** (2-3 days)

Add automatic image resizing/caching to EntityPreviewImage component.

**Problem**: Preview images are 1MB+ each. Loading entity lists with 50+ items causes long load times and excessive bandwidth usage.

**Solution**: Automatically generate small (100x100px) and medium (600x600px) versions of all preview images.

#### 0.1 Backend - Image Resizing Service (1 day)

**Create**: `api/services/image_optimizer.py`

```python
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional, Dict

class ImageOptimizer:
    """
    Creates cached, optimized versions of preview images

    Sizes:
    - small: 100x100px (for grid cards)
    - medium: 600x600px (for preview panels)
    - full: Original resolution (for detail view)
    """

    SIZES = {
        'small': (100, 100),
        'medium': (600, 600),
        'full': None  # Original size
    }

    def optimize_preview(
        self,
        source_path: str,
        entity_type: str,
        entity_id: str
    ) -> Dict[str, str]:
        """
        Generate optimized versions of preview image

        Args:
            source_path: Path to original preview image
            entity_type: Entity type (e.g., 'clothing_item', 'character')
            entity_id: Entity UUID

        Returns:
            Dict with paths to all sizes:
            {
                'small': '/entity_previews/{type}/{id}_preview_small.png',
                'medium': '/entity_previews/{type}/{id}_preview_medium.png',
                'full': '/entity_previews/{type}/{id}_preview.png'
            }
        """
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source image not found: {source_path}")

        # Load original image
        img = Image.open(source)

        # Output directory
        output_dir = Path(f"entity_previews/{entity_type}")
        output_dir.mkdir(parents=True, exist_ok=True)

        result = {}

        # Generate each size
        for size_name, dimensions in self.SIZES.items():
            if dimensions is None:
                # Full size - just reference original
                result['full'] = f"/entity_previews/{entity_type}/{entity_id}_preview.png"
                continue

            # Resize with high-quality downsampling
            resized = img.copy()
            resized.thumbnail(dimensions, Image.Resampling.LANCZOS)

            # Save optimized version with compression
            output_path = output_dir / f"{entity_id}_preview_{size_name}.png"
            resized.save(output_path, optimize=True, quality=85)

            result[size_name] = f"/entity_previews/{entity_type}/{entity_id}_preview_{size_name}.png"

        return result

    def cleanup_old_versions(self, entity_type: str, entity_id: str):
        """Delete old optimized versions when preview is regenerated"""
        output_dir = Path(f"entity_previews/{entity_type}")

        for size_name in ['small', 'medium']:
            old_file = output_dir / f"{entity_id}_preview_{size_name}.png"
            if old_file.exists():
                old_file.unlink()
```

#### 0.2 Update Preview Generation Jobs (1 day)

Modify all preview generation jobs to create optimized versions automatically.

**Files to update**:
- `api/workers/jobs.py` - `preview_generation_job` (clothing items)
- `api/workers/jobs.py` - `preset_preview_generation_job` (all JSON entities)
- Future: `outfit_preview_generation_job` (Phase 2)

**Pattern** (apply to all preview generation jobs):

```python
def preview_generation_job(job_id: str, item_id: str):
    """Generate preview image for a clothing item"""
    from api.services.image_optimizer import ImageOptimizer

    async def _async_preview_generation():
        job_manager = get_job_queue_manager()
        job_manager.start_job(job_id)

        async with get_session() as session:
            service = ClothingItemServiceDB(session, user_id=None)

            # Generate full-resolution preview
            item = await service.generate_preview(item_id)
            preview_path = item.get('preview_image_path')

            if not preview_path:
                job_manager.fail_job(job_id, "Preview generation failed")
                return

            # Create optimized versions
            optimizer = ImageOptimizer()
            optimizer.cleanup_old_versions('clothing_item', item_id)

            # Convert web path to filesystem path
            fs_path = preview_path.replace('/entity_previews/', 'entity_previews/')
            optimized_paths = optimizer.optimize_preview(
                fs_path,
                'clothing_item',
                item_id
            )

            # Complete job with all paths
            job_manager.complete_job(job_id, {
                'entity_type': 'clothing_item',
                'entity_id': item_id,
                'preview_image_path': optimized_paths['full'],
                'preview_image_small': optimized_paths['small'],
                'preview_image_medium': optimized_paths['medium'],
                # ... other item data ...
            })

    run_async_job(_async_preview_generation)
```

#### 0.3 Frontend - EntityPreviewImage Size Selection (4 hours)

Update EntityPreviewImage to automatically load the appropriate size based on `size` prop.

**File**: `frontend/src/components/entities/EntityPreviewImage.jsx`

**Changes**:

```jsx
function EntityPreviewImage({
  entityType,
  entityId,
  previewImageUrl,
  standInIcon = '🖼️',
  size = 'medium',  // 'small', 'medium', or 'large'
  shape = 'square',
  onUpdate
}) {
  // Helper: Determine which size to load based on size prop
  const getSizedImageUrl = (baseUrl, sizeRequested) => {
    if (!baseUrl) return null

    // Extract base path (remove existing size suffix if present)
    const basePath = baseUrl.replace(/_(?:small|medium)\.png$/, '.png')

    // Map size prop to image size
    const sizeMap = {
      'small': '_small.png',   // 100x100px
      'medium': '_medium.png', // 600x600px
      'large': '.png'          // Full resolution
    }

    // Replace extension with sized version
    return basePath.replace('.png', sizeMap[sizeRequested] || sizeMap['medium'])
  }

  const [currentImageUrl, setCurrentImageUrl] = useState(
    getSizedImageUrl(previewImageUrl, size)
  )

  // Update image URL when previewImageUrl prop changes
  useEffect(() => {
    if (!previewImageUrl) {
      setCurrentImageUrl(null)
      return
    }

    const urlWithSize = getSizedImageUrl(previewImageUrl, size)
    const urlWithTimestamp = `${urlWithSize}?t=${Date.now()}`
    setCurrentImageUrl(urlWithTimestamp)
  }, [previewImageUrl, size])

  // ... rest of component unchanged ...
}
```

#### 0.4 Testing (2 hours)

**Manual tests**:
1. Generate preview for clothing item
2. Verify 3 files created: `_small.png`, `_medium.png`, and `.png` (full)
3. Check file sizes: small ~5-10KB, medium ~50-100KB, full ~1MB
4. Load entity list in UI - verify small images load
5. Open preview panel - verify medium images load
6. Open detail view - verify full images load

**Success Criteria**:
- ✅ Small previews load 100x100px versions (~5-10KB instead of 1MB)
- ✅ Medium previews load 600x600px versions (~50-100KB)
- ✅ Detail views load full resolution
- ✅ Old cached versions deleted when preview regenerated
- ✅ Page load times improve by 80-90% for entity lists
- ✅ No visual quality degradation at appropriate sizes

---

### **Phase 1: Quick Wins - EntityPreviewImage Rollout** (2-3 days)

Apply EntityPreviewImage component to all entities that already have images.

#### 1.1 Characters Entity (1 hour)

**File**: `frontend/src/components/entities/configs/charactersConfig.jsx`

**Changes**:
- Import EntityPreviewImage
- Add to `renderCard`: Use 'small' size
- Add to `renderPreview`: Use 'medium' size
- Add to `renderDetail`: Use 'large' size
- Image source: `item.referenceImage` (already exists in character data)
- Stand-in icon: '👤'
- No backend work needed - just display existing reference images

**Example**:
```jsx
renderCard: (item) => (
  <div className="entity-card">
    <EntityPreviewImage
      entityType="character"
      entityId={item.id}
      previewImageUrl={item.referenceImage}
      standInIcon="👤"
      size="small"
      shape="square"
    />
    {/* ... rest of card ... */}
  </div>
)
```

#### 1.2 Visualization Configs Entity (1 hour)

**File**: `frontend/src/components/entities/configs/visualizationConfigsConfig.jsx`

**Changes**:
- Import EntityPreviewImage
- Replace LazyImage with EntityPreviewImage in renderCard
- Image source: `entity.data.reference_image_path`
- Stand-in icon: '🎨'
- **Fix authentication issue** - Verify frontend sends auth headers
- No backend work needed

#### 1.3 Images Entity (1 hour)

**File**: `frontend/src/components/entities/configs/imagesConfig.jsx`

**Changes**:
- Import EntityPreviewImage
- Add EntityPreviewImage to card and preview views
- Image source: `item.file_path` (image entities ARE images)
- Stand-in icon: '🖼️'
- No backend work needed

#### 1.4 Entity Categories (JSON Files - 4-6 hours)

Add EntityPreviewImage to all JSON-based entity categories.

**Categories to update**:
- hair_styles (24 files)
- hair_colors (18 files)
- expressions (16 files)
- makeup (12 files)
- accessories (12 files)
- visual_styles (64 files)
- art_styles (12 files)
- story_themes, story_prose_styles, story_audiences

**Files to create/update**:
- `frontend/src/components/entities/configs/hairStylesConfig.jsx`
- `frontend/src/components/entities/configs/hairColorsConfig.jsx`
- `frontend/src/components/entities/configs/expressionsConfig.jsx`
- `frontend/src/components/entities/configs/makeupConfig.jsx`
- `frontend/src/components/entities/configs/accessoriesConfig.jsx`
- `frontend/src/components/entities/configs/visualStylesConfig.jsx`
- `frontend/src/components/entities/configs/artStylesConfig.jsx`
- `frontend/src/components/entities/configs/storyThemesConfig.jsx`
- `frontend/src/components/entities/configs/storyProseStylesConfig.jsx`
- `frontend/src/components/entities/configs/storyAudiencesConfig.jsx`

**Pattern for each config**:

```jsx
import EntityPreviewImage from '../EntityPreviewImage'
import api from '../../../api/client'

function HairStyleCard({ entity }) {
  return (
    <div className="entity-card">
      <EntityPreviewImage
        entityType="hair_style"
        entityId={entity.preset_id}
        previewImageUrl={`/presets/hair_styles/${entity.preset_id}_preview.png`}
        standInIcon="💇"
        size="small"
      />
      {/* ... rest of card ... */}
    </div>
  )
}

function HairStylePreview({ entity, onUpdate }) {
  const handleGeneratePreview = async () => {
    await api.post(`/presets/hair_styles/${entity.preset_id}/generate-preview`)
  }

  return (
    <div>
      <EntityPreviewImage
        entityType="hair_style"
        entityId={entity.preset_id}
        previewImageUrl={`/presets/hair_styles/${entity.preset_id}_preview.png`}
        standInIcon="💇"
        size="medium"
        onUpdate={onUpdate}
      />

      <button onClick={handleGeneratePreview}>
        🎨 Generate Preview
      </button>
    </div>
  )
}

export const hairStylesConfig = {
  entityType: 'hair_style',
  title: 'Hair Styles',
  icon: '💇',
  // ... rest of config ...
  renderCard: (entity) => <HairStyleCard entity={entity} />,
  renderPreview: (entity, onUpdate) => <HairStylePreview entity={entity} onUpdate={onUpdate} />,
}
```

**Stand-in icons**:
- hair_styles: '💇'
- hair_colors: '🎨'
- expressions: '😊'
- makeup: '💄'
- accessories: '👑'
- visual_styles: '🖼️'
- art_styles: '🎨'
- story_themes: '📖'
- story_prose_styles: '✍️'
- story_audiences: '👥'

#### 1.5 Register New Entity Configs (1 hour)

**File**: `frontend/src/App.jsx` (or wherever entity routes are defined)

Add routes for all new entity types:
```jsx
<Route path="/entities/hair-styles" element={<EntityBrowser config={hairStylesConfig} />} />
<Route path="/entities/hair-colors" element={<EntityBrowser config={hairColorsConfig} />} />
// ... etc for all entity types
```

**Success Criteria**:
- ✅ 12+ entity types show EntityPreviewImage
- ✅ All preview images auto-update when generation completes
- ✅ Stand-in icons display when no preview exists
- ✅ "Generate Preview" buttons work for all categories
- ✅ All entity types accessible via navigation

---

### **Phase 2: Outfit Previews & LLM Job Audit** (2-3 days)

#### 2.1 Outfit Preview Generation (1-2 days)

Outfits are database entities but lack preview generation system.

**2.1.1 Backend - Outfit Preview Generation Service (3-4 hours)**

**File**: `api/services/outfit_service_db.py` (create or extend existing)

```python
async def generate_preview(self, outfit_id: str) -> dict:
    """Generate preview image for outfit using PresetVisualizer"""
    from ai_tools.shared.visualizer import PresetVisualizer
    from api.services.visualization_config_service_db import VisualizationConfigServiceDB
    from api.services.image_optimizer import ImageOptimizer

    # Load outfit from database
    outfit = await self.get_outfit(outfit_id)
    if not outfit:
        raise ValueError(f"Outfit {outfit_id} not found")

    # Get visualization config for outfits
    viz_service = VisualizationConfigServiceDB(self.session, user_id=None)
    viz_config = await viz_service.get_default_config("outfit")

    # Use PresetVisualizer to render outfit
    visualizer = PresetVisualizer()
    output_file = f"entity_previews/outfits/{outfit_id}_preview.png"

    # Generate preview
    preview_path = await visualizer.create_preset_preview(
        preset_data=outfit_to_dict(outfit),
        output_file=output_file,
        category="outfit",
        viz_config=viz_config
    )

    # Create optimized versions
    optimizer = ImageOptimizer()
    optimizer.cleanup_old_versions('outfit', outfit_id)
    optimized_paths = optimizer.optimize_preview(
        output_file,
        'outfit',
        outfit_id
    )

    # Update database with preview paths
    outfit.preview_image_path = optimized_paths['full']
    outfit.preview_image_small = optimized_paths['small']
    outfit.preview_image_medium = optimized_paths['medium']
    await self.session.commit()

    return await self.get_outfit(outfit_id)
```

**2.1.2 API Endpoint (1 hour)**

**File**: `api/routes/outfits.py` - Add preview generation endpoint

```python
@router.post("/{outfit_id}/generate-preview")
async def generate_outfit_preview(
    outfit_id: str,
    async_mode: bool = Query(True, description="Run in background"),
    db: AsyncSession = Depends(get_db)
):
    """Generate preview image for outfit (queues RQ job)"""
    from api.services.job_queue import get_job_queue_manager
    from api.services.rq_worker import get_rq_service
    from api.models.jobs import JobType

    # Get outfit info for better job title/description
    service = OutfitServiceDB(db, user_id=None)
    outfit = await service.get_outfit(outfit_id)

    if not outfit:
        raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found")

    # Get visualization config to determine model
    from api.services.visualization_config_service_db import VisualizationConfigServiceDB
    config_service = VisualizationConfigServiceDB(db, user_id=None)
    config_dict = await config_service.get_default_config("outfit")

    # Extract model name (or use default)
    model_name = "gemini-2.5-flash-image"  # default
    if config_dict and 'model' in config_dict:
        model_name = config_dict['model']
        # Strip "gemini/" prefix if present for cleaner display
        if model_name.startswith("gemini/"):
            model_name = model_name[len("gemini/"):]

    # Create job with descriptive title and description
    job_id = get_job_queue_manager().create_job(
        job_type=JobType.GENERATE_IMAGE,
        title=f"Create Preview Image ({model_name})",
        description=f"Outfit: {outfit.get('suggested_name', outfit_id)}",
        metadata={
            "entity_type": "outfit",
            "entity_id": outfit_id
        }
    )

    # Enqueue RQ job
    get_rq_service().enqueue(
        outfit_preview_generation_job,
        job_id,
        outfit_id,
        priority='normal'
    )

    return {"job_id": job_id, "status": "queued"}
```

**2.1.3 RQ Worker Job (1 hour)**

**File**: `api/workers/jobs.py` - Add outfit preview job

```python
def outfit_preview_generation_job(job_id: str, outfit_id: str):
    """Generate preview image for an outfit"""
    async def _async_preview_generation():
        try:
            job_manager = get_job_queue_manager()
            job_manager.start_job(job_id)
            job_manager.update_progress(job_id, 0.1, "Loading outfit...")

            async with get_session() as session:
                service = OutfitServiceDB(session, user_id=None)

                job_manager.update_progress(job_id, 0.3, "Generating preview image...")
                outfit = await service.generate_preview(outfit_id)

                if not outfit:
                    job_manager.fail_job(job_id, f"Outfit {outfit_id} not found")
                    return

                job_manager.update_progress(job_id, 0.9, "Finalizing...")

                # Complete job with outfit data
                job_manager.complete_job(job_id, {
                    'entity_type': 'outfit',
                    'entity_id': outfit['outfit_id'],
                    'preview_image_path': outfit['preview_image_path'],
                    'preview_image_small': outfit.get('preview_image_small'),
                    'preview_image_medium': outfit.get('preview_image_medium')
                })

        except Exception as e:
            logger.error(f"Outfit preview generation failed: {e}", exc_info=True)
            get_job_queue_manager().fail_job(job_id, str(e))

    run_async_job(_async_preview_generation)
```

**2.1.4 Frontend - Outfit Config (1 hour)**

**File**: `frontend/src/components/entities/configs/outfitsConfig.jsx` (create or extend)

- Add EntityPreviewImage to renderCard, renderPreview, renderDetail
- Add "Generate Preview" button
- Pattern same as clothing_items

#### 2.2 LLM Job Audit (CRITICAL - 1 day)

**Principle**: **Every LLM call must spawn an RQ job. Nothing should block the UI.**

**Action**: Audit all tool endpoints to ensure 100% compliance.

**Files to audit**:
- `api/routes/tools.py` - All analyzer endpoints
- `api/routes/analyzers.py` - If separate
- `api/routes/workflows.py` - Story generation, etc.
- `api/routes/generators.py` - Image generation endpoints
- Any route that calls `router.agenerate()` or similar LLM methods

**Pattern to enforce**:

```python
@router.post("/tools/{tool_name}/analyze")
async def run_tool(
    tool_name: str,
    file: UploadFile = File(...),
    async_mode: bool = Query(True, description="Run in background (recommended)")
):
    """
    Run analyzer tool

    ALWAYS returns job_id immediately.
    Frontend tracks progress via SSE job stream.
    """
    if async_mode:
        # Get model for this tool from config
        from api.services.tool_configs import load_models_config
        models_config = await load_models_config()
        model = models_config.get('defaults', {}).get(tool_name, 'gemini/gemini-2.0-flash-exp')

        # Strip "gemini/" prefix for cleaner display
        model_display = model
        if model_display.startswith("gemini/"):
            model_display = model_display[len("gemini/"):]

        # Format tool name for display (e.g., "outfit_analyzer" → "Outfit")
        tool_display = tool_name.replace('_analyzer', '').replace('_', ' ').title()

        # Create job with descriptive title
        job_id = get_job_queue_manager().create_job(
            job_type=JobType.ANALYZE,
            title=f"Analyze {tool_display} ({model_display})",
            description=f"File: {file.filename}",
            metadata={
                "tool_name": tool_name,
                "file_name": file.filename
            }
        )

        # Enqueue RQ job
        get_rq_service().enqueue(
            tool_execution_job,
            job_id,
            tool_name,
            temp_file_path,
            priority='normal'
        )

        return {"job_id": job_id, "status": "queued"}
    else:
        # ONLY for testing/debugging - should not be used in production
        logger.warning(f"Synchronous mode used for {tool_name} - this blocks the UI!")
        return await execute_tool_sync(tool_name, temp_file_path)
```

**Checklist**:
- [ ] Character appearance analyzer spawns job
- [ ] Outfit analyzer spawns job (already done)
- [ ] All preset analyzers spawn jobs
- [ ] Image generators spawn jobs
- [ ] Story workflow spawns job (check if done)
- [ ] No synchronous LLM calls in request handlers
- [ ] All tools return job_id
- [ ] Frontend tracks all jobs via SSE

**Violations to fix**:
- Any synchronous LLM calls that block request/response
- Tools that don't return job_id
- Frontend components that use `await` on LLM responses

**Success Criteria**:
- ✅ 100% of LLM calls spawn RQ jobs
- ✅ Zero blocking LLM calls in UI
- ✅ All tools trackable in job queue
- ✅ async_mode=False only used for testing

---

### **Phase 3: Testing Infrastructure** (2-3 days)

Add comprehensive test suite to prevent regressions.

#### 3.1 Backend Tests (2 days)

**Create test structure**:
```
tests/
├── unit/
│   ├── test_image_optimizer.py
│   ├── test_preview_generation.py
│   └── test_job_spawning.py
├── integration/
│   ├── test_clothing_items_api.py
│   ├── test_preview_endpoints.py
│   └── test_job_flows.py
└── e2e/
    └── test_preview_generation_flow.py
```

**3.1.1 Unit Tests (1 day)**

**File**: `tests/unit/test_image_optimizer.py`

```python
import pytest
from pathlib import Path
from api.services.image_optimizer import ImageOptimizer

def test_optimize_preview_creates_all_sizes(tmp_path):
    """Test that optimizer creates small, medium, full versions"""
    # Create test image
    from PIL import Image
    test_img = Image.new('RGB', (1024, 1024), color='red')
    test_img.save(tmp_path / 'test.png')

    optimizer = ImageOptimizer()
    paths = optimizer.optimize_preview(
        str(tmp_path / 'test.png'),
        'test_entity',
        'test_id'
    )

    # Verify all paths returned
    assert 'small' in paths
    assert 'medium' in paths
    assert 'full' in paths

    # Verify files exist
    assert Path(paths['small'].replace('/entity_previews/', 'entity_previews/')).exists()
    assert Path(paths['medium'].replace('/entity_previews/', 'entity_previews/')).exists()

def test_small_image_size():
    """Verify small images are 100x100px"""
    # ... test implementation

def test_medium_image_size():
    """Verify medium images are 600x600px"""
    # ... test implementation

def test_cleanup_removes_old_versions():
    """Test that cleanup removes old cached images"""
    # ... test implementation
```

**File**: `tests/unit/test_preview_generation.py`

```python
def test_preview_generation_spawns_job():
    """Test that preview generation creates RQ job"""
    response = client.post("/clothing-items/test_id/generate-preview")

    assert response.status_code == 200
    assert "job_id" in response.json()

    # Verify job exists in queue
    job_id = response.json()["job_id"]
    job = get_job_queue_manager().get_job(job_id)
    assert job is not None

def test_job_metadata_includes_entity_info():
    """Test that job metadata has entity_type and entity_id"""
    response = client.post("/clothing-items/test_id/generate-preview")
    job_id = response.json()["job_id"]

    job = get_job_queue_manager().get_job(job_id)
    assert job.metadata["entity_type"] == "clothing_item"
    assert job.metadata["entity_id"] == "test_id"
```

**File**: `tests/unit/test_job_spawning.py`

```python
def test_all_tools_spawn_jobs():
    """Test that all tool endpoints spawn RQ jobs"""
    tools = [
        'character_appearance_analyzer',
        'outfit_analyzer',
        'hair_style_analyzer',
        # ... all tools
    ]

    for tool in tools:
        response = client.post(f"/tools/{tool}/analyze", files={'file': dummy_image})
        assert response.status_code == 200
        assert "job_id" in response.json(), f"{tool} did not return job_id"
```

**3.1.2 Integration Tests (1 day)**

**File**: `tests/integration/test_job_flows.py`

```python
def test_preview_generation_end_to_end():
    """Test complete preview generation flow"""
    # 1. Create clothing item
    item = create_test_clothing_item()

    # 2. Queue preview job
    response = client.post(f"/clothing-items/{item.id}/generate-preview")
    job_id = response.json()["job_id"]

    # 3. Wait for job to complete (with timeout)
    job = wait_for_job_completion(job_id, timeout=60)
    assert job.status == "completed"

    # 4. Verify preview images exist
    assert Path(f"entity_previews/clothing_items/{item.id}_preview_small.png").exists()
    assert Path(f"entity_previews/clothing_items/{item.id}_preview_medium.png").exists()
    assert Path(f"entity_previews/clothing_items/{item.id}_preview.png").exists()

    # 5. Verify job result has correct structure
    assert job.result["entity_type"] == "clothing_item"
    assert job.result["entity_id"] == item.id
    assert "preview_image_small" in job.result
    assert "preview_image_medium" in job.result

def test_llm_calls_never_block():
    """Test that no LLM call blocks the request/response"""
    import time

    # All tool endpoints should return immediately with job_id
    start_time = time.time()
    response = client.post("/tools/outfit_analyzer/analyze", files={'file': dummy_image})
    elapsed = time.time() - start_time

    # Should return in <1 second (not wait for LLM)
    assert elapsed < 1.0, f"Tool endpoint took {elapsed}s - likely blocking on LLM"
    assert "job_id" in response.json()
```

#### 3.2 Frontend Tests (1 day)

**Install dependencies**:
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

**Create test files**:
```
frontend/src/__tests__/
├── EntityPreviewImage.test.jsx
├── clothingItemsConfig.test.jsx
└── jobTracking.test.jsx
```

**File**: `frontend/src/__tests__/EntityPreviewImage.test.jsx`

```jsx
import { render, waitFor } from '@testing-library/react'
import EntityPreviewImage from '../components/entities/EntityPreviewImage'

test('loads correct size based on size prop', () => {
  const { getByRole } = render(
    <EntityPreviewImage
      entityType="clothing_item"
      entityId="test_id"
      previewImageUrl="/entity_previews/clothing_items/test_id_preview.png"
      size="small"
    />
  )

  const img = getByRole('img')
  expect(img.src).toContain('_small.png')
})

test('loads medium size by default', () => {
  const { getByRole } = render(
    <EntityPreviewImage
      entityType="clothing_item"
      entityId="test_id"
      previewImageUrl="/entity_previews/clothing_items/test_id_preview.png"
    />
  )

  const img = getByRole('img')
  expect(img.src).toContain('_medium.png')
})

test('detects and displays job progress', async () => {
  // Mock job stream
  mockJobStream([
    { job_id: 'job1', status: 'running', progress: 0.5, metadata: { entity_type: 'clothing_item', entity_id: 'test_id' } }
  ])

  const { getByTestId } = render(
    <EntityPreviewImage
      entityType="clothing_item"
      entityId="test_id"
      previewImageUrl="/entity_previews/clothing_items/test_id_preview.png"
    />
  )

  // Should show loading indicator
  await waitFor(() => {
    expect(getByTestId('loading-indicator')).toBeInTheDocument()
  })
})

test('auto-updates image when job completes', async () => {
  // ... test implementation
})

test('shows stand-in icon when no preview exists', () => {
  const { getByText } = render(
    <EntityPreviewImage
      entityType="clothing_item"
      entityId="test_id"
      previewImageUrl={null}
      standInIcon="👕"
    />
  )

  expect(getByText('👕')).toBeInTheDocument()
})
```

#### 3.3 CI/CD Integration (4 hours)

**Create/update**: `.github/workflows/test.yml`

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: lifeos_test
          POSTGRES_USER: lifeos
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx

      - name: Run tests
        run: |
          pytest tests/ -v --cov=api --cov-report=term --cov-report=html
        env:
          DATABASE_URL: postgresql+asyncpg://lifeos:test_password@localhost:5432/lifeos_test
          REDIS_URL: redis://localhost:6379/0

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm install

      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json
```

**Success Criteria**:
- ✅ 80%+ backend test coverage
- ✅ 40%+ frontend test coverage
- ✅ All critical paths tested (preview generation, job spawning, image optimization)
- ✅ Tests run in CI/CD on every PR
- ✅ Coverage reports generated
- ✅ No flaky tests (all tests deterministic)

---

### **Phase 4: Database Migration** (2-3 weeks)

Migrate all JSON-based entity categories to PostgreSQL database.

**Terminology**: ✅ **NO "presets" in database schema** - these are all **entities** now.

#### 4.1 Database Schema Design (1 day)

**Use separate tables per entity type** (as preferred for type safety).

**Create Alembic migration**: `alembic/versions/xxx_create_entity_tables.py`

```sql
-- Example: hair_styles table
CREATE TABLE hair_styles (
  hair_style_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(50),  -- e.g., "long", "short", "curly"
  style_data JSONB,      -- Flexible for entity-specific fields
  preview_image_small VARCHAR(500),
  preview_image_medium VARCHAR(500),
  preview_image_full VARCHAR(500),
  source_image VARCHAR(500),
  user_id INTEGER REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  archived BOOLEAN DEFAULT FALSE,
  archived_at TIMESTAMP,
  CONSTRAINT hair_styles_name_unique UNIQUE (name, user_id)
);

CREATE INDEX idx_hair_styles_user ON hair_styles(user_id);
CREATE INDEX idx_hair_styles_archived ON hair_styles(archived);
CREATE INDEX idx_hair_styles_category ON hair_styles(category);
CREATE INDEX idx_hair_styles_name_search ON hair_styles USING gin(to_tsvector('english', name));

-- Add updated_at trigger
CREATE TRIGGER update_hair_styles_updated_at
  BEFORE UPDATE ON hair_styles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

**Repeat for all entity types**:
- `hair_colors`
- `expressions`
- `makeup`
- `accessories`
- `visual_styles`
- `art_styles`
- `story_themes`
- `story_prose_styles`
- `story_audiences`

#### 4.2 Create Repositories (1-2 days)

Create one repository per entity type (following existing pattern).

**Pattern**: Same as `ClothingItemRepository`

**Files to create**:
- `api/repositories/hair_style_repository.py`
- `api/repositories/hair_color_repository.py`
- `api/repositories/expression_repository.py`
- `api/repositories/makeup_repository.py`
- `api/repositories/accessories_repository.py`
- `api/repositories/visual_style_repository.py`
- `api/repositories/art_style_repository.py`
- `api/repositories/story_theme_repository.py`
- etc.

**Example**: `api/repositories/hair_style_repository.py`

```python
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from uuid import UUID

from api.models.database import HairStyle  # SQLAlchemy model

class HairStyleRepository:
    """Data access layer for hair_styles table"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict) -> HairStyle:
        """Create new hair style"""
        hair_style = HairStyle(**data)
        self.session.add(hair_style)
        await self.session.flush()
        return hair_style

    async def get_by_id(self, hair_style_id: UUID) -> Optional[HairStyle]:
        """Get hair style by ID"""
        result = await self.session.execute(
            select(HairStyle).where(HairStyle.hair_style_id == hair_style_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        user_id: Optional[int] = None,
        category: Optional[str] = None,
        archived: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[HairStyle]:
        """List hair styles with filters"""
        query = select(HairStyle)

        if user_id is not None:
            query = query.where(HairStyle.user_id == user_id)

        if category:
            query = query.where(HairStyle.category == category)

        query = query.where(HairStyle.archived == archived)
        query = query.order_by(HairStyle.updated_at.desc())

        if limit:
            query = query.limit(limit)

        query = query.offset(offset)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, hair_style_id: UUID, data: Dict) -> Optional[HairStyle]:
        """Update hair style"""
        await self.session.execute(
            update(HairStyle)
            .where(HairStyle.hair_style_id == hair_style_id)
            .values(**data)
        )
        return await self.get_by_id(hair_style_id)

    async def archive(self, hair_style_id: UUID) -> bool:
        """Archive hair style (soft delete)"""
        from datetime import datetime
        result = await self.session.execute(
            update(HairStyle)
            .where(HairStyle.hair_style_id == hair_style_id)
            .values(archived=True, archived_at=datetime.utcnow())
        )
        return result.rowcount > 0

    async def unarchive(self, hair_style_id: UUID) -> bool:
        """Unarchive hair style"""
        result = await self.session.execute(
            update(HairStyle)
            .where(HairStyle.hair_style_id == hair_style_id)
            .values(archived=False, archived_at=None)
        )
        return result.rowcount > 0

    async def search(self, query: str, user_id: Optional[int] = None) -> List[HairStyle]:
        """Full-text search in name and description"""
        # ... search implementation
```

#### 4.3 Create Services (1-2 days)

Create service layer with preview generation support.

**Files to create**:
- `api/services/hair_style_service_db.py`
- `api/services/hair_color_service_db.py`
- etc.

**Pattern**: Same as `ClothingItemServiceDB`

**Example**: `api/services/hair_style_service_db.py`

```python
class HairStyleServiceDB:
    """Business logic for hair styles"""

    def __init__(self, session: AsyncSession, user_id: Optional[int] = None):
        self.session = session
        self.user_id = user_id
        self.repository = HairStyleRepository(session)

    async def create_hair_style(self, data: Dict) -> Dict:
        """Create new hair style"""
        hair_style = await self.repository.create({
            **data,
            'user_id': self.user_id
        })
        return self._to_dict(hair_style)

    async def generate_preview(self, hair_style_id: str) -> Dict:
        """Generate preview using PresetVisualizer"""
        from ai_tools.shared.visualizer import PresetVisualizer
        from api.services.visualization_config_service_db import VisualizationConfigServiceDB
        from api.services.image_optimizer import ImageOptimizer

        # Load hair style
        hair_style = await self.repository.get_by_id(UUID(hair_style_id))
        if not hair_style:
            raise ValueError(f"Hair style {hair_style_id} not found")

        # Get visualization config
        viz_service = VisualizationConfigServiceDB(self.session, user_id=None)
        viz_config = await viz_service.get_default_config("hair_style")

        # Generate preview
        visualizer = PresetVisualizer()
        output_file = f"entity_previews/hair_styles/{hair_style_id}_preview.png"

        preview_path = await visualizer.create_preset_preview(
            preset_data=self._to_dict(hair_style),
            output_file=output_file,
            category="hair_style",
            viz_config=viz_config
        )

        # Create optimized versions
        optimizer = ImageOptimizer()
        optimizer.cleanup_old_versions('hair_style', hair_style_id)
        optimized_paths = optimizer.optimize_preview(
            output_file,
            'hair_style',
            hair_style_id
        )

        # Update database
        await self.repository.update(UUID(hair_style_id), {
            'preview_image_full': optimized_paths['full'],
            'preview_image_medium': optimized_paths['medium'],
            'preview_image_small': optimized_paths['small']
        })

        return await self.get_hair_style(hair_style_id)

    # ... other methods
```

#### 4.4 Create API Routes (1-2 days)

Create REST API routes for each entity type.

**Files to create**:
- `api/routes/hair_styles.py`
- `api/routes/hair_colors.py`
- etc.

**Pattern**: Same as `api/routes/clothing_items.py`

**Example**: `api/routes/hair_styles.py`

```python
@router.get("/", response_model=HairStyleListResponse)
@cached(cache_type="list", include_user=True)
async def list_hair_styles(
    request: Request,
    category: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """List all hair styles"""
    service = HairStyleServiceDB(db, user_id=current_user.id if current_user else None)
    hair_styles = await service.list_hair_styles(category=category, limit=limit, offset=offset)
    return HairStyleListResponse(items=hair_styles)

@router.post("/", response_model=HairStyleInfo)
@invalidates_cache(entity_types=["hair_styles"])
async def create_hair_style(
    request: HairStyleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Create new hair style"""
    service = HairStyleServiceDB(db, user_id=current_user.id if current_user else None)
    hair_style = await service.create_hair_style(request.dict())
    return HairStyleInfo(**hair_style)

@router.post("/{hair_style_id}/generate-preview")
async def generate_preview(
    hair_style_id: str,
    async_mode: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """Generate preview image for hair style (queues RQ job)"""
    from api.services.job_queue import get_job_queue_manager
    from api.services.rq_worker import get_rq_service
    from api.models.jobs import JobType

    # Get hair style info for better job title/description
    service = HairStyleServiceDB(db, user_id=None)
    hair_style = await service.get_hair_style(hair_style_id)

    if not hair_style:
        raise HTTPException(status_code=404, detail=f"Hair style {hair_style_id} not found")

    # Get visualization config to determine model
    from api.services.visualization_config_service_db import VisualizationConfigServiceDB
    config_service = VisualizationConfigServiceDB(db, user_id=None)
    config_dict = await config_service.get_default_config("hair_style")

    # Extract model name (or use default)
    model_name = "gemini-2.5-flash-image"  # default
    if config_dict and 'model' in config_dict:
        model_name = config_dict['model']
        # Strip "gemini/" prefix if present for cleaner display
        if model_name.startswith("gemini/"):
            model_name = model_name[len("gemini/"):]

    # Create job with descriptive title and description
    job_id = get_job_queue_manager().create_job(
        job_type=JobType.GENERATE_IMAGE,
        title=f"Create Preview Image ({model_name})",
        description=f"Hair Style: {hair_style.get('name', hair_style_id)}",
        metadata={
            "entity_type": "hair_style",
            "entity_id": hair_style_id
        }
    )

    get_rq_service().enqueue(
        hair_style_preview_generation_job,
        job_id,
        hair_style_id,
        priority='normal'
    )

    return {"job_id": job_id, "status": "queued"}

@router.post("/{hair_style_id}/archive")
@invalidates_cache(entity_types=["hair_styles"])
async def archive_hair_style(
    hair_style_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Archive hair style (soft delete)"""
    service = HairStyleServiceDB(db, user_id=current_user.id if current_user else None)
    await service.archive_hair_style(hair_style_id)
    return {"message": f"Hair style {hair_style_id} archived"}

# ... other endpoints (get, update, unarchive, delete)
```

**Register routes in `api/main.py`**:
```python
app.include_router(hair_styles.router, prefix="/hair-styles", tags=["hair_styles"])
app.include_router(hair_colors.router, prefix="/hair-colors", tags=["hair_colors"])
# ... etc for all entity types
```

#### 4.5 Migration Script (1 day)

Create one-time script to migrate JSON → Database.

**File**: `scripts/migrate_entities_to_db.py`

```python
"""
Migrate all JSON-based entities to PostgreSQL database

Usage:
    python scripts/migrate_entities_to_db.py --category hair_styles
    python scripts/migrate_entities_to_db.py --all
"""

import asyncio
import json
from pathlib import Path
from uuid import UUID
import argparse
import shutil

from api.database import get_session
from api.services.hair_style_service_db import HairStyleServiceDB
from api.services.hair_color_service_db import HairColorServiceDB
# ... import all services

async def migrate_category(category: str, service_class):
    """Migrate all entities in category from JSON to database"""
    json_dir = Path(f"presets/{category}")
    if not json_dir.exists():
        print(f"⚠️  Directory not found: {json_dir}")
        return

    migrated_count = 0
    failed_count = 0

    async with get_session() as session:
        service = service_class(session, user_id=None)

        for json_file in json_dir.glob("*.json"):
            if json_file.name.endswith("_preview.png"):
                continue  # Skip preview images

            entity_id = json_file.stem

            try:
                # Load JSON data
                with open(json_file) as f:
                    data = json.load(f)

                # Remove metadata if present
                data.pop('_metadata', None)
                data.pop('preset_id', None)

                # Create database entity
                print(f"  Migrating: {data.get('name', entity_id)}")
                entity = await service.create_entity(data)

                # Copy preview images to entity_previews
                for size in ['', '_small', '_medium']:
                    preview_src = json_dir / f"{entity_id}_preview{size}.png"
                    if preview_src.exists():
                        preview_dst = Path(f"entity_previews/{category}/{entity['id']}_preview{size}.png")
                        preview_dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(preview_src, preview_dst)
                        print(f"    Copied preview: {preview_src.name}")

                migrated_count += 1

            except Exception as e:
                print(f"  ❌ Failed to migrate {json_file.name}: {e}")
                failed_count += 1

        await session.commit()

    print(f"\n✅ {category}: {migrated_count} migrated, {failed_count} failed")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', help='Category to migrate (e.g., hair_styles)')
    parser.add_argument('--all', action='store_true', help='Migrate all categories')
    args = parser.parse_args()

    categories = {
        'hair_styles': HairStyleServiceDB,
        'hair_colors': HairColorServiceDB,
        'expressions': ExpressionServiceDB,
        'makeup': MakeupServiceDB,
        'accessories': AccessoriesServiceDB,
        'visual_styles': VisualStyleServiceDB,
        'art_styles': ArtStyleServiceDB,
        'story_themes': StoryThemeServiceDB,
        'story_prose_styles': StoryProseStyleServiceDB,
        'story_audiences': StoryAudienceServiceDB
    }

    if args.all:
        for category, service_class in categories.items():
            print(f"\n🔄 Migrating {category}...")
            await migrate_category(category, service_class)
    elif args.category:
        if args.category not in categories:
            print(f"❌ Unknown category: {args.category}")
            print(f"Available: {', '.join(categories.keys())}")
            return

        print(f"\n🔄 Migrating {args.category}...")
        await migrate_category(args.category, categories[args.category])
    else:
        print("❌ Please specify --category or --all")
        parser.print_help()

if __name__ == '__main__':
    asyncio.run(main())
```

**Run migration**:
```bash
# Migrate one category
python scripts/migrate_entities_to_db.py --category hair_styles

# Migrate all
python scripts/migrate_entities_to_db.py --all
```

#### 4.6 Update Image Composer (2-3 days)

Update Image Composer to fetch entities from database instead of JSON files.

**Files to update**:
- `frontend/src/ModularGenerator.jsx` (or wherever entity loading happens)
- `frontend/src/Composer.jsx`

**Changes**:

```jsx
// Before (JSON files):
const response = await api.get(`/presets/hair_styles`)
const hairStyles = response.data.presets || []

// After (database):
const response = await api.get(`/hair-styles/`)
const hairStyles = response.data.items || []
```

**Important**: Update ALL entity loading in Image Composer to use new database endpoints.

#### 4.7 Frontend Entity Configs (1 day)

Update or create entity configs to use database endpoints.

**Files to update** (from Phase 1.4):
- All entity configs created in Phase 1.4

**Changes**:
```jsx
// Update fetchEntities to use database endpoint
fetchEntities: async () => {
  const response = await api.get('/hair-styles/')  // Database endpoint
  return (response.data.items || []).map(item => ({
    id: item.hair_style_id,
    title: item.name,
    // ... map database fields to UI fields
  }))
}
```

**Success Criteria**:
- ✅ All 8+ entity categories migrated to database
- ✅ Image Composer works with database entities
- ✅ Preview generation works for all migrated entities
- ✅ JSON files deprecated (kept as backup, not used)
- ✅ Entity management (archive, tag, search) works for all types
- ✅ 93+ entities successfully migrated without data loss
- ✅ Zero "preset" terminology in database or codebase

---

### **Phase 5: Image Composer UX Improvements** (1-2 days)

Make characters work like other entities (drag-and-drop, not dropdown).

**Problem**: Characters are currently selected from a dropdown menu, unlike other entities which are dragged onto the canvas. This creates an inconsistent UX.

**Goal**: Characters should work exactly like outfits, expressions, etc. - dragged from an entity library onto the canvas.

#### 5.1 Refactor Character Selection (1-2 days)

**Files to update**:
- `frontend/src/ModularGenerator.jsx` or `frontend/src/Composer.jsx` (whichever handles entity selection)

**Changes**:

1. **Remove character dropdown**
   - Delete dropdown UI component
   - Remove character selection state

2. **Add character entity library panel**
   - Same UI pattern as other entity types
   - Shows character cards with preview images
   - Draggable character cards

3. **Update canvas to accept characters**
   - Character becomes first item in applied entities stack
   - Character layer shows as "Base: [Character Name]"
   - Can remove/replace character like other entities

4. **Update entity ordering**
   - Character (if present) always renders first
   - Other entities render on top in order

**Example implementation**:

```jsx
// Entity library with character support
const entityTypes = [
  { type: 'character', label: 'Characters', icon: '👤' },
  { type: 'outfit', label: 'Outfits', icon: '👔' },
  { type: 'hair_style', label: 'Hair Styles', icon: '💇' },
  { type: 'expression', label: 'Expressions', icon: '😊' },
  // ... etc
]

// Applied entities stack (in render order)
const appliedEntities = [
  { type: 'character', id: 'char123', name: 'Jenny' },      // Base layer
  { type: 'outfit', id: 'outfit456', name: 'Summer Dress' }, // Layer 1
  { type: 'hair_style', id: 'hair789', name: 'Ponytail' },  // Layer 2
  // ... etc
]
```

**Success Criteria**:
- ✅ Characters work like other entities (drag-and-drop)
- ✅ Character shows in applied entities stack
- ✅ Can remove/replace character like other entities
- ✅ Character always renders as base layer
- ✅ Consistent UX across all entity types
- ✅ No dropdown menus for entity selection

---

## 📅 Implementation Timeline (Updated)

### **✅ Week 1 COMPLETE: Optimization & Entity Rollout**
- ✅ Days 1-2: Phase 0.3-0.4 (Frontend size selection, on-demand optimization)
- ✅ Day 3: Phase 1.1-1.3 (Characters, Viz Configs, Images)
- ✅ Days 4-5: Phase 1.4-1.5 (All preset entities, job naming standards)

**Results**: 13 entity types now have EntityPreviewImage, ~300 lines of code deleted, all jobs follow naming standards

### **Week 2: Finish Phase 0 & Start Testing** (NEXT)
- Day 1: Phase 0.2 (Update preview generation jobs to create optimized versions)
- Days 2-3: Phase 2.2 (LLM job audit - ensure all tool endpoints spawn jobs)
- Days 4-5: Phase 3.1 (Backend tests for preview system)

### **Week 3: Testing & UX**
- Days 1-2: Phase 3.2-3.3 (Frontend tests, CI/CD)
- Days 3-5: Phase 5 (Image Composer UX - characters drag-and-drop)

### **Weeks 4-6: Database Migration (Phase 4)**
- Week 4: Phase 4.1-4.3 (Schema, repositories, services)
- Week 5: Phase 4.4-4.5 (Routes, migration script)
- Week 6: Phase 4.6-4.7 (Image Composer, entity configs)

**Note**: Phase 2.1 (Outfit preview generation) already complete - outfits use API endpoints like other preset entities

---

## ✅ Overall Success Criteria

**Phase 0 Complete**:
- ✅ Image optimization reduces bandwidth by 80-90%
- ✅ EntityPreviewImage automatically loads appropriate sizes
- ✅ Page load times dramatically improved

**Phase 1 Complete**:
- ✅ All 17 entity types show EntityPreviewImage
- ✅ Preview images auto-update via SSE job stream
- ✅ Stand-in icons display when no preview exists
- ✅ "Generate Preview" buttons work for all entity types

**Phase 2 Complete**:
- ✅ Outfits have full preview generation system
- ✅ 100% of LLM calls spawn RQ jobs
- ✅ Zero blocking operations in UI
- ✅ All tools trackable in job queue

**Phase 3 Complete**:
- ✅ 80%+ backend test coverage
- ✅ 40%+ frontend test coverage
- ✅ All critical paths tested
- ✅ CI/CD runs tests on every PR
- ✅ No flaky tests

**Phase 4 Complete**:
- ✅ All JSON entities migrated to database
- ✅ Zero "preset" terminology in codebase
- ✅ Image Composer works with database entities
- ✅ Entity management works for all types
- ✅ No data loss during migration

**Phase 5 Complete**:
- ✅ Characters work like other entities (drag-and-drop)
- ✅ Consistent UX across all entity types
- ✅ No dropdown menus for entity selection

**Final Success**:
- ✅ Unified entity preview system across 17+ entity types
- ✅ Consistent job-based execution for all tools
- ✅ Single source of truth (database, not JSON files)
- ✅ Scalable foundation for future entity types
- ✅ Comprehensive test coverage prevents regressions
- ✅ ROADMAP 2.14 complete

---

## 🎯 Key Improvements

1. ✅ **Image optimization** - 80-90% bandwidth savings
2. ✅ **Testing infrastructure** - Prevents regressions
3. ✅ **LLM job audit** - No blocking calls
4. ✅ **Terminology cleanup** - "Preset" → "Entity"
5. ✅ **Image Composer UX** - Characters work like other entities
6. ✅ **Comprehensive tests** - 80%+ backend, 40%+ frontend coverage

---

## 🚨 Critical Reminders

1. **RQ workers must be rebuilt** after ANY backend code changes
2. **Commit only after full phase complete** (not incremental)
3. **Every LLM call MUST spawn RQ job** (no exceptions)
4. **Image optimization MUST run on all preview generation** (automatic)
5. **Test coverage required** before merging to main

---

**Ready to begin Phase 0 (Image Optimization System)**
