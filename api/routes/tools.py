"""
Unified Tools Routes

Consolidated endpoint for all AI tools (analyzers, generators, agents).
Provides a single, consistent interface with automatic preset saving.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Query, Depends
from typing import Optional
from pathlib import Path
import aiofiles
import uuid
import threading

from api.models.auth import User
from api.models.jobs import JobType
from api.dependencies.auth import get_current_active_user
from api.services.job_queue import get_job_queue_manager
from api.config import settings
from api.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


# Map tool names to preset categories for preview generation
PRESET_ANALYZERS = {
    "expression_analyzer": "expressions",
    "makeup_analyzer": "makeup",
    "accessories_analyzer": "accessories",
    "art_style_analyzer": "art_styles",
    "visual_style_analyzer": "visual_styles",
    "hair_color_analyzer": "hair_colors",
    "hair_style_analyzer": "hair_styles"
}


def run_preset_preview_generation_job(job_id: str, category: str, preset_id: str, preset_name: str):
    """Background task to generate preset preview image"""
    try:
        get_job_queue_manager().start_job(job_id)
        get_job_queue_manager().update_progress(job_id, 0.2, "Loading preset...")

        # Import here to avoid circular imports
        from ai_tools.shared.visualizer import PresetVisualizer
        from api.services.visualization_config_service_db import VisualizationConfigServiceDB
        from api.database import get_session

        # Load preset data
        preset_path = settings.presets_dir / category / f"{preset_id}.json"
        if not preset_path.exists():
            get_job_queue_manager().fail_job(job_id, f"Preset not found: {preset_id}")
            return

        import json
        with open(preset_path, 'r') as f:
            preset_data = json.load(f)

        get_job_queue_manager().update_progress(job_id, 0.3, "Loading visualization config...")

        # Load visualization config for this entity type
        # Convert category to entity_type (e.g., "expressions" -> "expression")
        entity_type = category.rstrip('s') if category.endswith('s') else category

        # Get default visualization config for this entity type from database
        import asyncio
        async def get_viz_config():
            async with get_session() as session:
                viz_service = VisualizationConfigServiceDB(session, user_id=None)
                return await viz_service.get_default_config(entity_type)

        viz_config = asyncio.run(get_viz_config())

        if not viz_config:
            logger.warning(f"No visualization config found for {entity_type}, using defaults")
            viz_config = None

        get_job_queue_manager().update_progress(job_id, 0.4, "Generating preview image...")

        # Generate preview using visualizer with config
        visualizer = PresetVisualizer()
        output_path = settings.presets_dir / category / f"{preset_id}_preview.png"

        visualizer.create_preset_preview(
            preset_data=preset_data,
            output_path=str(output_path),
            category=category,
            viz_config=viz_config  # Pass the visualization config
        )

        logger.info(f"Preview generated, creating optimized versions for {category}/{preset_id}")
        get_job_queue_manager().update_progress(job_id, 0.7, "Creating optimized preview sizes...")

        # Create optimized versions (small, medium) for faster loading
        from api.services.image_optimizer import ImageOptimizer

        optimized_paths = {}

        try:
            optimizer = ImageOptimizer()

            # Clean up old cached versions
            optimizer.cleanup_old_versions(category, preset_id)

            # Generate optimized versions
            optimized_paths = optimizer.optimize_preview(
                str(output_path),
                category,
                preset_id
            )
            logger.info(f"Created optimized preview versions for {category}/{preset_id}")
        except Exception as e:
            logger.warning(f"Failed to create optimized previews for {category}/{preset_id}: {e}")
            # Non-fatal - continue with just the full-size preview
            optimized_paths = {'full': f"/presets/{category}/{preset_id}_preview.png"}

        get_job_queue_manager().update_progress(job_id, 0.9, "Finalizing...")
        get_job_queue_manager().complete_job(job_id, {
            "status": "success",
            "entity_type": category,  # For EntityPreviewImage component detection
            "entity_id": preset_id,   # For EntityPreviewImage component detection
            "preview_path": str(output_path),  # Backward compatibility
            "preview_image_path": optimized_paths.get('full', f"/presets/{category}/{preset_id}_preview.png"),
            "preview_image_small": optimized_paths.get('small'),
            "preview_image_medium": optimized_paths.get('medium'),
            "preset_id": preset_id
        })

        logger.info(f"Generated preview for {category}/{preset_id}", extra={'extra_fields': {
            'category': category,
            'preset_id': preset_id,
            'output_path': str(output_path)
        }})

    except Exception as e:
        logger.error(f"Preview generation failed: {e}", exc_info=e)
        get_job_queue_manager().fail_job(job_id, str(e))


async def run_analyzer_job(
    job_id: str,
    tool_name: str,
    temp_path: Path,
    user_id: Optional[int] = None
):
    """Background task to run analyzer and update job"""
    try:
        get_job_queue_manager().start_job(job_id)
        get_job_queue_manager().update_progress(job_id, 0.1, "Loading configuration...")

        # Load model config
        from api.routes.tool_configs import load_models_config
        models_config = await load_models_config()
        model = models_config.get('defaults', {}).get(tool_name, 'gemini/gemini-2.0-flash-exp')

        get_job_queue_manager().update_progress(job_id, 0.3, "Analyzing...")

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
                analyzer = OutfitAnalyzer(model=model, db_session=session, user_id=user_id)
                result = await analyzer.aanalyze(temp_path)
                await session.commit()

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
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "art_style_analyzer":
            from ai_tools.art_style_analyzer.tool import ArtStyleAnalyzer
            analyzer = ArtStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "expression_analyzer":
            from ai_tools.expression_analyzer.tool import ExpressionAnalyzer
            analyzer = ExpressionAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "hair_color_analyzer":
            from ai_tools.hair_color_analyzer.tool import HairColorAnalyzer
            analyzer = HairColorAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "hair_style_analyzer":
            from ai_tools.hair_style_analyzer.tool import HairStyleAnalyzer
            analyzer = HairStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "makeup_analyzer":
            from ai_tools.makeup_analyzer.tool import MakeupAnalyzer
            analyzer = MakeupAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "visual_style_analyzer":
            from ai_tools.visual_style_analyzer.tool import VisualStyleAnalyzer
            analyzer = VisualStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        else:
            get_job_queue_manager().fail_job(job_id, f"Unknown analyzer: {tool_name}")
            return

        # Convert to dict
        result_dict = result.model_dump()

        get_job_queue_manager().update_progress(job_id, 0.9, "Finalizing...")
        get_job_queue_manager().complete_job(job_id, {
            "status": "success",
            "result": result_dict
        })

        # Auto-generate preview for preset-based analyzers
        if tool_name in PRESET_ANALYZERS and isinstance(result_dict, dict):
            preset_id = result_dict.get("preset_id")
            name = result_dict.get("name") or result_dict.get("title", "Preset")
            category = PRESET_ANALYZERS[tool_name]

            if preset_id:
                logger.info(f"Auto-generating preview for {category}/{preset_id}", extra={'extra_fields': {
                    'tool': tool_name,
                    'category': category,
                    'preset_id': preset_id
                }})

                preview_job_id = get_job_queue_manager().create_job(
                    job_type=JobType.GENERATE_IMAGE,
                    title=f"Preview: {name}",
                    description=f"Category: {category}"
                )

                thread = threading.Thread(
                    target=run_preset_preview_generation_job,
                    args=(preview_job_id, category, preset_id, name)
                )
                thread.daemon = True
                thread.start()

        # For outfit analyzer, automatically queue preview generation for clothing items
        if tool_name == "outfit_analyzer" and isinstance(result_dict, dict):
            clothing_items = result_dict.get("clothing_items", [])
            if clothing_items:
                logger.info("Auto-generating previews for clothing items", extra={'extra_fields': {'item_count': len(clothing_items)}})

                from api.routes.clothing_items import run_preview_generation_job
                import threading

                for item in clothing_items:
                    item_id = item.get("item_id")
                    if item_id:
                        preview_job_id = get_job_queue_manager().create_job(
                            job_type=JobType.GENERATE_IMAGE,
                            title=f"Preview: {item.get('item', 'Clothing Item')}",
                            description=f"Category: {item.get('category', 'unknown')}"
                        )

                        thread = threading.Thread(
                            target=run_preview_generation_job,
                            args=(preview_job_id, item_id)
                        )
                        thread.daemon = True
                        thread.start()

    except Exception as e:
        logger.error(f"Analyzer job failed: {e}", exc_info=e)
        get_job_queue_manager().fail_job(job_id, str(e))

    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


@router.post("/analyzers/{analyzer_name}")
async def run_analyzer(
    analyzer_name: str,
    image: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    async_mode: bool = Query(True, description="Run analysis in background and return job_id"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Run an analyzer tool

    Available analyzers:
    - outfit: Analyze outfit details and save clothing items
    - expression: Analyze facial expression
    - makeup: Analyze makeup
    - accessories: Analyze accessories
    - art-style: Analyze artistic style
    - visual-style: Analyze photograph composition
    - hair-style: Analyze hair structure
    - hair-color: Analyze hair color
    - character-appearance: Analyze character physical appearance

    All analyzers automatically save results as presets.

    Query Parameters:
    - async_mode: If true (default), returns job_id immediately and processes in background
    """
    # Convert kebab-case to snake_case for tool lookup
    tool_name = analyzer_name.replace('-', '_') + '_analyzer'

    # Save uploaded image temporarily
    temp_dir = settings.base_dir / "uploads" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    temp_filename = f"{uuid.uuid4()}_{image.filename}"
    temp_path = temp_dir / temp_filename

    async with aiofiles.open(temp_path, 'wb') as f:
        content = await image.read()
        await f.write(content)

    # Async mode: Create job and return immediately
    if async_mode:
        display_name = analyzer_name.replace('-', ' ').title()

        job_id = get_job_queue_manager().create_job(
            job_type=JobType.ANALYZE,
            title=f"{display_name} Analysis",
            description=f"Image: {image.filename}"
        )

        background_tasks.add_task(
            run_analyzer_job,
            job_id,
            tool_name,
            temp_path,
            current_user.id if current_user else None
        )

        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Analysis queued. Use /jobs/{job_id} to check status."
        }

    # Synchronous mode: Run immediately and return result
    try:
        from api.routes.tool_configs import load_models_config
        models_config = await load_models_config()
        model = models_config.get('defaults', {}).get(tool_name, 'gemini/gemini-2.0-flash-exp')

        # Import and run the tool
        if tool_name == "outfit_analyzer":
            from ai_tools.outfit_analyzer.tool import OutfitAnalyzer
            from api.database import get_session

            async with get_session() as session:
                analyzer = OutfitAnalyzer(model=model, db_session=session, user_id=current_user.id if current_user else None)
                result = await analyzer.aanalyze(temp_path)
                await session.commit()

            return {"status": "success", "result": result}
        elif tool_name == "accessories_analyzer":
            from ai_tools.accessories_analyzer.tool import AccessoriesAnalyzer
            analyzer = AccessoriesAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "art_style_analyzer":
            from ai_tools.art_style_analyzer.tool import ArtStyleAnalyzer
            analyzer = ArtStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "expression_analyzer":
            from ai_tools.expression_analyzer.tool import ExpressionAnalyzer
            analyzer = ExpressionAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "hair_color_analyzer":
            from ai_tools.hair_color_analyzer.tool import HairColorAnalyzer
            analyzer = HairColorAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "hair_style_analyzer":
            from ai_tools.hair_style_analyzer.tool import HairStyleAnalyzer
            analyzer = HairStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "makeup_analyzer":
            from ai_tools.makeup_analyzer.tool import MakeupAnalyzer
            analyzer = MakeupAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "visual_style_analyzer":
            from ai_tools.visual_style_analyzer.tool import VisualStyleAnalyzer
            analyzer = VisualStyleAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path, save_as_preset=True)
        elif tool_name == "character_appearance_analyzer":
            from ai_tools.character_appearance_analyzer.tool import CharacterAppearanceAnalyzer
            analyzer = CharacterAppearanceAnalyzer(model=model)
            result = await analyzer.aanalyze(temp_path)
        else:
            raise HTTPException(status_code=404, detail=f"Analyzer not found: {analyzer_name}")

        result_dict = result.model_dump()

        # Auto-generate preview for preset-based analyzers (sync mode)
        if tool_name in PRESET_ANALYZERS and isinstance(result_dict, dict):
            preset_id = result_dict.get("preset_id")
            name = result_dict.get("name") or result_dict.get("title", "Preset")
            category = PRESET_ANALYZERS[tool_name]

            if preset_id:
                logger.info(f"Auto-generating preview for {category}/{preset_id}", extra={'extra_fields': {
                    'tool': tool_name,
                    'category': category,
                    'preset_id': preset_id
                }})

                preview_job_id = get_job_queue_manager().create_job(
                    job_type=JobType.GENERATE_IMAGE,
                    title=f"Preview: {name}",
                    description=f"Category: {category}"
                )

                thread = threading.Thread(
                    target=run_preset_preview_generation_job,
                    args=(preview_job_id, category, preset_id, name)
                )
                thread.daemon = True
                thread.start()

        return {"status": "success", "result": result_dict}

    except Exception as e:
        logger.error(f"Analyzer execution failed: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    finally:
        # Clean up temp file (only in sync mode, async handles its own cleanup)
        if not async_mode and temp_path.exists():
            temp_path.unlink()
