"""
AI-Studio FastAPI Application

Main API application with routes for analyzers, generators, and preset management.
"""

import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from api.config import settings
from api.logging_config import setup_logging
from api.models.responses import APIInfo, HealthResponse
from api.services import AnalyzerService, GeneratorService, PresetService
from api.routes import discovery, analyzers, generators, presets, jobs, auth

# Initialize logging
setup_logging(log_dir=settings.base_dir / "logs", log_level="INFO")

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc"
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

# Log CORS configuration on startup
print(f"✅ CORS configured for origins: {settings.cors_origins}")

# Log authentication status
if settings.require_authentication:
    print(f"🔒 Authentication: REQUIRED (JWT)")
else:
    print(f"⚠️  Authentication: DISABLED (development mode)")

# Serve static files (generated images, uploads)
try:
    app.mount("/output", StaticFiles(directory=str(settings.output_dir)), name="output")
    app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")
except RuntimeError:
    # Directories might not exist yet
    pass

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(discovery.router, tags=["discovery"])
app.include_router(analyzers.router, prefix="/analyze", tags=["analyzers"])
app.include_router(generators.router, prefix="/generate", tags=["generators"])
app.include_router(presets.router, prefix="/presets", tags=["presets"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
