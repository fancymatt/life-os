"""
Entity Merge Routes

API endpoints for merging duplicate entities.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from api.services.merge_service import MergeService
from api.database import get_db
from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from api.logging_config import get_logger
from api.middleware.cache import invalidates_cache

router = APIRouter()
logger = get_logger(__name__)


class FindReferencesRequest(BaseModel):
    """Request to find all references to an entity"""
    entity_type: str
    entity_id: str


class AnalyzeMergeRequest(BaseModel):
    """Request to analyze merge between two entities"""
    entity_type: str
    source_entity: dict
    target_entity: dict


class ExecuteMergeRequest(BaseModel):
    """Request to execute a merge"""
    entity_type: str
    source_id: str  # Keep this entity
    target_id: str  # Archive this entity
    merged_data: dict


class MergeResponse(BaseModel):
    """Response from merge operation"""
    status: str
    message: str
    merged_entity_id: Optional[str] = None
    archived_entity_id: Optional[str] = None
    references_updated: Optional[int] = None


class ReferencesResponse(BaseModel):
    """Response with entity references"""
    entity_type: str
    entity_id: str
    references: dict
    total_references: int


class MergeAnalysisResponse(BaseModel):
    """Response from merge analysis"""
    merged_data: dict
    changes_summary: Optional[dict] = None


@router.post("/find-references", response_model=ReferencesResponse)
async def find_entity_references(
    request: FindReferencesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Find all references to an entity across the system.

    Used to show user what will be affected by a merge.
    """
    try:
        service = MergeService(db, user_id=current_user.id if current_user else None)
        references = await service.find_references(
            request.entity_type,
            request.entity_id
        )

        # Count total references
        total = sum(len(refs) for refs in references.values())

        logger.info(f"Found {total} references for {request.entity_type} {request.entity_id}")

        return ReferencesResponse(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            references=references,
            total_references=total
        )

    except Exception as e:
        logger.error(f"Error finding references: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=MergeAnalysisResponse)
async def analyze_merge(
    request: AnalyzeMergeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Use AI to analyze two entities and generate merged version.

    The merged data can be edited by user before executing the merge.
    """
    try:
        service = MergeService(db, user_id=current_user.id if current_user else None)

        merged_data = await service.analyze_merge(
            request.entity_type,
            request.source_entity,
            request.target_entity
        )

        # Generate a summary of what changed
        changes_summary = {
            "fields_from_source": 0,
            "fields_from_target": 0,
            "fields_merged": 0
        }

        for key in merged_data.keys():
            if key in request.source_entity and merged_data[key] == request.source_entity[key]:
                changes_summary["fields_from_source"] += 1
            elif key in request.target_entity and merged_data[key] == request.target_entity[key]:
                changes_summary["fields_from_target"] += 1
            else:
                changes_summary["fields_merged"] += 1

        logger.info(f"AI merge analysis complete: {changes_summary}")

        return MergeAnalysisResponse(
            merged_data=merged_data,
            changes_summary=changes_summary
        )

    except Exception as e:
        logger.error(f"Error analyzing merge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=MergeResponse)
@invalidates_cache(entity_types=["characters", "clothing_items", "board_games", "stories", "images"])
async def execute_merge(
    request: ExecuteMergeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Execute entity merge:
    1. Update source entity with merged data
    2. Update all references from target to source
    3. Archive target entity with merged_into metadata

    **Cache Invalidation**: Clears all entity caches since references may span multiple types
    """
    try:
        service = MergeService(db, user_id=current_user.id if current_user else None)

        result = await service.execute_merge(
            request.entity_type,
            request.source_id,
            request.target_id,
            request.merged_data
        )

        logger.info(f"Merge executed successfully: {result}")

        return MergeResponse(**result)

    except ValueError as e:
        logger.error(f"Invalid merge request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing merge: {e}")
        raise HTTPException(status_code=500, detail=str(e))
