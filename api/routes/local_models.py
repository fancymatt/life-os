"""
Local LLM Model Management Routes

Endpoints for managing local models via Ollama.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import os
import httpx
from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from api.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Ollama base URL (from environment)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")


# Request/Response Models
class ModelPullRequest(BaseModel):
    """Request to pull a model"""
    model_name: str
    insecure: bool = False  # Allow insecure connections


class ModelDeleteRequest(BaseModel):
    """Request to delete a model"""
    model_name: str


class ModelInfo(BaseModel):
    """Information about a model"""
    name: str
    size: Optional[int] = None
    digest: Optional[str] = None
    modified_at: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ModelListResponse(BaseModel):
    """Response with list of models"""
    models: List[ModelInfo]
    count: int


class OllamaStatusResponse(BaseModel):
    """Ollama service status"""
    status: str  # "running", "error", "unavailable"
    version: Optional[str] = None
    models_count: int = 0
    error: Optional[str] = None


class ModelPullProgress(BaseModel):
    """Progress update for model pull"""
    status: str
    digest: Optional[str] = None
    total: Optional[int] = None
    completed: Optional[int] = None


async def get_ollama_client() -> httpx.AsyncClient:
    """Get httpx client configured for Ollama"""
    return httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=300.0)


@router.get("/status", response_model=OllamaStatusResponse)
async def get_ollama_status(
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Check Ollama service status

    Returns status, version, and model count.
    """
    try:
        async with await get_ollama_client() as client:
            # Check version endpoint
            version_response = await client.get("/api/version")
            version_data = version_response.json()

            # Get models count
            models_response = await client.get("/api/tags")
            models_data = models_response.json()
            models_count = len(models_data.get("models", []))

            return OllamaStatusResponse(
                status="running",
                version=version_data.get("version"),
                models_count=models_count
            )

    except httpx.ConnectError:
        return OllamaStatusResponse(
            status="unavailable",
            models_count=0,
            error="Ollama service is not running or unreachable"
        )
    except Exception as e:
        return OllamaStatusResponse(
            status="error",
            models_count=0,
            error=str(e)
        )


@router.get("/", response_model=ModelListResponse)
async def list_models(
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all downloaded local models

    Returns list of models with their metadata.
    """
    try:
        async with await get_ollama_client() as client:
            response = await client.get("/api/tags")
            response.raise_for_status()

            data = response.json()
            models = data.get("models", [])

            model_infos = []
            for model in models:
                model_infos.append(ModelInfo(
                    name=model.get("name", ""),
                    size=model.get("size"),
                    digest=model.get("digest"),
                    modified_at=model.get("modified_at"),
                    details=model.get("details", {})
                ))

            return ModelListResponse(
                models=model_infos,
                count=len(model_infos)
            )

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Ollama service is not running. Start it with: docker-compose up ollama"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/{model_name}", response_model=ModelInfo)
async def get_model_info(
    model_name: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific model

    Args:
        model_name: Name of the model (e.g., "llama2:7b", "mistral")
    """
    try:
        async with await get_ollama_client() as client:
            response = await client.post(
                "/api/show",
                json={"name": model_name}
            )
            response.raise_for_status()

            data = response.json()

            return ModelInfo(
                name=model_name,
                size=data.get("size"),
                digest=data.get("digest"),
                modified_at=data.get("modified_at"),
                details=data.get("details", {})
            )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
        raise HTTPException(status_code=500, detail=str(e))
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Ollama service is not running"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")


@router.post("/pull")
async def pull_model(
    request: ModelPullRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Pull a model from Ollama registry

    This runs in the background and returns immediately.
    Use GET /local-models/ to check when the model is ready.

    Popular models:
    - llama3.2:3b (3B params, ~2GB) - Fast, good for testing
    - llama2:7b (7B params, ~4GB) - Good balance
    - mistral:7b (7B params, ~4GB) - Fast inference
    - qwen2.5:7b (7B params, ~4.7GB) - Strong performance
    - codellama:7b (7B params, ~4GB) - Code generation
    - mixtral:8x7b (47B params, ~26GB) - Very powerful
    - qwen2.5:72b (72B params, ~41GB) - Large model

    Args:
        request: Model pull request with model name
    """
    async def do_pull():
        """Background task to pull model"""
        try:
            logger.info(f"Pulling model: {request.model_name}", extra={'extra_fields': {
                'model_name': request.model_name
            }})

            async with await get_ollama_client() as client:
                # Stream the pull progress
                async with client.stream(
                    "POST",
                    "/api/pull",
                    json={
                        "name": request.model_name,
                        "insecure": request.insecure
                    },
                    timeout=3600.0  # 1 hour timeout for large models
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            logger.debug(f"Pull progress: {line}", extra={'extra_fields': {
                                'model_name': request.model_name
                            }})

            logger.info(f"Model pulled successfully", extra={'extra_fields': {
                'model_name': request.model_name
            }})

        except Exception as e:
            logger.error(f"Failed to pull model", exc_info=e, extra={'extra_fields': {
                'model_name': request.model_name,
                'error': str(e)
            }})

    # Queue the background task
    background_tasks.add_task(do_pull)

    return {
        "status": "pulling",
        "model": request.model_name,
        "message": f"Pulling {request.model_name} in background. This may take several minutes depending on model size."
    }


@router.delete("/{model_name}")
async def delete_model(
    model_name: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete a local model

    Args:
        model_name: Name of the model to delete (e.g., "llama2:7b")
    """
    try:
        async with await get_ollama_client() as client:
            response = await client.delete(
                "/api/delete",
                json={"name": model_name}
            )
            response.raise_for_status()

            return {
                "status": "deleted",
                "model": model_name,
                "message": f"Model {model_name} deleted successfully"
            }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
        raise HTTPException(status_code=500, detail=str(e))
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Ollama service is not running"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete model: {str(e)}")


@router.post("/test/{model_name}")
async def test_model(
    model_name: str,
    prompt: str = "Hello! Tell me a short joke.",
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Test a local model with a simple prompt

    Args:
        model_name: Name of the model to test
        prompt: Test prompt (default: ask for a joke)
    """
    try:
        async with await get_ollama_client() as client:
            response = await client.post(
                "/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60.0
            )
            response.raise_for_status()

            data = response.json()

            return {
                "status": "success",
                "model": model_name,
                "prompt": prompt,
                "response": data.get("response", ""),
                "eval_count": data.get("eval_count"),
                "eval_duration": data.get("eval_duration")
            }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Model {model_name} not found. Pull it first with POST /local-models/pull"
            )
        raise HTTPException(status_code=500, detail=str(e))
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Ollama service is not running"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model test failed: {str(e)}")
