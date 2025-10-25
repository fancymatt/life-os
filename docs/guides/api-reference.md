# API Architecture Plan

## Vision

Self-hosted web app with REST API that:
- Discovers and exposes all available tools
- Manages presets (CRUD operations)
- Executes analysis and generation tasks
- Tracks job status and progress
- Provides cost estimates
- **Supplements** (not replaces) existing CLI tools

## Design Principles

1. **CLI-First**: API wraps existing tools, doesn't reimplement them
2. **Shared Logic**: Reuse existing analyzer/generator classes
3. **Non-Invasive**: API lives in separate `api/` directory
4. **Async Support**: Long-running tasks use background jobs
5. **Type-Safe**: Leverage existing Pydantic specs
6. **Self-Documenting**: Auto-generated OpenAPI/Swagger docs

## Technology Stack

```
FastAPI (API framework)
├── Pydantic (validation - already using)
├── uvicorn (ASGI server)
├── Celery or rq (background jobs)
└── Redis (job queue + caching)
```

**Why FastAPI?**
- Already using Pydantic specs
- Auto-generates OpenAPI docs
- Built-in async support
- Type hints for validation
- Fast and modern

## Directory Structure

```
life-os/
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── discovery.py           # GET /tools, /presets
│   │   ├── analyzers.py           # POST /analyze/*
│   │   ├── generators.py          # POST /generate/*
│   │   ├── presets.py             # CRUD /presets/*
│   │   ├── batch.py               # POST /batch/*
│   │   └── jobs.py                # GET /jobs/:id
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py            # API request models
│   │   └── responses.py           # API response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analyzer_service.py    # Wraps ai_tools analyzers
│   │   ├── generator_service.py   # Wraps ai_tools generators
│   │   ├── preset_service.py      # Wraps shared.preset
│   │   ├── cache_service.py       # Wraps shared.cache
│   │   └── job_service.py         # Background job management
│   ├── workers/
│   │   ├── __init__.py
│   │   └── tasks.py               # Celery/rq tasks
│   └── config.py                  # API configuration
├── ai_tools/                       # Existing tools (unchanged)
├── ai_capabilities/                # Existing specs (unchanged)
├── presets/                        # Existing presets (unchanged)
└── cache/                          # Existing cache (unchanged)
```

## API Endpoints

### Discovery & Status

```
GET  /                              # API info and version
GET  /health                        # Health check
GET  /tools                         # List all available tools
GET  /tools/:tool_name              # Tool details and schema
GET  /presets                       # List all preset categories
GET  /presets/:category             # List presets in category
```

### Analyzers

```
POST /analyze/outfit                # Analyze outfit
POST /analyze/visual-style          # Analyze visual style
POST /analyze/art-style             # Analyze art style
POST /analyze/hair-style            # Analyze hair style
POST /analyze/hair-color            # Analyze hair color
POST /analyze/makeup                # Analyze makeup
POST /analyze/expression            # Analyze expression
POST /analyze/accessories           # Analyze accessories
POST /analyze/comprehensive         # Run all analyzers

# Request body:
{
  "image_url": "http://..." or "image_data": "base64...",
  "save_as_preset": "preset-name" (optional),
  "skip_cache": false (optional)
}

# Response:
{
  "job_id": "uuid",
  "status": "queued" | "processing" | "completed" | "failed",
  "result": { ... spec ... } (if completed),
  "preset_path": "presets/category/name.json" (if saved),
  "cost": 0.001,
  "cache_hit": false
}
```

### Generators

```
POST /generate/modular              # Modular generation
POST /generate/outfit               # Outfit generation
POST /generate/style-transfer       # Style transfer
POST /generate/art-style            # Art style generation
POST /generate/combined             # Combined transformation

# Request body:
{
  "subject_image_url": "http://..." or "subject_image_data": "base64...",
  "outfit": "preset-name" or { ...spec... },
  "visual_style": "preset-name" or { ...spec... },
  "hair_style": "preset-name" (optional),
  "hair_color": "preset-name" (optional),
  "makeup": "preset-name" (optional),
  "expression": "preset-name" (optional),
  "accessories": "preset-name" (optional),
  "temperature": 0.8
}

# Response:
{
  "job_id": "uuid",
  "status": "queued" | "processing" | "completed" | "failed",
  "result": {
    "image_url": "/api/output/uuid.png",
    "image_data": "base64..." (optional),
    "generation_time": 9.5,
    "cost": 0.04
  }
}
```

### Batch Operations

```
POST /batch/analyze                 # Batch analysis
POST /batch/generate                # Batch generation

# Batch analyze request:
{
  "images": [
    {"url": "http://...", "save_as": "name1"},
    {"url": "http://...", "save_as": "name2"}
  ],
  "analyzer": "outfit" | "comprehensive",
  "skip_cache": false
}

# Batch generate request:
{
  "subjects": ["preset1", "preset2"],
  "outfits": ["outfit1", "outfit2"],
  "styles": ["style1", "style2"]
}

# Response:
{
  "batch_id": "uuid",
  "total": 12,
  "status": "queued",
  "progress_url": "/api/jobs/uuid"
}
```

### Presets Management

```
GET    /presets/:category                    # List presets in category
GET    /presets/:category/:name              # Get preset details
POST   /presets/:category                    # Create preset
PUT    /presets/:category/:name              # Update preset
DELETE /presets/:category/:name              # Delete preset
POST   /presets/:category/:name/duplicate    # Duplicate preset

# Create/Update body:
{
  "name": "my-preset",
  "data": { ...spec... },
  "notes": "Optional notes"
}
```

### Jobs & Progress

```
GET  /jobs/:job_id                  # Get job status
GET  /jobs/:job_id/result           # Get job result
POST /jobs/:job_id/cancel           # Cancel job
GET  /jobs                          # List recent jobs

# Job response:
{
  "job_id": "uuid",
  "type": "analyze" | "generate" | "batch",
  "status": "queued" | "processing" | "completed" | "failed",
  "progress": {
    "current": 5,
    "total": 10,
    "percent": 50
  },
  "created_at": "2025-10-14T16:00:00Z",
  "started_at": "2025-10-14T16:00:05Z",
  "completed_at": "2025-10-14T16:02:30Z",
  "result": { ... },
  "error": "Error message if failed",
  "cost": 0.04
}
```

### File Upload

```
POST /upload                        # Upload image
DELETE /upload/:filename            # Delete uploaded image

# Upload response:
{
  "filename": "uuid.jpg",
  "url": "/api/uploads/uuid.jpg",
  "size": 1024000,
  "mime_type": "image/jpeg"
}
```

## API Models (Pydantic)

```python
# api/models/requests.py
from pydantic import BaseModel, HttpUrl
from typing import Optional, Union, List
from ai_capabilities.specs import *

class ImageInput(BaseModel):
    """Image can be URL or base64 data"""
    image_url: Optional[HttpUrl] = None
    image_data: Optional[str] = None  # base64 encoded

class AnalyzeRequest(BaseModel):
    """Request to analyze an image"""
    image: ImageInput
    save_as_preset: Optional[str] = None
    skip_cache: bool = False

class GenerateRequest(BaseModel):
    """Request to generate an image"""
    subject_image: ImageInput
    outfit: Optional[Union[str, OutfitSpec]] = None
    visual_style: Optional[Union[str, VisualStyleSpec]] = None
    art_style: Optional[Union[str, ArtStyleSpec]] = None
    hair_style: Optional[Union[str, HairStyleSpec]] = None
    hair_color: Optional[Union[str, HairColorSpec]] = None
    makeup: Optional[Union[str, MakeupSpec]] = None
    expression: Optional[Union[str, ExpressionSpec]] = None
    accessories: Optional[Union[str, AccessoriesSpec]] = None
    temperature: float = 0.8

class BatchAnalyzeRequest(BaseModel):
    """Request to batch analyze images"""
    images: List[ImageInput]
    analyzer: str  # "outfit", "comprehensive", etc.
    save_as_prefix: Optional[str] = None
    skip_cache: bool = False

class PresetCreate(BaseModel):
    """Request to create a preset"""
    name: str
    data: dict
    notes: Optional[str] = None
```

```python
# api/models/responses.py
from pydantic import BaseModel
from typing import Optional, Any, Literal
from datetime import datetime

class JobResponse(BaseModel):
    """Response for async jobs"""
    job_id: str
    type: Literal["analyze", "generate", "batch"]
    status: Literal["queued", "processing", "completed", "failed"]
    progress: Optional[dict] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    cost: Optional[float] = None

class AnalyzeResponse(BaseModel):
    """Response from analysis"""
    job_id: str
    status: str
    result: Optional[dict] = None
    preset_path: Optional[str] = None
    cost: float
    cache_hit: bool

class GenerateResponse(BaseModel):
    """Response from generation"""
    job_id: str
    status: str
    result: Optional[dict] = None  # {image_url, generation_time, cost}

class ToolInfo(BaseModel):
    """Information about a tool"""
    name: str
    category: Literal["analyzer", "generator", "workflow"]
    description: str
    input_schema: dict
    output_schema: dict
    estimated_cost: float

class APIInfo(BaseModel):
    """API information"""
    name: str = "AI-Studio API"
    version: str = "1.0.0"
    tools_count: int
    presets_count: int
    docs_url: str = "/docs"
```

## Service Layer

Services wrap existing tools and handle API-specific logic:

```python
# api/services/analyzer_service.py
from pathlib import Path
from typing import Optional, Union
from ai_tools.outfit_analyzer.tool import OutfitAnalyzer
from ai_tools.comprehensive_analyzer.tool import ComprehensiveAnalyzer
# ... import all analyzers

class AnalyzerService:
    """Service for running analyzers"""

    def __init__(self):
        self.analyzers = {
            "outfit": OutfitAnalyzer(),
            "visual_style": VisualStyleAnalyzer(),
            "comprehensive": ComprehensiveAnalyzer(),
            # ... all analyzers
        }

    async def analyze(
        self,
        analyzer_name: str,
        image_path: Path,
        save_as_preset: Optional[str] = None,
        skip_cache: bool = False
    ):
        """Run analyzer and return result"""
        analyzer = self.analyzers.get(analyzer_name)
        if not analyzer:
            raise ValueError(f"Unknown analyzer: {analyzer_name}")

        # Run analyzer (wraps existing tool)
        result = analyzer.analyze(
            image_path,
            skip_cache=skip_cache,
            save_as_preset=save_as_preset
        )

        return result

    def list_analyzers(self):
        """List all available analyzers"""
        return list(self.analyzers.keys())
```

```python
# api/services/preset_service.py
from pathlib import Path
from typing import List
from ai_tools.shared.preset import PresetManager

class PresetService:
    """Service for managing presets"""

    def __init__(self):
        self.preset_manager = PresetManager()

    def list_categories(self) -> List[str]:
        """List all preset categories"""
        return ["outfits", "visual_styles", "art_styles",
                "hair_styles", "hair_colors", "makeup",
                "expressions", "accessories"]

    def list_presets(self, category: str) -> List[str]:
        """List presets in category"""
        return self.preset_manager.list(category)

    def get_preset(self, category: str, name: str):
        """Get preset data"""
        # Load and return preset JSON
        preset_path = Path("presets") / category / f"{name}.json"
        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {category}/{name}")

        import json
        with open(preset_path) as f:
            return json.load(f)

    def create_preset(self, category: str, name: str, data: dict, notes: str = None):
        """Create new preset"""
        return self.preset_manager.save(category, name, data, notes=notes)

    def update_preset(self, category: str, name: str, data: dict):
        """Update existing preset"""
        return self.preset_manager.save(category, name, data)

    def delete_preset(self, category: str, name: str):
        """Delete preset"""
        preset_path = Path("presets") / category / f"{name}.json"
        if preset_path.exists():
            preset_path.unlink()
```

## Background Jobs

For long-running operations (generation, batch processing):

```python
# api/workers/tasks.py
from celery import Celery
from api.services.analyzer_service import AnalyzerService
from api.services.generator_service import GeneratorService

celery_app = Celery('ai_studio', broker='redis://localhost:6379/0')

@celery_app.task(bind=True)
def analyze_image(self, analyzer_name, image_path, save_as_preset=None):
    """Background task for analysis"""
    service = AnalyzerService()

    # Update progress
    self.update_state(state='PROCESSING', meta={'progress': 0})

    try:
        result = service.analyze(analyzer_name, image_path, save_as_preset)
        return {'status': 'completed', 'result': result}
    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

@celery_app.task(bind=True)
def generate_image(self, subject_image, specs):
    """Background task for generation"""
    service = GeneratorService()

    self.update_state(state='PROCESSING', meta={'progress': 0})

    try:
        result = service.generate(subject_image, **specs)
        return {'status': 'completed', 'result': result}
    except Exception as e:
        return {'status': 'failed', 'error': str(e)}
```

## Main API Application

```python
# api/main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import discovery, analyzers, generators, presets, batch, jobs
from api.models.responses import APIInfo

app = FastAPI(
    title="AI-Studio API",
    description="API for AI-powered image analysis and generation",
    version="1.0.0"
)

# CORS for web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated images
app.mount("/output", StaticFiles(directory="output"), name="output")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(discovery.router, tags=["discovery"])
app.include_router(analyzers.router, prefix="/analyze", tags=["analyzers"])
app.include_router(generators.router, prefix="/generate", tags=["generators"])
app.include_router(presets.router, prefix="/presets", tags=["presets"])
app.include_router(batch.router, prefix="/batch", tags=["batch"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

@app.get("/", response_model=APIInfo)
async def root():
    """API information"""
    from api.services.preset_service import PresetService

    preset_service = PresetService()
    total_presets = sum(
        len(preset_service.list_presets(cat))
        for cat in preset_service.list_categories()
    )

    return APIInfo(
        tools_count=17,  # 9 analyzers + 6 generators + 2 video
        presets_count=total_presets
    )

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}
```

## Example Route Implementation

```python
# api/routes/analyzers.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.models.requests import AnalyzeRequest
from api.models.responses import AnalyzeResponse
from api.services.analyzer_service import AnalyzerService
from api.workers.tasks import analyze_image
import uuid

router = APIRouter()
service = AnalyzerService()

@router.post("/outfit", response_model=AnalyzeResponse)
async def analyze_outfit(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Analyze outfit in image"""

    # Download/decode image
    image_path = await download_image(request.image)

    # For quick operations, run synchronously
    if True:  # Could check file size or have sync/async flag
        try:
            result = service.analyze(
                "outfit",
                image_path,
                save_as_preset=request.save_as_preset,
                skip_cache=request.skip_cache
            )

            return AnalyzeResponse(
                job_id=str(uuid.uuid4()),
                status="completed",
                result=result.model_dump(),
                cost=0.001,
                cache_hit=not request.skip_cache
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # For long operations, use background task
    else:
        job_id = str(uuid.uuid4())
        task = analyze_image.delay("outfit", str(image_path), request.save_as_preset)

        return AnalyzeResponse(
            job_id=job_id,
            status="queued",
            cost=0.001
        )

@router.get("/")
async def list_analyzers():
    """List all available analyzers"""
    return {
        "analyzers": service.list_analyzers(),
        "count": len(service.list_analyzers())
    }
```

## Running the API

```bash
# Development
uvicorn api.main:app --reload --port 8000

# Production
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# With Celery worker (for background jobs)
celery -A api.workers.tasks worker --loglevel=info
```

## API Documentation

FastAPI auto-generates:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Testing the API

```bash
# Analyze outfit
curl -X POST http://localhost:8000/analyze/outfit \
  -H "Content-Type: application/json" \
  -d '{
    "image": {"image_url": "http://example.com/photo.jpg"},
    "save_as_preset": "my-outfit"
  }'

# List presets
curl http://localhost:8000/presets/outfits

# Get preset
curl http://localhost:8000/presets/outfits/my-outfit

# Generate image
curl -X POST http://localhost:8000/generate/modular \
  -H "Content-Type: application/json" \
  -d '{
    "subject_image": {"image_url": "http://example.com/subject.jpg"},
    "outfit": "my-outfit",
    "visual_style": "film-noir"
  }'
```

## Web App Integration

The web app would:

```javascript
// React/Vue/etc example
const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// List tools
const tools = await api.get('/tools');

// Analyze image
const formData = new FormData();
formData.append('file', imageFile);
const uploadRes = await api.post('/upload', formData);

const analyzeRes = await api.post('/analyze/outfit', {
  image: { image_url: uploadRes.data.url },
  save_as_preset: 'my-outfit'
});

// Generate image
const generateRes = await api.post('/generate/modular', {
  subject_image: { image_url: subjectUrl },
  outfit: 'my-outfit',
  visual_style: 'film-noir'
});

// Poll for result if async
const checkJob = async (jobId) => {
  const job = await api.get(`/jobs/${jobId}`);
  if (job.data.status === 'completed') {
    return job.data.result;
  }
  setTimeout(() => checkJob(jobId), 1000);
};
```

## Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./presets:/app/presets
      - ./cache:/app/cache
      - ./output:/app/output
    depends_on:
      - redis

  worker:
    build: .
    command: celery -A api.workers.tasks worker --loglevel=info
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./presets:/app/presets
      - ./cache:/app/cache
      - ./output:/app/output
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Security Considerations

1. **API Key Protection**: Don't expose internal API keys through API
2. **Rate Limiting**: Implement rate limiting per IP/user
3. **File Upload Validation**: Validate file types, sizes
4. **CORS**: Configure properly for production
5. **Authentication**: Add JWT/OAuth for production use

## Cost Tracking

Add cost tracking service:

```python
# api/services/cost_service.py
class CostService:
    def __init__(self):
        self.costs = []

    def track_cost(self, operation: str, cost: float):
        """Track operation cost"""
        self.costs.append({
            "operation": operation,
            "cost": cost,
            "timestamp": datetime.now()
        })

    def get_daily_cost(self):
        """Get today's total cost"""
        today = datetime.now().date()
        return sum(
            c["cost"] for c in self.costs
            if c["timestamp"].date() == today
        )
```

## Next Steps

1. Implement basic FastAPI app with discovery endpoints
2. Add analyzer endpoints (reusing existing tools)
3. Add preset management endpoints
4. Add background job support for generators
5. Add file upload handling
6. Create web app frontend
7. Add authentication
8. Deploy with Docker

This API layer will make all your CLI tools accessible via HTTP while maintaining the existing workflow for direct CLI usage.
