"""
RQ Job Functions

Background job functions executed by RQ workers.
These wrap async functions to run in RQ's synchronous context.
"""

import asyncio
from pathlib import Path
from typing import Optional

from api.logging_config import get_logger

logger = get_logger(__name__)


def run_async_job(async_func, *args, **kwargs):
    """
    Helper to run async functions in RQ workers

    RQ workers are synchronous, so we need to create an event loop
    to run async functions.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(async_func(*args, **kwargs))
    finally:
        loop.close()


# ========== Clothing Item Jobs ==========

def preview_generation_job(job_id: str, item_id: str):
    """
    Generate preview image for a clothing item

    This is the RQ-compatible wrapper for the async preview generation logic.

    Args:
        job_id: Job tracking ID (from JobQueueManager)
        item_id: Clothing item UUID
    """
    import sys
    from api.services.job_queue import get_job_queue_manager
    from api.database import get_session
    from api.services.clothing_items_service_db import ClothingItemServiceDB

    print(f"[WORKER] preview_generation_job called: job_id={job_id}, item_id={item_id}", file=sys.stderr, flush=True)

    async def _async_preview_generation():
        try:
            print(f"[WORKER] Getting job manager...", file=sys.stderr, flush=True)
            job_manager = get_job_queue_manager()
            print(f"[WORKER] Starting job {job_id}...", file=sys.stderr, flush=True)
            job_manager.start_job(job_id)
            print(f"[WORKER] Job started, updating progress...", file=sys.stderr, flush=True)
            job_manager.update_progress(job_id, 0.1, "Loading clothing item...")

            async with get_session() as session:
                service = ClothingItemServiceDB(session, user_id=None)

                print(f"[WORKER] Updating progress to 0.3...", file=sys.stderr, flush=True)
                job_manager.update_progress(job_id, 0.3, "Generating preview image...")

                print(f"[WORKER] Calling generate_preview for item {item_id}...", file=sys.stderr, flush=True)
                # Generate preview
                item = await service.generate_preview(item_id)

                if not item:
                    print(f"[WORKER] Item not found, failing job...", file=sys.stderr, flush=True)
                    job_manager.fail_job(job_id, f"Clothing item {item_id} not found")
                    return

                print(f"[WORKER] Preview generated, finalizing...", file=sys.stderr, flush=True)
                job_manager.update_progress(job_id, 0.9, "Finalizing...")

                # Complete job with item data
                result = {
                    'item_id': item['item_id'],
                    'category': item['category'],
                    'item': item['item'],
                    'fabric': item['fabric'],
                    'color': item['color'],
                    'details': item['details'],
                    'source_image': item.get('source_image'),
                    'preview_image_path': item.get('preview_image_path'),
                    'created_at': item.get('created_at', '')
                }

                print(f"[WORKER] Completing job {job_id}...", file=sys.stderr, flush=True)
                job_manager.complete_job(job_id, result)
                print(f"[WORKER] Job {job_id} completed successfully!", file=sys.stderr, flush=True)

        except Exception as e:
            print(f"[WORKER] ERROR in job {job_id}: {e}", file=sys.stderr, flush=True)
            logger.error(f"Preview generation job failed: {e}", exc_info=True)
            get_job_queue_manager().fail_job(job_id, str(e))

    print(f"[WORKER] Calling run_async_job...", file=sys.stderr, flush=True)
    run_async_job(_async_preview_generation)
    print(f"[WORKER] run_async_job returned", file=sys.stderr, flush=True)


def test_image_generation_job(job_id: str, item_id: str, character_id: str, visual_style_id: str):
    """
    Generate test image of character wearing clothing item

    Args:
        job_id: Job tracking ID
        item_id: Clothing item UUID
        character_id: Character UUID
        visual_style_id: Visual style UUID
    """
    from api.services.job_queue import get_job_queue_manager
    from api.database import get_session
    from api.services.clothing_items_service_db import ClothingItemServiceDB
    from api.services.character_service_db import CharacterServiceDB
    from ai_tools.modular_image_generator.tool import ModularImageGenerator
    from ai_capabilities.specs import OutfitSpec, ClothingItem

    async def _async_test_generation():
        try:
            job_manager = get_job_queue_manager()
            job_manager.start_job(job_id)
            job_manager.update_progress(job_id, 0.1, "Loading clothing item and character...")

            async with get_session() as session:
                # Load clothing item
                service = ClothingItemServiceDB(session, user_id=None)
                item = await service.get_clothing_item(item_id)

                if not item:
                    job_manager.fail_job(job_id, f"Clothing item {item_id} not found")
                    return

                # Load character by ID
                character_service = CharacterServiceDB(session, user_id=None)
                character = await character_service.get_character(character_id)

                if not character:
                    job_manager.fail_job(job_id, f"Character '{character_id}' not found")
                    return

                # Get character reference image
                reference_image_path = character.get('reference_image_path')
                if not reference_image_path:
                    job_manager.fail_job(job_id, f"Character {character_id} has no reference image")
                    return

                subject_path = Path(reference_image_path)
                if not subject_path.exists():
                    job_manager.fail_job(job_id, f"Character reference image not found: {reference_image_path}")
                    return

                job_manager.update_progress(job_id, 0.3, "Generating test image...")

                # Generate image with modular generator
                generator = ModularImageGenerator()

                # Create a temporary outfit spec with morphsuit + clothing item
                morphsuit_outfit = OutfitSpec(
                    suggested_name=f"Test: {item['item']}",
                    style_genre="Contemporary",
                    formality="Casual",
                    aesthetic=f"Black morphsuit showcasing {item['item']}",
                    clothing_items=[
                        ClothingItem(
                            item="black morphsuit",
                            fabric="stretch jersey",
                            color="solid black",
                            details="Full body coverage from neck to ankles, completely black and featureless, serves as neutral base"
                        ),
                        ClothingItem(
                            item=item['item'],
                            fabric=item['fabric'],
                            color=item['color'],
                            details=item['details']
                        )
                    ],
                    color_palette=["black", item['color']],
                    suggested_description=f"Black morphsuit base with {item['item']} ({item['color']} {item['fabric']}) as the focal point"
                )

                # Generate using character reference + outfit + visual style
                result = await generator.agenerate(
                    subject_image=str(subject_path),
                    outfit=morphsuit_outfit,
                    visual_style=visual_style_id,  # Pass UUID
                    output_dir="output/test_generations/clothing_items"
                )

                job_manager.update_progress(job_id, 0.9, "Finalizing...")

                # Complete job with result
                job_manager.complete_job(job_id, {
                    'file_path': str(result.file_path),
                    'item_id': item_id,
                    'character_id': character_id,
                    'visual_style_id': visual_style_id
                })

        except Exception as e:
            logger.error(f"Test image generation job failed: {e}", exc_info=True)
            get_job_queue_manager().fail_job(job_id, str(e))

    run_async_job(_async_test_generation)


# ========== Tool Testing Jobs ==========

def tool_test_job(job_id: str, tool_name: str, temp_path_str: str, user_id: Optional[int] = None):
    """
    Run a tool test with an uploaded image

    Args:
        job_id: Job tracking ID
        tool_name: Name of the tool to test
        temp_path_str: Path to temporary uploaded image
        user_id: Optional user ID (for outfit analyzer to save items)
    """
    from api.services.job_queue import get_job_queue_manager
    from api.models.jobs import JobType
    from pathlib import Path

    async def _async_tool_test():
        temp_path = Path(temp_path_str)

        try:
            job_manager = get_job_queue_manager()
            job_manager.start_job(job_id)
            job_manager.update_progress(job_id, 0.1, "Loading tool configuration...")

            # Load current config
            from api.services.tool_configs import load_models_config
            models_config = await load_models_config()
            model = models_config.get('defaults', {}).get(tool_name, 'gemini/gemini-2.0-flash-exp')

            job_manager.update_progress(job_id, 0.3, "Running analysis...")

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
                job_manager.update_progress(job_id, 0.9, "Finalizing...")
                job_manager.complete_job(job_id, {
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
                job_manager.fail_job(job_id, f"Testing not yet implemented for {tool_name}")
                return

            # Convert to dict
            result_dict = result.model_dump()

            job_manager.update_progress(job_id, 0.9, "Finalizing...")
            job_manager.complete_job(job_id, {
                "status": "success",
                "result": result_dict
            })

            # Auto-generate preview for preset-based analyzers
            from api.routes.tools import PRESET_ANALYZERS
            from api.services.rq_worker import get_rq_service
            if tool_name in PRESET_ANALYZERS and isinstance(result_dict, dict):
                preset_id = result_dict.get("preset_id")
                name = result_dict.get("name") or result_dict.get("title", "Preset")
                category = PRESET_ANALYZERS[tool_name]

                if preset_id:
                    logger.info(f"Auto-generating preview for {category}/{preset_id}")

                    preview_job_id = get_job_queue_manager().create_job(
                        job_type=JobType.GENERATE_IMAGE,
                        title=f"Preview: {name}",
                        description=f"Category: {category}"
                    )

                    # Enqueue preview generation via RQ
                    get_rq_service().enqueue(
                        preset_preview_generation_job,
                        preview_job_id,
                        category,
                        preset_id,
                        name,
                        priority='low'
                    )

            # For outfit analyzer, auto-generate previews for clothing items
            if tool_name == "outfit_analyzer" and isinstance(result_dict, dict):
                clothing_items = result_dict.get("clothing_items", [])
                if clothing_items:
                    logger.info(f"Auto-generating previews for {len(clothing_items)} clothing items")

                    for item in clothing_items:
                        item_id = item.get("item_id")
                        if item_id:
                            # Create job for this item's preview
                            preview_job_id = get_job_queue_manager().create_job(
                                job_type=JobType.GENERATE_IMAGE,
                                title=f"Preview: {item.get('item', 'Clothing Item')}",
                                description=f"Category: {item.get('category', 'unknown')}"
                            )

                            # Enqueue via RQ
                            get_rq_service().enqueue(
                                preview_generation_job,
                                preview_job_id,
                                item_id,
                                priority='low'
                            )

        except Exception as e:
            logger.error(f"Tool test job failed: {e}", exc_info=True)
            get_job_queue_manager().fail_job(job_id, str(e))

        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()

    run_async_job(_async_tool_test)


def preset_preview_generation_job(job_id: str, category: str, preset_id: str, name: str):
    """
    Generate preview image for a preset

    Args:
        job_id: Job tracking ID
        category: Preset category
        preset_id: Preset UUID
        name: Preset display name
    """
    # Import here to avoid circular dependencies
    from api.routes.tools import run_preset_preview_generation_job

    # This function is already sync, so we can call it directly
    run_preset_preview_generation_job(job_id, category, preset_id, name)
