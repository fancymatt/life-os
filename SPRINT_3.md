# Sprint 3: Composer Enhancements & UX Improvements

## Completed Features

### 1. Gallery with Comparison Mode ✅
- Grid view of generated images
- Select up to 4 images for comparison
- Full-screen preview with download
- Auto-refresh from completed jobs

### 2. Favorites System ✅
- Backend API (`/api/favorites/add`, `/api/favorites/remove`, `/api/favorites`)
- JSON file persistence per user
- Star button on preset thumbnails
- Integrated in both Composer and ModularGenerator
- Favorited presets sort to top of library

### 3. Preset Composer (Drag & Drop) ✅
- Full-page three-column layout (Library | Canvas | Applied Stack)
- HTML5 drag-and-drop for presets
- Cumulative preset stacking:
  - Outfits can layer (multiple outfits combine)
  - Other categories replace (one hair color, one makeup, etc.)
- Smart caching system (same combination = cached result)
- Auto-generation on preset drop/removal
- Subtle corner loading indicator (keeps image visible)
- Integration with job queue system

## Current Sprint 3 Work

### In Progress: Subject Image Selector
**Goal**: Allow users to choose which subject image to use instead of hardcoded "jenny.png"

**Tasks**:
1. Create `/api/subjects` endpoint to list available subject images
   - Check `/uploads/` directory for uploaded images
   - Check root directory for default subjects (jenny.png, etc.)
   - Return list with filename, path, URL, thumbnail

2. Update Composer UI
   - Add subject selector dropdown in canvas header
   - Show thumbnail preview of selected subject
   - Update cache key when subject changes
   - Clear applied presets when subject changes (optional)

3. Update subject upload flow
   - Integrate with existing `/api/upload` endpoint
   - Auto-refresh subject list after upload

### Planned Features

1. **Preset Search/Filtering** (Priority: Medium)
   - Search box in preset library
   - Filter by name, tags, or description
   - Maintain favorites-first sorting

2. **Save/Load Preset Combinations** (Priority: Medium)
   - Save current applied presets as named "composition"
   - List saved compositions
   - Quick-load to recreate complex setups

3. **Download Button for Generated Images** (Priority: Low)
   - Add download button on canvas
   - Include metadata (presets used, generation date)

4. **Variation Count Control** (Priority: Low)
   - Slider to generate 1-4 variations at once
   - Show all variations in grid
   - Select favorite from variations

## Technical Notes

### Key Files Modified This Sprint
- `frontend/src/Composer.jsx` - Main composer component
- `frontend/src/Composer.css` - Full-page layout styling
- `frontend/src/Gallery.jsx` - Image gallery with comparison
- `frontend/nginx.conf` - **CRITICAL**: Proxy `/output/` and `/uploads/` to API
- `api/routes/favorites.py` - Favorites endpoints
- `api/services/favorites_service.py` - Favorites persistence

### Important Patterns
- **Outfit layering**: Check `preset.category === 'outfits'` to allow stacking
- **Cache keys**: `${subject}|${sorted_preset_ids}` format
- **Image URLs**: Must start with `/` for nginx proxying
- **Job polling**: 2-second intervals, 60 max attempts (2 minutes)

### Common Issues Solved
1. **Missing leading slash in image URLs** - Fixed in `pollForCompletion()`
2. **Nginx not proxying static files** - Added `/output/` and `/uploads/` locations
3. **Import errors in favorites** - Use `api.dependencies.auth` not `api.services.auth_service`

## Image Generation Strategy

We use a hybrid approach optimized for each use case:

### Preview Thumbnails (Pure Text-to-Image)
- **Model**: DALL-E 3
- **Use case**: Generating standalone preset preview images
- **Why**: Pure text-to-image with no source subject
- **Limitation**: 4000 character prompt limit (we truncate if needed)

### Modular Generator (Subject Transformation)
- **Model**: Gemini 2.5 Flash
- **Use case**: Applying presets to subject photos (main generation)
- **Why**: Requires source image, excels at image transformation
- **Advantage**: No prompt length limits, better subject preservation

This approach uses each model's strengths - DALL-E for creation, Gemini for transformation.

## Next Sprint Ideas (Sprint 4)

- Real-time collaboration (multiple users composing together)
- Preset categories expansion (poses, backgrounds, lighting)
- Advanced caching with IndexedDB for offline support
- Export composition as JSON for sharing
- Batch generation (generate with multiple subjects at once)
