# Life-OS

Multi-domain AI platform for image generation, analysis, and workflow orchestration. Built with FastAPI (Python), React (Vite), PostgreSQL, and Redis.

## Overview

Life-OS is a **web-based AI platform** that specializes in **image generation and analysis** with expanding capabilities into **story generation**, **board game tools**, and **document processing**.

### Key Features

- **24 AI Tools** - Analyzers, generators, and processors for images and documents
- **Entity Management** - PostgreSQL-backed CRUD for 20+ entity types (characters, clothing, outfits, stories, etc.)
- **Composer Application** - Drag-and-drop visual outfit composition canvas
- **Story Workflow** - Multi-agent pipeline (planner → writer → illustrator)
- **Board Game Tools** - BGG integration, rulebook fetching, RAG-based Q&A
- **Job Queue** - Background processing with real-time progress tracking
- **Preset Library** - Reusable style configurations (22 categories)
- **Multi-User** - JWT authentication, per-user data isolation
- **Mobile-Responsive** - Works on phones, tablets, and desktops

## Quick Start

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env and add GEMINI_API_KEY and OPENAI_API_KEY

# 2. Start all services
docker-compose up -d

# 3. Create admin user
docker-compose exec api python scripts/create_admin_user.py

# 4. Access web interface
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
```

### Key Workflows

1. **Character Creation**: Upload image → Analyze appearance → Create character entity
2. **Outfit Composition**: Select character → Add clothing/styles → Generate image
3. **Story Generation**: Select character + theme → Generate illustrated story
4. **Style Extraction**: Upload image → Analyze style → Save as reusable preset

## Installation

### Prerequisites

- Docker & Docker Compose
- API keys: Gemini (required), OpenAI (optional)

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/life-os.git
cd life-os

# Setup environment variables
cp .env.example .env
# Edit .env and add:
#   GEMINI_API_KEY=your_key
#   OPENAI_API_KEY=your_key (optional)
#   REQUIRE_AUTH=true (for production)

# Start all containers
docker-compose up -d

# Check logs
docker logs ai-studio-api --tail 50
docker logs ai-studio-frontend --tail 50

# Create first user
docker-compose exec api python scripts/create_admin_user.py
```

### Services

- **Frontend** - React + Vite (port 3000)
- **API** - FastAPI (port 8000)
- **PostgreSQL** - Database (port 5432)
- **Redis** - Job queue (port 6379)
- **RQ Workers** - Background task processors (4 workers)

### Common Commands

```bash
# View logs
docker logs ai-studio-api --tail 100
docker logs life-os-rq-worker-1 --tail 50

# Rebuild after code changes
docker-compose up -d --build api
docker-compose up -d --build frontend
docker-compose up -d --build rq-worker

# Database access
docker exec ai-studio-postgres psql -U lifeos -d lifeos

# Redis access
docker exec -it ai-studio-redis redis-cli

# Run tests
docker-compose exec api pytest tests/unit/ -v
```

## Architecture

### Stack

**Backend**:
- FastAPI (async Python 3.9+)
- PostgreSQL 15 with asyncpg
- SQLAlchemy 2.0+ (async ORM)
- Redis (job queue)
- LiteLLM (multi-provider LLM router)

**Frontend**:
- React 18.2 + Vite 5.0
- React Router v6
- Axios (with JWT interceptors)
- Component-scoped CSS

**AI Providers**:
- Gemini 2.0/2.5 Flash (primary)
- OpenAI DALL-E 3 / GPT-4 / Sora
- Claude (via LiteLLM)

### Service Layer Pattern

```
Routes (api/routes/) → Handle HTTP concerns
  ↓
Services (api/services/) → Business logic
  ↓
Repositories (api/repositories/) → Data access
  ↓
Database (PostgreSQL)
```

### Directory Structure

```
life-os/
├── api/                          # Backend (Python/FastAPI)
│   ├── routes/                   # API endpoints
│   ├── services/                 # Business logic
│   ├── repositories/             # Data access layer
│   ├── models/                   # Pydantic + SQLAlchemy models
│   ├── agents/                   # Story generation agents
│   └── database.py               # Database connection
├── ai_tools/                     # AI tool implementations
│   ├── shared/                   # Shared utilities
│   ├── outfit_analyzer/          # Individual tools
│   ├── modular_image_generator/
│   └── [22 other tools]/
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── pages/                # Page components
│   │   ├── components/           # Reusable components
│   │   ├── contexts/             # React contexts
│   │   └── api/                  # API client
│   └── vite.config.js
├── presets/                      # Preset JSON files
├── data/                         # Runtime data
├── output/                       # Generated images
├── docs/                         # Documentation
│   ├── guides/                   # How-to guides
│   ├── setup/                    # Setup documentation
│   ├── features/                 # Feature specs
│   └── archive/                  # Historical docs
└── configs/                      # Configuration files
```

## Core Entities

Life-OS manages structured data through 20+ entity types stored in PostgreSQL.

### Content Entities

- **Characters** - People for story generation and image generation (visual description, personality, reference image)
- **Stories** - Generated narrative content with multiple scenes and illustrations
- **Story Scenes** - Individual scenes within stories with text and illustration
- **Clothing Items** - Articles of clothing (15 categories: headwear, tops, bottoms, footwear, etc.)
- **Outfits** - Complete outfit combinations referencing multiple clothing items
- **Board Games** - Board game catalog with BGG metadata
- **Images** - All AI-generated images with polymorphic relationships to entities
- **Documents** - PDF documents (rulebooks, manuals) with RAG processing

### Configuration Entities

- **Presets** (22 categories) - Reusable style configurations:
  - Visual styles, art styles, hair styles, hair colors
  - Makeup, expressions, accessories
  - Story themes, audiences, prose styles
- **Visualization Configs** - Templates for generating preview images
- **Story Configs** - Planner, Writer, Illustrator configuration entities

### User Data Entities

- **Users** - User accounts with JWT authentication
- **Favorites** - User's favorite presets
- **Compositions** - Saved combinations of presets

## AI Tools

### Image Analyzers (9 tools)

Extract structured information from images:

- **Outfit Analyzer** - 15 clothing categories with fabric, color, details
- **Character Appearance Analyzer** - Age, skin tone, face, hair, body
- **Visual Style Analyzer** - 17 photographic aspects (composition, lighting, mood, etc.)
- **Art Style Analyzer** - Medium, technique, art movement, mood
- **Hair Style Analyzer** - Cut, length, layers, texture, volume
- **Hair Color Analyzer** - Base color, undertones, highlights, lowlights
- **Makeup Analyzer** - Complexion, eyes, lips, intensity
- **Expression Analyzer** - Emotion, intensity, facial features, gaze
- **Accessories Analyzer** - Jewelry, bags, belts, hats, watches
- **Comprehensive Analyzer** - Run all 8 analyzers at once

### Image Generators (6 tools)

Create new images using AI models:

- **Modular Image Generator** - Combine any specs (outfit, style, hair, makeup, expression, accessories)
- **Outfit Generator** - Generate outfits from text descriptions
- **Style Transfer Generator** - Transfer visual style while preserving subject
- **Art Style Generator** - Generate in specific artistic styles
- **Sora Video Generator** - Generate videos with Sora API
- **Video Prompt Enhancer** - Enhance video prompts with GPT-4o

### Visualization Tools (3 tools)

Generate preview images for entities:

- **Clothing Item Visualizer** - Isolated product-style images
- **Outfit Visualizer** - Outfits shown on mannequin or model
- **Item Visualizer** - General-purpose item previews

### Document Processing Tools (3 tools)

- **Board Game Rules Gatherer** - Search BGG, fetch metadata, download rulebooks
- **Document RAG Preparer** - Extract text, chunk, embed, store in vector DB
- **Document QA** - Answer questions about documents with citations

## Web Applications

### Composer (`/apps/composer`)

Visual outfit composition canvas with drag-and-drop interface.

**Features**:
- Drag-and-drop preset library (22 categories)
- Character selection (subject for generation)
- Multi-preset layering (15 clothing categories, can layer multiple per category)
- Real-time preview generation
- Favorites system for quick access
- Search and filter presets
- Save/load compositions
- Mobile-responsive with tab navigation
- LRU cache (50 generations) for instant previews
- Auto-generate mode (live preview) or manual mode (build first)

**Use Case**: Build complete character looks by combining clothing, hair, makeup, and style presets.

### Story Workflow (`/workflows/story`)

End-to-end illustrated story generation with multi-agent orchestration.

**Process**:
1. **Planning** - Story planner creates outline with scene breakdown
2. **Writing** - Story writer generates narrative content for each scene
3. **Illustration** - Story illustrator creates images for each scene

**Features**:
- Real-time progress tracking
- Creates story entity with all scenes
- Saves illustrations and links to scenes
- Configurable via entity-based configs
- Character-aware (uses character descriptions)

**Use Case**: Generate complete illustrated stories in minutes.

## Entity Management Pages

Each entity type has a dedicated web page:

**Common Features** (all pages):
- List view with search and filter
- Detail view with edit capabilities
- Create/import options
- Delete with confirmation
- Bulk actions for batch operations
- Related data display (e.g., images using a character)

**Entity Pages**:
- Stories, Images, Characters, Clothing Items, Outfits
- Expressions, Makeup, Hair Styles, Hair Colors
- Visual Styles, Art Styles, Accessories
- Story Themes, Audiences, Prose Styles, Configs
- Board Games, Documents, QAs
- Visualization Configs

## Tool Pages

Direct access to individual AI tools via web interface:

**Analyzer Tools**:
- Character Appearance, Outfit, Accessories
- Art Style, Expression, Hair Color, Hair Style
- Makeup, Visual Style, Comprehensive

**Generator Tools**:
- Modular Generator

**Story Tools**:
- Story Planner, Writer, Illustrator

**Board Game Tools**:
- BGG Rulebook Fetcher, Document Processor, Document Question Asker

## Configuration

### Model Configuration

Edit `configs/models.yaml` to change default models:

```yaml
defaults:
  # Analysis Tools
  outfit_analyzer: "gemini/gemini-2.0-flash-exp"
  visual_style_analyzer: "gemini/gemini-2.0-flash-exp"

  # Image Generation
  modular_image_generator: "gemini/gemini-2.5-flash-image"

  # Story Generation
  story_writer: "gemini/gemini-2.0-flash-exp"
  story_illustrator: "gemini/gemini-2.5-flash-image"
```

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
OPENAI_API_KEY=your_openai_api_key

# Authentication
REQUIRE_AUTH=true                    # Enable JWT auth
JWT_SECRET_KEY=your_secret_key       # Use secure random key in production

# Database
DATABASE_URL=postgresql+asyncpg://lifeos:password@postgres:5432/lifeos

# Job Queue
REDIS_URL=redis://redis:6379/0
```

## Performance

### Typical Response Times

- **Image Analysis**: 5-10 seconds (Gemini 2.0 Flash)
- **Image Generation**: 30-60 seconds (Gemini 2.5 Flash Image)
- **Story Generation** (3 scenes): 2-5 minutes
- **Document Processing**: 1-3 minutes

### Caching

- **Analysis Cache**: File-based, 30-day TTL
- **Generation Cache**: LRU in-memory, 50 items
- **Preset Cache**: In-memory, cleared on change

### Cost Tracking

- **Gemini 2.5 Flash Image**: ~$0.002 per image
- **Gemini 2.0 Flash**: ~$0.001 per analysis
- **DALL-E 3**: ~$0.04 per image

**Typical Costs**:
- Single image generation: $0.002
- Comprehensive analysis (9 analyzers): $0.009
- 5-scene illustrated story: ~$0.05

## Development

### Running Tests

```bash
# All unit tests
docker-compose exec api pytest tests/unit/ -v

# Specific test file
docker-compose exec api pytest tests/unit/test_cache.py -v

# With coverage
docker-compose exec api pytest tests/unit/ --cov=api --cov-report=html
```

### Making Changes

**Backend changes** (Python/API):
```bash
# 1. Edit files in api/ or ai_tools/
# 2. Rebuild API + workers
docker-compose up -d --build api
docker-compose up -d --build rq-worker
docker-compose up -d --scale rq-worker=4
# 3. Check logs
docker logs ai-studio-api --tail 50
```

**Frontend changes** (React):
```bash
# 1. Edit files in frontend/src/
# 2. Rebuild frontend
docker-compose up -d --build frontend
# 3. Hard refresh browser (Cmd+Shift+R)
```

### Adding New AI Tools

See `ai_tools/README_TOOL_DEVELOPMENT.md` for complete checklist.

**Required steps**:
1. Create tool files: `ai_tools/{tool_name}/{tool.py,template.md,README.md}`
2. Add to `configs/models.yaml` defaults
3. Add route to `frontend/src/App.jsx`
4. Add sidebar link to `Sidebar.jsx`
5. Add test UI to `ToolConfigPage.jsx` (if needed)
6. Rebuild API and frontend

### CI/CD Workflow

**Branches**:
- `staging` - Development branch, auto-deploys on push
- `main` - Production branch, requires PR approval

**Workflow**:
```bash
# 1. Develop on staging
git checkout staging
# ... make changes ...

# 2. Run tests
docker-compose exec api pytest tests/unit/ -v

# 3. Commit and push
git add .
git commit -m "feat: Add feature"
git push origin staging

# 4. Create PR to main when ready
gh pr create --base main --head staging

# 5. After PR approval, main deploys to production
```

See `docs/guides/deployment.md` for detailed deployment instructions.

## Documentation

- **README.md** (this file) - Project overview and quick start
- **ROADMAP.md** - Development phases and priorities
- **claude.md** - AI assistant development guide
- **docs/guides/** - How-to guides (API reference, design patterns, deployment, etc.)
- **docs/setup/** - Setup documentation (Alembic migrations, etc.)
- **docs/features/** - Feature specifications (ComfyUI integration, planned features)
- **docs/archive/** - Historical documentation

## Mobile Experience

Life-OS is fully mobile-responsive:

- **Composer**: Tab navigation (Library / Canvas / Applied)
- **Entity Pages**: Vertical scrolling, touch-friendly controls
- **Tool Pages**: Optimized forms and results display
- **Navigation**: Collapsible sidebar

## Data Flow Examples

### Example 1: Creating a Character from an Image

1. User uploads image to Character Appearance Analyzer (`/tools/analyzers/character-appearance`)
2. Analyzer extracts: age, skin tone, face, hair, body descriptions
3. User reviews analysis results
4. User clicks "Create Character"
5. Character entity created in database with reference image
6. Character appears in character selector throughout the app

### Example 2: Generating an Image

1. User selects character in Composer (`/apps/composer`)
2. User drags "noir" visual style preset to canvas
3. User drags "leather jacket" clothing item to canvas
4. User drags "smokey eye" makeup preset to canvas
5. Auto-generate creates job in queue
6. Job manager polls for completion via SSE
7. Generated image appears in canvas
8. Image entity created with relationships to character, visual style, clothing item, makeup

### Example 3: Creating an Illustrated Story

1. User navigates to Story Workflow page (`/workflows/story`)
2. User selects character, theme, audience, prose style
3. User sets number of scenes (e.g., 5)
4. User clicks "Generate Story"
5. Planner agent creates story outline (5 scenes)
6. Writer agent writes each scene sequentially
7. Illustrator agent generates image for each scene
8. Story entity created with all scenes and illustrations
9. User can view/edit story in Stories entity page (`/entities/stories`)

## Advanced Features

### CLI Tools

Life-OS AI tools can also be used via command line:

```bash
# Analyze an image
python ai_tools/comprehensive_analyzer/tool.py photo.jpg --save-all --prefix my-look

# Generate image with presets
python ai_tools/modular_image_generator/tool.py subject.jpg \
  --outfit casual-outfit \
  --visual-style film-noir \
  --hair-style beach-waves

# Batch generate (3 subjects × 2 outfits × 2 styles = 12 images)
python workflows/batch_outfit_generator.py \
  --subjects photos/*.jpg \
  --outfits casual,formal \
  --styles vintage,modern
```

See tool-specific READMEs in `ai_tools/` for detailed CLI documentation.

### Presets

Presets are user-editable JSON files in `presets/` organized by category:

```
presets/
├── outfits/
├── visual_styles/
├── art_styles/
├── hair_styles/
├── hair_colors/
├── makeup/
├── expressions/
└── accessories/
```

**Format** (example outfit preset):
```json
{
  "clothing_items": [
    {
      "item": "leather jacket",
      "fabric": "distressed brown leather",
      "color": "chocolate brown",
      "details": "asymmetric zip, quilted shoulders"
    }
  ],
  "style_genre": "edgy casual",
  "formality": "casual",
  "aesthetic": "urban streetwear"
}
```

## Troubleshooting

### Common Issues

**"File not found" errors**:
- Check paths are correct (container paths start with `/app/`)
- Verify file permissions
- See `api/utils/file_paths.py` for path normalization utilities

**Jobs complete but no output**:
- Rebuild RQ workers: `docker-compose up -d --build rq-worker`
- Check worker logs: `docker logs life-os-rq-worker-1 --tail 50`

**Frontend not updating after changes**:
- Rebuild frontend: `docker-compose up -d --build frontend`
- Hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)
- Check build logs: `docker logs ai-studio-frontend --tail 50`

**Database connection errors**:
- Check PostgreSQL is running: `docker ps | grep postgres`
- Verify connection string in `.env`
- Check database logs: `docker logs ai-studio-postgres --tail 50`

### Getting Help

- **GitHub Issues**: [repo-url]/issues
- **Documentation**: See `docs/` directory
- **API Docs**: http://localhost:8000/docs (interactive Swagger UI)

## Credits

Built with:
- **AI Models**: Gemini 2.0/2.5 Flash, OpenAI DALL-E 3 / GPT-4 / Sora, Claude
- **Backend**: FastAPI, PostgreSQL, SQLAlchemy, Redis, RQ
- **Frontend**: React, Vite, Axios
- **AI Infrastructure**: LiteLLM, Pydantic, Docling, ChromaDB
- **Deployment**: Docker, Nginx

## License

[Your License]

---

**See [ROADMAP.md](ROADMAP.md) for planned features and development priorities.**
