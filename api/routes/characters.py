"""
Character Routes

Endpoints for managing character entities.
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.responses import FileResponse
from typing import Optional
import base64
from pathlib import Path

from api.models.requests import CharacterCreate, CharacterUpdate, CharacterFromSubject
from api.models.responses import CharacterInfo, CharacterListResponse, CharacterFromSubjectResponse
from api.services.character_service import CharacterService
from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from api.config import settings

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


@router.post("/", response_model=CharacterInfo)
async def create_character(
    request: CharacterCreate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new character

    Creates a character entity with name, visual description, personality, etc.
    Optionally accepts a reference image.
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
        personality=character_data.get('personality'),
        reference_image_url=ref_image_url,
        tags=character_data.get('tags', []),
        created_at=character_data.get('created_at'),
        metadata=character_data.get('metadata', {})
    )


@router.post("/from-subject", response_model=CharacterFromSubjectResponse)
async def create_character_from_subject(
    request: CharacterFromSubject,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a character from a subject image

    Promotes a subject image to a character entity. Optionally analyzes the image
    first to generate visual description and presets.

    Args:
        request: Character creation request with subject path
        current_user: Authenticated user

    Returns:
        Character data with optional analysis results and created presets
    """
    from api.services.analyzer_service import AnalyzerService
    from ai_tools.comprehensive_analyzer.tool import ComprehensiveAnalyzer

    service = CharacterService()

    # Resolve subject image path
    subject_path = None

    # Try as relative path from subjects_dir
    subjects_dir = Path(settings.subjects_dir)
    candidate = subjects_dir / request.subject_path
    if candidate.exists():
        subject_path = str(candidate)
    else:
        # Try upload_dir
        upload_dir = Path(settings.upload_dir)
        candidate = upload_dir / request.subject_path
        if candidate.exists():
            subject_path = str(candidate)
        else:
            # Try as absolute path
            candidate = Path(request.subject_path)
            if candidate.exists():
                subject_path = str(candidate)

    if not subject_path:
        raise HTTPException(
            status_code=404,
            detail=f"Subject image not found: {request.subject_path}. "
                   f"Tried subjects_dir, upload_dir, and as absolute path."
        )

    # Run comprehensive analysis if requested
    analysis_results = None
    created_presets = []

    if request.analyze_first:
        try:
            analyzer = ComprehensiveAnalyzer()
            analyzer_service = AnalyzerService()

            # Run analysis
            result = await analyzer.run(
                subject_path,
                save_as_preset=request.create_presets
            )

            if result.get('status') == 'success':
                analysis_results = result.get('results', {})

                # Get created presets if any
                if request.create_presets and 'created_presets' in result:
                    created_presets = result['created_presets']

        except Exception as e:
            print(f"Warning: Analysis failed: {e}")
            # Continue without analysis

    # Create character from subject
    character_data, visual_description = service.create_character_from_subject(
        subject_path=subject_path,
        name=request.name,
        analysis_results=analysis_results,
        personality=request.personality,
        tags=request.tags
    )

    # Build reference image URL
    ref_image_url = None
    if character_data.get('reference_image_path'):
        ref_image_url = f"/api/characters/{character_data['character_id']}/image"

    # Build response
    character_info = CharacterInfo(
        character_id=character_data['character_id'],
        name=character_data['name'],
        visual_description=character_data.get('visual_description'),
        personality=character_data.get('personality'),
        reference_image_url=ref_image_url,
        tags=character_data.get('tags', []),
        created_at=character_data.get('created_at'),
        metadata=character_data.get('metadata', {})
    )

    return CharacterFromSubjectResponse(
        character=character_info,
        analysis=analysis_results,
        created_presets=created_presets
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


@router.get("/{character_id}/image")
async def get_character_image(
    character_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
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

    # Build reference image URL
    ref_image_url = f"/api/characters/{character_id}/image"

    return CharacterInfo(
        character_id=character_data['character_id'],
        name=character_data['name'],
        visual_description=character_data.get('visual_description'),
        personality=character_data.get('personality'),
        reference_image_url=ref_image_url,
        tags=character_data.get('tags', []),
        created_at=character_data.get('created_at'),
        metadata=character_data.get('metadata', {})
    )


