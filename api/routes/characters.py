"""
Character Routes

Endpoints for managing character entities.
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, BackgroundTasks, Query, Request
from fastapi.responses import FileResponse
from typing import Optional, List
import base64
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.requests import CharacterCreate, CharacterUpdate, CharacterFromSubject
from api.models.responses import CharacterInfo, CharacterListResponse, CharacterFromSubjectResponse
from api.services.character_service_db import CharacterServiceDB
from api.database import get_db
from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from api.config import settings
from api.services.job_queue import get_job_queue_manager
from api.models.jobs import JobType
from ai_tools.character_appearance_analyzer.tool import CharacterAppearanceAnalyzer
from api.logging_config import get_logger
from api.middleware.cache import cached, invalidates_cache

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=CharacterListResponse)
@cached(cache_type="list", include_user=True)
async def list_characters(
    request: Request,
    limit: Optional[int] = Query(None, description="Maximum number of characters to return"),
    offset: int = Query(0, description="Number of characters to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all characters

    Returns a list of character entities with their metadata.
    Supports pagination via limit/offset parameters.

    **Cached**: 60 seconds (user-specific)
    """
    service = CharacterServiceDB(db, user_id=current_user.id if current_user else None)

    # Get both characters and total count
    characters = await service.list_characters(limit=limit, offset=offset)
    total_count = await service.count_characters()

    character_infos = []
    for char in characters:
        # Build reference image URL if exists
        ref_image_url = None
        if char.get('reference_image_path'):
            ref_image_url = f"/api/characters/{char['character_id']}/image"

        character_infos.append(CharacterInfo(
            character_id=char['character_id'],
            name=char['name'],
            visual_description=char.get('visual_description'),
            physical_description=char.get('physical_description'),
            personality=char.get('personality'),
            reference_image_url=ref_image_url,
            tags=char.get('tags', []),
            created_at=char.get('created_at'),
            archived=char.get('archived', False),
            archived_at=char.get('archived_at'),
            metadata=char.get('metadata', {}),
            age=char.get('age'),
            skin_tone=char.get('skin_tone'),
            face_description=char.get('face_description'),
            hair_description=char.get('hair_description'),
            body_description=char.get('body_description')
        ))

    return CharacterListResponse(
        count=total_count,
        characters=character_infos
    )


@router.post("/multipart", response_model=CharacterInfo)
@invalidates_cache(entity_types=["characters"])
async def create_character_multipart(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    personality: str = Form(""),
    tags: str = Form("[]"),
    reference_image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new character with multipart form data

    Accepts form data including a reference image file.
    Physical appearance is automatically analyzed from the image in the background.
    Returns immediately without waiting for analysis to complete.

    **Cache Invalidation**: Clears all character list caches
    """
    service = CharacterServiceDB(db, user_id=current_user.id if current_user else None)

    # Parse tags from JSON string
    tag_list = json.loads(tags) if tags else []

    # Create character
    character_data = await service.create_character(
        name=name,
        personality=personality if personality else None,
        tags=tag_list
    )

    character_id = character_data['character_id']

    # Handle reference image if provided
    if reference_image:
        # Save reference image
        image_data = await reference_image.read()
        reference_image_path = service.save_reference_image(character_id, image_data)

        # Update character with image path
        character_data = await service.update_character(
            character_id,
            reference_image_path=reference_image_path
        )

        # Queue appearance analysis in background (don't block response)
        async def analyze_appearance():
            """Background task to analyze character appearance"""
            try:
                logger.info(f"Analyzing character appearance for {name}", extra={'extra_fields': {
                    'character_id': character_id,
                    'character_name': name
                }})
                from api.database import get_session
                async with get_session() as session:
                    service = CharacterServiceDB(session, user_id=None)  # TODO: Use current_user.id when auth is migrated to PostgreSQL
                    analyzer = CharacterAppearanceAnalyzer()
                    appearance_spec = await analyzer.aanalyze(Path(reference_image_path))

                    # Save all appearance fields to character
                    await service.update_character(
                        character_id,
                        physical_description=appearance_spec.overall_description,
                        age=appearance_spec.age,
                        skin_tone=appearance_spec.skin_tone,
                        face_description=appearance_spec.face_description,
                        hair_description=appearance_spec.hair_description,
                        body_description=appearance_spec.body_description
                    )
                logger.info(f"Physical description analyzed and saved for {name}", extra={'extra_fields': {
                    'character_id': character_id,
                    'character_name': name
                }})
            except Exception as e:
                logger.warning(f"Appearance analysis failed for {name}: {e}", extra={'extra_fields': {
                    'character_id': character_id,
                    'character_name': name,
                    'error': str(e)
                }})
                # Non-critical failure - character already created

        background_tasks.add_task(analyze_appearance)

    # Build reference image URL
    ref_image_url = None
    if character_data.get('reference_image_path'):
        ref_image_url = f"/api/characters/{character_id}/image"

    return CharacterInfo(
        character_id=character_data['character_id'],
        name=character_data['name'],
        visual_description=character_data.get('visual_description'),
        physical_description=character_data.get('physical_description'),
        personality=character_data.get('personality'),
        reference_image_url=ref_image_url,
        tags=character_data.get('tags', []),
        created_at=character_data.get('created_at'),
        metadata=character_data.get('metadata', {}),
        age=character_data.get('age'),
        skin_tone=character_data.get('skin_tone'),
        face_description=character_data.get('face_description'),
        hair_description=character_data.get('hair_description'),
        body_description=character_data.get('body_description')
    )


@router.post("/", response_model=CharacterInfo)
@invalidates_cache(entity_types=["characters"])
async def create_character(
    request: CharacterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new character (JSON API)

    Creates a character entity with name, visual description, personality, etc.
    Optionally accepts a reference image in base64 format.

    Note: For file uploads, use the /multipart endpoint instead.

    **Cache Invalidation**: Clears all character list caches
    """
    service = CharacterServiceDB(db, user_id=current_user.id if current_user else None)

    # Handle reference image if provided
    reference_image_path = None
    if request.reference_image:
        # For now, we'll handle image upload separately
        # This endpoint accepts image data in base64 format
        if request.reference_image.image_data:
            # Decode base64 image
            image_data = base64.b64decode(request.reference_image.image_data.split(',')[-1])

            # Create character first to get ID
            character_data = await service.create_character(
                name=request.name,
                visual_description=request.visual_description,
                personality=request.personality,
                tags=request.tags
            )

            # Save reference image
            reference_image_path = service.save_reference_image(
                character_data['character_id'],
                image_data
            )

            # Update character with image path
            character_data = await service.update_character(
                character_data['character_id'],
                reference_image_path=reference_image_path
            )
        elif request.reference_image.image_url:
            # TODO: Download image from URL
            character_data = await service.create_character(
                name=request.name,
                visual_description=request.visual_description,
                personality=request.personality,
                tags=request.tags
            )
    else:
        character_data = await service.create_character(
            name=request.name,
            visual_description=request.visual_description,
            personality=request.personality,
            tags=request.tags
        )

    # Build reference image URL
    ref_image_url = None
    if character_data.get('reference_image_path'):
        ref_image_url = f"/api/characters/{character_data['character_id']}/image"

    return CharacterInfo(
        character_id=character_data['character_id'],
        name=character_data['name'],
        visual_description=character_data.get('visual_description'),
        physical_description=character_data.get('physical_description'),
        personality=character_data.get('personality'),
        reference_image_url=ref_image_url,
        tags=character_data.get('tags', []),
        created_at=character_data.get('created_at'),
        metadata=character_data.get('metadata', {}),
        age=character_data.get('age'),
        skin_tone=character_data.get('skin_tone'),
        face_description=character_data.get('face_description'),
        hair_description=character_data.get('hair_description'),
        body_description=character_data.get('body_description')
    )


@router.get("/{character_id}/image")
async def get_character_image(
    character_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get character reference image

    Returns the reference image file for the character.
    """
    service = CharacterServiceDB(db, user_id=None)
    image_path = service.get_reference_image_path(character_id)

    if not image_path:
        raise HTTPException(status_code=404, detail=f"No reference image for character {character_id}")

    return FileResponse(image_path, media_type="image/png")


@router.post("/{character_id}/image", response_model=CharacterInfo)
@invalidates_cache(entity_types=["characters"])
async def upload_character_image(
    character_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Upload reference image for a character

    Accepts an image file upload and sets it as the character's reference image.
    Automatically analyzes the image to extract physical appearance.

    **Cache Invalidation**: Clears all character caches
    """
    service = CharacterServiceDB(db, user_id=current_user.id if current_user else None)

    # Verify character exists
    character_data = await service.get_character(character_id)
    if not character_data:
        raise HTTPException(status_code=404, detail=f"Character {character_id} not found")

    # Read and save image
    image_data = await file.read()
    reference_image_path = service.save_reference_image(character_id, image_data)

    # Update character with image path
    character_data = await service.update_character(
        character_id,
        reference_image_path=reference_image_path
    )

    # Analyze appearance from image (only if physical_description not already set)
    if not character_data.get('physical_description'):
        try:
            logger.info(f"Analyzing character appearance for {character_data['name']}", extra={'extra_fields': {
                'character_id': character_id,
                'character_name': character_data['name']
            }})
            analyzer = CharacterAppearanceAnalyzer()
            appearance_spec = await analyzer.aanalyze(Path(reference_image_path))

            # Save all appearance fields to character
            character_data = await service.update_character(
                character_id,
                physical_description=appearance_spec.overall_description,
                age=appearance_spec.age,
                skin_tone=appearance_spec.skin_tone,
                face_description=appearance_spec.face_description,
                hair_description=appearance_spec.hair_description,
                body_description=appearance_spec.body_description
            )
            logger.info(f"Physical description analyzed and saved", extra={'extra_fields': {
                'character_id': character_id
            }})
        except Exception as e:
            logger.warning(f"Appearance analysis failed: {e}", extra={'extra_fields': {
                'character_id': character_id,
                'error': str(e)
            }})
            # Continue without analysis - not critical

    # Build reference image URL
    ref_image_url = f"/api/characters/{character_id}/image"

    return CharacterInfo(
        character_id=character_data['character_id'],
        name=character_data['name'],
        visual_description=character_data.get('visual_description'),
        physical_description=character_data.get('physical_description'),
        personality=character_data.get('personality'),
        reference_image_url=ref_image_url,
        tags=character_data.get('tags', []),
        created_at=character_data.get('created_at'),
        metadata=character_data.get('metadata', {}),
        age=character_data.get('age'),
        skin_tone=character_data.get('skin_tone'),
        face_description=character_data.get('face_description'),
        hair_description=character_data.get('hair_description'),
        body_description=character_data.get('body_description')
    )


@router.get("/{character_id}", response_model=CharacterInfo)
@cached(cache_type="detail", include_user=True)
async def get_character(
    request: Request,
    character_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a character by ID

    Returns full character data including visual description, personality, etc.

    **Cached**: 5 minutes (user-specific)
    """
    service = CharacterServiceDB(db, user_id=current_user.id if current_user else None)
    character_data = await service.get_character(character_id)

    if not character_data:
        raise HTTPException(status_code=404, detail=f"Character {character_id} not found")

    # Build reference image URL
    ref_image_url = None
    if character_data.get('reference_image_path'):
        ref_image_url = f"/api/characters/{character_id}/image"

    return CharacterInfo(
        character_id=character_data['character_id'],
        name=character_data['name'],
        visual_description=character_data.get('visual_description'),
        physical_description=character_data.get('physical_description'),
        personality=character_data.get('personality'),
        reference_image_url=ref_image_url,
        tags=character_data.get('tags', []),
        created_at=character_data.get('created_at'),
        metadata=character_data.get('metadata', {}),
        age=character_data.get('age'),
        skin_tone=character_data.get('skin_tone'),
        face_description=character_data.get('face_description'),
        hair_description=character_data.get('hair_description'),
        body_description=character_data.get('body_description')
    )


@router.put("/{character_id}", response_model=CharacterInfo)
@invalidates_cache(entity_types=["characters"])
async def update_character(
    character_id: str,
    request: CharacterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update a character

    Updates character fields. Only provided fields will be updated.

    **Cache Invalidation**: Clears all character caches
    """
    service = CharacterServiceDB(db, user_id=current_user.id if current_user else None)

    # Handle reference image update if provided
    reference_image_path = None
    if request.reference_image:
        if request.reference_image.image_data:
            # Decode and save base64 image
            image_data = base64.b64decode(request.reference_image.image_data.split(',')[-1])
            reference_image_path = service.save_reference_image(character_id, image_data)
        elif request.reference_image.image_url:
            # TODO: Download image from URL
            pass

    character_data = await service.update_character(
        character_id=character_id,
        name=request.name,
        visual_description=request.visual_description,
        personality=request.personality,
        reference_image_path=reference_image_path,
        tags=request.tags
    )

    if not character_data:
        raise HTTPException(status_code=404, detail=f"Character {character_id} not found")

    # Build reference image URL
    ref_image_url = None
    if character_data.get('reference_image_path'):
        ref_image_url = f"/api/characters/{character_id}/image"

    return CharacterInfo(
        character_id=character_data['character_id'],
        name=character_data['name'],
        visual_description=character_data.get('visual_description'),
        physical_description=character_data.get('physical_description'),
        personality=character_data.get('personality'),
        reference_image_url=ref_image_url,
        tags=character_data.get('tags', []),
        created_at=character_data.get('created_at'),
        metadata=character_data.get('metadata', {}),
        age=character_data.get('age'),
        skin_tone=character_data.get('skin_tone'),
        face_description=character_data.get('face_description'),
        hair_description=character_data.get('hair_description'),
        body_description=character_data.get('body_description')
    )


@router.delete("/{character_id}")
@invalidates_cache(entity_types=["characters"])
async def delete_character(
    character_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Archive a character (soft delete)

    Archives the character instead of permanently deleting it.
    Archived characters are hidden from default listings but can be restored.

    **Cache Invalidation**: Clears all character caches
    """
    service = CharacterServiceDB(db, user_id=current_user.id if current_user else None)
    success = await service.delete_character(character_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Character {character_id} not found")

    return {"message": f"Character {character_id} archived successfully"}


@router.post("/{character_id}/archive")
@invalidates_cache(entity_types=["characters"])
async def archive_character(
    character_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Archive a character

    Hides the character from default listings. Archived characters can be restored later.

    **Cache Invalidation**: Clears all character caches
    """
    service = CharacterServiceDB(db, user_id=current_user.id if current_user else None)
    success = await service.archive_character(character_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Character {character_id} not found")

    return {"message": f"Character {character_id} archived successfully", "archived": True}


@router.post("/{character_id}/unarchive")
@invalidates_cache(entity_types=["characters"])
async def unarchive_character(
    character_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Unarchive a character

    Restores an archived character to active status.

    **Cache Invalidation**: Clears all character caches
    """
    service = CharacterServiceDB(db, user_id=current_user.id if current_user else None)
    success = await service.unarchive_character(character_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Character {character_id} not found")

    return {"message": f"Character {character_id} restored successfully", "archived": False}


@router.post("/{character_id}/re-analyze-appearance", response_model=CharacterInfo)
async def re_analyze_character_appearance(
    character_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Re-analyze appearance for a specific character

    Forces re-analysis of the character's reference image, updating all appearance fields.
    Returns updated character info immediately.
    """
    service = CharacterServiceDB(db, user_id=current_user.id if current_user else None)

    # Get character
    character_data = await service.get_character(character_id)
    if not character_data:
        raise HTTPException(status_code=404, detail=f"Character {character_id} not found")

    # Check for reference image
    if not character_data.get('reference_image_path'):
        raise HTTPException(status_code=400, detail=f"Character {character_id} has no reference image")

    try:
        logger.info(f"Re-analyzing character appearance for {character_data['name']}", extra={'extra_fields': {
            'character_id': character_id,
            'character_name': character_data['name']
        }})
        analyzer = CharacterAppearanceAnalyzer()
        appearance_spec = await analyzer.aanalyze(Path(character_data['reference_image_path']))

        # Update character with all appearance fields
        character_data = await service.update_character(
            character_id,
            physical_description=appearance_spec.overall_description,
            age=appearance_spec.age,
            skin_tone=appearance_spec.skin_tone,
            face_description=appearance_spec.face_description,
            hair_description=appearance_spec.hair_description,
            body_description=appearance_spec.body_description
        )
        logger.info(f"Physical description re-analyzed and saved", extra={'extra_fields': {
            'character_id': character_id
        }})

    except Exception as e:
        logger.error(f"Appearance analysis failed: {str(e)}", exc_info=e, extra={'extra_fields': {
            'character_id': character_id
        }})
        raise HTTPException(status_code=500, detail=f"Appearance analysis failed: {str(e)}")

    # Build reference image URL
    ref_image_url = f"/api/characters/{character_id}/image"

    return CharacterInfo(
        character_id=character_data['character_id'],
        name=character_data['name'],
        visual_description=character_data.get('visual_description'),
        physical_description=character_data.get('physical_description'),
        personality=character_data.get('personality'),
        reference_image_url=ref_image_url,
        tags=character_data.get('tags', []),
        created_at=character_data.get('created_at'),
        metadata=character_data.get('metadata', {}),
        age=character_data.get('age'),
        skin_tone=character_data.get('skin_tone'),
        face_description=character_data.get('face_description'),
        hair_description=character_data.get('hair_description'),
        body_description=character_data.get('body_description')
    )


@router.post("/analyze-appearances", response_model=dict)
async def analyze_character_appearances(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Analyze appearances for all characters with images but missing physical descriptions

    Finds characters that have reference images but no physical_description field filled in,
    queues a background job to analyze them, and populates the physical_description field.

    Returns:
        Dict with job_id for tracking progress via /api/jobs/{job_id}
    """
    service = CharacterServiceDB(db, user_id=current_user.id if current_user else None)

    # Get all characters
    characters = await service.list_characters()

    # Filter for characters with images but missing descriptions
    chars_to_analyze = []
    for char in characters:
        has_image = char.get('reference_image_path')
        missing_description = not char.get('physical_description') or char.get('physical_description', '').strip() == ''

        if has_image and missing_description:
            chars_to_analyze.append(char)

    if not chars_to_analyze:
        return {
            "status": "completed",
            "message": "No characters need appearance analysis",
            "job_id": None
        }

    # Create job for tracking
    job_manager = get_job_queue_manager()
    job_id = job_manager.create_job(
        job_type=JobType.BATCH_ANALYZE,
        title=f"Analyze Appearances: {len(chars_to_analyze)} Characters",
        description=f"Analyzing physical appearance for {len(chars_to_analyze)} characters",
        total_steps=len(chars_to_analyze),
        cancelable=False
    )

    # Define background task
    async def execute_analysis():
        """Execute the character appearance analysis"""
        from api.database import get_session

        job_manager = get_job_queue_manager()
        analyzer = CharacterAppearanceAnalyzer()

        try:
            job_manager.start_job(job_id)
            job_manager.update_progress(job_id, 0.0, "Starting character appearance analysis...")

            results = []
            success_count = 0

            for idx, char in enumerate(chars_to_analyze, 1):
                character_id = char['character_id']
                name = char['name']
                image_path = Path(char['reference_image_path'])

                try:
                    progress = (idx - 1) / len(chars_to_analyze)
                    job_manager.update_progress(job_id, progress, f"Analyzing {name}...")

                    logger.info(f"Analyzing appearance for {name}", extra={'extra_fields': {
                        'character_id': character_id,
                        'character_name': name,
                        'progress': f"{idx}/{len(chars_to_analyze)}"
                    }})

                    # Run appearance analyzer
                    appearance_spec = await analyzer.aanalyze(image_path)

                    # Update character with all appearance fields
                    async with get_session() as session:
                        service = CharacterServiceDB(session, user_id=None)  # TODO: Use current_user.id when auth is migrated to PostgreSQL
                        await service.update_character(
                            character_id,
                            physical_description=appearance_spec.overall_description,
                            age=appearance_spec.age,
                            skin_tone=appearance_spec.skin_tone,
                            face_description=appearance_spec.face_description,
                            hair_description=appearance_spec.hair_description,
                            body_description=appearance_spec.body_description
                        )

                    results.append({
                        "character_id": character_id,
                        "name": name,
                        "status": "success"
                    })

                    success_count += 1
                    logger.info(f"Successfully analyzed {name}", extra={'extra_fields': {
                        'character_id': character_id,
                        'character_name': name
                    }})

                except Exception as e:
                    error_message = str(e)
                    results.append({
                        "character_id": character_id,
                        "name": name,
                        "status": "failed",
                        "error": error_message
                    })
                    logger.error(f"Failed to analyze {name}: {error_message}", extra={'extra_fields': {
                        'character_id': character_id,
                        'character_name': name,
                        'error': error_message
                    }})

            # Mark job as complete
            job_manager.update_progress(job_id, 1.0, f"Completed: {success_count} of {len(chars_to_analyze)} analyzed successfully")
            job_manager.complete_job(
                job_id,
                result={
                    "analyzed_count": success_count,
                    "total_attempted": len(chars_to_analyze),
                    "results": results
                }
            )

        except Exception as e:
            logger.error(f"Character appearance analysis failed: {e}", exc_info=e, extra={'extra_fields': {
                'job_id': job_id,
                'error': str(e)
            }})
            job_manager.fail_job(job_id, str(e))

    # Queue the background task
    background_tasks.add_task(execute_analysis)

    return {
        "status": "queued",
        "message": f"Queued analysis for {len(chars_to_analyze)} characters",
        "job_id": job_id
    }


