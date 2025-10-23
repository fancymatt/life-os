"""
Tool Configuration Routes

API endpoints for configuring non-preset tools (analyzers, generators, agents).
Allows editing prompts, models, and parameters for system tools.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from pathlib import Path
import yaml
import aiofiles

from api.logging_config import get_logger
from api.models.auth import User
from api.models.jobs import JobType
from api.dependencies.auth import get_current_active_user
from api.services.job_queue import get_job_queue_manager
from api.config import settings

router = APIRouter()


def get_tool_dir(tool_name: str) -> Path:
    """Get the directory for a tool"""
    tool_dir = settings.base_dir / "ai_tools" / tool_name
    if not tool_dir.exists():
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
    return tool_dir


def get_models_config_path() -> Path:
    """Get path to models.yaml (read-only base config)"""
    return settings.base_dir / "configs" / "models.yaml"


def get_tool_config_overrides_path() -> Path:
    """Get path to tool config overrides (writable)"""
    path = settings.base_dir / "data" / "tool_configs" / "overrides.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


async def load_models_config() -> Dict[str, Any]:
    """Load models.yaml configuration with overrides"""
    # Load base config (read-only)
    base_config_path = get_models_config_path()
    async with aiofiles.open(base_config_path, 'r') as f:
        content = await f.read()
        base_config = yaml.safe_load(content)

    # Load overrides (writable)
    overrides_path = get_tool_config_overrides_path()
    if overrides_path.exists():
        async with aiofiles.open(overrides_path, 'r') as f:
            content = await f.read()
            overrides = yaml.safe_load(content) or {}

            # Merge overrides into base config
            if 'defaults' in overrides:
                base_config.setdefault('defaults', {}).update(overrides['defaults'])
            if 'tool_settings' in overrides:
                base_config.setdefault('tool_settings', {}).update(overrides['tool_settings'])

    return base_config


async def save_models_config(config: Dict[str, Any]):
    """Save tool config overrides (not base config)"""
    # Only save the parts that can be customized
    overrides = {
        'defaults': config.get('defaults', {}),
        'tool_settings': config.get('tool_settings', {})
    }

    overrides_path = get_tool_config_overrides_path()
    async with aiofiles.open(overrides_path, 'w') as f:
        await f.write(yaml.dump(overrides, default_flow_style=False, sort_keys=False))


@router.get("/tools")
async def list_tools(
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all available tools

    Returns tools organized by type (analyzers, generators, agents)
    """
    tools_dir = settings.base_dir / "ai_tools"

    tools = {
        "analyzers": [],
        "generators": [],
        "agents": []
    }

    # Scan tools directory
    for tool_path in tools_dir.iterdir():
        if tool_path.is_dir() and not tool_path.name.startswith('_') and tool_path.name != 'shared':
            tool_name = tool_path.name

            # Categorize by suffix
            if tool_name.endswith('_analyzer'):
                category = "analyzers"
                display_name = tool_name.replace('_analyzer', '').replace('_', ' ').title()
            elif tool_name.endswith('_generator'):
                category = "generators"
                display_name = tool_name.replace('_generator', '').replace('_', ' ').title()
            else:
                category = "agents"
                display_name = tool_name.replace('_', ' ').title()

            # Check if has template.md (indicates configurable tool)
            template_path = tool_path / "template.md"
            has_template = template_path.exists()

            tools[category].append({
                "name": tool_name,
                "display_name": display_name,
                "has_template": has_template,
                "path": str(tool_path)
            })

    return tools


@router.get("/tools/{tool_name}")
async def get_tool_config(
    tool_name: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get tool configuration

    Returns:
    - Tool metadata (name, description)
    - Model configuration
    - Temperature setting
    - Prompt template (if exists)
    """
    tool_dir = get_tool_dir(tool_name)

    # Load models config
    models_config = await load_models_config()

    # Get model for this tool
    model = models_config.get('defaults', {}).get(tool_name, 'gemini/gemini-2.0-flash-exp')

    # Get temperature for this tool
    tool_settings = models_config.get('tool_settings', {})
    temperature = tool_settings.get(tool_name, {}).get('temperature', 0.7)

    # Load template (check for custom override first, then base template)
    template = None
    custom_template_path = settings.base_dir / "data" / "tool_configs" / f"{tool_name}_template.md"
    base_template_path = tool_dir / "template.md"

    if custom_template_path.exists():
        # Load custom template
        async with aiofiles.open(custom_template_path, 'r') as f:
            template = await f.read()
    elif base_template_path.exists():
        # Load base template
        async with aiofiles.open(base_template_path, 'r') as f:
            template = await f.read()

    # Load tool.py to get description
    tool_py_path = tool_dir / "tool.py"
    description = None
    if tool_py_path.exists():
        async with aiofiles.open(tool_py_path, 'r') as f:
            content = await f.read()
            # Extract docstring
            if '"""' in content:
                parts = content.split('"""')
                if len(parts) >= 3:
                    description = parts[1].strip()

    return {
        "name": tool_name,
        "display_name": tool_name.replace('_', ' ').title(),
        "description": description,
        "model": model,
        "temperature": temperature,
        "template": template,
        "has_template": template is not None
    }


@router.put("/tools/{tool_name}")
async def update_tool_config(
    tool_name: str,
    config: Dict[str, Any],
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update tool configuration

    Accepts:
    - model: Model to use
    - temperature: Temperature setting
    - template: Prompt template (if tool has template.md)
    """
    tool_dir = get_tool_dir(tool_name)

    # Load models config
    models_config = await load_models_config()

    # Update model if provided
    if 'model' in config:
        if 'defaults' not in models_config:
            models_config['defaults'] = {}
        models_config['defaults'][tool_name] = config['model']

    # Update temperature if provided
    if 'temperature' in config:
        if 'tool_settings' not in models_config:
            models_config['tool_settings'] = {}
        if tool_name not in models_config['tool_settings']:
            models_config['tool_settings'][tool_name] = {}
        models_config['tool_settings'][tool_name]['temperature'] = config['temperature']

    # Save models config
    await save_models_config(models_config)

    # Update template if provided
    if 'template' in config:
        # Check if base template exists
        base_template_path = tool_dir / "template.md"
        if not base_template_path.exists():
            raise HTTPException(status_code=400, detail=f"Tool {tool_name} does not have a template")

        # Save to custom template location (writable)
        custom_template_path = settings.base_dir / "data" / "tool_configs" / f"{tool_name}_template.md"
        custom_template_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(custom_template_path, 'w') as f:
            await f.write(config['template'])

    return {"message": "Tool configuration updated successfully"}


async def run_tool_test_job(
    job_id: str,
    tool_name: str,
    temp_path: Path
):
    """Background task to run tool test and update job"""
    try:
        get_job_queue_manager().start_job(job_id)
        get_job_queue_manager().update_progress(job_id, 0.1, "Loading tool configuration...")

        # Load current config
        models_config = await load_models_config()
        model = models_config.get('defaults', {}).get(tool_name, 'gemini/gemini-2.0-flash-exp')

        get_job_queue_manager().update_progress(job_id, 0.3, "Running analysis...")

        # Import and run the tool based on tool_name
        result = None
        if tool_name == "character_appearance_analyzer":
            from ai_tools.character_appearance_analyzer.tool import CharacterAppearanceAnalyzer
            analyzer = CharacterAppearanceAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "outfit_analyzer":
            from ai_tools.outfit_analyzer.tool import OutfitAnalyzer
            from api.database import get_session

            # Create database session for outfit analyzer to save clothing items
            async with get_session() as session:
                analyzer = OutfitAnalyzer(model=model, db_session=session, user_id=None)
                result = await analyzer.aanalyze(temp_path)
                await session.commit()  # Commit clothing item creations

            # Outfit analyzer returns dict directly
            get_job_queue_manager().update_progress(job_id, 0.9, "Finalizing...")
            get_job_queue_manager().complete_job(job_id, {
                "status": "success",
                "result": result
            })
            return
        elif tool_name == "accessories_analyzer":
            from ai_tools.accessories_analyzer.tool import AccessoriesAnalyzer
            analyzer = AccessoriesAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "art_style_analyzer":
            from ai_tools.art_style_analyzer.tool import ArtStyleAnalyzer
            analyzer = ArtStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "expression_analyzer":
            from ai_tools.expression_analyzer.tool import ExpressionAnalyzer
            analyzer = ExpressionAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "hair_color_analyzer":
            from ai_tools.hair_color_analyzer.tool import HairColorAnalyzer
            analyzer = HairColorAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "hair_style_analyzer":
            from ai_tools.hair_style_analyzer.tool import HairStyleAnalyzer
            analyzer = HairStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "makeup_analyzer":
            from ai_tools.makeup_analyzer.tool import MakeupAnalyzer
            analyzer = MakeupAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "visual_style_analyzer":
            from ai_tools.visual_style_analyzer.tool import VisualStyleAnalyzer
            analyzer = VisualStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        else:
            get_job_queue_manager().fail_job(job_id, f"Testing not yet implemented for {tool_name}")
            return

        # Convert to dict
        result_dict = result.model_dump()

        get_job_queue_manager().update_progress(job_id, 0.9, "Finalizing...")
        get_job_queue_manager().complete_job(job_id, {
            "status": "success",
            "result": result_dict
        })

        # For outfit analyzer, automatically queue preview generation for clothing items
        if tool_name == "outfit_analyzer" and isinstance(result_dict, dict):
            clothing_items = result_dict.get("clothing_items", [])
            if clothing_items:
                logger.info("Auto-generating previews for clothing items", extra={'extra_fields': {'item_count': len(clothing_items)}})

                # Import here to avoid circular dependency
                from api.routes.clothing_items import run_preview_generation_job

                for item in clothing_items:
                    item_id = item.get("item_id")
                    if item_id:
                        # Create job for this item's preview
                        preview_job_id = get_job_queue_manager().create_job(
                            job_type=JobType.GENERATE_IMAGE,
                            title=f"Preview: {item.get('item', 'Clothing Item')}",
                            description=f"Category: {item.get('category', 'unknown')}"
                        )

                        # Run preview generation in a thread to avoid blocking
                        import threading
                        thread = threading.Thread(
                            target=run_preview_generation_job,
                            args=(preview_job_id, item_id)
                        )
                        thread.daemon = True
                        thread.start()

                        print(f"   ✅ Queued preview for {item.get('item')} (job: {preview_job_id[:8]}...)")

    except Exception as e:
        get_job_queue_manager().fail_job(job_id, str(e))

    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


@router.post("/tools/{tool_name}/test")
async def test_tool(
    tool_name: str,
    image: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    async_mode: bool = Query(True, description="Run test in background and return job_id"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Test a tool with an uploaded image

    Runs the tool and returns the analysis results.

    Query Parameters:
    - async_mode: If true (default), returns job_id immediately and processes in background
    """
    tool_dir = get_tool_dir(tool_name)

    # Save uploaded image temporarily
    temp_dir = settings.base_dir / "uploads" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    import uuid
    temp_filename = f"{uuid.uuid4()}_{image.filename}"
    temp_path = temp_dir / temp_filename

    # Save file
    async with aiofiles.open(temp_path, 'wb') as f:
        content = await image.read()
        await f.write(content)

    # Async mode: Create job and return immediately
    if async_mode:
        # Determine job title
        display_name = tool_name.replace('_analyzer', '').replace('_', ' ').title()

        # Create job
        job_id = get_job_queue_manager().create_job(
            job_type=JobType.ANALYZE,
            title=f"Testing {display_name}",
            description=f"Image: {image.filename}"
        )

        # Queue background task
        background_tasks.add_task(
            run_tool_test_job,
            job_id,
            tool_name,
            temp_path
        )

        # Return job info
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Analysis queued. Use /jobs/{job_id} to check status."
        }

    # Synchronous mode: Run test and return result
    try:
        # Load current config
        models_config = await load_models_config()
        model = models_config.get('defaults', {}).get(tool_name, 'gemini/gemini-2.0-flash-exp')

        # Import and run the tool based on tool_name
        if tool_name == "character_appearance_analyzer":
            from ai_tools.character_appearance_analyzer.tool import CharacterAppearanceAnalyzer
            analyzer = CharacterAppearanceAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "outfit_analyzer":
            from ai_tools.outfit_analyzer.tool import OutfitAnalyzer
            from api.database import get_session

            # Create database session for outfit analyzer to save clothing items
            async with get_session() as session:
                analyzer = OutfitAnalyzer(model=model, db_session=session, user_id=current_user.id if current_user else None)
                result = await analyzer.aanalyze(temp_path)
                await session.commit()  # Commit clothing item creations

            # Outfit analyzer now returns dict directly (new architecture)
            return {
                "status": "success",
                "result": result
            }
        elif tool_name == "accessories_analyzer":
            from ai_tools.accessories_analyzer.tool import AccessoriesAnalyzer
            analyzer = AccessoriesAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "art_style_analyzer":
            from ai_tools.art_style_analyzer.tool import ArtStyleAnalyzer
            analyzer = ArtStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "expression_analyzer":
            from ai_tools.expression_analyzer.tool import ExpressionAnalyzer
            analyzer = ExpressionAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "hair_color_analyzer":
            from ai_tools.hair_color_analyzer.tool import HairColorAnalyzer
            analyzer = HairColorAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "hair_style_analyzer":
            from ai_tools.hair_style_analyzer.tool import HairStyleAnalyzer
            analyzer = HairStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "makeup_analyzer":
            from ai_tools.makeup_analyzer.tool import MakeupAnalyzer
            analyzer = MakeupAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        elif tool_name == "visual_style_analyzer":
            from ai_tools.visual_style_analyzer.tool import VisualStyleAnalyzer
            analyzer = VisualStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        else:
            raise HTTPException(status_code=400, detail=f"Testing not yet implemented for {tool_name}")

        # Convert to dict
        result_dict = result.model_dump()

        return {
            "status": "success",
            "result": result_dict
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

    finally:
        # Clean up temp file (only in sync mode, async mode handles its own cleanup)
        if not async_mode and temp_path.exists():
            temp_path.unlink()


@router.get("/models")
async def list_available_models(
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all available models

    Returns models organized by provider, filtered by available API keys.
    For Ollama, only returns actually downloaded models.
    """
    import os
    import httpx

    # Load models registry
    models_registry_path = settings.base_dir / "configs" / "available_models.yaml"
    async with aiofiles.open(models_registry_path, 'r') as f:
        content = await f.read()
        registry = yaml.safe_load(content)

    # Check which providers have API keys configured
    available_models = {}

    for provider, config in registry.get('providers', {}).items():
        env_var = config.get('env_var')

        # Check if API key exists
        if env_var and os.getenv(env_var):
            # Special handling for Ollama - only show downloaded models
            if provider == "ollama":
                try:
                    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{ollama_url}/api/tags", timeout=5.0)
                        if response.status_code == 200:
                            data = response.json()
                            downloaded_models = {model['name'] for model in data.get('models', [])}

                            # Filter registry models to only include downloaded ones
                            models = []
                            for model in config.get('models', []):
                                # Extract model name from id (e.g., "ollama/gpt-oss:120b" -> "gpt-oss:120b")
                                model_id = model['id']
                                if model_id.startswith('ollama/'):
                                    model_name = model_id[7:]  # Remove "ollama/" prefix
                                else:
                                    model_name = model_id

                                # Only include if downloaded
                                if model_name in downloaded_models:
                                    model_info = {
                                        "id": model['id'],
                                        "name": model['name']
                                    }

                                    if 'temperature_restrictions' in model:
                                        model_info['temperature_restrictions'] = model['temperature_restrictions']

                                    models.append(model_info)

                            if models:
                                available_models[provider] = models
                except Exception as e:
                    # If Ollama is unavailable, skip it
                    logger.warning(f"Could not fetch Ollama models: {e}")
            else:
                # For other providers, show all models from registry
                models = []
                for model in config.get('models', []):
                    model_info = {
                        "id": model['id'],
                        "name": model['name']
                    }

                    # Include temperature restrictions if present
                    if 'temperature_restrictions' in model:
                        model_info['temperature_restrictions'] = model['temperature_restrictions']

                    models.append(model_info)

                if models:  # Only include provider if they have models
                    available_models[provider] = models

    return available_models
