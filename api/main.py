"""
AI-Studio FastAPI Application

Main API application with routes for analyzers, generators, and preset management.
"""

import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from starlette.middleware.gzip import GZIPMiddleware  # Will add back with correct import
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from api.config import settings
from api.logging_config import setup_logging, get_logger
from api.models.responses import APIInfo, HealthResponse
from api.services import AnalyzerService, GeneratorService, PresetService
from api.routes import discovery, analyzers, generators, presets, jobs, auth, favorites, compositions, workflows, story_tools, characters, configs, tool_configs, local_models, board_games, documents, qa, clothing_items, outfits, visualization_configs, images, cache
from api.middleware.request_id import RequestIDMiddleware

# Initialize logging
setup_logging(log_dir=settings.base_dir / "logs", log_level="INFO")

# Get logger for main module
logger = get_logger(__name__)


# Database lifecycle management
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: startup and shutdown events
    """
    # Startup
    from api.database import init_db

    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    from api.database import close_db
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Track start time for uptime
START_TIME = time.time()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Request ID middleware for log correlation
app.add_middleware(RequestIDMiddleware)

# GZIP compression middleware (60-80% bandwidth reduction)
# TODO: Add GZIP middleware with correct import
# app.add_middleware(GZIPMiddleware, minimum_size=1000)

# Log CORS configuration on startup
logger.info(f"CORS configured for origins: {settings.cors_origins}")
# logger.info("GZIP compression enabled (min size: 1KB)")

# Log authentication status
if settings.require_authentication:
    logger.info("Authentication: REQUIRED (JWT)")
else:
    logger.warning("Authentication: DISABLED (development mode)")


# Custom StaticFiles class with Cache-Control headers
class CachedStaticFiles(StaticFiles):
    """StaticFiles with Cache-Control headers for better caching"""

    def __init__(self, *args, max_age: int = 3600, **kwargs):
        self.max_age = max_age
        super().__init__(*args, **kwargs)

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        # Add Cache-Control header for better browser caching
        response.headers["Cache-Control"] = f"public, max-age={self.max_age}"
        return response


# Serve static files (generated images, uploads) with caching
try:
    # Generated images: 1 hour cache (they don't change once generated)
    app.mount("/output", CachedStaticFiles(directory=str(settings.output_dir), max_age=3600), name="output")
    # Uploads: 30 minute cache (temporary files)
    app.mount("/uploads", CachedStaticFiles(directory=str(settings.upload_dir), max_age=1800), name="uploads")
    logger.info("Static file caching enabled (Cache-Control headers)")
except RuntimeError as e:
    # Directories might not exist yet
    logger.warning(f"Could not mount static files: {e}")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(discovery.router, tags=["discovery"])
app.include_router(analyzers.router, prefix="/analyze", tags=["analyzers"])
app.include_router(generators.router, prefix="/generate", tags=["generators"])
app.include_router(presets.router, prefix="/presets", tags=["presets"])
app.include_router(configs.router, prefix="/configs", tags=["configurations"])
app.include_router(tool_configs.router, prefix="/tool-configs", tags=["tool-configuration"])
app.include_router(local_models.router, prefix="/local-models", tags=["local-models"])
app.include_router(characters.router, prefix="/characters", tags=["characters"])
app.include_router(clothing_items.router, prefix="/clothing-items", tags=["clothing-items"])
app.include_router(outfits.router, prefix="/outfits", tags=["outfits"])
app.include_router(visualization_configs.router, prefix="/visualization-configs", tags=["visualization-configs"])
app.include_router(board_games.router, prefix="/board-games", tags=["board-games"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(qa.router, prefix="/qa", tags=["qa"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
app.include_router(compositions.router, prefix="/compositions", tags=["compositions"])
app.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
app.include_router(story_tools.router, prefix="/story-tools", tags=["story-tools"])
app.include_router(images.router, prefix="/images", tags=["images"])
app.include_router(cache.router, tags=["cache"])


@app.get("/", response_model=APIInfo)
async def root():
    """
    Get API information

    Returns information about the API including available tools and presets.
    """
    analyzer_service = AnalyzerService()
    generator_service = GeneratorService()
    preset_service = PresetService()

    tools_count = len(analyzer_service.list_analyzers()) + len(generator_service.list_generators())
    presets_count = preset_service.get_total_presets()

    return APIInfo(
        tools_count=tools_count,
        presets_count=presets_count,
        categories=preset_service.list_categories()
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint

    Returns the health status of the API and its dependencies.
    """
    uptime = time.time() - START_TIME

    # Check various components
    checks = {
        "api_keys": bool(settings.gemini_api_key),
        "presets_dir": settings.presets_dir.exists(),
        "cache_dir": settings.cache_dir.exists(),
        "output_dir": settings.output_dir.exists()
    }

    # Determine overall status
    if all(checks.values()):
        status = "healthy"
    elif checks["api_keys"] and checks["presets_dir"]:
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthResponse(
        status=status,
        version=settings.api_version,
        uptime_seconds=uptime,
        checks=checks
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions"""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(FileNotFoundError)
async def not_found_handler(request, exc):
    """Handle FileNotFoundError exceptions"""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )


@app.exception_handler(FileExistsError)
async def exists_handler(request, exc):
    """Handle FileExistsError exceptions"""
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler to catch and log all unhandled errors"""
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {exc}",
        exc_info=exc,
        extra={'extra_fields': {
            'method': request.method,
            'url': str(request.url),
            'error_type': type(exc).__name__,
        }}
    )

    # Return 500 error to client
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {str(exc)}"}
    )


# Handle FastAPI validation errors
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Handle validation errors with detailed logging"""
    errors = exc.errors()

    # Sanitize errors for logging (remove large byte fields)
    sanitized_errors = []
    for error in errors:
        if 'input' in error and isinstance(error['input'], bytes):
            error_copy = error.copy()
            error_copy['input'] = f"<bytes: {len(error['input'])} bytes>"
            sanitized_errors.append(error_copy)
        else:
            sanitized_errors.append(error)

    logger.warning(
        f"Validation error: {request.method} {request.url}",
        extra={'extra_fields': {
            'method': request.method,
            'url': str(request.url),
            'content_type': request.headers.get('content-type'),
            'errors': sanitized_errors[:5],  # Limit to first 5 errors
        }}
    )

    # Return simplified error to client (without raw bytes in errors)
    safe_errors = []
    for error in errors:
        safe_error = {k: v for k, v in error.items() if k != 'input'}
        safe_error['msg'] = error.get('msg', 'Validation error')
        safe_errors.append(safe_error)

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error - check server logs",
            "errors": safe_errors
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
