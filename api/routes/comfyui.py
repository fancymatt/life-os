"""ComfyUI API Routes

Simple test endpoint for ComfyUI integration
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pathlib import Path
from typing import Optional
import uuid
from pydantic import BaseModel

from api.services.comfyui_service import get_comfyui_service
from api.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ComfyUIHealthResponse(BaseModel):
    """Health check response"""
    status: str
    available: bool
    gpu: Optional[str] = None
    vram_total_gb: Optional[float] = None
    vram_free_gb: Optional[float] = None
    comfyui_version: Optional[str] = None
    error: Optional[str] = None


class QwenEditResponse(BaseModel):
    """Qwen edit response"""
    status: str
    output_path: Optional[str] = None
    prompt: Optional[str] = None
    error: Optional[str] = None
    execution_time_seconds: Optional[float] = None


@router.get("/health", response_model=ComfyUIHealthResponse)
async def comfyui_health():
    """Check ComfyUI server health"""
    try:
        service = get_comfyui_service()
        health = await service.health_check()
        return ComfyUIHealthResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-edit", response_model=QwenEditResponse)
async def test_qwen_edit(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    steps: int = Form(50),
    cfg: float = Form(4.0),
    denoise: float = Form(0.85)
):
    """
    Simple test endpoint for Qwen-Image-Edit

    Upload an image and a prompt, get back an edited image.

    Example:
        curl -X POST http://localhost:8000/api/comfyui/test-edit \
          -F "file=@input.png" \
          -F "prompt=Transform into a cyberpunk character" \
          -F "steps=50"
    """
    import time
    start_time = time.time()

    try:
        service = get_comfyui_service()

        if not service.enabled:
            raise HTTPException(status_code=503, detail="ComfyUI is not enabled")

        # Save uploaded file temporarily
        upload_dir = Path("/app/uploads")
        upload_dir.mkdir(exist_ok=True)

        temp_filename = f"comfyui_test_{uuid.uuid4().hex[:8]}_{file.filename}"
        temp_path = upload_dir / temp_filename

        logger.info(f"Saving uploaded file to: {temp_path}")
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Create output directory
        output_dir = Path("/app/output")
        output_dir.mkdir(exist_ok=True)

        # Run Qwen edit
        logger.info(f"Starting Qwen edit: prompt='{prompt}', steps={steps}")
        result = await service.edit_image_qwen(
            input_image_path=temp_path,
            prompt=prompt,
            output_dir=output_dir,
            steps=steps,
            cfg=cfg,
            denoise=denoise
        )

        # Clean up temp file
        temp_path.unlink()

        execution_time = time.time() - start_time
        logger.info(f"Qwen edit completed in {execution_time:.2f}s")

        return QwenEditResponse(
            status="success",
            output_path=result["output_path"],
            prompt=prompt,
            execution_time_seconds=execution_time
        )

    except Exception as e:
        logger.error(f"Qwen edit failed: {e}")
        return QwenEditResponse(
            status="failed",
            error=str(e)
        )
