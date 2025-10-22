"""
Visualization Config Routes

Endpoints for managing visualization configuration entities.
These configs control how different entity types are rendered as preview images.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import Optional, List
from pydantic import BaseModel

from api.services.visualization_config_service import VisualizationConfigService
from api.models.auth import User
from api.dependencies.auth import get_current_active_user

router = APIRouter()


# Request/Response Models
class VisualizationConfigCreate(BaseModel):
    """Request to create a visualization config"""
    entity_type: str
    display_name: str
    composition_style: str = "product"
    framing: str = "medium"
    angle: str = "front"
    background: str = "white"
    lighting: str = "soft_even"
    art_style_id: Optional[str] = None
    reference_image_path: Optional[str] = None
    additional_instructions: str = ""
    image_size: str = "1024x1024"
    model: str = "gemini/gemini-2.5-flash-image"
    is_default: bool = False


class VisualizationConfigUpdate(BaseModel):
    """Request to update a visualization config"""
    display_name: Optional[str] = None
    composition_style: Optional[str] = None
    framing: Optional[str] = None
    angle: Optional[str] = None
    background: Optional[str] = None
    lighting: Optional[str] = None
    art_style_id: Optional[str] = None
    reference_image_path: Optional[str] = None
    additional_instructions: Optional[str] = None
    image_size: Optional[str] = None
    model: Optional[str] = None
    is_default: Optional[bool] = None


class VisualizationConfigInfo(BaseModel):
    """Visualization config response"""
    config_id: str
    entity_type: str
    display_name: str
    composition_style: str
    framing: str
    angle: str
    background: str
    lighting: str
    art_style_id: Optional[str] = None
    reference_image_path: Optional[str] = None
    additional_instructions: str
    image_size: str
    model: str
    is_default: bool
    created_at: str
    updated_at: str


class VisualizationConfigListResponse(BaseModel):
    """Response for listing visualization configs"""
    count: int
    configs: List[VisualizationConfigInfo]
    entity_type_filter: Optional[str] = None


class EntityTypesSummaryResponse(BaseModel):
    """Summary of configs per entity type"""
    entity_types: dict  # {entity_type: count}
    total_configs: int


# Routes
@router.get("/", response_model=VisualizationConfigListResponse)
async def list_visualization_configs(
    entity_type: Optional[str] = Query(None, description="Filter by entity type (e.g., 'clothing_item', 'character')"),
    limit: Optional[int] = Query(None, description="Maximum number of configs to return"),
    offset: int = Query(0, description="Number of configs to skip"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all visualization configs

    Optionally filter by entity type and paginate results.
    Returns configs sorted by updated_at (newest first).
    """
    service = VisualizationConfigService()
    configs = service.list_configs(entity_type=entity_type, limit=limit, offset=offset)

    config_infos = [
        VisualizationConfigInfo(
            config_id=config['config_id'],
            entity_type=config['entity_type'],
            display_name=config['display_name'],
            composition_style=config['composition_style'],
            framing=config['framing'],
            angle=config['angle'],
            background=config['background'],
            lighting=config['lighting'],
            art_style_id=config.get('art_style_id'),
            reference_image_path=config.get('reference_image_path'),
            additional_instructions=config.get('additional_instructions', ''),
            image_size=config.get('image_size', '1024x1024'),
            model=config.get('model', 'gemini/gemini-2.5-flash-image'),
            is_default=config.get('is_default', False),
            created_at=config.get('created_at', ''),
            updated_at=config.get('updated_at', '')
        )
        for config in configs
    ]

    return VisualizationConfigListResponse(
        count=len(config_infos),
        configs=config_infos,
        entity_type_filter=entity_type
    )


@router.get("/entity-types", response_model=EntityTypesSummaryResponse)
async def get_entity_types_summary(
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get summary of configs per entity type

    Returns a dict mapping each entity type to the number of configs for that type.
    Useful for showing entity type counts in the UI.
    """
    service = VisualizationConfigService()
    summary = service.get_entity_types_summary()

    return EntityTypesSummaryResponse(
        entity_types=summary,
        total_configs=sum(summary.values())
    )


@router.get("/default/{entity_type}", response_model=VisualizationConfigInfo)
async def get_default_config(
    entity_type: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get the default visualization config for an entity type

    Returns the config marked as default, or the first available config if none is marked.
    Useful for automatically applying visualization settings when creating new entities.
    """
    service = VisualizationConfigService()
    config = service.get_default_config(entity_type)

    if not config:
        raise HTTPException(status_code=404, detail=f"No visualization config found for entity type: {entity_type}")

    return VisualizationConfigInfo(
        config_id=config['config_id'],
        entity_type=config['entity_type'],
        display_name=config['display_name'],
        composition_style=config['composition_style'],
        framing=config['framing'],
        angle=config['angle'],
        background=config['background'],
        lighting=config['lighting'],
        art_style_id=config.get('art_style_id'),
        reference_image_path=config.get('reference_image_path'),
        additional_instructions=config.get('additional_instructions', ''),
        image_size=config.get('image_size', '1024x1024'),
        model=config.get('model', 'gemini/gemini-2.5-flash-image'),
        is_default=config.get('is_default', False),
        created_at=config.get('created_at', ''),
        updated_at=config.get('updated_at', '')
    )


@router.get("/{config_id}", response_model=VisualizationConfigInfo)
async def get_visualization_config(
    config_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a visualization config by ID

    Returns full config data including all settings.
    """
    service = VisualizationConfigService()
    config = service.get_config(config_id)

    if not config:
        raise HTTPException(status_code=404, detail=f"Visualization config {config_id} not found")

    return VisualizationConfigInfo(
        config_id=config['config_id'],
        entity_type=config['entity_type'],
        display_name=config['display_name'],
        composition_style=config['composition_style'],
        framing=config['framing'],
        angle=config['angle'],
        background=config['background'],
        lighting=config['lighting'],
        art_style_id=config.get('art_style_id'),
        reference_image_path=config.get('reference_image_path'),
        additional_instructions=config.get('additional_instructions', ''),
        image_size=config.get('image_size', '1024x1024'),
        model=config.get('model', 'gemini/gemini-2.5-flash-image'),
        is_default=config.get('is_default', False),
        created_at=config.get('created_at', ''),
        updated_at=config.get('updated_at', '')
    )


@router.post("/", response_model=VisualizationConfigInfo)
async def create_visualization_config(
    request: VisualizationConfigCreate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new visualization config

    Defines how entities of a specific type should be visualized as preview images.
    Can specify composition, lighting, art style, and reference images.
    """
    service = VisualizationConfigService()

    config = service.create_config(
        entity_type=request.entity_type,
        display_name=request.display_name,
        composition_style=request.composition_style,
        framing=request.framing,
        angle=request.angle,
        background=request.background,
        lighting=request.lighting,
        art_style_id=request.art_style_id,
        reference_image_path=request.reference_image_path,
        additional_instructions=request.additional_instructions,
        image_size=request.image_size,
        model=request.model,
        is_default=request.is_default
    )

    return VisualizationConfigInfo(
        config_id=config['config_id'],
        entity_type=config['entity_type'],
        display_name=config['display_name'],
        composition_style=config['composition_style'],
        framing=config['framing'],
        angle=config['angle'],
        background=config['background'],
        lighting=config['lighting'],
        art_style_id=config.get('art_style_id'),
        reference_image_path=config.get('reference_image_path'),
        additional_instructions=config.get('additional_instructions', ''),
        image_size=config.get('image_size', '1024x1024'),
        model=config.get('model', 'gemini/gemini-2.5-flash-image'),
        is_default=config.get('is_default', False),
        created_at=config.get('created_at', ''),
        updated_at=config.get('updated_at', '')
    )


@router.put("/{config_id}", response_model=VisualizationConfigInfo)
async def update_visualization_config(
    config_id: str,
    request: VisualizationConfigUpdate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update a visualization config

    Updates config fields. Only provided fields will be updated.
    """
    service = VisualizationConfigService()

    config = service.update_config(
        config_id=config_id,
        display_name=request.display_name,
        composition_style=request.composition_style,
        framing=request.framing,
        angle=request.angle,
        background=request.background,
        lighting=request.lighting,
        art_style_id=request.art_style_id,
        reference_image_path=request.reference_image_path,
        additional_instructions=request.additional_instructions,
        image_size=request.image_size,
        model=request.model,
        is_default=request.is_default
    )

    if not config:
        raise HTTPException(status_code=404, detail=f"Visualization config {config_id} not found")

    return VisualizationConfigInfo(
        config_id=config['config_id'],
        entity_type=config['entity_type'],
        display_name=config['display_name'],
        composition_style=config['composition_style'],
        framing=config['framing'],
        angle=config['angle'],
        background=config['background'],
        lighting=config['lighting'],
        art_style_id=config.get('art_style_id'),
        reference_image_path=config.get('reference_image_path'),
        additional_instructions=config.get('additional_instructions', ''),
        image_size=config.get('image_size', '1024x1024'),
        model=config.get('model', 'gemini/gemini-2.5-flash-image'),
        is_default=config.get('is_default', False),
        created_at=config.get('created_at', ''),
        updated_at=config.get('updated_at', '')
    )


@router.delete("/{config_id}")
async def delete_visualization_config(
    config_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete a visualization config

    Removes the config permanently.
    Warning: If this is the default config for an entity type, entities of that type
    will have no default visualization settings.
    """
    service = VisualizationConfigService()
    success = service.delete_config(config_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Visualization config {config_id} not found")

    return {"message": f"Visualization config {config_id} deleted successfully"}
