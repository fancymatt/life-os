# Life-OS Development Roadmap

**Last Updated**: 2025-10-23
**Status**: Phase 1 COMPLETE ✅ - Archive feature 80% complete
**Version**: 4.0 - **Comprehensive Personal AI Assistant**

---

## Overview

Life-OS is evolving from a specialized **AI image generation platform** into a **comprehensive personal AI assistant** with autonomous task execution across multiple domains. This roadmap consolidates all future development into clear phases, from critical fixes → infrastructure → creative tools → daily operating system → full autonomy.

**Current State** (October 2025):
- ✅ **Database Foundation**: PostgreSQL with 12 tables, Alembic migrations
- ✅ **17 Entity Types**: Characters, Stories, Clothing Items, Outfits, Board Games, etc.
- ✅ **24 AI Tools**: 8 analyzers + 6 generators + workflow orchestration
- ✅ **Testing Infrastructure**: 158 backend tests, CI/CD with GitHub Actions
- ✅ **Archive System**: 80% complete (database + backend done, frontend pending)
- ✅ **Local LLM Integration**: Ollama backend complete, 120B model in production use

**Vision** (12-18 months):
- 🎯 **Daily Operating System**: Morning brief, rolling feed, auto-prep/tidy
- 🎯 **Creative Intelligence**: Taste graph, variant exploration, recipe reuse
- 🎯 **Reproducible Assets**: Full provenance, one-click reproduce
- 🎯 **Developer Autopilot**: Complete ticket via MCP, nightly PR factory
- 🎯 **Policy-Bound Autonomy**: Propose-first agents with guardrails
- 🎯 **Cross-Domain Taste**: Unified taste across creative, media, and knowledge

---

## Implementation Priorities (Updated 2025-10-23)

### 🔥 ACTIVE WORK (This Week)
1. ✅ Archive Instead of Delete (80% complete - database + backend done, frontend pending)
   - ✅ Alembic migration applied (archived + archived_at columns)
   - ✅ Character repository + service with archive/unarchive
   - ✅ Archive/unarchive API endpoints
   - ⏳ Update remaining CharacterInfo response fields
   - ⏳ Frontend: Archive button, archived badge, filter toggle
   - ⏳ Apply pattern to other entities (ClothingItem, BoardGame, etc.)

### 📋 NEXT 2 WEEKS (Critical Fixes)
2. Mobile Responsiveness Basics (2 days)
   - Viewport meta tag fixes
   - Collapsible sidebar on mobile
   - Touch-friendly buttons and spacing

3. UI Theme System (3 days)
   - Dark/light/auto modes
   - CSS variable architecture
   - Persistent user preference

4. Visualization Config Linking (1 day)
   - Link visualization configs to entities
   - Batch generation with configs

### 📅 NEXT 4-6 WEEKS (High-Value Features)
5. Tagging System (3-4 days)
   - Multi-select tags on all entities
   - Tag-based filtering and search
   - Tag analytics and suggestions

6. Entity Merge Tool (1 week)
   - AI-assisted merging with reference migration
   - Preview merged entity before committing
   - Archive source entity with merge metadata

7. Alterations Entity (1 week)
   - New entity type for body modifications
   - Analyzer to extract alterations from images
   - Integration with story workflow

8. TasteProfile Foundation (2-3 weeks)
   - Embedding model for favorites/tags
   - Similarity search across entities
   - Basic taste-based ranker

---

## User-Requested Features (Organized by Category)

*Note: These features are organized by theme with priority/complexity estimates. Features from Phases are detailed below.*

### 🗂️ Category: Data Management & Integrity

#### Archive Instead of Delete ⏳ **80% COMPLETE**
**Priority**: CRITICAL
**Complexity**: Medium (2-3 days)
**Status**: Database + backend complete, frontend pending
**Phase**: 1

Replace entity deletion with archiving to maintain referential integrity.

**✅ Completed**:
- Database migration (archived + archived_at columns on 9 tables)
- SQLAlchemy models updated
- Character repository with archive/unarchive methods
- Character service with include_archived parameters
- Archive/unarchive API endpoints
- CharacterInfo response model with archived fields

**⏳ Remaining**:
- Update remaining 5 CharacterInfo instantiations in routes
- Frontend Archive button (replace Delete)
- Archived badge/visual indicator
- Filter toggle to show/hide archived
- Apply pattern to 8 other entities

**Benefits**:
- Prevents broken links (images with archived characters still show names)
- Reversible operation (unarchive capability)
- Better data integrity and audit trail

---

#### Entity Merge Tool
**Priority**: HIGH
**Complexity**: High (1 week)
**Status**: Planned
**Phase**: 2

AI-assisted merging of similar entities with reference migration.

**Workflow**:
1. User selects Entity A (keep) and Entity B (merge into A)
2. System finds all references to Entity B
3. AI analyzes both and generates merged description
4. Preview merged entity (user can edit)
5. Update all references from B → A
6. Archive Entity B with `merged_into: entity_a_id` metadata

**Example**: Merge two similar jacket clothing items into one comprehensive entity.

---

### 🎨 Category: Creative Intelligence & Exploration

#### TasteProfile (Taste Graph)
**Priority**: HIGH - Foundation for many other features
**Complexity**: High (2-3 weeks for v1)
**Status**: Planned
**Phase**: 3

Embedding-based taste model that learns from favorites, tags, accepted outputs, and reuse patterns.

**v1 Features**:
- Embedding model for all entity types (characters, styles, outfits, stories, media)
- "Find Similar" based on embedding distance
- Simple aesthetic heuristics (color harmony, composition balance, contrast)
- Taste-based ranking for sweeps and suggestions

**Data Sources**:
- Favorites (explicit positive signal)
- Tags applied by user (categorization preferences)
- Accepted vs rejected outputs (implicit feedback)
- Re-use patterns (what gets used in compositions/stories)
- Modification history (what changes user makes)

**Powers**:
- Variant Orchards ranker
- Daily Brief personalization
- Auto-Prep content selection
- Media Companion shortlists
- Better defaults everywhere

**Implementation**:
- Use SentenceTransformers or OpenAI embeddings
- Store vectors in PostgreSQL with pgvector extension
- Cosine similarity search for "find similar"
- Logistic regression or simple neural net for preference predictor

---

#### Variant Orchards
**Priority**: MEDIUM - Creative exploration tool
**Complexity**: High (1-2 weeks)
**Status**: Planned
**Phase**: 3
**Depends on**: TasteProfile foundation

Structured exploration instead of ad-hoc retries: batch sweeps across controllable axes.

**Concept**:
- Generate variants along multiple axes (palette, lighting, angle, style intensity)
- Auto-rank with aesthetic heuristics + LLM rubric
- Browse as "branches" you can prune and promote

**Example Workflow**:
1. User selects base image/prompt
2. Choose exploration axes:
   - Palette: warm/cool/vibrant/muted
   - Lighting: soft/dramatic/natural/studio
   - Angle: front/side/three-quarter/overhead
   - Style intensity: subtle/moderate/extreme
3. Generate grid of variants (2-4 per axis = 16-64 images)
4. Auto-rank by:
   - Composition balance (rule of thirds, golden ratio)
   - Color harmony (complementary, analogous, triadic)
   - Contrast and readability
   - LLM rubric: "Rate aesthetic quality 1-10, explain reasoning"
   - TasteProfile similarity to user's favorites
5. Present as tree view: prune weak branches, promote winners
6. Winners become new base for next iteration

**UI**:
- Tree/grid toggle view
- Filter by rank threshold
- Quick compare mode (side-by-side)
- One-click "explore this branch deeper"

**Cost Control**:
- Batch generation API calls (cheaper)
- Local LLM for ranking rubric (zero cost)
- User-set budget cap per orchard
- Cache embeddings for variants

---

#### Recipe Builder & Reuse
**Priority**: MEDIUM - Improves workflow efficiency
**Complexity**: Medium (1 week)
**Status**: Planned
**Phase**: 3

Every winning run becomes a reusable "recipe" you can re-apply or evolve.

**What is a Recipe**:
- Inputs: entity IDs, parameters, model settings
- Process: tool chain, workflow steps
- Outputs: generated entities, images, stories
- Provenance: full lineage for reproducibility

**Features**:
- Save any successful generation as recipe
- Name and tag recipes
- Browse recipe library
- Apply recipe to new inputs (e.g., different character, same visual style)
- Compare recipes (diff viewer for inputs/params)
- Evolve recipe (modify params, save as new version)
- Recipe templates (common patterns like "character portrait in style X")

**UI**:
- "Save as Recipe" button after generation
- Recipe library page with search/filter
- Recipe detail view with full provenance
- "Apply to..." action to reuse recipe

**Backend**:
- Store recipe JSON with entity references
- Track recipe usage (which recipes are most popular)
- Version recipes (recipe_v1, recipe_v2)

**Think CI for Prompts**: Capture, compare, replay winning configurations.

---

#### Inspiration Ingestion
**Priority**: MEDIUM
**Complexity**: Medium (1 week)
**Status**: Planned
**Phase**: 3

Web/screenshot clipper and Inspiration Inbox that turns references into presets/styles.

**Features**:
- Browser extension: "Save to LifeOS" button
- Screenshot hotkey (system-wide)
- Mobile share target (iOS/Android)
- Inspiration Inbox: staging area for clipped content
- Auto-analyze with outfit/style/character analyzers
- Convert to entities with one click
- Link to TasteProfile (these influenced your taste)

**Example Workflow**:
1. User sees great outfit on Pinterest
2. Clicks "Save to LifeOS" browser button
3. Image appears in Inspiration Inbox
4. System suggests: "Looks like an outfit - analyze?"
5. User clicks "Analyze"
6. Creates clothing item entities for each piece
7. Links to TasteProfile as "inspiration source"
8. Available in future searches/suggestions

**Backend**:
- Inbox entity type (image + URL + notes)
- Auto-analyzer dispatcher based on content type
- Entity creation from inbox items
- Track provenance: created_from_inspiration

---

#### Extremify Tool
**Priority**: LOW - Fun creative feature
**Complexity**: Medium (2-3 days)
**Status**: Planned
**Phase**: 3

Generate avant-garde versions of clothing items by amplifying unique features.

**Input**:
- Clothing item entity
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

**Use Cases**:
- Avant-garde fashion exploration
- Costume design
- Design boundary testing

---

#### Clothing Item Modification Tools
**Priority**: HIGH - Iterative design
**Complexity**: Medium (2-3 days)
**Status**: Planned
**Phase**: 2

**Modify Existing** (in-place update):
- Text input: "Make these shoulder-length" or "Change to red"
- AI updates description in place
- Mark as `manually_modified: true`

**Create Variant** (copy with changes):
- Same input, but creates new entity
- Keep `source_entity_id` reference
- Name: "{original_name} (Variant)"

**Backend**: Single endpoint handles both
**UI**: Modal with text input and action selector

---

### 🔄 Category: Reproducibility & Asset Management

#### One-Asset Model with Provenance & Reproduce
**Priority**: HIGH - Core feature for reproducibility
**Complexity**: High (2-3 weeks)
**Status**: Planned
**Phase**: 4

Unify images, docs, audio, video under canonical Asset with full lineage.

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
    illustrates: List[UUID]   # Story scenes, etc.

    # Metadata
    created_at: datetime
    user_id: int
```

**Features**:
- "Reproduce" button on every asset
- Side-by-side input diff viewer
- Lineage graph visualization
- Cost rollup (this asset + all dependencies)
- "Why does this look this way?" explanation

**Powers**:
- Exact reproduction months later
- Understanding creative decisions
- Debugging unexpected outputs
- Audit trail for commercial work

---

#### Asset Relations as First-Class Graph
**Priority**: MEDIUM
**Complexity**: Medium (1 week)
**Status**: Planned
**Phase**: 4
**Depends on**: One-Asset Model

Explicit relations for smarter navigation.

**Relation Types**:
- `inspired_by`: This outfit inspired by that Pinterest save
- `derived_from`: This variant derived from that base image
- `illustrates`: This image illustrates that story scene
- `references`: This generation references that style preset

**Powers**:
- "Show everything derived from this style ref"
- "What inspired this outfit?"
- "Find all illustrations for this story"
- Orphan detection (assets with no incoming relations = might be duplicates)

**UI**:
- Relation graph visualization (D3.js)
- Relation panel in detail view
- "Add relation" modal with search
- Auto-suggested relations based on metadata

---

### 🛠️ Category: Developer Velocity & Quality

#### Claude Code "Complete Ticket" via MCP
**Priority**: HIGH - Major productivity multiplier
**Complexity**: High (2-3 weeks)
**Status**: Planned
**Phase**: 5

Expose LifeOS dev tools as MCP endpoints for orchestrated development.

**MCP Endpoints**:
- `repo.survey`: Analyze codebase for ticket context
- `change.plan`: Generate implementation plan
- `patch.generate`: Create code changes
- `tests.run`: Execute test suite
- `review.report`: Generate review report
- `pr.open`: Open pull request

**Workflow**:
1. User: "Claude, complete ticket #42: Add dark mode"
2. Claude Code via MCP:
   - Calls `repo.survey` → understands codebase structure
   - Calls `change.plan` → generates implementation plan
   - Calls `patch.generate` → creates code changes
   - Calls `tests.run` → runs test suite
   - If tests fail → fixes and reruns
   - Calls `review.report` → generates review report
   - Calls `pr.open` → opens PR with checks green

**Policy Enforcement**:
- Path limits (only modify approved directories)
- Diff size limits (max 500 lines per PR)
- Cost limits (max $5 in API calls per ticket)
- Approval required before merge

**Benefits**:
- Complete tickets in chat without context switching
- Always green checks before PR
- Consistent code quality
- Faster iteration cycles

---

#### Small-PR Factory (Nightly)
**Priority**: MEDIUM
**Complexity**: Medium (1 week)
**Status**: Planned
**Phase**: 5

Opinionated nightly PRs for docs/tests/tiny refactors.

**Examples**:
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

---

#### Default-On Quality Gates
**Priority**: HIGH - Prevents regressions
**Complexity**: Medium (1 week)
**Status**: Planned
**Phase**: 5

Non-negotiable quality checks in PRs.

**Gates**:
- Tests pass (backend + frontend)
- Coverage floor (80% backend, 40% frontend)
- Linting (zero warnings)
- a11y checks (WCAG AA compliance)
- Design System compliance (no ad-hoc styles)

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

---

#### Prompt-Eval Guardrails
**Priority**: MEDIUM
**Complexity**: Medium (1 week)
**Status**: Planned
**Phase**: 5

Keep prompt regressions in check.

**Golden Set**:
- 10-20 test cases per tool
- Known good inputs → expected outputs
- Stored as fixtures

**Checks**:
- Structured output parsing (does JSON match schema?)
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

---

### 🎨 Category: Design System & Design Intelligence

#### Design System 2.0: Figma ↔ Tokens ↔ React
**Priority**: MEDIUM
**Complexity**: High (2-3 weeks)
**Status**: Planned
**Phase**: 6

Sync design tokens from Figma to code.

**Process**:
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

---

#### Component Registry + Usage Telemetry
**Priority**: LOW
**Complexity**: Medium (1 week)
**Status**: Planned
**Phase**: 6

Track component usage to find dead code and over-customization.

**Features**:
- `@lifeos/ui` package with semver
- Storybook documentation
- Usage telemetry (which components used where)
- Dead variant detection
- Over-customization warnings

---

#### Pattern Ingestion & "Argue-Back" Critique
**Priority**: LOW - Creative tool
**Complexity**: High (2 weeks)
**Status**: Planned
**Phase**: 6

Paste URL/screenshot → extract patterns + critique.

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
  - "Typography: 32px heading, 16px body, 1.5 line-height"
  - "⚠️ Contrast ratio 3.2:1 (fails WCAG AA)"
  - "⚠️ No focus states on interactive elements"
  - "💡 Suggest: Use Card component with Grid layout"

---

### 🌅 Category: Daily Operating Layer & Context

#### 5:00 AM Daily Brief + Rolling Feed
**Priority**: HIGH - Core user experience
**Complexity**: High (3-4 weeks)
**Status**: Planned
**Phase**: 7 - **Daily Operating System**

First-screen brief with personalized cards and rolling feed.

**Daily Brief (5:00 AM)**:
- 5 cards: 2 work, 1 life, 1 creative pack, 1 maintenance
- Each card includes:
  - What: Brief description
  - Why: Reason this surfaced
  - Action: One-tap action button
  - Provenance: Drawer showing full reasoning
- Examples:
  - "Review PR #42" (work) - why: Checks green, awaiting review
  - "Finish 'Dark Knight' story" (creative) - why: Draft saved 3 days ago, 80% complete
  - "Backup database" (maintenance) - why: Last backup 7 days ago

**Rolling Feed (Throughout Day)**:
- Context changes → new cards surface
- Examples:
  - Story published → "Share on social?"
  - Image generated → "Explore variants?"
  - PR merged → "Deploy to staging?"
- Lightweight notifications (not intrusive)
- Grouped by context (work, creative, life, maintenance)

**Backend**:
- Event bus emits domain events
- Card generator subscribes to events
- Ranking algorithm (TasteProfile + recency + context)
- Card storage (brief history)

**UI**:
- Dedicated `/brief` page
- Card components with provenance drawer
- Rolling feed sidebar or banner
- One-tap actions (approve, dismiss, snooze)

---

#### Event + Context Bus
**Priority**: HIGH - Foundation for Brief and Auto-Prep
**Complexity**: High (2 weeks)
**Status**: Planned
**Phase**: 7
**Depends on**: None (foundational)

Tiny event system that emits domain events and assembles context slices.

**Events**:
- `image_generated`: When image generation completes
- `story_published`: When story workflow finishes
- `pr_opened`: When PR created
- `entity_archived`: When entity archived
- `recipe_used`: When recipe applied
- `favorite_added`: When user favorites something

**Context Slices**:
- Recent & Relevant: Last 24 hours of user activity
- Pending: Drafts, open PRs, queued jobs
- Maintenance: Backups needed, disk space, cache size
- Creative Packs: Generated but not reviewed

**Consumers**:
- Daily Brief (primary consumer)
- Auto-Prep (schedules work based on context)
- TasteProfile (learns from events)
- Recipe Builder (detects patterns in events)

**Implementation**:
- Redis pub/sub for event bus
- PostgreSQL for event store (audit trail)
- Context manager assembles slices from events
- Subscribers register handlers for event types

---

#### Auto-Prep / Auto-Tidy Modes
**Priority**: MEDIUM
**Complexity**: High (2-3 weeks)
**Status**: Planned
**Phase**: 7
**Depends on**: Event Bus, Policy System

Hands-off nightly preparation and post-session tidying.

**Auto-Prep (Runs Nightly)**:
- Draft tomorrow's creative packs (based on TasteProfile)
- Prepare PR review queue (green checks first)
- Queue maintenance tasks (backups, cache clear)
- Generate morning brief cards
- All under policy caps (max spend, max time)

**Auto-Tidy (Runs Post-Session)**:
- File generated images into collections
- Tag entities based on content
- Link related assets (inspired_by, derived_from)
- Archive unused drafts (7+ days old, never opened)
- All reversible (can undo any tidying action)

**Policy Caps**:
- Max $5 spend per night
- Max 1 hour compute time
- Max 50 actions per session
- Always produce Brief cards (never silent)

**Example Auto-Prep**:
- 11:00 PM: Auto-Prep runs
- Generates 3 creative packs aligned with taste
- Drafts 2 outfit compositions
- Queues 1 variant orchard for morning
- Prepares PR review for most urgent ticket
- Total cost: $2.30, time: 15 min
- Morning Brief: "3 packs ready, 2 outfits drafted, 1 PR to review"

**Example Auto-Tidy**:
- User finishes creative session
- Generated 12 images
- Auto-Tidy runs:
  - Files 10 images into "Character Portraits" collection
  - Tags 2 images as "Needs Review"
  - Links 5 images as derived_from source image
  - Archives 3 draft outfits (unused for 10 days)
- Brief card: "Tidied 12 images, archived 3 stale drafts"

---

### 🤖 Category: Policy-Bound Autonomy

#### Policy as Data
**Priority**: HIGH - Foundation for all autonomy
**Complexity**: Medium (1 week)
**Status**: Planned
**Phase**: 8

Simple, editable policy model applied uniformly across agents.

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
- Visual policy editor (YAML with schema validation)
- Policy versioning (track changes)
- Per-user policies (different users, different caps)
- Policy override (admin can bypass)
- Policy audit log (all policy decisions logged)

**Enforcement**:
- Every agent action checks policy
- Policy violations → log + block + notify
- Policy changes → immediate effect (no restart)

---

#### Visual Autopilot (Propose-First)
**Priority**: MEDIUM
**Complexity**: High (2-3 weeks)
**Status**: Planned
**Phase**: 8
**Depends on**: TasteProfile, Policy System, Event Bus

Nightly taste-aligned image packs under budget cap.

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
- Brief card with 3 thumbnails
- Tap to see full previews
- "Approve All" or individual approval
- "Regenerate" if taste misaligned

---

#### Dev Autopilot (Docs/Tests Only)
**Priority**: MEDIUM
**Complexity**: High (2-3 weeks)
**Status**: Planned
**Phase**: 8
**Depends on**: MCP Tools, Policy System

Constrained to safe scopes, opens PRs with green checks.

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

---

### 📺 Category: Media Companion (Jellyfin & Friends)

#### Library Mirror & Embeddings
**Priority**: LOW - Nice to have
**Complexity**: High (2 weeks)
**Status**: Planned
**Phase**: 9

Mirror Jellyfin items into MediaAsset entities with embeddings.

**Features**:
- Sync Jellyfin library → MediaAsset entities
- Generate embeddings for titles, descriptions, genres
- "Find similar" based on embedding distance
- Curated lists aligned with TasteProfile
- "Tonight's Shortlist" card in Brief

**Example**:
- User watches "Blade Runner 2049"
- System suggests:
  - "Similar: Arrival, Ex Machina, Dune"
  - "You might like: Ghost in the Shell, Akira"
  - "Based on your style preferences: Neon aesthetic films"

---

#### Opportunistic Downloads (Read-Only)
**Priority**: LOW
**Complexity**: Medium (1 week)
**Status**: Planned
**Phase**: 9

Read-only awareness of Sonarr/Radarr/yt-dlp.

**Features**:
- If services detected → surface in Brief
- Propose wishlists based on taste
- See queue health
- Surface relevant items
- Actions are propose-first (never auto-downloads)

---

#### Cross-Modal Taste
**Priority**: LOW - Advanced feature
**Complexity**: High (2 weeks)
**Status**: Planned
**Phase**: 9
**Depends on**: TasteProfile, Media Companion

Blend creative and media taste.

**Concept**:
- User favorites noir visual style
- System suggests noir films
- User watches cyberpunk anime
- System suggests cyberpunk visual styles
- Bidirectional influence

---

### 📊 Category: Cost & Performance Optimizer

#### Self-Observation to Actionable Deltas
**Priority**: MEDIUM
**Complexity**: Medium (1-2 weeks)
**Status**: Planned
**Phase**: 10

Weekly card with three concrete improvements.

**Examples**:
- "Batch these 5 API calls → save $2.30/week"
- "Raise cache TTL on presets → save 200ms/request"
- "Switch outfit_analyzer to local → save $15/week"

**Features**:
- Analyzes metrics and run histories
- Proposes specific optimizations
- One-click config change or PR
- Shows projected savings
- Tracks actual savings after change

**UI**:
- Weekly Brief card: "3 optimizations available"
- Each with:
  - What: Brief description
  - Impact: Projected savings (cost/time)
  - Action: One-click apply
  - Provenance: Full analysis

---

### 📝 Category: Capture & Knowledge Mesh

#### Everywhere Capture
**Priority**: MEDIUM
**Complexity**: Medium (1-2 weeks)
**Status**: Planned
**Phase**: 11

Ubiquitous capture to Inbox.

**Capture Methods**:
- Mobile share target (iOS/Android)
- Browser extension button
- Screenshot hotkey
- Email forwarding address
- API endpoint (for integrations)

**Inbox**:
- Staging area for captured content
- Auto-categorize (image → style ref, link → article, text → note)
- Promote to entities with one tap
- Archive or delete unwanted captures

---

#### Personal Knowledge Connectors (Private, Opt-In)
**Priority**: LOW - Privacy-sensitive
**Complexity**: High (2-3 weeks)
**Status**: Planned
**Phase**: 11

**Connectors** (All Opt-In, All Private):
- Gmail: Unread emails needing response, calendar reminders
- Calendar: Upcoming meetings, prep briefs
- Notes: Unfinished drafts
- GitHub: Open PRs, issues assigned to you

**Features**:
- Clear toggle to pause any source
- Brief-quality cards only (no noise)
- Citations and provenance
- Never stores content (ephemeral context only)

**Example**:
- Brief card: "Meeting in 1 hour: Design Review"
- Provenance: Google Calendar event + related docs
- Action: "Prepare brief" → generates summary of docs

---

## Phase Roadmap (Revised with New Features)

### Phase 1: Foundation ✅ **COMPLETE**
**Duration**: 8 weeks (Completed October 2025)
**Goal**: Stable, scalable foundation

**Completed**:
- ✅ PostgreSQL migration (12 tables)
- ✅ Testing infrastructure (158 tests)
- ✅ CI/CD (GitHub Actions)
- ✅ Entity unification (17 types)
- ✅ Local LLM backend (Ollama)
- ✅ Archive system (80% - backend complete)

---

### Phase 2: User Experience & Core Features
**Duration**: 4-6 weeks
**Goal**: Polish existing features, high-value user requests

**Features**:
- [ ] Complete Archive system (frontend)
- [ ] Apply Archive to all entities
- [ ] Mobile responsiveness
- [ ] UI theme system (dark/light)
- [ ] Tagging system
- [ ] Entity merge tool
- [ ] Alterations entity
- [ ] Clothing modification tools
- [ ] Visualization config linking

**Success Criteria**:
- Zero broken links from deleted entities
- Mobile experience matches desktop
- All entities taggable and mergeable
- User can theme UI

---

### Phase 3: Creative Intelligence
**Duration**: 6-8 weeks
**Goal**: TasteProfile, exploration tools, reuse

**Features**:
- [ ] TasteProfile v1 (embeddings + similarity)
- [ ] Variant Orchards
- [ ] Recipe Builder & Reuse
- [ ] Inspiration Ingestion
- [ ] Extremify tool
- [ ] Enhanced outfit composer

**Success Criteria**:
- "Find Similar" works across all entities
- Can explore 50+ variants efficiently
- Recipes reusable and evolvable
- Taste-based ranking functional

---

### Phase 4: Reproducibility & Provenance
**Duration**: 3-4 weeks
**Goal**: Full asset lineage, one-click reproduce

**Features**:
- [ ] One-Asset Model unified
- [ ] Provenance tracking
- [ ] "Reproduce" button
- [ ] Asset Relations graph
- [ ] Lineage visualization

**Success Criteria**:
- Can reproduce any generation from 6 months ago
- Asset relations navigable
- Full cost attribution
- Provenance explanations clear

---

### Phase 5: Developer Autopilot
**Duration**: 6-8 weeks
**Goal**: MCP-powered development, quality gates

**Features**:
- [ ] MCP endpoints (repo.survey, patch.generate, etc.)
- [ ] "Complete Ticket" workflow
- [ ] Small-PR Factory (nightly)
- [ ] Default-On Quality Gates
- [ ] Prompt-Eval Guardrails
- [ ] Auto-fix common failures

**Success Criteria**:
- Can complete ticket via chat
- Nightly PRs always green
- Zero regressions in prompts
- Quality gates enforced

---

### Phase 6: Design System Intelligence
**Duration**: 4-5 weeks
**Goal**: Figma sync, component registry, critique

**Features**:
- [ ] Figma ↔ Tokens ↔ React sync
- [ ] Component Registry + Telemetry
- [ ] Pattern Ingestion
- [ ] "Argue-Back" Critique
- [ ] Design System compliance lint

**Success Criteria**:
- Design tokens auto-sync from Figma
- Dead components detected
- Pattern critique actionable
- Ad-hoc styles rejected

---

### Phase 7: Daily Operating System 🌟 **MAJOR MILESTONE**
**Duration**: 8-10 weeks
**Goal**: Morning brief, rolling feed, auto-prep

**Features**:
- [ ] Event + Context Bus
- [ ] 5:00 AM Daily Brief
- [ ] Rolling Feed
- [ ] Auto-Prep (nightly)
- [ ] Auto-Tidy (post-session)
- [ ] Policy as Data

**Success Criteria**:
- Brief surfaces 5 cards every morning
- Cards have clear "why surfaced" reasoning
- Auto-Prep runs under budget cap
- Auto-Tidy actions reversible
- Policy editor functional

---

### Phase 8: Policy-Bound Autonomy
**Duration**: 6-8 weeks
**Goal**: Propose-first agents with guardrails

**Features**:
- [ ] Policy enforcement framework
- [ ] Visual Autopilot
- [ ] Dev Autopilot
- [ ] Policy versioning + audit log
- [ ] Graduation system (expand scope after trust)

**Success Criteria**:
- Agents never exceed policy caps
- All actions logged and auditable
- User approval required for risky actions
- Autopilot trust score increases with approvals

---

### Phase 9: Media Companion
**Duration**: 4-5 weeks
**Goal**: Jellyfin integration, cross-modal taste

**Features**:
- [ ] Library Mirror & Embeddings
- [ ] "Tonight's Shortlist" card
- [ ] Opportunistic Downloads (read-only)
- [ ] Cross-Modal Taste

**Success Criteria**:
- Jellyfin library mirrored
- Taste-aligned media suggestions
- Cross-domain taste influences work

---

### Phase 10: Cost & Performance Optimizer
**Duration**: 2-3 weeks
**Goal**: Self-improving efficiency

**Features**:
- [ ] Self-Observation analysis
- [ ] Weekly optimization cards
- [ ] One-click config/PR for optimizations
- [ ] Savings tracking

**Success Criteria**:
- Proposes 3 optimizations/week
- Projected savings accurate within 20%
- Optimization acceptance rate >50%

---

### Phase 11: Capture & Knowledge Mesh
**Duration**: 4-5 weeks
**Goal**: Everywhere capture, private connectors

**Features**:
- [ ] Everywhere Capture (mobile, web, screenshot)
- [ ] Inspiration Inbox
- [ ] Personal Knowledge Connectors (opt-in)
- [ ] Brief-quality card generation

**Success Criteria**:
- Can save to LifeOS from any device
- Connectors surface relevant context only
- Privacy controls clear and effective
- No noise in Brief

---

## Success Metrics by Phase

**Phase 2 (UX & Core)**:
- [ ] Archive system 100% complete
- [ ] Mobile experience rating >8/10
- [ ] Zero broken entity links
- [ ] Tagging adoption >60% of entities

**Phase 3 (Creative Intelligence)**:
- [ ] TasteProfile learns from 100+ interactions
- [ ] "Find Similar" accuracy >80%
- [ ] Recipe library has 20+ saved recipes
- [ ] Variant Orchards used weekly

**Phase 7 (Daily OS)** 🌟:
- [ ] Brief surfaces every morning at 5:00 AM
- [ ] Card acceptance rate >70%
- [ ] Auto-Prep stays under budget 95% of days
- [ ] Auto-Tidy reversal rate <10%
- [ ] User reports "indispensable" rating

**Phase 8 (Autonomy)**:
- [ ] Visual Autopilot approval rate >80%
- [ ] Dev Autopilot PR merge rate >90%
- [ ] Zero policy violations in production
- [ ] Agents graduate to wider scope

---

## Timeline Overview (12-18 Months)

**Months 1-2**: Phase 2 (UX & Core) - Polish and high-value features
**Months 3-4**: Phase 3 (Creative Intelligence) - TasteProfile and exploration
**Month 5**: Phase 4 (Reproducibility) - Provenance and lineage
**Months 6-8**: Phase 5 (Dev Autopilot) - MCP and quality gates
**Months 9-10**: Phase 6 (Design System) - Figma sync and critique
**Months 11-13**: Phase 7 (Daily OS) - **MAJOR MILESTONE** - Brief, feed, auto-prep 🌟
**Months 14-16**: Phase 8 (Autonomy) - Policy-bound agents
**Month 17**: Phase 9 (Media Companion) - Jellyfin integration
**Month 18**: Phases 10-11 (Optimizer + Capture) - Self-improvement and knowledge mesh

**By Month 13**: LifeOS becomes your **daily operating system** - you wake up to a personalized brief, context-aware agents prepare work overnight, and autonomous actions stay within policy guardrails.

**By Month 18**: LifeOS is a **comprehensive personal AI assistant** spanning creative work, software development, media consumption, and knowledge capture—all unified by taste, policy, and provenance.

---

## Architectural Principles

1. **Infrastructure Before Features**: Build solid foundations first
2. **Policy Before Autonomy**: No agent action without policy approval
3. **Propose Before Act**: Surface cards in Brief, get user approval
4. **Provenance Always**: Full lineage for reproducibility
5. **Taste as Foundation**: TasteProfile influences everything
6. **Reversible Actions**: Auto-Tidy and Autopilot can be undone
7. **Privacy by Default**: Personal connectors opt-in only
8. **Cost Awareness**: Track and optimize every dollar spent

---

## Feature Priority Matrix

**CRITICAL (Do First)**:
- Archive Instead of Delete (80% done)
- Mobile Responsiveness
- Tagging System
- TasteProfile Foundation

**HIGH (Do Soon)**:
- Entity Merge Tool
- Clothing Modification
- Event + Context Bus
- Daily Brief

**MEDIUM (Do Later)**:
- Variant Orchards
- Recipe Builder
- Visual Autopilot
- MCP "Complete Ticket"

**LOW (Nice to Have)**:
- Extremify Tool
- Media Companion
- Pattern Critique
- Knowledge Connectors

---

## Cost Estimates by Phase

**Phase 2 (UX & Core)**: Minimal ($0 - mostly UI work)
**Phase 3 (Creative Intelligence)**: Medium ($200-500 for embeddings, variant testing)
**Phase 4 (Reproducibility)**: Minimal ($0 - data modeling)
**Phase 5 (Dev Autopilot)**: Medium ($300-600 for MCP testing)
**Phase 6 (Design System)**: Minimal ($0 - code generation)
**Phase 7 (Daily OS)**: High ($500-1000 for brief generation, auto-prep testing)
**Phase 8 (Autonomy)**: Medium ($400-800 for autopilot testing with caps)
**Phase 9 (Media Companion)**: Low ($100-200 for embedding generation)
**Phase 10-11 (Optimizer + Capture)**: Low ($100-300 for optimization analysis)

**Total Estimated Development Cost**: $1,600 - $3,500 over 18 months

---

## Questions & Open Issues

**TasteProfile**:
- Which embedding model? (SentenceTransformers vs OpenAI)
- How to handle multi-modal taste? (images + text + media)
- What's the update frequency? (real-time vs batch)

**Daily Brief**:
- How to prevent notification fatigue?
- What's the card ranking algorithm?
- How to handle Brief on weekends/vacation?

**Auto-Prep**:
- How to detect "successful" vs "failed" prep?
- What's the feedback loop for improvement?
- How to handle conflicting policies (spend cap vs prepare 5 packs)?

**Policy System**:
- How granular should policies be?
- How to override policy in emergencies?
- How to version policies without breaking agents?

**MCP Integration**:
- Which MCP tools to expose first?
- How to handle MCP endpoint failures?
- What's the fallback if MCP unavailable?

---

## Appendix: Full Feature List

This roadmap incorporates **50+ features** across 11 categories. See detailed feature specs in the category sections above.

**Categories**:
1. Data Management & Integrity (2 features)
2. Creative Intelligence & Exploration (5 features)
3. Reproducibility & Asset Management (2 features)
4. Developer Velocity & Quality (4 features)
5. Design System & Design Intelligence (3 features)
6. Daily Operating Layer & Context (3 features)
7. Policy-Bound Autonomy (3 features)
8. Media Companion (3 features)
9. Cost & Performance Optimizer (1 feature)
10. Capture & Knowledge Mesh (2 features)
11. Miscellaneous Tools & Entities (3 features)

**Total**: 31 major features + 20+ minor enhancements = 50+ feature requests tracked

---

**Last Updated**: 2025-10-23
**Next Review**: After Phase 2 completion
**Maintained By**: Life-OS development team
