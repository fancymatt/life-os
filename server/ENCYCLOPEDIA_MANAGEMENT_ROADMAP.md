# Encyclopedia Management Tool - Development Roadmap

**Created**: 2025-10-24
**Purpose**: Admin tool for managing card game encyclopedia data
**Goal**: Replace JSON-based card data with database-backed management system with full CRUD capabilities

---

## Executive Summary

This roadmap outlines development of a standalone **Encyclopedia Management Tool** - an admin interface for managing trading card game data (cards, sets, variations, pricing). The tool will replace manual JSON editing with a proper database-backed system, enabling efficient data management and reliable exports for the mobile app.

**Key Learnings Applied** (from Entity Preview Migration & Phase 1 work):
- ✅ Database-first architecture (avoid JSON → DB migration pain)
- ✅ Service layer pattern (separation of concerns)
- ✅ Job queue for long operations (imports, exports, bulk operations)
- ✅ SSE for real-time progress tracking
- ✅ Entity/config pattern for frontend (reusable, consistent)
- ✅ Proper job naming standards
- ✅ Background tasks for async operations
- ✅ Phase-based development with incremental testing

---

## Current State Analysis

### Existing System (JSON-based)
- **Data Storage**: JSON files (likely in `data/board_games/` or similar)
- **Management**: Manual editing of JSON files
- **Issues**:
  - Hard to parse and understand database state
  - Difficult to find cards with missing metadata
  - No visual interface for browsing/searching
  - Error-prone manual editing
  - No relational data management (sets, variations, pricing)
  - No audit trail or change history

### Requirements for New System
1. **Data Management**: Full CRUD for cards, sets, variations, pricing
2. **Browsing**: Browse sets, search cards, filter by metadata completeness
3. **Validation**: Identify missing metadata, pricing gaps, inconsistencies
4. **Export**: Generate export files for mobile app consumption
5. **Visibility**: Clear dashboards showing database state
6. **Reliability**: Transaction-safe updates, data integrity constraints

---

## Architecture Overview

### Tech Stack (Following Life-OS Patterns)

**Backend**:
- **Framework**: FastAPI (async, consistent with Life-OS API)
- **Database**: PostgreSQL (relational data, proper constraints)
- **ORM**: SQLAlchemy 2.0 (async, type-safe)
- **Job Queue**: Redis + Background Tasks (for imports/exports)
- **Validation**: Pydantic v2 (request/response models)

**Frontend**:
- **Framework**: React 18.2 + Vite 5.0 (consistent with Life-OS frontend)
- **State Management**: Context API (AuthContext pattern)
- **HTTP Client**: Axios with interceptors
- **Styling**: Vanilla CSS (component-scoped, following EntityBrowser patterns)
- **Real-time Updates**: SSE (Server-Sent Events) for job progress

**Infrastructure**:
- **Containerization**: Docker Compose (separate services)
- **Database**: Separate PostgreSQL container (encyclopedia-db)
- **Reverse Proxy**: Nginx (separate port, e.g., :8001)

### Directory Structure

```
server/
├── api/                              # FastAPI backend
│   ├── routes/                       # API endpoints
│   │   ├── cards.py                 # Card CRUD endpoints
│   │   ├── sets.py                  # Set CRUD endpoints
│   │   ├── variations.py            # Card variation endpoints
│   │   ├── pricing.py               # Pricing data endpoints
│   │   ├── imports.py               # Import operations (JSON → DB)
│   │   ├── exports.py               # Export operations (DB → Mobile)
│   │   ├── jobs.py                  # Job tracking (imports/exports)
│   │   └── dashboards.py            # Dashboard data (stats, gaps)
│   ├── services/                    # Business logic layer
│   │   ├── card_service.py          # Card management logic
│   │   ├── set_service.py           # Set management logic
│   │   ├── variation_service.py     # Variation management logic
│   │   ├── pricing_service.py       # Pricing data logic
│   │   ├── import_service.py        # Import orchestration
│   │   ├── export_service.py        # Export generation
│   │   └── job_queue.py             # Job queue manager (reuse from Life-OS)
│   ├── models/                      # Pydantic schemas
│   │   ├── card.py                  # Card request/response models
│   │   ├── set.py                   # Set request/response models
│   │   ├── variation.py             # Variation request/response models
│   │   ├── pricing.py               # Pricing request/response models
│   │   └── jobs.py                  # Job models
│   ├── database/                    # Database layer
│   │   ├── models.py                # SQLAlchemy models
│   │   ├── session.py               # Database session management
│   │   └── migrations/              # Alembic migrations
│   ├── config.py                    # Configuration
│   ├── logging_config.py            # Logging setup
│   └── main.py                      # Application entry point
│
├── frontend/                        # React frontend
│   ├── src/
│   │   ├── pages/                   # Page components
│   │   │   ├── SetsPage.jsx        # Browse/manage sets
│   │   │   ├── CardsPage.jsx       # Browse/search cards
│   │   │   ├── VariationsPage.jsx  # Manage card variations
│   │   │   ├── PricingPage.jsx     # Review pricing data
│   │   │   ├── ImportPage.jsx      # Import data from JSON
│   │   │   ├── ExportPage.jsx      # Generate exports
│   │   │   └── DashboardPage.jsx   # Overview & stats
│   │   ├── components/              # Reusable components
│   │   │   ├── CardForm.jsx        # Card create/edit form
│   │   │   ├── SetForm.jsx         # Set create/edit form
│   │   │   ├── CardBrowser.jsx     # Card browsing grid (like EntityBrowser)
│   │   │   ├── SetBrowser.jsx      # Set browsing grid
│   │   │   ├── JobProgress.jsx     # Job progress modal (SSE-based)
│   │   │   └── SearchBar.jsx       # Reusable search component
│   │   ├── contexts/                # React contexts
│   │   │   └── JobStreamContext.jsx # SSE job tracking (reuse from Life-OS)
│   │   ├── api/
│   │   │   └── client.js            # Axios instance
│   │   ├── App.jsx                  # Main router
│   │   └── main.jsx                 # Entry point
│   ├── public/
│   ├── vite.config.js               # Vite configuration
│   └── package.json
│
├── docker-compose.yml               # Multi-container orchestration
├── Dockerfile.api                   # API container
├── Dockerfile.frontend              # Frontend container
├── .env.example                     # Environment variables template
└── README.md                        # Setup instructions
```

---

## Database Schema Design

### Core Entities

#### `sets` Table
```sql
CREATE TABLE sets (
    set_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    set_code VARCHAR(20) UNIQUE NOT NULL,          -- e.g., "BASE", "NEO1"
    set_name VARCHAR(200) NOT NULL,                -- e.g., "Base Set", "Neo Genesis"
    release_date DATE,
    series VARCHAR(100),                           -- e.g., "Original Series", "Sword & Shield"
    total_cards INTEGER,                           -- Expected card count
    icon_url VARCHAR(500),                         -- Set icon image
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Metadata completeness tracking
    has_complete_data BOOLEAN DEFAULT FALSE,       -- All cards have required metadata
    last_validated_at TIMESTAMP
);

CREATE INDEX idx_sets_code ON sets(set_code);
CREATE INDEX idx_sets_series ON sets(series);
```

#### `cards` Table
```sql
CREATE TABLE cards (
    card_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    set_id UUID NOT NULL REFERENCES sets(set_id) ON DELETE CASCADE,

    -- Card identity
    card_number VARCHAR(20) NOT NULL,              -- e.g., "001", "025/165"
    card_name VARCHAR(200) NOT NULL,               -- e.g., "Pikachu", "Charizard VMAX"
    card_type VARCHAR(50),                         -- e.g., "Pokemon", "Trainer", "Energy"

    -- Card attributes (extensible JSON for game-specific data)
    attributes JSONB DEFAULT '{}',                 -- Type, HP, attacks, abilities, etc.

    -- Metadata
    rarity VARCHAR(50),                            -- e.g., "Common", "Rare Holo", "Secret Rare"
    artist VARCHAR(200),
    description TEXT,

    -- Images
    image_url VARCHAR(500),                        -- Card front image
    image_back_url VARCHAR(500),                   -- Card back image (if different)

    -- Flags
    is_reverse_holo BOOLEAN DEFAULT FALSE,
    is_first_edition BOOLEAN DEFAULT FALSE,
    is_shadowless BOOLEAN DEFAULT FALSE,

    -- Completeness tracking
    has_complete_metadata BOOLEAN DEFAULT FALSE,   -- All required fields filled
    missing_fields TEXT[],                         -- Array of missing field names

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(set_id, card_number)                    -- No duplicate numbers per set
);

CREATE INDEX idx_cards_set ON cards(set_id);
CREATE INDEX idx_cards_name ON cards(card_name);
CREATE INDEX idx_cards_rarity ON cards(rarity);
CREATE INDEX idx_cards_incomplete ON cards(has_complete_metadata) WHERE has_complete_metadata = FALSE;
```

#### `card_variations` Table
```sql
CREATE TABLE card_variations (
    variation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id UUID NOT NULL REFERENCES cards(card_id) ON DELETE CASCADE,

    -- Variation details
    variation_type VARCHAR(50) NOT NULL,           -- e.g., "Reverse Holo", "First Edition", "Shadowless"
    variation_name VARCHAR(200),                   -- Human-readable name
    description TEXT,

    -- Differentiating attributes
    attributes JSONB DEFAULT '{}',                 -- Variation-specific attributes

    -- Images (if different from base card)
    image_url VARCHAR(500),

    -- Pricing may differ by variation
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(card_id, variation_type)                -- One variation of each type per card
);

CREATE INDEX idx_variations_card ON card_variations(card_id);
CREATE INDEX idx_variations_type ON card_variations(variation_type);
```

#### `pricing_data` Table
```sql
CREATE TABLE pricing_data (
    pricing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id UUID NOT NULL REFERENCES cards(card_id) ON DELETE CASCADE,
    variation_id UUID REFERENCES card_variations(variation_id) ON DELETE CASCADE,

    -- Pricing info
    source VARCHAR(100) NOT NULL,                  -- e.g., "TCGPlayer", "eBay", "CardMarket"
    condition VARCHAR(50) NOT NULL,                -- e.g., "Near Mint", "Lightly Played"
    price_usd DECIMAL(10, 2),
    price_eur DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',

    -- Price metadata
    market_price DECIMAL(10, 2),                   -- Average market price
    low_price DECIMAL(10, 2),                      -- Lowest listing
    high_price DECIMAL(10, 2),                     -- Highest listing

    -- Tracking
    fetched_at TIMESTAMP NOT NULL,                 -- When price was retrieved
    is_current BOOLEAN DEFAULT TRUE,               -- Mark old prices as FALSE

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pricing_card ON pricing_data(card_id);
CREATE INDEX idx_pricing_variation ON pricing_data(variation_id);
CREATE INDEX idx_pricing_source ON pricing_data(source);
CREATE INDEX idx_pricing_current ON pricing_data(is_current) WHERE is_current = TRUE;
```

#### `import_jobs` Table
```sql
CREATE TABLE import_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL,                 -- e.g., "JSON_IMPORT", "BULK_UPDATE"

    -- Job status
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, running, completed, failed
    progress FLOAT DEFAULT 0.0,                    -- 0.0 to 1.0
    status_message TEXT,

    -- Job details
    source_file VARCHAR(500),                      -- Original file path/name
    records_total INTEGER,
    records_processed INTEGER DEFAULT 0,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,

    -- Error tracking
    error_message TEXT,
    error_details JSONB,

    -- Results
    result JSONB,                                  -- Import summary

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Metadata
    metadata JSONB DEFAULT '{}'                    -- Additional job metadata
);

CREATE INDEX idx_import_jobs_status ON import_jobs(status);
CREATE INDEX idx_import_jobs_created ON import_jobs(created_at DESC);
```

### Key Design Decisions

1. **UUIDs for Primary Keys**: Better for distributed systems, no collisions
2. **JSONB for Extensibility**: Game-specific attributes vary by card type
3. **Metadata Completeness Tracking**: Built-in flags for missing data detection
4. **Pricing History**: Keep old prices, mark current with `is_current`
5. **Cascade Deletes**: Deleting a set removes all cards (intentional)
6. **Unique Constraints**: Prevent duplicate card numbers per set
7. **Indexes**: Optimized for common queries (search, filter, incomplete data)

---

## Phase-Based Development Plan

### Phase 0: Foundation Setup (Week 1)
**Goal**: Infrastructure and basic CRUD

**Tasks**:
1. ✅ Project structure setup
   - Create `server/` directory with API and frontend subdirectories
   - Initialize FastAPI project with SQLAlchemy
   - Initialize React + Vite project
   - Create docker-compose.yml with PostgreSQL, API, frontend

2. ✅ Database setup
   - Define SQLAlchemy models (`sets`, `cards`, `card_variations`, `pricing_data`)
   - Create Alembic migrations
   - Add database session management (async)
   - Seed database with sample data for testing

3. ✅ Service layer pattern
   - Create base service classes
   - Implement `SetService` with basic CRUD
   - Implement `CardService` with basic CRUD
   - Follow Life-OS service layer pattern (routes call services, services handle business logic)

4. ✅ Basic API endpoints
   - `GET/POST /api/sets` - List/create sets
   - `GET/PUT/DELETE /api/sets/{set_id}` - Manage individual sets
   - `GET/POST /api/cards` - List/create cards (with filtering)
   - `GET/PUT/DELETE /api/cards/{card_id}` - Manage individual cards

5. ✅ Basic frontend structure
   - Setup React Router
   - Create layout components (header, sidebar navigation)
   - Implement SetsPage with basic grid (following EntityBrowser pattern)
   - Implement CardsPage with basic grid
   - Setup Axios client with error handling

**Deliverables**:
- ✅ Running API + frontend + database in Docker
- ✅ Can create/edit/delete sets and cards via UI
- ✅ Basic list/grid views for sets and cards

**Success Criteria**:
- Can run `docker-compose up` and access UI at http://localhost:8001
- Can create a set, add cards to it, view card details

---

### Phase 1: Search, Filtering & Metadata Validation (Week 2)
**Goal**: Advanced browsing and data quality tools

**Tasks**:
1. ✅ Advanced search & filtering
   - Full-text search on card names
   - Filter by set, rarity, card type
   - Filter by metadata completeness
   - Sort options (name, card number, rarity, date added)

2. ✅ Metadata validation system
   - Define required fields per card type
   - Implement validation service
   - Auto-populate `has_complete_metadata` and `missing_fields`
   - Create validation endpoint: `POST /api/cards/{card_id}/validate`

3. ✅ Dashboard page
   - Total sets/cards count
   - Completion percentage (cards with full metadata)
   - Top 10 incomplete cards
   - Recent additions
   - Sets with missing cards (total_cards vs actual count)

4. ✅ Card variations UI
   - CRUD operations for variations
   - Display variations on card detail page
   - Create variation directly from card page

**Deliverables**:
- ✅ Powerful search and filtering on cards page
- ✅ Dashboard showing database health
- ✅ Can identify and navigate to incomplete cards

**Success Criteria**:
- Can find all cards missing artist names
- Can see at a glance which sets are incomplete
- Dashboard loads in <500ms

---

### Phase 2: Pricing Data Management (Week 3)
**Goal**: Pricing data integration and validation

**Tasks**:
1. ✅ Pricing CRUD
   - `GET/POST /api/pricing` - List/create pricing records
   - `GET/PUT/DELETE /api/pricing/{pricing_id}` - Manage individual records
   - Endpoint to get latest pricing for a card: `GET /api/cards/{card_id}/pricing`

2. ✅ Pricing data service
   - Validation: Price > 0, valid source, valid condition
   - Mark old prices as `is_current = FALSE` when new price added
   - Calculate market price statistics (avg, low, high)

3. ✅ Pricing review UI
   - Pricing page showing cards with pricing data
   - Filter by source, condition, price range
   - Highlight cards with missing pricing
   - Inline editing for quick price updates

4. ✅ Card detail enhancements
   - Show pricing history on card detail page
   - Price chart (basic line chart showing price over time)
   - Add pricing button (quick add modal)

**Deliverables**:
- ✅ Can view and manage pricing data for all cards
- ✅ Can identify cards missing pricing
- ✅ Pricing history visible on card detail page

**Success Criteria**:
- Can add pricing from multiple sources
- Can see price trends over time
- Can bulk-filter cards by missing pricing

---

### Phase 3: Import System (Week 4)
**Goal**: Import existing JSON data into database

**Tasks**:
1. ✅ Import service architecture
   - Job queue setup (reuse Life-OS `job_queue.py`)
   - SSE endpoint for job progress: `GET /api/jobs/stream`
   - Import background task pattern

2. ✅ JSON import logic
   - Parse existing JSON card data format
   - Map JSON structure to database schema
   - Handle missing fields gracefully (mark as incomplete)
   - Bulk insert optimization (batch inserts)

3. ✅ Import API endpoint
   - `POST /api/imports/json` - Upload JSON file
   - Create import job immediately
   - Run import in background task
   - Return job_id for tracking

4. ✅ Import UI
   - Import page with file upload
   - Job progress display (SSE-based, following JobStreamContext pattern)
   - Import summary (created/updated/failed counts)
   - Error log display for failed records

5. ✅ Proper job naming
   - Title: `"Import Cards from JSON ({filename})"`
   - Description: `"Processing {total_records} cards"`
   - Metadata: `{"source": "json_upload", "filename": "cards.json"}`

**Deliverables**:
- ✅ Can upload JSON file and import cards
- ✅ Real-time progress tracking via SSE
- ✅ Import errors clearly displayed

**Success Criteria**:
- Can import 1000+ cards without issues
- Progress updates smoothly during import
- Failed records logged with clear error messages

---

### Phase 4: Export System (Week 5)
**Goal**: Generate exports for mobile app consumption

**Tasks**:
1. ✅ Export service
   - Generate optimized export format (JSON or SQLite)
   - Include only required fields (mobile app doesn't need all metadata)
   - Compress images/data for mobile bandwidth
   - Export validation (ensure referential integrity)

2. ✅ Export endpoint
   - `POST /api/exports/generate` - Create export job
   - Query parameters: `format` (json/sqlite), `sets` (filter by sets)
   - Run export in background task
   - Return job_id and download URL when complete

3. ✅ Export UI
   - Export page with options (format, set selection)
   - Job progress display (SSE-based)
   - Download button when complete
   - Export history (previous exports with download links)

4. ✅ Export formats
   - **JSON format**: Optimized structure for mobile parsing
   - **SQLite format**: Pre-built database file for mobile app
   - Versioning: Include schema version in export

5. ✅ Proper job naming
   - Title: `"Generate Mobile Export (JSON)"`
   - Description: `"Exporting {set_count} sets, {card_count} cards"`
   - Metadata: `{"export_type": "mobile", "format": "json"}`

**Deliverables**:
- ✅ Can generate exports in multiple formats
- ✅ Mobile-optimized export structure
- ✅ Download links for generated exports

**Success Criteria**:
- Export completes for full encyclopedia in <30 seconds
- Mobile app can directly consume export file
- Export includes all required metadata

---

### Phase 5: Bulk Operations & Polish (Week 6)
**Goal**: Productivity features and UI polish

**Tasks**:
1. ✅ Bulk operations
   - Bulk edit (select multiple cards, update field)
   - Bulk delete (with confirmation)
   - Bulk validation (run validation on all cards)
   - Bulk pricing import (CSV upload)

2. ✅ Advanced card features
   - Card duplication (create variation quickly)
   - Card templates (pre-fill common attributes)
   - Card history (track changes over time)

3. ✅ UI polish
   - Loading states (skeletons, spinners)
   - Error handling (toast notifications)
   - Keyboard shortcuts (Cmd+S to save, Cmd+K for search)
   - Responsive design (works on tablet/laptop)
   - Dark mode toggle

4. ✅ Documentation
   - API documentation (auto-generated via FastAPI /docs)
   - User guide (how to use the tool)
   - Developer guide (how to extend the system)

**Deliverables**:
- ✅ Polished, production-ready interface
- ✅ Bulk operations for efficient data management
- ✅ Complete documentation

**Success Criteria**:
- Can bulk-edit 100+ cards at once
- UI feels responsive and professional
- Documentation covers all features

---

## Best Practices (Applied from Phase 1 Work)

### 1. Service Layer Pattern
```python
# ✅ CORRECT - Routes delegate to services
@router.post("/cards/")
async def create_card(request: CardCreate, db: AsyncSession = Depends(get_db)):
    service = CardService(db)
    card = await service.create_card(request)
    return CardInfo.from_orm(card)

# ❌ WRONG - Business logic in route
@router.post("/cards/")
async def create_card(request: CardCreate, db: AsyncSession = Depends(get_db)):
    # ... 50 lines of validation and database logic ...
```

### 2. Job Naming Standards
```python
# ✅ CORRECT - Descriptive job names
job_id = job_queue.create_job(
    job_type=JobType.IMPORT,
    title=f"Import Cards from JSON ({filename})",
    description=f"Processing {total_records} cards from {filename}",
    metadata={
        "source": "json_upload",
        "filename": filename,
        "total_records": total_records
    }
)

# ❌ WRONG - Generic job names
job_id = job_queue.create_job(
    job_type=JobType.IMPORT,
    title="Import job",
    description=f"Job ID: {job_id}"
)
```

### 3. SSE for Real-Time Updates
```javascript
// ✅ CORRECT - Use shared JobStreamContext (reuse from Life-OS)
const { subscribe } = useJobStream()

useEffect(() => {
  const handleJobUpdate = (job) => {
    if (job.job_id === importJobId) {
      setProgress(job.progress)
      setStatus(job.status)
    }
  }

  const unsubscribe = subscribe(handleJobUpdate)
  return () => unsubscribe()
}, [importJobId])

// ❌ WRONG - Manual polling
setInterval(() => {
  fetch(`/api/jobs/${jobId}`)
    .then(res => res.json())
    .then(job => setProgress(job.progress))
}, 1000)
```

### 4. Entity/Config Pattern for Frontend
```javascript
// ✅ CORRECT - Config-based entity management (reusable)
export const cardsConfig = {
  entityType: 'card',
  title: 'Cards',
  icon: '🎴',
  enableSearch: true,
  enableSort: true,
  searchFields: ['card_name', 'card_number'],

  fetchEntities: async (filters) => {
    const response = await api.get('/cards/', { params: filters })
    return response.data
  },

  renderCard: (card) => (
    <div className="entity-card">
      <img src={card.image_url} alt={card.card_name} />
      <h3>{card.card_name}</h3>
      <p>{card.card_number} - {card.rarity}</p>
    </div>
  )
}

// ❌ WRONG - Hardcoded, non-reusable component
function CardsPage() {
  // ... 500 lines of hardcoded logic ...
}
```

### 5. Async File I/O
```python
# ✅ CORRECT - Use async file operations
import aiofiles

async def export_to_json(cards: List[Card], output_path: Path):
    data = [card.dict() for card in cards]
    async with aiofiles.open(output_path, 'w') as f:
        await f.write(json.dumps(data, indent=2))

# ❌ WRONG - Blocking file I/O
def export_to_json(cards: List[Card], output_path: Path):
    data = [card.dict() for card in cards]
    with open(output_path, 'w') as f:
        f.write(json.dumps(data, indent=2))
```

### 6. Background Tasks for Long Operations
```python
# ✅ CORRECT - Long operations in background
@router.post("/imports/json")
async def import_json(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Create job immediately
    job_id = job_queue.create_job(...)

    # Queue background task
    background_tasks.add_task(run_import_job, job_id, file, db)

    return {"job_id": job_id, "status": "queued"}

# ❌ WRONG - Blocking the request
@router.post("/imports/json")
async def import_json(file: UploadFile, db: AsyncSession = Depends(get_db)):
    # ... 60 seconds of processing ...
    return {"status": "completed"}
```

### 7. Proper Error Handling
```python
# ✅ CORRECT - Catch specific errors, provide context
@router.get("/cards/{card_id}")
async def get_card(card_id: str, db: AsyncSession = Depends(get_db)):
    try:
        service = CardService(db)
        card = await service.get_card(card_id)
        if not card:
            raise HTTPException(status_code=404, detail=f"Card {card_id} not found")
        return CardInfo.from_orm(card)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching card {card_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ❌ WRONG - Generic error handling
@router.get("/cards/{card_id}")
async def get_card(card_id: str):
    try:
        # ... logic ...
        return card
    except Exception as e:
        return {"error": str(e)}
```

---

## Testing Strategy

### Backend Tests (pytest + httpx)
```python
# tests/unit/test_card_service.py
import pytest
from api.services.card_service import CardService

@pytest.mark.asyncio
async def test_create_card(db_session):
    service = CardService(db_session)

    card_data = {
        "set_id": "test-set-uuid",
        "card_number": "001",
        "card_name": "Test Card",
        "rarity": "Common"
    }

    card = await service.create_card(card_data)

    assert card.card_name == "Test Card"
    assert card.card_number == "001"

# tests/integration/test_card_endpoints.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_card_endpoint(client: AsyncClient):
    response = await client.post("/api/cards/", json={
        "set_id": "test-set-uuid",
        "card_number": "001",
        "card_name": "Test Card",
        "rarity": "Common"
    })

    assert response.status_code == 200
    assert response.json()["card_name"] == "Test Card"
```

### Frontend Tests (Vitest + React Testing Library)
```javascript
// tests/components/CardForm.test.jsx
import { render, screen, fireEvent } from '@testing-library/react'
import CardForm from '../src/components/CardForm'

test('renders card form with all fields', () => {
  render(<CardForm onSubmit={jest.fn()} />)

  expect(screen.getByLabelText('Card Name')).toBeInTheDocument()
  expect(screen.getByLabelText('Card Number')).toBeInTheDocument()
  expect(screen.getByLabelText('Rarity')).toBeInTheDocument()
})

test('submits form with valid data', async () => {
  const handleSubmit = jest.fn()
  render(<CardForm onSubmit={handleSubmit} />)

  fireEvent.change(screen.getByLabelText('Card Name'), { target: { value: 'Pikachu' } })
  fireEvent.change(screen.getByLabelText('Card Number'), { target: { value: '025' } })
  fireEvent.click(screen.getByRole('button', { name: 'Save' }))

  expect(handleSubmit).toHaveBeenCalledWith({
    card_name: 'Pikachu',
    card_number: '025',
    // ...
  })
})
```

### Critical Path Tests (E2E)
```python
# tests/smoke/test_critical_paths.py
@pytest.mark.asyncio
async def test_create_set_and_add_card(client: AsyncClient):
    """Test the most common workflow: create set, add card"""

    # Create set
    set_response = await client.post("/api/sets/", json={
        "set_code": "BASE",
        "set_name": "Base Set",
        "series": "Original"
    })
    assert set_response.status_code == 200
    set_id = set_response.json()["set_id"]

    # Add card to set
    card_response = await client.post("/api/cards/", json={
        "set_id": set_id,
        "card_number": "001",
        "card_name": "Bulbasaur",
        "rarity": "Common"
    })
    assert card_response.status_code == 200

    # Verify card appears in set
    cards_response = await client.get(f"/api/cards/?set_id={set_id}")
    assert len(cards_response.json()) == 1
```

---

## Deployment & Operations

### Docker Compose Setup
```yaml
# server/docker-compose.yml
version: '3.8'

services:
  encyclopedia-db:
    image: postgres:15
    environment:
      POSTGRES_DB: encyclopedia
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: changeme
    volumes:
      - encyclopedia-data:/var/lib/postgresql/data
    ports:
      - "5433:5432"  # Different port from Life-OS

  encyclopedia-redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"  # Different port from Life-OS

  encyclopedia-api:
    build:
      context: .
      dockerfile: Dockerfile.api
    environment:
      DATABASE_URL: postgresql+asyncpg://admin:changeme@encyclopedia-db:5432/encyclopedia
      REDIS_URL: redis://encyclopedia-redis:6379/0
    volumes:
      - ./api:/app/api
      - ./exports:/app/exports
    ports:
      - "8001:8000"
    depends_on:
      - encyclopedia-db
      - encyclopedia-redis

  encyclopedia-frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    volumes:
      - ./frontend/src:/app/src
    ports:
      - "5174:5173"  # Different port from Life-OS
    depends_on:
      - encyclopedia-api

volumes:
  encyclopedia-data:
```

### Environment Variables
```bash
# .env.example
DATABASE_URL=postgresql+asyncpg://admin:changeme@encyclopedia-db:5432/encyclopedia
REDIS_URL=redis://encyclopedia-redis:6379/0

# API settings
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Export settings
EXPORT_DIR=/app/exports
MAX_EXPORT_SIZE_MB=500

# Import settings
MAX_UPLOAD_SIZE_MB=100
IMPORT_BATCH_SIZE=1000
```

### Startup Commands
```bash
# Development
cd server/
docker-compose up -d

# Run migrations
docker-compose exec encyclopedia-api alembic upgrade head

# Access UI
open http://localhost:5174

# View logs
docker-compose logs -f encyclopedia-api
docker-compose logs -f encyclopedia-frontend
```

---

## Success Metrics

### Phase 0 Success
- ✅ Can create/edit/delete sets via UI
- ✅ Can create/edit/delete cards via UI
- ✅ Database persists data across restarts
- ✅ API endpoints documented at `/docs`

### Phase 1 Success
- ✅ Can search cards by name in <200ms
- ✅ Can filter to only incomplete cards
- ✅ Dashboard shows accurate statistics

### Phase 2 Success
- ✅ Can view pricing history for any card
- ✅ Can identify all cards missing pricing
- ✅ Pricing data validates correctly (no negative prices)

### Phase 3 Success
- ✅ Can import 1000+ cards from JSON without errors
- ✅ Import job progress updates in real-time
- ✅ Import errors clearly displayed with context

### Phase 4 Success
- ✅ Can generate mobile export in <30 seconds
- ✅ Export file works directly in mobile app (no manual processing)
- ✅ Export includes all required metadata

### Phase 5 Success
- ✅ Can bulk-edit 100+ cards simultaneously
- ✅ UI loads in <1 second for all pages
- ✅ Zero console errors during normal usage

---

## Future Enhancements (Post-Launch)

### Enhanced Features
1. **Audit Log**: Track all changes to cards/sets with user attribution
2. **Bulk Pricing Import**: Import pricing from CSV (TCGPlayer exports, etc.)
3. **Image Management**: Upload/crop card images directly in the tool
4. **Duplicate Detection**: Identify potential duplicate cards
5. **Data Validation Rules**: Configurable rules for metadata validation
6. **Export Scheduling**: Auto-generate exports daily/weekly
7. **API for Mobile App**: Direct API access (no export files needed)
8. **Multi-User Support**: Multiple admins with different permission levels
9. **Change History**: View history of changes for any card
10. **Advanced Analytics**: Price trends, set completion charts, rarity distribution

### Integration Opportunities
1. **TCGPlayer API**: Auto-import pricing data
2. **Scryfall API** (if Magic: The Gathering): Auto-import card data
3. **Image Recognition**: Auto-populate card metadata from images
4. **Mobile App Sync**: Two-way sync instead of one-way export

---

## Risks & Mitigations

### Risk 1: Large Import Performance
**Risk**: Importing 10,000+ cards may be slow
**Mitigation**:
- Batch inserts (1000 records at a time)
- Database indexing
- Progress updates every 100 records
- Background processing (non-blocking)

### Risk 2: Data Migration from JSON
**Risk**: Existing JSON structure may not map cleanly to database schema
**Mitigation**:
- Flexible import logic (handle missing fields)
- Manual review step after import (dashboard shows incomplete cards)
- Dry-run mode (test import without committing)

### Risk 3: Mobile App Compatibility
**Risk**: Export format may not match mobile app expectations
**Mitigation**:
- Define export schema upfront (collaborate on structure)
- Versioning in export (mobile app checks version)
- Validation step before export (ensure referential integrity)

### Risk 4: Complex Variations
**Risk**: Some cards have many variations (different artworks, editions, etc.)
**Mitigation**:
- Flexible `attributes` JSONB field (extensible)
- Variation templates (common variation types pre-defined)
- Hierarchical variations (base card → variation → sub-variation)

---

## Conclusion

This roadmap provides a comprehensive plan for building a production-ready Encyclopedia Management Tool, informed by the best practices and lessons learned from the Entity Preview Migration work in Life-OS.

**Key Differentiators**:
- Database-first architecture (no JSON → DB migration pain)
- Job queue for all long operations (imports, exports)
- SSE for real-time progress tracking
- Service layer pattern (clean separation of concerns)
- Entity/config pattern for frontend (reusable, maintainable)
- Phase-based development (incremental, testable)

**Timeline**: 6 weeks for full implementation (MVP in 2 weeks)

**Estimated Effort**:
- Phase 0: 30 hours
- Phase 1: 25 hours
- Phase 2: 20 hours
- Phase 3: 25 hours
- Phase 4: 20 hours
- Phase 5: 20 hours
- **Total**: ~140 hours (~3.5 weeks full-time)

**Next Steps**:
1. Review roadmap with stakeholders
2. Setup Phase 0 infrastructure (Docker, database, basic API)
3. Begin implementation following phase-based approach
4. Test incrementally, commit frequently
5. Iterate based on real-world usage

---

*This roadmap will be updated as development progresses and new requirements emerge.*
