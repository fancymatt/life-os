# lifeOS v2.5.1 (109) - Development Roadmap

**Last Updated**: 2025-10-23
**Current Phase**: Phase 2 - User Experience & Core Features
**Next**: Phase 2.5 - Tagging System

---

## Overview

Life-OS is evolving from a specialized **AI image generation platform** into a **comprehensive personal AI assistant** with autonomous task execution across multiple domains.

**Current State** (October 2025):
- ✅ **Phase 1 Complete**: PostgreSQL database, 158 tests, CI/CD, 17 entity types
- ✅ **Archive System**: ✅ 100% COMPLETE (database + backend + frontend + filter toggle)
- ✅ **Database Persistence**: ✅ Stories now persist to PostgreSQL (Phase 2.3 complete)
- ✅ **Local LLM**: 95% complete (backend + 120B model running, frontend UI pending)
- ✅ **24 AI Tools**: 8 analyzers + 6 generators + workflow orchestration

**Vision** (18-24 months):
- 🎯 **Daily Operating System**: Morning brief, rolling feed, auto-prep/tidy
- 🎯 **Creative Intelligence**: Taste graph, variant exploration, recipe reuse
- 🎯 **Reproducible Assets**: Full provenance, one-click reproduce
- 🎯 **Developer Autopilot**: Complete tickets via MCP, nightly PR factory
- 🎯 **Policy-Bound Autonomy**: Propose-first agents with guardrails
- 🎯 **Cross-Domain Taste**: Unified taste across creative, media, and knowledge

---

## Phase Organization Principles

**Infrastructure Before Features**: Build foundations before complexity
**Easy Before Hard**: Prioritize features that work with current infrastructure
**Value Before Polish**: High-value features before nice-to-haves
**Maintenance Built In**: Regular refactoring phases to prevent technical debt

---

## Phase 1: Foundation & Critical Fixes ✅ **COMPLETE**

**Duration**: 8 weeks (Completed October 2025)
**Goal**: Stable, scalable foundation

### What We Built:
- ✅ PostgreSQL database with 12 tables
- ✅ Pagination + caching (60s list, 5min detail, 1hr static)
- ✅ Clean logging infrastructure (zero print() in production)
- ✅ GitHub Actions CI/CD
- ✅ 158 backend tests
- ✅ All 8 preset entities unified
- ✅ Pydantic v2 migration complete
- ✅ Archive system (80% - database + backend)
- ✅ Local LLM backend (Ollama + 120B model)

**Test Results**: 73 passing, 16 failing (fixture issues, not production bugs)
**Production Ready**: Yes

---

## Phase 2: User Experience & Core Features (4-6 weeks)

**Goal**: Polish existing features, complete high-value user requests
**Why Now**: These features work with current infrastructure and deliver immediate value

### 2.1 Complete Archive System ✅ **100% COMPLETE** (Oct 23, 2025)
**Status**: ✅ COMPLETE - All features delivered
**Priority**: CRITICAL - Prevents broken links

**Completed Work** (Oct 23, 2025):
- ✅ Database: Added archived/archived_at columns to all 12 entity tables
- ✅ Backend: Archive/unarchive methods in 6 repositories (ClothingItem, BoardGame, Image, Outfit, Composition, VisualizationConfig)
- ✅ Backend: Archive/unarchive endpoints in 6 API routes
- ✅ Frontend: Changed "Delete" button to "Archive" in EntityBrowser
- ✅ Frontend: Orange "📦 ARCHIVED" badge on archived items in 4 configs (ClothingItem, BoardGame, Image, VisualizationConfig)
- ✅ Frontend: Dimmed archived items (opacity: 0.6)
- ✅ Frontend: archive/unarchive functions in entity configs
- ✅ Frontend: "Show archived" filter toggle in EntityBrowser (default: hidden)

**Success Criteria**:
- ✅ Zero broken links from deleted entities (archive replaces delete)
- ✅ Archive/unarchive works on all database entities
- ✅ Archived filter shows/hides correctly
- ✅ Archived items visually distinct with badge and dimming

---

### 2.2 Mobile Responsiveness ✅ **100% COMPLETE** (Oct 23, 2025)
**Status**: ✅ COMPLETE - All mobile improvements delivered
**Priority**: HIGH - Current mobile experience is poor
**Complexity**: Medium

**Completed Work** (Oct 23, 2025):
- ✅ Viewport meta tag already present in `frontend/index.html`
- ✅ Collapsible sidebar fully functional on mobile (<768px)
- ✅ All buttons meet 44x44px minimum touch target size
- ✅ Proper spacing from edges (16px minimum padding)
- ✅ TaskManager floating button repositioned for mobile
- ✅ Sidebar nav links increased to 44px min-height with larger icons
- ✅ Filter tabs and action buttons touch-friendly
- ✅ Responsive breakpoints: 768px (mobile) and 480px (small mobile)

**Success Criteria**:
- ✅ All touch targets meet 44x44px minimum
- ✅ Proper edge spacing (16px minimum)
- ✅ Comfortable reading and navigation on mobile devices

---

### 2.3 Complete Database Persistence ✅ **COMPLETE** (Oct 23, 2025)
**Status**: ✅ COMPLETE - Stories now persist to database
**Priority**: HIGH - User data is being lost
**Complexity**: Medium

**Problem Solved**: Database tables existed but stories were not being saved to the database. Stories were only stored in temporary job results and lost when jobs cleared.

**Completed Work** (Oct 23, 2025):

**Stories Persistence** ✅ **100% COMPLETE**:
- ✅ Created `StoryRepository` (api/repositories/story_repository.py - 207 lines)
  - Data access layer for Story and StoryScene entities
  - CRUD operations with pagination, search, and archive support
  - Full-text search in title and content
- ✅ Created `StoryServiceDB` (api/services/story_service_db.py - 422 lines)
  - Business logic layer converting workflow results to DB records
  - `create_story_from_workflow_result()` method for seamless workflow integration
  - User filtering and permission checks
- ✅ Created `/api/stories/` routes (api/routes/stories.py - 213 lines)
  - GET /stories/ - List stories with pagination
  - GET /stories/{id} - Get story detail with scenes
  - POST /stories/{id}/archive - Archive story
  - POST /stories/{id}/unarchive - Restore story
  - DELETE /stories/{id} - Soft delete
  - Cache decorators for performance optimization
- ✅ Registered stories routes in main.py
- ✅ Updated story workflow (api/routes/workflows.py)
  - Persist story to database after successful generation
  - Error handling ensures job still completes if DB write fails
- ✅ Updated frontend (storiesConfig.jsx)
  - Fetch from `/api/stories/` instead of `/api/jobs`
  - Maps new API response format to frontend expectations
  - Extracts illustrations from scenes array

**Q&As Persistence** ⏳ **DEFERRED**:
- Q&As still using JSON file storage in `data/qas/`
- Deferred to future work (low priority - no data loss reported)

**Success Criteria**:
- ✅ Stories persist in database after workflow completes
- ✅ Stories visible in `/entities/stories` even after page refresh
- ✅ Stories survive job queue clears
- ✅ No story data loss
- ⏳ Q&As database migration (deferred)

**Impact**:
- Stories now permanent in PostgreSQL (no more data loss)
- Full CRUD operations available
- Archive/unarchive support
- Search functionality enabled
- User filtering ready for multi-tenancy
- Fixes critical data loss issue (269 images generated, 0 rows saved)

**Commit**: `173107c` - "feat: Implement database persistence for stories (Phase 2.3)"

---

### 2.4 UI Theme System ✅ **100% COMPLETE** (Oct 23, 2025)
**Status**: ✅ COMPLETE - All theme infrastructure delivered
**Priority**: HIGH - Foundation for all future UI work
**Complexity**: Medium

**Completed Work** (Oct 23, 2025):
- ✅ Created `frontend/src/theme.js` (348 lines) - Comprehensive design token system
- ✅ Dark/light/auto mode toggle implemented with dropdown UI
- ✅ CSS variable architecture (`frontend/src/theme.css`) with 190 lines
- ✅ Persistent user preference (localStorage) with auto-detection
- ✅ ThemeContext provider for global theme state
- ✅ ThemeToggle component integrated into header
- ✅ Touch-friendly styling (44px min-height for mobile)
- ✅ Smooth transitions between themes (200ms)

**Files Created**:
- `frontend/src/theme.js` - Design token definitions (colors, spacing, typography, shadows, radius, z-index)
- `frontend/src/theme.css` - CSS custom properties for both light and dark themes
- `frontend/src/contexts/ThemeContext.jsx` - React context provider
- `frontend/src/components/ThemeToggle.jsx` - Theme selection dropdown
- `frontend/src/components/ThemeToggle.css` - Component styles

**Files Modified**:
- `frontend/src/main.jsx` - Added ThemeProvider and theme.css import
- `frontend/src/components/layout/Layout.jsx` - Added ThemeToggle to header

**Success Criteria**:
- ✅ Seamless dark/light/auto switching working
- ✅ Theme preference persisted across sessions
- ✅ Comprehensive token system (50+ color tokens, spacing scale, typography, shadows)
- ⏳ Update EntityBrowser to use theme (deferred to Phase 3)
- ⏳ Create component library (deferred to Phase 3 - Button, Card, Modal, Input, Badge, Tabs)

---

### 2.5 Tagging System (3-4 days)
**Priority**: HIGH - Improves organization across all entities
**Complexity**: Medium

**Database Schema**:
```sql
CREATE TABLE tags (
  tag_id UUID PRIMARY KEY,
  name VARCHAR(100) UNIQUE,
  category VARCHAR(50),  -- material, style, season, genre
  color VARCHAR(20),
  created_at TIMESTAMP
);

CREATE TABLE entity_tags (
  entity_type VARCHAR(50),
  entity_id UUID,
  tag_id UUID,
  PRIMARY KEY (entity_type, entity_id, tag_id)
);
```

**Features**:
- [ ] Tag autocomplete (suggest existing)
- [ ] Create new tags inline
- [ ] Filter entity lists by tag(s)
- [ ] Multi-tag filtering (AND/OR logic)
- [ ] Tag cloud visualization

**Success Criteria**:
- Tagging adoption >60% of entities
- Tag filtering fast (<300ms)
- Tag suggestions helpful

---

### 2.6 Entity Merge Tool (1 week)
**Priority**: HIGH - Reduces duplicates
**Complexity**: High

**Workflow**:
1. User selects Entity A (keep) and Entity B (merge into A)
2. System finds all references to Entity B
3. AI analyzes both and generates merged description
4. Preview merged entity (user can edit)
5. Update all references from B → A
6. Archive Entity B with `merged_into: entity_a_id` metadata

**UI**:
- [ ] "Merge into..." button in entity actions
- [ ] Side-by-side comparison view
- [ ] AI-generated merge preview (editable)
- [ ] Confirmation dialog showing affected references

**Success Criteria**:
- Merge preserves all unique information
- All references updated correctly
- Merge reversible via unarchive

---

### 2.7 Visualization Config Linking (1 day)
**Priority**: MEDIUM - Better discoverability
**Complexity**: Low

**Implementation**:
- [ ] Add `visualization_config_id` field to entities
- [ ] Show config name with entity data
- [ ] Link to config detail page
- [ ] Fallback to default if not set
- [ ] "Set Visualization Config" button when missing

**Success Criteria**:
- Config linking visible on all entities
- Easy to change config
- Clear which config is used

---

### 2.8 Clothing Modification Tools (2-3 days)
**Priority**: HIGH - Iterative design
**Complexity**: Low-Medium

**Two Tools**:

**1. Modify Existing** (in-place update):
- Text input: "Make these shoulder-length" or "Change to red"
- AI updates description
- Mark as `manually_modified: true`

**2. Create Variant** (copy with changes):
- Same input, creates new entity
- Keep `source_entity_id` reference
- Name: "{original_name} (Variant)"

**Success Criteria**:
- Modifications applied correctly
- Variants preserve lineage
- Preview before applying

---

### 2.9 Alterations Entity (1 week)
**Priority**: HIGH - Expands creative possibilities
**Complexity**: High

**What are Alterations?**
- Physical transformations: horns, wings, tail, pointed ears
- Skin modifications: color changes, scales, fur
- Proportional changes: extreme musculature, height
- Facial features: fangs, glowing eyes

**Database Schema**:
```sql
CREATE TABLE alterations (
  alteration_id UUID PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  category VARCHAR(50),  -- skin, appendages, proportions, facial_features
  intensity VARCHAR(50), -- subtle, moderate, extreme
  source_image VARCHAR(500),
  preview_image_path VARCHAR(500),
  tags TEXT[],
  user_id INTEGER,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  metadata JSONB,
  archived BOOLEAN DEFAULT FALSE,
  archived_at TIMESTAMP
);
```

**Implementation**:
- [ ] Create database table + migration
- [ ] Create `AlterationServiceDB`
- [ ] Create API routes (`/api/alterations/`)
- [ ] Create analyzer tool (`alteration_analyzer`)
- [ ] Create frontend entity config
- [ ] Integrate with Image Composer

**Success Criteria**:
- Can analyze images for alterations
- Alterations work in Image Composer
- Alterations work in Story Generator

---

### 2.10 Story Import & Text-to-Story (2-3 days)
**Priority**: MEDIUM - Content flexibility
**Complexity**: Low-Medium

**Features**:
- [ ] Import full story text (paste or file upload)
- [ ] Parse story into title + body
- [ ] Create story entity in database
- [ ] Optional: Parse into scenes (AI-assisted)
- [ ] Link to character if mentioned
- [ ] Generate thumbnail from first paragraph

**UI**:
- [ ] "Import Story" button in Stories entity browser
- [ ] Text area for paste or file upload
- [ ] Preview before saving
- [ ] Optional scene splitting

**Success Criteria**:
- Can import stories from external sources
- Stories properly formatted and saved
- Searchable and browsable like generated stories

---

### 2.11 NSFW Content Routing (1-2 days)
**Priority**: MEDIUM - Content flexibility
**Complexity**: Low

**Problem**: Some LLM providers reject NSFW content, blocking generation

**Solution**: Fallback routing to uncensored models

**Implementation**:
- [ ] Add NSFW detection in `ai_tools/shared/router.py`
- [ ] Configure fallback model list in `configs/models.yaml`:
  ```yaml
  nsfw_fallback_models:
    - "ollama/llama3.1:70b-instruct-q4"  # Local uncensored model
    - "openrouter/meta-llama/llama-3.1-70b-instruct"  # Cloud fallback
  ```
- [ ] Catch content policy errors from Gemini/OpenAI
- [ ] Auto-retry with fallback model
- [ ] Log routing decisions for cost tracking

**Workflow**:
1. User generates image/story with mature content
2. Gemini/OpenAI rejects request with policy error
3. Router detects rejection, selects fallback model
4. Retry generation with uncensored model
5. Log warning: "Used NSFW fallback model"

**Success Criteria**:
- NSFW content generates without manual intervention
- Fallback routing transparent to user
- Cost tracking includes fallback usage

---

### 2.12 Extremify Tool (2-3 days)
**Priority**: LOW - Fun creative feature
**Complexity**: Medium

**Input**:
- Clothing item or alteration entity
- Intensity multiplier (1-5x)

**AI Prompt**:
```
Create an avant-garde version of this {item_type} that is {intensity}x more extreme.
Amplify all unique features by {intensity}:
- Thickness → {intensity}x thicker
- Length → {intensity}x longer
- Volume → {intensity}x more voluminous
- Decorative elements → {intensity}x more pronounced
```

**Success Criteria**:
- Generates believable extremified versions
- Intensity slider feels natural
- Fun to use
- Works with both clothing and alterations

---

### 2.13 Story Collections & Series (2-3 days)
**Priority**: MEDIUM - Content organization
**Complexity**: Low
**Depends on**: Stories saved to database (Section 2.3)

**Problem**: Users will create related stories. Need organization.

**Database Schema**:
```sql
CREATE TABLE story_collections (
  collection_id UUID PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  display_order INTEGER[], -- Array of story IDs in order
  user_id INTEGER,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  archived BOOLEAN DEFAULT FALSE,
  archived_at TIMESTAMP
);
```

**Features**:
- [ ] Group stories into collections/series
- [ ] Set collection order (Book 1, Book 2, etc.)
- [ ] Collection-level metadata (series description, genre)
- [ ] "Next in series" suggestions in Brief
- [ ] Export entire collection as epub anthology

**UI**:
- [ ] "Create Collection" button in Stories browser
- [ ] Drag-and-drop to reorder stories in collection
- [ ] Collection detail page with all stories listed
- [ ] Badge on story cards showing collection membership
- [ ] Filter stories by collection

**Success Criteria**:
- Easy to create and organize collections
- Collections useful for multi-book series
- Export works seamlessly
- "Next in series" suggestions helpful

---

### Phase 2 Success Metrics

- ✅ Archive system 100% complete
- ✅ Zero broken entity links (archive replaces delete)
- ✅ Archive filter toggle implemented
- ✅ Archived items visually distinct
- ✅ Mobile responsiveness 100% complete
- ✅ All touch targets meet 44x44px minimum
- ✅ Proper edge spacing (16px minimum)
- ✅ UI Theme System 100% complete
- ✅ Theme switching works flawlessly (light/dark/auto modes)
- ✅ Theme preference persisted in localStorage
- [ ] Tagging adoption >60% of entities
- [ ] All high-value UX features delivered

**Total Duration**: 4-6 weeks
**Total Features**: 9 major features

---

## Phase 3: Creative Intelligence & Maintenance (7-9 weeks)

**Goal**: Build taste learning, creative exploration tools, and clean up technical debt
**Why Now**: Foundation for many future features (autopilot, brief, suggestions) + prevent compound interest on technical debt

### 3.1 Component Refactoring (3 days)
**Priority**: HIGH - Prevent technical debt
**Complexity**: Medium

- [ ] Split Composer.jsx (910 lines → 300 + subcomponents)
  - [ ] PresetLibrary.jsx (200 lines)
  - [ ] PresetCanvas.jsx (200 lines)
  - [ ] AppliedPresetsStack.jsx (150 lines)
  - [ ] CompositionManager.jsx (150 lines)
- [ ] Unify OutfitAnalyzer + GenericAnalyzer (eliminate 500 line duplication)
  - [ ] Create BaseAnalyzer.jsx (shared logic)
  - [ ] OutfitAnalyzer extends BaseAnalyzer
  - [ ] GenericAnalyzer extends BaseAnalyzer

**Success Criteria**:
- No component over 500 lines
- Code duplication eliminated

---

### 3.2 Frontend Testing (2 days)
**Priority**: HIGH - Critical path coverage
**Complexity**: Medium

- [ ] EntityBrowser component tests
- [ ] Character import flow tests (critical path)
- [ ] Story workflow UI tests (critical path)
- [ ] Target: 40% coverage overall

**Success Criteria**:
- Frontend coverage >40%
- Critical paths tested

---

### 3.3 Code Quality Cleanup (2 days)
**Priority**: MEDIUM - Error handling
**Complexity**: Low

- [ ] Standardized error response models
- [ ] Error codes for programmatic handling
- [ ] Global error handler middleware
- [ ] Fix remaining 16 test failures (fixture data)

**Success Criteria**:
- All tests passing (100%)
- Consistent error handling

---

### 3.4 TasteProfile v1 (2-3 weeks) 🌟 **FOUNDATIONAL**
**Priority**: HIGH - Powers many other features
**Complexity**: High

**Core Features**:
- [ ] Embedding model for all entity types (SentenceTransformers or OpenAI)
- [ ] PostgreSQL pgvector extension
- [ ] Store vectors in database
- [ ] "Find Similar" based on embedding distance
- [ ] Simple aesthetic heuristics:
  - Color harmony (complementary, analogous, triadic)
  - Composition balance (rule of thirds, golden ratio)
  - Contrast and readability
- [ ] Taste-based ranking for suggestions

**Data Sources**:
- Favorites (explicit positive signal)
- Tags applied by user
- Accepted vs rejected outputs
- Re-use patterns (what gets used in compositions/stories)
- Modification history

**Success Criteria**:
- "Find Similar" accuracy >80%
- TasteProfile learns from 100+ interactions
- Similarity search <300ms
- Powers variant ranking

---

### 3.5 Variant Orchards (1-2 weeks)
**Priority**: MEDIUM - Creative exploration
**Complexity**: High
**Depends on**: TasteProfile

**Concept**: Structured exploration across controllable axes

**Workflow**:
1. User selects base image/prompt
2. Choose exploration axes:
   - Palette: warm/cool/vibrant/muted
   - Lighting: soft/dramatic/natural/studio
   - Angle: front/side/three-quarter/overhead
   - Style intensity: subtle/moderate/extreme
3. Generate grid of variants (2-4 per axis = 16-64 images)
4. Auto-rank by:
   - Composition balance
   - Color harmony
   - Contrast
   - LLM rubric: "Rate aesthetic quality 1-10"
   - TasteProfile similarity
5. Present as tree view: prune weak branches, promote winners

**UI**:
- [ ] Tree/grid toggle view
- [ ] Filter by rank threshold
- [ ] Quick compare mode (side-by-side)
- [ ] One-click "explore this branch deeper"

**Cost Control**:
- Batch generation (cheaper)
- Local LLM for ranking (zero cost)
- User-set budget cap per orchard

**Success Criteria**:
- Can explore 50+ variants efficiently
- Ranking helpful (user agrees >70% of time)
- Cost per orchard <$5

---

### 3.6 Recipe Builder & Reuse (1 week)
**Priority**: MEDIUM - Improves workflow efficiency
**Complexity**: Medium

**What is a Recipe**:
- Inputs: entity IDs, parameters, model settings
- Process: tool chain, workflow steps
- Outputs: generated entities, images, stories
- Provenance: full lineage for reproducibility

**Features**:
- [ ] Save any successful generation as recipe
- [ ] Name and tag recipes
- [ ] Browse recipe library
- [ ] Apply recipe to new inputs
- [ ] Compare recipes (diff viewer)
- [ ] Evolve recipe (modify params, save as new version)
- [ ] Recipe templates (common patterns)

**UI**:
- [ ] "Save as Recipe" button after generation
- [ ] Recipe library page with search/filter
- [ ] Recipe detail view with full provenance
- [ ] "Apply to..." action to reuse recipe

**Success Criteria**:
- Recipe library has 20+ saved recipes
- Recipes reusable and evolvable
- Recipe application success rate >90%

---

### 3.7 Inspiration Ingestion (1 week)
**Priority**: MEDIUM - Content capture
**Complexity**: Medium

**Features**:
- [ ] Browser extension: "Save to LifeOS" button
- [ ] Screenshot hotkey (system-wide)
- [ ] Mobile share target (iOS/Android)
- [ ] Inspiration Inbox (staging area)
- [ ] Auto-analyze with analyzers
- [ ] Convert to entities with one click
- [ ] Link to TasteProfile

**Workflow**:
1. User sees great outfit on Pinterest
2. Clicks "Save to LifeOS" browser button
3. Image appears in Inspiration Inbox
4. System suggests: "Looks like an outfit - analyze?"
5. User clicks "Analyze"
6. Creates clothing item entities
7. Links to TasteProfile as inspiration source

**Success Criteria**:
- Can save from any device
- Auto-categorization >80% accurate
- One-click entity creation

---

### 3.8 Story Editing & Revision Workflow (1-2 weeks)
**Priority**: HIGH - Iterative creative process
**Complexity**: Medium
**Depends on**: Stories saved to database (Section 2.3)

**Problem**: Users can only generate stories, not edit them. Need AI-assisted editing.

**Features**:
- [ ] Edit story content in-place with AI assistance
- [ ] "Rewrite this scene to be more suspenseful"
- [ ] "Expand this character introduction"
- [ ] "Change the tone to be lighter"
- [ ] Track revision history (provenance for edits)
- [ ] A/B comparison view (original vs revised)
- [ ] Apply TasteProfile to suggest improvements
- [ ] Undo/redo revisions

**Revision Agent**:
- [ ] Takes instruction + story section
- [ ] Generates revised version preserving context
- [ ] Maintains character consistency
- [ ] Preserves story arc and timeline
- [ ] Suggests improvements based on TasteProfile

**UI**:
- [ ] "Edit Story" mode in story detail page
- [ ] Click any scene to edit
- [ ] Text input for revision instructions
- [ ] Side-by-side comparison (before/after)
- [ ] Accept/reject changes
- [ ] Revision history timeline
- [ ] Quick actions: "Make it longer", "Add more detail", "Change tone"

**Database**:
```sql
CREATE TABLE story_revisions (
  revision_id UUID PRIMARY KEY,
  story_id UUID,
  scene_id UUID,
  original_content TEXT,
  revised_content TEXT,
  revision_instruction TEXT,
  created_at TIMESTAMP,
  user_id INTEGER
);
```

**Success Criteria**:
- Can edit any story scene with AI help
- Revision history navigable
- Integration with TasteProfile for style consistency
- Undo/redo works reliably
- Preserves narrative continuity

---

### 3.9 Character Relationship Graph (1 week)
**Priority**: MEDIUM - Depth for storytelling
**Complexity**: Medium

**Problem**: Characters exist in isolation. Relationships add depth to storytelling.

**Database Schema**:
```sql
CREATE TABLE character_relationships (
  relationship_id UUID PRIMARY KEY,
  character_a_id UUID,
  character_b_id UUID,
  relationship_type VARCHAR(50), -- family, friends, rivals, romantic, mentor_student
  strength INTEGER, -- 1-10 closeness indicator
  description TEXT,
  timeline_start DATE,
  timeline_end DATE,
  user_id INTEGER,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**Features**:
- [ ] Visual graph of character relationships (D3.js)
- [ ] Relationship types: family, friends, rivals, romantic, mentor/student
- [ ] Strength/closeness indicators (1-10 scale)
- [ ] Timeline of relationship changes
- [ ] Auto-suggest relationships from stories (AI reads story, detects interactions)
- [ ] Filter stories by relationship ("Show all stories with X and Y")
- [ ] Bidirectional relationships (A→B and B→A)

**Auto-Detection Agent**:
- [ ] Reads story content
- [ ] Identifies character interactions
- [ ] Infers relationship type and strength
- [ ] Suggests relationships for user approval
- [ ] Updates existing relationships based on story events

**UI**:
- [ ] D3.js graph visualization
- [ ] Drag-to-create relationships
- [ ] Click relationship to edit details
- [ ] Filter by relationship type
- [ ] Timeline view of relationship evolution
- [ ] "Suggest Relationships" button (runs AI analysis)

**Success Criteria**:
- Relationship graph helps with story planning
- Auto-detection >70% accurate
- Easy to navigate and understand
- Graph performant with 50+ characters
- Useful for tracking character arcs

---

### 3.10 Character Development Tracker (1 week)
**Priority**: MEDIUM - Character arc visualization
**Complexity**: Medium
**Depends on**: Stories saved to database (Section 2.3)

**Problem**: Characters evolve across stories. Need to track their arcs.

**Features**:
- [ ] Timeline view of character across stories
- [ ] Track changes: personality traits, relationships, appearance, skills
- [ ] Visual arc visualization (character growth over time)
- [ ] Consistency warnings ("Character died in Story 3 but appears in Story 5")
- [ ] Trait evolution tracking ("Brave in Story 1 → Cautious in Story 3")
- [ ] Milestone detection (first appearance, major events, final appearance)

**Analysis Engine**:
- [ ] Reads all stories featuring character
- [ ] Extracts character traits per story
- [ ] Detects changes over time
- [ ] Identifies inconsistencies
- [ ] Generates development summary

**Database**:
```sql
CREATE TABLE character_snapshots (
  snapshot_id UUID PRIMARY KEY,
  character_id UUID,
  story_id UUID,
  traits JSONB, -- {"brave": 8, "cautious": 3, "compassionate": 7}
  relationships JSONB,
  major_events TEXT[],
  created_at TIMESTAMP
);
```

**UI**:
- [ ] Timeline visualization (horizontal axis = time/stories)
- [ ] Trait evolution chart (line graph)
- [ ] Milestone markers on timeline
- [ ] Consistency warning badges
- [ ] "Character in Story X" snapshot cards
- [ ] Export character arc summary

**Example Output**:
```
Character Arc: Luna
- Story 1 (Origin): Timid, inexperienced, eager to prove herself
- Story 2 (Growth): More confident, learns magic, befriends mentor
- Story 3 (Trial): Faces fear, overcomes challenge, becomes leader
- Story 4 (Mastery): Confident, skilled, mentors others

⚠️ Consistency Warning: Luna uses fire magic in Story 2 but can't in Story 4
```

**Success Criteria**:
- Can see character evolution at a glance
- Consistency warnings prevent plot holes
- Useful for series/multi-story arcs
- Timeline visualization clear and intuitive
- Helps writers maintain character consistency

---

### 3.11 Retroactive Story Illustration (1 week)
**Priority**: MEDIUM - Enhance existing stories
**Complexity**: Medium
**Depends on**: Stories saved to database (Section 2.3)

**Problem**: User has past stories (imported or old) without illustrations

**Features**:
- [ ] "Generate Illustrations" button on any story detail page
- [ ] AI reads story and plans most impactful scenes to illustrate
- [ ] User selects how many images (1-10)
- [ ] AI generates illustration prompts for selected scenes
- [ ] Generate images and link to story scenes
- [ ] Update story with embedded images

**Illustration Planning Agent**:
- [ ] Reads full story text
- [ ] Identifies key narrative moments:
  - Character introductions
  - Climactic scenes
  - Emotional turning points
  - Visually striking descriptions
- [ ] Ranks scenes by illustration impact
- [ ] Generates detailed art direction for each:
  - Composition guidance
  - Lighting/mood suggestions
  - Character positioning
  - Environmental details
- [ ] Maintains visual consistency across illustrations

**UI Flow**:
1. User views story in `/entities/stories`
2. Clicks "Generate Illustrations" button
3. AI shows suggested scenes (ranked by impact)
4. User selects scenes to illustrate (or accepts top N)
5. AI generates art direction previews
6. User approves or tweaks directions
7. Generates illustrations
8. Inserts images into story at scene markers

**Success Criteria**:
- Can illustrate any existing story
- Illustration planning identifies impactful scenes
- Art direction generates visually consistent images
- Illustrations enhance story experience

---

### Phase 3 Success Metrics

- [ ] No component over 500 lines
- [ ] Frontend coverage >40%
- [ ] All tests passing (100%)
- [ ] Consistent error handling
- [ ] TasteProfile learns from 100+ interactions
- [ ] "Find Similar" accuracy >80%
- [ ] Recipe library has 20+ saved recipes
- [ ] Variant Orchards used weekly
- [ ] Inspiration Inbox captures 50+ items
- [ ] All creative exploration and maintenance tasks complete

**Total Duration**: 7-9 weeks
**Total Features**: 7 major features (3 maintenance + 4 creative intelligence)

---

## Phase 4: Reproducibility & Provenance (3-4 weeks)

**Goal**: Full asset lineage, one-click reproduce
**Why Now**: Foundation for debugging, cost tracking, commercial work

### 4.1 One-Asset Model (2-3 weeks) 🌟 **FOUNDATIONAL**
**Priority**: HIGH - Core reproducibility feature
**Complexity**: High

**Asset Schema**:
```python
class Asset:
    asset_id: UUID
    asset_type: Enum["image", "doc", "audio", "video"]
    file_path: str

    # Provenance
    tool_name: str
    model_name: str
    template_revision: str
    input_entity_ids: List[UUID]
    generation_params: Dict
    seed: Optional[int]
    cost_usd: float

    # Relationships
    derived_from: List[UUID]  # Parent assets
    inspired_by: List[UUID]   # Reference assets
    illustrates: List[UUID]   # Story scenes

    # Metadata
    created_at: datetime
    user_id: int
```

**Features**:
- [ ] Unify images, docs, audio, video under canonical Asset
- [ ] Track full provenance for every asset
- [ ] "Reproduce" button on every asset
- [ ] Side-by-side input diff viewer
- [ ] Lineage graph visualization
- [ ] Cost rollup (asset + all dependencies)
- [ ] "Why does this look this way?" explanation

**Success Criteria**:
- Can reproduce any generation from 6 months ago
- Asset relations navigable
- Full cost attribution
- Provenance explanations clear

---

### 4.2 One-Click Image Restore (3-5 days)
**Priority**: HIGH - Continue from where you left off
**Complexity**: Medium
**Depends on**: One-Asset Model

**Concept**: Restore Image Composer state from any generated image

**Features**:
- [ ] "Restore in Composer" button on every generated image
- [ ] Extract all applied presets/entities from generation metadata:
  - Subject (character)
  - Applied clothing items
  - Applied alterations
  - Visual styles
  - Expression, hair color, makeup, accessories
  - Visualization config used
- [ ] Re-open Image Composer with all components loaded
- [ ] Do NOT re-render automatically
- [ ] User can:
  - See exactly what was used to create the image
  - Modify any component (swap outfit, change expression, etc.)
  - Generate new variations from this starting point
  - Save as new composition

**Implementation**:
- [ ] Store complete generation context in asset metadata:
  ```json
  {
    "generation_params": {
      "subject_id": "uuid",
      "presets_applied": [
        {"category": "clothing_items", "id": "uuid", "order": 1},
        {"category": "expressions", "id": "uuid", "order": 2},
        // ...
      ],
      "visualization_config_id": "uuid",
      "additional_instructions": "text"
    }
  }
  ```
- [ ] API endpoint: `POST /api/images/{image_id}/restore-to-composer`
  - Returns: Complete state object for Image Composer
- [ ] Frontend: Restore state in Image Composer
  - Load subject
  - Apply presets in correct order
  - Set visualization config
  - Fill additional instructions
  - Ready to modify/regenerate

**UI Flow**:
1. User views generated image in gallery
2. Clicks "Restore in Composer" button
3. Image Composer opens with all components loaded
4. User sees the exact recipe that created the image
5. User modifies any component
6. User generates new variation

**Success Criteria**:
- Can restore any generated image to Image Composer
- All components load correctly in the right order
- State matches exactly what was used in original generation
- User can immediately modify and regenerate
- Works for images from 6+ months ago (if provenance tracked)

**Why This Matters**:
- **Iterative Design**: Continue refining without starting from scratch
- **Recipe Discovery**: See exactly what combination worked well
- **Learning**: Understand how components interact
- **Efficiency**: Skip composition setup, jump straight to variations

---

### 4.3 Asset Relations Graph (1 week)
**Priority**: MEDIUM - Smart navigation
**Complexity**: Medium
**Depends on**: One-Asset Model

**Relation Types**:
- `inspired_by`: This outfit inspired by that Pinterest save
- `derived_from`: This variant derived from that base image
- `illustrates`: This image illustrates that story scene
- `references`: This generation references that style preset

**Features**:
- [ ] Relation graph visualization (D3.js)
- [ ] Relation panel in detail view
- [ ] "Add relation" modal with search
- [ ] Auto-suggested relations based on metadata
- [ ] Orphan detection (assets with no incoming relations)

**UI**:
- [ ] Graph visualization page
- [ ] "Show everything derived from this style ref"
- [ ] "What inspired this outfit?"
- [ ] "Find all illustrations for this story"

**Success Criteria**:
- Relations easy to add and navigate
- Graph visualization performant with 1000+ assets
- Auto-suggestions helpful

---

### Phase 4 Success Metrics

- [ ] Can reproduce any generation from 6 months ago
- [ ] Can restore any image to Image Composer
- [ ] Asset relations navigable and useful
- [ ] Full cost attribution working
- [ ] Provenance explanations clear
- [ ] One-Asset Model adopted for all new generations

**Total Duration**: 4-5 weeks
**Total Features**: 3 major features

---

## Phase 5: Infrastructure Hardening (3-4 weeks)

**Goal**: Robust, secure, observable infrastructure
**Why Now**: Before adding autonomy, need solid monitoring and security

### 5.1 Monitoring & Observability (1 week)

**Metrics & Monitoring**:
- [ ] Prometheus metrics endpoint (`/metrics`)
- [ ] Track key metrics:
  - Request count/latency by endpoint
  - Error rate by endpoint
  - LLM API costs (by provider, tool, user)
  - Database query latency
  - Job queue depth
  - Cache hit rate
- [ ] Grafana dashboards:
  - System health overview
  - API performance
  - LLM cost breakdown
  - Job queue status
  - Error rate trends
- [ ] Alerting (email, Slack):
  - Error rate >5% (critical)
  - p95 latency >1s (warning)
  - Job queue depth >100 (warning)
  - LLM costs >$50/day (warning)

**Distributed Tracing**:
- [ ] OpenTelemetry integration
- [ ] Trace request flows (frontend → API → LLM)
- [ ] Identify slow operations
- [ ] Correlation IDs across services

**Health Checks**:
- [ ] `/health/ready` (service ready)
- [ ] `/health/live` (service alive)
- [ ] Database connectivity check
- [ ] Redis connectivity check
- [ ] External API connectivity check

**Success Criteria**:
- Prometheus scraping every 15s
- Grafana dashboards visualize all metrics
- Alerts trigger within 1 minute
- Cost tracking accurate to $0.10/day

---

### 5.2 Security Hardening (1 week)

**SQL Injection Prevention**:
- [ ] Audit all database queries (parameterized only)
- [ ] Add SQL injection tests (sqlmap)
- [ ] Input validation on all endpoints
- [ ] Query complexity limits

**XSS & CSRF Protection**:
- [ ] Content Security Policy (CSP) headers
- [ ] X-Frame-Options header
- [ ] X-Content-Type-Options header
- [ ] XSS vulnerability scanning (OWASP ZAP)
- [ ] CSRF token validation

**Authentication & Authorization**:
- [ ] JWT token expiration testing
- [ ] Refresh token implementation
- [ ] Session management (logout invalidates tokens)
- [ ] Password complexity requirements
- [ ] Rate limiting on login endpoint

**API Rate Limiting**:
- [ ] Add slowapi middleware
- [ ] Rate limits:
  - 10 generations/minute per user
  - 100 API calls/minute per user
  - 1000 API calls/hour per IP
- [ ] Rate limit headers
- [ ] Clear error messages when rate limited

**Success Criteria**:
- No SQL injection vulnerabilities
- No XSS vulnerabilities
- All security headers present
- Rate limiting effective

---

### 5.3 Backup & Disaster Recovery (1 week)

**Automated Backups**:
- [ ] PostgreSQL backups:
  - Daily full backups (retain 30 days)
  - Hourly incremental backups (retain 7 days)
  - Point-in-time recovery capability
- [ ] File backups:
  - Images, presets, configs
  - Daily snapshots (retain 14 days)
- [ ] Backup testing (restore monthly)

**Disaster Recovery**:
- [ ] Recovery Time Objective (RTO): <4 hours
- [ ] Recovery Point Objective (RPO): <1 hour
- [ ] Documented recovery procedures
- [ ] Tested restore from backup
- [ ] Off-site backup storage

**Success Criteria**:
- Backups run automatically daily
- Restore tested and working
- Recovery procedures documented
- RTO/RPO targets met

---

### 5.4 Local LLM Frontend (2-3 days)

**Complete Local LLM Integration** (95% → 100%):
- [ ] Local Models page (`/local-models`)
- [ ] List downloaded models with metadata
- [ ] Pull models with progress tracking
- [ ] Delete models
- [ ] Test model interface
- [ ] Disk usage display and warnings
- [ ] Model catalog with recommendations
- [ ] Clear labeling (local vs cloud in tool configs)

**Success Criteria**:
- Frontend UI for model management
- Non-technical users can download models
- Disk usage visible and warnings work

---

### Phase 5 Success Metrics

- [ ] Prometheus + Grafana operational
- [ ] All security scans passing
- [ ] Backups automated and tested
- [ ] Local LLM frontend complete (100%)
- [ ] Infrastructure ready for autonomy

**Total Duration**: 3-4 weeks
**Total Features**: 4 major infrastructure improvements

---

## Phase 6: Developer Autopilot (6-8 weeks)

**Goal**: MCP-powered development, quality gates
**Why Now**: Build developer tools before general autonomy

### 6.1 MCP Integration (2-3 weeks) 🌟 **FOUNDATIONAL**
**Priority**: HIGH - Enables ticket completion
**Complexity**: High

**MCP Endpoints**:
- [ ] `repo.survey` - Analyze codebase for ticket context
- [ ] `change.plan` - Generate implementation plan
- [ ] `patch.generate` - Create code changes
- [ ] `tests.run` - Execute test suite
- [ ] `review.report` - Generate review report
- [ ] `pr.open` - Open pull request

**"Complete Ticket" Workflow**:
1. User: "Claude, complete ticket #42: Add dark mode"
2. Claude Code via MCP:
   - Calls `repo.survey` → understands codebase
   - Calls `change.plan` → generates plan
   - Calls `patch.generate` → creates changes
   - Calls `tests.run` → runs tests
   - If tests fail → fixes and reruns
   - Calls `review.report` → generates report
   - Calls `pr.open` → opens PR with green checks

**Policy Enforcement**:
- [ ] Path limits (only approved directories)
- [ ] Diff size limits (max 500 lines per PR)
- [ ] Cost limits (max $5 per ticket)
- [ ] Approval required before merge

**Success Criteria**:
- Can complete ticket via chat
- Tests always green before PR
- Policy limits enforced
- PR quality high

---

### 6.2 Small-PR Factory (1 week)
**Priority**: MEDIUM - Nightly improvements
**Complexity**: Medium

**Nightly PRs** (opinionated):
- Add missing docstrings
- Add tests for uncovered functions
- Extract magic numbers to constants
- Fix typos in comments
- Update stale documentation
- Add type hints

**Process**:
- Runs nightly as scheduled job
- Analyzes codebase for opportunities
- Creates PR with one improvement
- Runs full test suite
- Adds review report to PR description
- User reviews and merges (never auto-merges)

**Policy**:
- Max 1 PR per night
- Max 100 lines changed
- Must have green checks
- Only safe refactors (no behavior changes)

**Success Criteria**:
- Nightly PRs always green
- PR merge rate >90%
- Code quality improving

---

### 6.3 Default-On Quality Gates (1 week)
**Priority**: HIGH - Prevents regressions
**Complexity**: Medium

**Gates**:
- [ ] Tests pass (backend + frontend)
- [ ] Coverage floor (80% backend, 40% frontend)
- [ ] Linting (zero warnings)
- [ ] a11y checks (WCAG AA compliance)
- [ ] Design System compliance (no ad-hoc styles)

**Autopilot Fixes**:
- Common test failures → auto-fix and amend PR
- Linting errors → auto-format and commit
- Missing tests → auto-generate and add

**Process**:
1. Developer opens PR
2. CI runs quality gates
3. Failures trigger Autopilot
4. Autopilot fixes and amends PR
5. CI reruns with fixes
6. If still failing → blocks merge

**Success Criteria**:
- Quality gates enforced on all PRs
- Auto-fix success rate >80%
- Zero regressions

---

### 6.4 Prompt-Eval Guardrails (1 week)
**Priority**: MEDIUM - Prevent prompt regressions
**Complexity**: Medium

**Golden Set**:
- 10-20 test cases per tool
- Known good inputs → expected outputs
- Stored as fixtures

**Checks**:
- Structured output parsing (JSON matches schema?)
- Semantic quality (model-graded rubric)
- Consistency (same input → similar output)
- Cost (prompt token count within budget)

**Process**:
- Runs on every prompt template change
- Fails build if:
  - Structured output breaks
  - Quality drops >10%
  - Cost increases >20%
- Shows before/after comparison

**Success Criteria**:
- Zero prompt regressions
- Quality stable
- Cost stable

---

### Phase 6 Success Metrics

- [ ] Can complete ticket via chat
- [ ] Nightly PRs always green
- [ ] Zero prompt regressions
- [ ] Quality gates enforced
- [ ] Developer velocity increased

**Total Duration**: 6-8 weeks
**Total Features**: 4 major developer tools

---

## Phase 7: Design System Intelligence (4-5 weeks)

**Goal**: Figma sync, component registry, critique
**Why Now**: Design consistency becomes critical as UI grows

### 7.1 Design System 2.0 (2-3 weeks)
**Priority**: MEDIUM - Single source of truth
**Complexity**: High

**Figma ↔ Tokens ↔ React Sync**:
1. Designer updates Figma variables (colors, spacing, typography)
2. Export design tokens as JSON
3. Generate CSS variables + TypeScript types
4. UI package imports tokens
5. Lint rule rejects ad-hoc styles

**Benefits**:
- Single source of truth (Figma)
- Type-safe design system
- Automated consistency
- Easy theme switching

**Success Criteria**:
- Design tokens auto-sync from Figma
- Ad-hoc styles rejected by linter
- Theme switching seamless

---

### 7.2 Component Registry + Telemetry (1 week)
**Priority**: LOW - Maintenance tool
**Complexity**: Medium

**Features**:
- [ ] `@lifeos/ui` package with semver
- [ ] Storybook documentation
- [ ] Usage telemetry (which components used where)
- [ ] Dead variant detection
- [ ] Over-customization warnings

**Success Criteria**:
- Dead components detected
- Component usage tracked
- Storybook documentation complete

---

### 7.3 Pattern Ingestion & Critique (1 week)
**Priority**: LOW - Creative tool
**Complexity**: High

**Features**:
- Upload screenshot or URL
- Extract layout, typography, patterns
- Map to Design System components
- Generate critique:
  - Low contrast issues
  - Missing states (hover, focus, disabled)
  - Weak hierarchy
  - Questionable UX patterns
- Propose Design System variant

**Example**:
- Input: Dribbble screenshot
- Output:
  - "Layout: 3-column grid, 16px gap"
  - "Typography: 32px heading, 16px body"
  - "⚠️ Contrast ratio 3.2:1 (fails WCAG AA)"
  - "💡 Suggest: Use Card component with Grid layout"

**Success Criteria**:
- Pattern critique actionable
- Contrast checks accurate
- Design System suggestions helpful

---

### Phase 7 Success Metrics

- [ ] Design tokens auto-sync from Figma
- [ ] Dead components detected
- [ ] Pattern critique actionable
- [ ] Design System compliance high

**Total Duration**: 4-5 weeks
**Total Features**: 3 design system tools

---

## Phase 8: Daily Operating System (8-10 weeks) 🌟 **MAJOR MILESTONE**

**Goal**: Morning brief, rolling feed, auto-prep
**Why Now**: Foundation complete, ready for daily OS features

### 8.1 Event + Context Bus (2 weeks) 🌟 **FOUNDATIONAL**
**Priority**: HIGH - Foundation for Brief and Auto-Prep
**Complexity**: High

**Events**:
- `image_generated` - Image generation completes
- `story_published` - Story workflow finishes
- `pr_opened` - PR created
- `entity_archived` - Entity archived
- `recipe_used` - Recipe applied
- `favorite_added` - User favorites something

**Context Slices**:
- **Recent & Relevant**: Last 24 hours of activity
- **Pending**: Drafts, open PRs, queued jobs
- **Maintenance**: Backups needed, disk space, cache size
- **Creative Packs**: Generated but not reviewed

**Consumers**:
- Daily Brief (primary)
- Auto-Prep (schedules work)
- TasteProfile (learns from events)
- Recipe Builder (detects patterns)

**Implementation**:
- [ ] Redis pub/sub for event bus
- [ ] PostgreSQL for event store (audit trail)
- [ ] Context manager assembles slices
- [ ] Subscribers register handlers

**Success Criteria**:
- Events emitted reliably
- Context slices accurate
- Consumers receive events
- Event store queryable

---

### 8.2 5:00 AM Daily Brief (3-4 weeks) 🌟 **CORE FEATURE**
**Priority**: HIGH - Core user experience
**Complexity**: High
**Depends on**: Event Bus, TasteProfile

**Daily Brief (5:00 AM)**:
- 5 cards: 2 work, 1 life, 1 creative pack, 1 maintenance
- Each card includes:
  - **What**: Brief description
  - **Why**: Reason this surfaced
  - **Action**: One-tap action button
  - **Provenance**: Drawer showing full reasoning

**Examples**:
- "Review PR #42" (work) - Checks green, awaiting review
- "Finish 'Dark Knight' story" (creative) - Draft 80% complete
- "Backup database" (maintenance) - Last backup 7 days ago

**Backend**:
- [ ] Event bus emits domain events
- [ ] Card generator subscribes to events
- [ ] Ranking algorithm (TasteProfile + recency + context)
- [ ] Card storage (brief history)

**UI**:
- [ ] Dedicated `/brief` page
- [ ] Card components with provenance drawer
- [ ] One-tap actions (approve, dismiss, snooze)

**Success Criteria**:
- Brief surfaces every morning at 5:00 AM
- Card acceptance rate >70%
- "Why surfaced" reasoning clear
- One-tap actions work reliably

---

### 8.3 Rolling Feed (1 week)
**Priority**: MEDIUM - Throughout-day context
**Complexity**: Medium
**Depends on**: Event Bus, Daily Brief

**Features**:
- Context changes → new cards surface
- Examples:
  - Story published → "Share on social?"
  - Image generated → "Explore variants?"
  - PR merged → "Deploy to staging?"
- Lightweight notifications (not intrusive)
- Grouped by context (work, creative, life, maintenance)

**UI**:
- [ ] Rolling feed sidebar or banner
- [ ] Card components (same as Brief)
- [ ] Dismiss/snooze actions
- [ ] Do not disturb mode

**Success Criteria**:
- Cards surface at right time
- Not intrusive/spammy
- Dismissible and snoozable

---

### 8.4 Policy as Data (1 week) 🌟 **FOUNDATIONAL**
**Priority**: HIGH - Foundation for all autonomy
**Complexity**: Medium

**Policy Schema**:
```yaml
policies:
  visual_autopilot:
    allowed_actions: [generate_pack, create_variant]
    daily_budget_usd: 10
    requires_approval: true

  dev_autopilot:
    allowed_actions: [add_tests, add_docs, safe_refactor]
    allowed_paths: [tests/, docs/, *.md]
    max_lines_per_pr: 500
    requires_approval: true

  auto_prep:
    allowed_actions: [draft_pack, queue_job, generate_brief]
    nightly_budget_usd: 5
    max_compute_minutes: 60

  auto_tidy:
    allowed_actions: [file, tag, link, archive_stale]
    all_reversible: true
    no_deletions: true
```

**Features**:
- [ ] Visual policy editor (YAML with schema validation)
- [ ] Policy versioning (track changes)
- [ ] Per-user policies
- [ ] Policy override (admin can bypass)
- [ ] Policy audit log

**Enforcement**:
- Every agent action checks policy
- Policy violations → log + block + notify
- Policy changes → immediate effect

**Success Criteria**:
- Policies easy to edit
- Enforcement 100% reliable
- Audit log complete

---

### 8.5 Auto-Prep Mode (2-3 weeks)
**Priority**: MEDIUM - Hands-off preparation
**Complexity**: High
**Depends on**: Event Bus, Policy System, TasteProfile

**Auto-Prep (Runs Nightly)**:
- Draft tomorrow's creative packs (based on TasteProfile)
- Prepare PR review queue (green checks first)
- Queue maintenance tasks (backups, cache clear)
- Generate morning brief cards
- All under policy caps (max spend, max time)

**Policy Caps**:
- Max $5 spend per night
- Max 1 hour compute time
- Max 50 actions per session
- Always produce Brief cards

**Example**:
- 11:00 PM: Auto-Prep runs
- Generates 3 creative packs aligned with taste
- Drafts 2 outfit compositions
- Queues 1 variant orchard for morning
- Prepares PR review for most urgent ticket
- Total cost: $2.30, time: 15 min
- Morning Brief: "3 packs ready, 2 outfits drafted, 1 PR to review"

**Success Criteria**:
- Auto-Prep stays under budget 95% of days
- Prepared content useful (acceptance >70%)
- No unwanted actions

---

### 8.6 Auto-Tidy Mode (1 week)
**Priority**: LOW - Post-session cleanup
**Complexity**: Medium
**Depends on**: Event Bus, Policy System

**Auto-Tidy (Runs Post-Session)**:
- File generated images into collections
- Tag entities based on content
- Link related assets (inspired_by, derived_from)
- Archive unused drafts (7+ days old, never opened)
- All reversible (can undo any tidying action)

**Policy Caps**:
- All actions reversible
- No deletions (archive only)
- Max 50 actions per session

**Example**:
- User finishes creative session
- Generated 12 images
- Auto-Tidy runs:
  - Files 10 images into "Character Portraits" collection
  - Tags 2 images as "Needs Review"
  - Links 5 images as derived_from source image
  - Archives 3 draft outfits (unused for 10 days)
- Brief card: "Tidied 12 images, archived 3 stale drafts"

**Success Criteria**:
- Auto-Tidy reversal rate <10%
- Actions sensible and helpful
- No unwanted changes

---

### Phase 8 Success Metrics 🌟

- [ ] Brief surfaces 5 cards every morning at 5:00 AM
- [ ] Card acceptance rate >70%
- [ ] Auto-Prep stays under budget 95% of days
- [ ] Auto-Tidy reversal rate <10%
- [ ] User reports "indispensable" rating
- [ ] LifeOS becomes daily operating system

**Total Duration**: 8-10 weeks
**Total Features**: 6 major features
**Impact**: LifeOS becomes your **daily operating system**

---

## Phase 9: Policy-Bound Autonomy (6-8 weeks)

**Goal**: Propose-first agents with guardrails
**Why Now**: Infrastructure ready, policies in place

### 9.1 Visual Autopilot (2-3 weeks)
**Priority**: MEDIUM - Nightly creative packs
**Complexity**: High
**Depends on**: TasteProfile, Policy System, Event Bus

**Process**:
1. Nightly scheduler triggers at 2:00 AM
2. TasteProfile suggests 3 creative directions
3. Autopilot generates preview images (low-res)
4. Ranks by taste alignment + aesthetic quality
5. Selects top 3 packs
6. Adds to Brief: "3 packs ready, $4.50 spent, approve?"
7. User approves with one tap
8. Autopilot generates full-resolution images
9. Files into collections

**Policy Caps**:
- Max $10/day budget
- Max 20 images generated
- All previewed before final generation
- User approval required

**UI**:
- [ ] Brief card with 3 thumbnails
- [ ] Tap to see full previews
- [ ] "Approve All" or individual approval
- [ ] "Regenerate" if taste misaligned

**Success Criteria**:
- Autopilot approval rate >80%
- Generated packs aligned with taste
- Never exceeds budget

---

### 9.2 Dev Autopilot (2-3 weeks)
**Priority**: MEDIUM - Docs/tests only
**Complexity**: High
**Depends on**: MCP Tools, Policy System

**Allowed Actions**:
- Add missing docstrings
- Generate tests for uncovered code
- Update stale documentation
- Safe refactors (extract constants, rename variables)

**Forbidden Actions**:
- Change business logic
- Modify API contracts
- Delete code
- Refactor outside allowed paths

**Process**:
1. Nightly scan finds opportunities
2. Autopilot creates branch
3. Makes changes (within policy limits)
4. Runs full test suite
5. Opens PR with review report
6. User reviews and merges (never auto-merges)

**Graduation**:
- After 10 consecutive approved PRs
- Graduates to small refactors
- Still requires approval, just wider scope

**Success Criteria**:
- Dev Autopilot PR merge rate >90%
- Zero policy violations
- Agents graduate to wider scope

---

### 9.3 Policy Enforcement Framework (1 week)
**Priority**: HIGH - Safety critical
**Complexity**: Medium

**Features**:
- [ ] Policy versioning (track all changes)
- [ ] Policy audit log (all decisions logged)
- [ ] Policy override (admin emergency bypass)
- [ ] Policy violation alerts (immediate notification)
- [ ] Graduation system (expand scope after trust)

**Success Criteria**:
- Zero policy violations in production
- Audit log complete and queryable
- Graduation system working

---

### Phase 9 Success Metrics

- [ ] Visual Autopilot approval rate >80%
- [ ] Dev Autopilot PR merge rate >90%
- [ ] Zero policy violations in production
- [ ] Agents graduate to wider scope
- [ ] User trust in autonomy high

**Total Duration**: 6-8 weeks
**Total Features**: 3 autonomy features

---

## Phase 10: Board Game Assistant (3-4 weeks)

**Goal**: Rules gathering, document RAG, Q&A
**Why Now**: Can leverage existing infrastructure (database, LLM, embeddings)

### 10.1 Rules Gatherer (1 week)
**Priority**: MEDIUM - BGG integration
**Complexity**: Medium

**Features**:
- [ ] BGG API integration (download rulebooks)
- [ ] Manual PDF upload (fallback)
- [ ] Document entity creation
- [ ] Metadata extraction (page count, file size)
- [ ] Store PDFs in `data/downloads/pdfs/{game_id}/`

**Success Criteria**:
- Can download rules from BGG
- Manual upload works for BGG failures
- Documents stored reliably

---

### 10.2 Document RAG Preparer (1-2 weeks)
**Priority**: HIGH - Core functionality
**Complexity**: High

**Features**:
- [ ] Docling integration (PDF → markdown + layout)
- [ ] ChromaDB vector store
- [ ] Document chunking (semantic)
- [ ] Embedding generation (SentenceTransformers or OpenAI)
- [ ] Vector storage with metadata

**Success Criteria**:
- PDFs processed reliably
- Embeddings stored correctly
- Semantic search working

---

### 10.3 Document Q&A System (1 week)
**Priority**: HIGH - User-facing feature
**Complexity**: Medium

**Features**:
- [ ] Semantic search (ChromaDB)
- [ ] Context assembly (top-k chunks)
- [ ] LLM answer generation (with citations)
- [ ] Citation linking (page numbers, sections)
- [ ] Q&A history (track questions asked)

**UI**:
- [ ] Chat interface for questions
- [ ] Answer with citations
- [ ] Click citation → jump to page
- [ ] Q&A history sidebar

**Success Criteria**:
- Answers accurate (>85% helpful)
- Citations correct
- Fast response (<3s)

---

### Phase 10 Success Metrics

- [ ] Can download rules from BGG
- [ ] Document Q&A helpful (>85%)
- [ ] Citations accurate
- [ ] Board game assistant usable

**Total Duration**: 3-4 weeks
**Total Features**: 3 board game tools

---

## Phase 11: Media Companion (4-5 weeks)

**Goal**: Jellyfin integration, cross-modal taste
**Why Now**: TasteProfile mature, embeddings working

### 11.1 Library Mirror & Embeddings (2 weeks)
**Priority**: LOW - Nice to have
**Complexity**: High

**Features**:
- [ ] Sync Jellyfin library → MediaAsset entities
- [ ] Generate embeddings for titles, descriptions, genres
- [ ] "Find similar" based on embedding distance
- [ ] Curated lists aligned with TasteProfile
- [ ] "Tonight's Shortlist" card in Brief

**Example**:
- User watches "Blade Runner 2049"
- System suggests:
  - "Similar: Arrival, Ex Machina, Dune"
  - "You might like: Ghost in the Shell, Akira"
  - "Based on your style preferences: Neon aesthetic films"

**Success Criteria**:
- Jellyfin library mirrored
- Suggestions aligned with taste
- "Find similar" helpful

---

### 11.2 Opportunistic Downloads (1 week)
**Priority**: LOW - Read-only awareness
**Complexity**: Medium

**Features**:
- If Sonarr/Radarr/yt-dlp detected → surface in Brief
- Propose wishlists based on taste
- See queue health
- Actions are propose-first (never auto-downloads)

**Success Criteria**:
- Read-only awareness working
- Wishlists sensible
- Never auto-downloads

---

### 11.3 Cross-Modal Taste (1-2 weeks)
**Priority**: LOW - Advanced feature
**Complexity**: High
**Depends on**: TasteProfile, Media Companion

**Concept**:
- User favorites noir visual style → System suggests noir films
- User watches cyberpunk anime → System suggests cyberpunk visual styles
- Bidirectional influence between creative and media taste

**Success Criteria**:
- Cross-domain suggestions helpful
- Bidirectional influence working
- Taste learning improved

---

### Phase 11 Success Metrics

- [ ] Jellyfin library mirrored
- [ ] Cross-domain taste influences work
- [ ] Media suggestions helpful
- [ ] Media Companion integrated

**Total Duration**: 4-5 weeks
**Total Features**: 3 media features

---

## Phase 12: Cost & Performance Optimizer (2-3 weeks)

**Goal**: Self-improving efficiency
**Why Now**: System mature, metrics available

### 12.1 Self-Observation to Actionable Deltas (2-3 weeks)
**Priority**: MEDIUM - Cost savings
**Complexity**: Medium

**Features**:
- Analyzes metrics and run histories
- Proposes specific optimizations
- Examples:
  - "Batch these 5 API calls → save $2.30/week"
  - "Raise cache TTL on presets → save 200ms/request"
  - "Switch outfit_analyzer to local → save $15/week"
- One-click config change or PR
- Shows projected savings
- Tracks actual savings after change

**UI**:
- [ ] Weekly Brief card: "3 optimizations available"
- [ ] Each optimization:
  - What: Brief description
  - Impact: Projected savings (cost/time)
  - Action: One-click apply
  - Provenance: Full analysis

**Success Criteria**:
- Proposes 3 optimizations/week
- Projected savings accurate within 20%
- Optimization acceptance rate >50%

---

### Phase 12 Success Metrics

- [ ] Proposes 3 optimizations/week
- [ ] Savings accurate
- [ ] Acceptance rate >50%
- [ ] System self-improving

**Total Duration**: 2-3 weeks
**Total Features**: 1 optimizer tool

---

## Phase 13: Capture & Knowledge Mesh (4-5 weeks)

**Goal**: Everywhere capture, private connectors
**Why Now**: Daily OS mature, ready for knowledge integration

### 13.1 Everywhere Capture (1-2 weeks)
**Priority**: MEDIUM - Ubiquitous capture
**Complexity**: Medium

**Capture Methods**:
- [ ] Mobile share target (iOS/Android)
- [ ] Browser extension button
- [ ] Screenshot hotkey
- [ ] Email forwarding address
- [ ] API endpoint (for integrations)

**Inbox**:
- [ ] Staging area for captured content
- [ ] Auto-categorize (image → style ref, link → article, text → note)
- [ ] Promote to entities with one tap
- [ ] Archive or delete unwanted captures

**Success Criteria**:
- Can save from any device
- Auto-categorization >80% accurate
- One-tap promotion

---

### 13.2 Personal Knowledge Connectors (2-3 weeks)
**Priority**: LOW - Privacy-sensitive
**Complexity**: High

**Connectors** (All Opt-In, All Private):
- [ ] Gmail: Unread emails needing response, calendar reminders
- [ ] Calendar: Upcoming meetings, prep briefs
- [ ] Notes: Unfinished drafts
- [ ] GitHub: Open PRs, issues assigned to you

**Features**:
- [ ] Clear toggle to pause any source
- [ ] Brief-quality cards only (no noise)
- [ ] Citations and provenance
- [ ] Never stores content (ephemeral context only)

**Example**:
- Brief card: "Meeting in 1 hour: Design Review"
- Provenance: Google Calendar event + related docs
- Action: "Prepare brief" → generates summary of docs

**Success Criteria**:
- Connectors surface relevant context only
- Privacy controls clear and effective
- No noise in Brief

---

### Phase 13 Success Metrics

- [ ] Can save to LifeOS from any device
- [ ] Connectors surface relevant context
- [ ] Privacy controls effective
- [ ] Knowledge mesh integrated

**Total Duration**: 4-5 weeks
**Total Features**: 2 capture/knowledge tools

---

## Phase 14: Advanced Features & Polish (Ongoing)

**Goal**: Nice-to-have features, experimental tools
**Why Now**: Core complete, time for exploration

### Features (No Specific Order):

**Outfit Composer Improvements**:
- [ ] Show preview images in Outfit Composer
- [ ] "Save as Outfit" button in Image Composer
- [ ] Auto-create outfit from image upload

**Jobs Manager Improvements**:
- [ ] Clear completed jobs button
- [ ] Hierarchical job display
- [ ] Remove fake progress indicators

**LLM Observability**:
- [ ] LangSmith integration
- [ ] LLM traces page
- [ ] Cost tracking dashboard

**Plugin Architecture** (Extensibility):
- [ ] Plugin discovery and loading system
- [ ] Plugin API with versioning
- [ ] Sandboxed plugin execution
- [ ] Plugin marketplace/registry
- [ ] Hot reload for plugin development

**Workflow Engine Enhancements**:
- [ ] Visual workflow editor (drag-and-drop)
- [ ] Conditional branching in workflows
- [ ] Loop/iteration support
- [ ] Parallel execution branches
- [ ] Workflow templates library

**Context Management System**:
- [ ] Sliding context window for long sessions
- [ ] Context compression strategies
- [ ] Relevant context retrieval (RAG for session history)
- [ ] Context budget management

**API Versioning**:
- [ ] Versioned API endpoints (/v1/, /v2/)
- [ ] Deprecation warnings for old versions
- [ ] Migration guides for breaking changes
- [ ] Backwards compatibility layer

**Load & Performance Testing**:
- [ ] Load test suite (100+ concurrent users)
- [ ] Performance regression tests
- [ ] Stress testing (failure scenarios)
- [ ] Benchmark tracking over time

**Story Narration Generation** (Audiobook-style):
- [ ] Local voice cloning (Coqui TTS, XTTS, Piper TTS)
- [ ] Custom AI voice per character
- [ ] Voice assignment UI (assign voice to character)
- [ ] Full story narration generation
- [ ] Separate narrator voice vs character dialogue
- [ ] Chapter/scene markers in audio
- [ ] Export as audiobook (MP3/M4B)
- [ ] Separate Docker container for voice services

**Workflow**:
1. User selects story for narration
2. System detects characters in story
3. User assigns voice to each character (voice library or clone)
4. User selects narrator voice
5. AI generates audio:
   - Narrator reads scene descriptions and actions
   - Character voices speak dialogue
   - Natural transitions between narrator and characters
   - Emotional tone matches scene mood
6. Stitches audio segments with chapter markers
7. Exports as audiobook file

**Advanced Features**:
- [ ] Voice cloning from user samples (3-10 min audio)
- [ ] Emotion control (happy, sad, angry, neutral)
- [ ] Pacing control (slow, normal, fast)
- [ ] Background music/ambiance (optional)
- [ ] Pronunciation dictionary (character names, fantasy words)

**Success Criteria**:
- Generates natural-sounding audiobook narration
- Character voices distinct and recognizable
- Smooth transitions between narrator and dialogue
- Export compatible with audiobook players

**Tool Configuration UI**:
- [ ] Visual tool configuration editor
- [ ] Model selection per tool
- [ ] Template customization interface
- [ ] Parameter tuning with live preview
- [ ] Configuration versioning

**TypeScript Migration** (Optional):
- [ ] Add TypeScript to Vite config
- [ ] Type definitions for API responses
- [ ] Migrate shared utilities
- [ ] Migrate components incrementally
- [ ] Target: 80% type coverage

**Story Video Dramatization** (Domain Expansion):
- [ ] Sora API integration (OpenAI)
- [ ] Video generation from story scenes
- [ ] Dramatize key story moments as short videos
- [ ] Video prompt enhancement (scene-to-video)
- [ ] Character consistency across video frames
- [ ] Video editing workflows (stitch scenes)
- [ ] Video asset management
- [ ] Export as video montage or individual clips

**Workflow**:
1. User selects story scene to dramatize
2. AI analyzes scene for:
   - Character actions and movements
   - Environment and setting
   - Emotional tone and pacing
   - Camera angles and transitions
3. Generates video prompt with:
   - Character descriptions (visual consistency)
   - Action sequence breakdown
   - Cinematic direction
4. Sends to Sora API for video generation
5. User reviews and can regenerate with tweaks
6. Option to stitch multiple scenes into montage

**Advanced Features**:
- [ ] Character reference images for consistency
- [ ] Scene-to-scene transitions
- [ ] Background music sync
- [ ] Voiceover narration (from narration feature)
- [ ] Multiple camera angles for same scene
- [ ] Export as trailer or full video story

**Success Criteria**:
- Videos match story scene descriptions
- Character appearance consistent across scenes
- Cinematic quality and composition
- Smooth transitions between scenes

**Code Management** (Domain Expansion):
- [ ] Repository analysis tools
- [ ] Code generation assistants
- [ ] Documentation generation
- [ ] Refactoring suggestions
- [ ] Code review automation

**Home Automation** (Domain Expansion):
- [ ] Smart home device integration
- [ ] Automation routine creation
- [ ] Scene management
- [ ] Energy usage tracking
- [ ] Voice control integration

**Educational Content** (Domain Expansion):
- [ ] Course material generation
- [ ] Quiz and assessment creation
- [ ] Video script creation for tutorials
- [ ] Interactive learning paths
- [ ] Progress tracking

---

## Timeline Overview (18-24 Months)

**Completed**: Phase 1 (8 weeks) ✅

**Month 1-2**: Phase 2 (UX & Core Features)
**Month 3-5**: Phase 3 (Creative Intelligence)
**Month 5-6**: Phase 4 (Reproducibility)
**Month 6-8**: Phase 5 (Infrastructure Hardening)
**Month 8-10**: Phase 6 (Developer Autopilot)
**Month 10-12**: Phase 7 (Design System Intelligence)
**Month 12-15**: Phase 8 (Daily Operating System) 🌟 **MAJOR MILESTONE**
**Month 15-17**: Phase 9 (Policy-Bound Autonomy)
**Month 17-18**: Phase 10 (Board Game Assistant)
**Month 18-20**: Phase 11 (Media Companion)
**Month 20-21**: Phase 12 (Cost Optimizer)
**Month 21-23**: Phase 13 (Capture & Knowledge)
**Month 23-24**: Phase 14 (Advanced Features)

---

## Critical Milestones

**Month 2** (Phase 2 Complete): All high-value UX features delivered
**Month 5** (Phase 3 Complete): TasteProfile learning, creative exploration working
**Month 8** (Phase 5 Complete): Infrastructure rock-solid, ready for autonomy
**Month 12** (Phase 7 Complete): Design system mature, developer tools working
**Month 15** (Phase 8 Complete): 🌟 **LifeOS becomes daily operating system**
**Month 17** (Phase 9 Complete): Agents autonomous within policy guardrails
**Month 24**: **LifeOS is comprehensive personal AI assistant**

---

## Success Metrics Summary

**Phase 2**: Archive 100%, Mobile >8/10, Tagging >60%, Theme working
**Phase 3**: TasteProfile >100 interactions, "Find Similar" >80%, Recipes >20
**Phase 4**: Reproduce from 6 months ago, Full cost attribution
**Phase 5**: Monitoring operational, Security scans passing, Backups automated
**Phase 6**: Complete ticket via chat, Nightly PRs green, Zero prompt regressions
**Phase 7**: Design tokens auto-sync, Dead components detected
**Phase 8** 🌟: Brief surfaces daily, Auto-Prep <$5/night, "Indispensable" rating
**Phase 9**: Autopilot approval >80%, PR merge >90%, Zero policy violations
**Phase 10**: Document Q&A >85% helpful, Citations accurate
**Phase 11**: Jellyfin mirrored, Cross-domain taste working
**Phase 12**: 3 optimizations/week, Savings accurate
**Phase 13**: Capture from any device, Privacy controls effective

---

## Architectural Principles

1. **Infrastructure Before Features** - Build solid foundations first
2. **Policy Before Autonomy** - No agent action without policy approval
3. **Propose Before Act** - Surface cards in Brief, get user approval
4. **Provenance Always** - Full lineage for reproducibility
5. **Taste as Foundation** - TasteProfile influences everything
6. **Reversible Actions** - Auto-Tidy and Autopilot can be undone
7. **Privacy by Default** - Personal connectors opt-in only
8. **Cost Awareness** - Track and optimize every dollar spent
9. **Maintenance Built In** - Regular refactoring prevents technical debt
10. **Easy Before Hard** - Build foundations incrementally

---

## Cost Estimates by Phase

**Phase 2**: Minimal ($0 - mostly UI work)
**Phase 2.5**: Minimal ($0 - refactoring)
**Phase 3**: Medium ($200-500 for embeddings, variant testing)
**Phase 4**: Minimal ($0 - data modeling)
**Phase 4.5**: Low ($100-200 for security scanning, monitoring tools)
**Phase 5**: Medium ($300-600 for MCP testing)
**Phase 6**: Minimal ($0 - code generation)
**Phase 7**: High ($500-1000 for brief generation, auto-prep testing)
**Phase 8**: Medium ($400-800 for autopilot testing with caps)
**Phase 9**: Low ($100-200 for document processing)
**Phase 10**: Low ($100-200 for embedding generation)
**Phase 11-12**: Low ($100-300 for optimization analysis)

**Total Estimated Development Cost**: $1,900 - $4,000 over 24 months

---

## Feature Priority Matrix

**CRITICAL** (Do First):
- Complete Archive system
- Mobile responsiveness
- Tagging system
- TasteProfile foundation
- Event + Context Bus
- Policy as Data

**HIGH** (Do Soon):
- Entity merge tool
- Clothing modification
- One-Asset Model
- Daily Brief
- Visual Autopilot
- Dev Autopilot
- MCP Integration

**MEDIUM** (Do Later):
- Variant Orchards
- Recipe Builder
- Auto-Prep/Auto-Tidy
- Monitoring & Observability
- Security Hardening
- Board Game Assistant
- Design System 2.0

**LOW** (Nice to Have):
- Extremify Tool
- Media Companion
- Pattern Critique
- Knowledge Connectors
- Outfit Composer Polish

---

## Next Steps

**Immediate** (This Week):
1. ✅ Complete Archive system UI (100% done - Oct 23, 2025)
2. ✅ Add filter toggle for archived items (COMPLETE - Oct 23, 2025)
3. ✅ Mobile responsiveness improvements (COMPLETE - Oct 23, 2025)
4. ✅ UI theme system (COMPLETE - Oct 23, 2025)
5. ✅ Database persistence for stories (COMPLETE - Oct 23, 2025)

**Next 2 Weeks**:
1. Tagging system (3-4 days) (Section 2.5)
2. Visualization config linking (1 day) (Section 2.7)
3. Entity merge tool (1 week) (Section 2.6)
4. Clothing modification tools (2-3 days) (Section 2.8)

**Next Month**:
1. Complete Phase 2 (all UX features)
2. Start Phase 2.5 (refactoring)

---

**Last Updated**: 2025-10-23 (Database Persistence: ✅ COMPLETE - Phase 2.1-2.4 all complete)
**Next Review**: After Phase 2 completion
**Maintained By**: Life-OS development team
