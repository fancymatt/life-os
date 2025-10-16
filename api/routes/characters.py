"""
Character Routes

Endpoints for managing character entities.
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional, List
import base64
import json
from pathlib import Path

from api.models.requests import CharacterCreate, CharacterUpdate, CharacterFromSubject
from api.models.responses import CharacterInfo, CharacterListResponse, CharacterFromSubjectResponse
from api.services.character_service import CharacterService
from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from api.config import settings
from api.services.job_queue import get_job_queue_manager
from api.models.jobs import JobType
from ai_tools.character_appearance_analyzer.tool import CharacterAppearanceAnalyzer

router = APIRouter()


@router.get("/", response_model=CharacterListResponse)
async def list_characters(
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all characters

    Returns a list of all character entities with their metadata.
    """
    service = CharacterService()
    characters = service.list_characters()

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
            metadata=char.get('metadata', {})
        ))

    return CharacterListResponse(
        count=len(character_infos),
        characters=character_infos
    )


@router.post("/multipart", response_model=CharacterInfo)
async def create_character_multipart(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    personality: str = Form(""),
    tags: str = Form("[]"),
    reference_image: Optional[UploadFile] = File(None),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new character with multipart form data

    Accepts form data including a reference image file.
    Physical appearance is automatically analyzed from the image in the background.
    Returns immediately without waiting for analysis to complete.
    """
    service = CharacterService()

    # Parse tags from JSON string
    tag_list = json.loads(tags) if tags else []

    # Create character
    character_data = service.create_character(
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
        character_data = service.update_character(
            character_id,
            reference_image_path=reference_image_path
        )

        # Queue appearance analysis in background (don't block response)
        async def analyze_appearance():
            """Background task to analyze character appearance"""
            try:
                print(f"🔍 Analyzing character appearance for {name}...")
                service = CharacterService()
                analyzer = CharacterAppearanceAnalyzer()
                appearance_spec = await analyzer.aanalyze(Path(reference_image_path))
                analyzed_appearance = appearance_spec.overall_description

                # Save physical description to character
                service.update_character(
                    character_id,
                    physical_description=analyzed_appearance
                )
                print(f"✅ Physical description analyzed and saved for {name}")
            except Exception as e:
                print(f"⚠️  Appearance analysis failed for {name}: {e}")
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
        metadata=character_data.get('metadata', {})
    )


@router.post("/", response_model=CharacterInfo)
async def create_character(
    request: CharacterCreate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new character (JSON API)

    Creates a character entity with name, visual description, personality, etc.
    Optionally accepts a reference image in base64 format.

    Note: For file uploads, use the /multipart endpoint instead.
    """
    service = CharacterService()

    # Handle reference image if provided
    reference_image_path = None
    if request.reference_image:
        # For now, we'll handle image upload separately
        # This endpoint accepts image data in base64 format
        if request.reference_image.image_data:
            # Decode base64 image
            image_data = base64.b64decode(request.reference_image.image_data.split(',')[-1])

            # Create character first to get ID
            character_data = service.create_character(
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
            character_data = service.update_character(
                character_data['character_id'],
                reference_image_path=reference_image_path
            )
        elif request.reference_image.image_url:
            # TODO: Download image from URL
            character_data = service.create_character(
                name=request.name,
                visual_description=request.visual_description,
                personality=request.personality,
                tags=request.tags
            )
    else:
        character_data = service.create_character(
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
        metadata=character_data.get('metadata', {})
    )


@router.get("/{character_id}/image")
async def get_character_image(
    character_id: str
):
    """
    Get character reference image

    Returns the reference image file for the character.
    """
    service = CharacterService()
    image_path = service.get_reference_image_path(character_id)

    if not image_path:
        raise HTTPException(status_code=404, detail=f"No reference image for character {character_id}")

    return FileResponse(image_path, media_type="image/png")


@router.post("/{character_id}/image", response_model=CharacterInfo)
async def upload_character_image(
    character_id: str,
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Upload reference image for a character

    Accepts an image file upload and sets it as the character's reference image.
    Automatically analyzes the image to extract physical appearance.
    """
    service = CharacterService()

    # Verify character exists
    character_data = service.get_character(character_id)
    if not character_data:
        raise HTTPException(status_code=404, detail=f"Character {character_id} not found")

    # Read and save image
    image_data = await file.read()
    reference_image_path = service.save_reference_image(character_id, image_data)

    # Update character with image path
    character_data = service.update_character(
        character_id,
        reference_image_path=reference_image_path
    )

    # Analyze appearance from image (only if physical_description not already set)
    if not character_data.get('physical_description'):
        try:
            print(f"🔍 Analyzing character appearance for {character_data['name']}...")
            analyzer = CharacterAppearanceAnalyzer()
            appearance_spec = await analyzer.aanalyze(Path(reference_image_path))
            analyzed_appearance = appearance_spec.overall_description

            # Save physical description to character
            character_data = service.update_character(
                character_id,
                physical_description=analyzed_appearance
            )
            print(f"✅ Physical description analyzed and saved")
        except Exception as e:
            print(f"⚠️  Appearance analysis failed: {e}")
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
        metadata=character_data.get('metadata', {})
    )


@router.get("/{character_id}", response_model=CharacterInfo)
async def get_character(
    character_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a character by ID

    Returns full character data including visual description, personality, etc.
    """
    service = CharacterService()
    character_data = service.get_character(character_id)

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
        metadata=character_data.get('metadata', {})
    )


@router.put("/{character_id}", response_model=CharacterInfo)
async def update_character(
    character_id: str,
    request: CharacterUpdate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update a character

    Updates character fields. Only provided fields will be updated.
    """
    service = CharacterService()

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

    character_data = service.update_character(
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
        metadata=character_data.get('metadata', {})
    )


@router.delete("/{character_id}")
async def delete_character(
    character_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete a character

    Removes the character and its associated reference image.
    """
    service = CharacterService()
    success = service.delete_character(character_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Character {character_id} not found")

    return {"message": f"Character {character_id} deleted successfully"}


@router.post("/analyze-appearances", response_model=dict)
async def analyze_character_appearances(
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Analyze appearances for all characters with images but missing physical descriptions

    Finds characters that have reference images but no physical_description field filled in,
    queues a background job to analyze them, and populates the physical_description field.

    Returns:
        Dict with job_id for tracking progress via /api/jobs/{job_id}
    """
    service = CharacterService()

    # Get all characters
    characters = service.list_characters()

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
        job_manager = get_job_queue_manager()
        service = CharacterService()
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

                    print(f"🔍 Analyzing appearance for {name}...")

                    # Run appearance analyzer
                    appearance_spec = await analyzer.aanalyze(image_path)
                    analyzed_description = appearance_spec.overall_description

                    # Update character with physical description
                    service.update_character(
                        character_id,
                        physical_description=analyzed_description
                    )

                    results.append({
                        "character_id": character_id,
                        "name": name,
                        "status": "success"
                    })

                    success_count += 1
                    print(f"✅ Successfully analyzed {name}")

                except Exception as e:
                    error_message = str(e)
                    results.append({
                        "character_id": character_id,
                        "name": name,
                        "status": "failed",
                        "error": error_message
                    })
                    print(f"❌ Failed to analyze {name}: {error_message}")

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
            print(f"❌ Character appearance analysis failed: {e}")
            job_manager.fail_job(job_id, str(e))

    # Queue the background task
    background_tasks.add_task(execute_analysis)

    return {
        "status": "queued",
        "message": f"Queued analysis for {len(chars_to_analyze)} characters",
        "job_id": job_id
    }


