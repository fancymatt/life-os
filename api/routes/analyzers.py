"""
Analyzer Routes

Endpoints for running image analyzers.
"""

import time
import tempfile
import base64
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Query
from typing import List

from api.models.requests import AnalyzeRequest
from api.models.responses import AnalyzeResponse, ToolInfo
from api.models.jobs import JobType
from api.services import AnalyzerService
from api.services.job_queue import get_job_queue_manager
from api.config import settings

router = APIRouter()
analyzer_service = AnalyzerService()


async def download_or_decode_image(image_input) -> Path:
    """Download or decode image to temporary file"""
    temp_file = Path(tempfile.mktemp(suffix=".jpg", dir=settings.upload_dir))

    if image_input.image_data:
        # Decode base64
        image_bytes = base64.b64decode(image_input.image_data)
        with open(temp_file, 'wb') as f:
            f.write(image_bytes)
    elif image_input.image_url:
        # Download from URL
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(str(image_input.image_url))
            response.raise_for_status()
            with open(temp_file, 'wb') as f:
                f.write(response.content)
    else:
        raise ValueError("Either image_url or image_data must be provided")

    return temp_file


@router.get("/", response_model=List[ToolInfo])
async def list_analyzers():
    """List all available analyzers"""
    analyzers = analyzer_service.list_analyzers()
    return [ToolInfo(**a) for a in analyzers]


def run_analyzer_job(
    job_id: str,
    analyzer_name: str,
    image_path: Path,
    request: AnalyzeRequest
):
    """Background task to run analyzer and update job"""
    try:
        get_job_queue_manager().start_job(job_id)
        get_job_queue_manager().update_progress(job_id, 0.1, "Starting analysis...")

        # Run analyzer
        result = analyzer_service.analyze(
            analyzer_name,
            image_path,
            save_as_preset=request.save_as_preset,
            skip_cache=request.skip_cache,
            background_tasks=None,  # No nested background tasks in async mode
            selected_analyses=request.selected_analyses
        )

        get_job_queue_manager().update_progress(job_id, 0.9, "Finalizing...")

        # Complete job with result
        get_job_queue_manager().complete_job(job_id, result)

    except Exception as e:
        get_job_queue_manager().fail_job(job_id, str(e))
    finally:
        # Cleanup temp file
        if image_path.exists():
            image_path.unlink()


@router.post("/{analyzer_name}")
async def analyze_image(
    analyzer_name: str,
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    async_mode: bool = Query(False, description="Run analysis in background and return job_id")
):
    """
    Analyze an image with a specific analyzer

    Available analyzers:
    - outfit: Analyze outfit details
    - visual-style: Analyze photograph composition
    - art-style: Analyze artistic style
    - hair-style: Analyze hair structure
    - hair-color: Analyze hair color
    - makeup: Analyze makeup
    - expression: Analyze facial expression
    - accessories: Analyze accessories
    - comprehensive: Run all analyzers

    Query Parameters:
    - async_mode: If true, returns job_id immediately and processes in background
    """
    if not analyzer_service.validate_analyzer(analyzer_name):
        raise HTTPException(status_code=404, detail=f"Analyzer not found: {analyzer_name}")

    # Download or decode image
    image_path = await download_or_decode_image(request.image)

    # Async mode: Create job and return immediately
    if async_mode:
        # Determine job type
        if analyzer_name == "comprehensive":
            job_type = JobType.COMPREHENSIVE_ANALYZE
            title = "Comprehensive analysis"
        else:
            job_type = JobType.ANALYZE
            title = f"Analyzing {analyzer_name}"

        # Create job
        job_id = get_job_queue_manager().create_job(
            job_type=job_type,
            title=title,
            description=f"Image: {image_path.name}"
        )

        # Queue background task
        background_tasks.add_task(
            run_analyzer_job,
            job_id,
            analyzer_name,
            image_path,
            request
        )

        # Return job info
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Analysis queued. Use /jobs/{job_id} to check status."
        }

    # Synchronous mode: Run analysis and return result
    start_time = time.time()

    try:
        # Run analyzer
        result = analyzer_service.analyze(
            analyzer_name,
            image_path,
            save_as_preset=request.save_as_preset,
            skip_cache=request.skip_cache,
            background_tasks=background_tasks,
            selected_analyses=request.selected_analyses
        )

        processing_time = time.time() - start_time

        # Get cost info
        analyzer_info = analyzer_service.get_analyzer_info(analyzer_name)

        # Handle comprehensive analyzer differently (it returns created_presets structure)
        if analyzer_name == "comprehensive":
            return AnalyzeResponse(
                status="completed",
                result=result,  # Contains 'created_presets' and 'results'
                preset_id=None,  # Comprehensive doesn't have single preset_id
                preset_display_name=None,
                cost=analyzer_info["estimated_cost"],
                cache_hit=not request.skip_cache,
                processing_time=processing_time
            )

        # Get preset ID if saved (for individual analyzers)
        preset_id = None
        preset_display_name = None
        if request.save_as_preset and result and "_metadata" in result:
            preset_id = result["_metadata"].get("preset_id")
            preset_display_name = result["_metadata"].get("display_name")

        return AnalyzeResponse(
            status="completed",
            result=result,
            preset_id=preset_id,
            preset_display_name=preset_display_name,
            cost=analyzer_info["estimated_cost"],
            cache_hit=not request.skip_cache,
            processing_time=processing_time
        )

    except Exception as e:
        return AnalyzeResponse(
            status="failed",
            cost=0.0,
            cache_hit=False,
            error=str(e)
        )
    finally:
        # Cleanup temp file (only in sync mode, async mode handles its own cleanup)
        if not async_mode and 'image_path' in locals() and image_path.exists():
            image_path.unlink()


@router.post("/upload", response_model=dict)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image file

    Returns a temporary URL that can be used for analysis.
    """
    # Validate file type
    if not any(file.filename.lower().endswith(ext) for ext in settings.allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.allowed_extensions}"
        )

    # Save file
    file_path = settings.upload_dir / file.filename
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    return {
        "filename": file.filename,
        "url": f"/uploads/{file.filename}",
        "size_bytes": len(content)
    }
