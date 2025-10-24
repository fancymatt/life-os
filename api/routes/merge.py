"""
Entity Merge Routes

API endpoints for merging duplicate entities.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from api.services.merge_service import MergeService
from api.database import get_db, get_session
from api.models.auth import User
from api.models.jobs import JobType
from api.dependencies.auth import get_current_active_user
from api.services.job_queue import get_job_queue_manager
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
    source_id: Optional[str] = None  # Source entity ID (will keep this one) - extracted from source_entity if not provided
    target_id: Optional[str] = None  # Target entity ID (will be archived) - extracted from target_entity if not provided
    auto_approve: bool = False  # If True, skip Brief card and execute merge immediately


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


async def run_merge_analysis_job(
    job_id: str,
    entity_type: str,
    source_entity: dict,
    target_entity: dict,
    source_id: str,
    target_id: str,
    auto_approve: bool,
    user_id: Optional[int] = None
):
    """
    Background task to analyze merge and optionally execute

    If auto_approve=False: Pause job and create Brief card
    If auto_approve=True: Execute merge automatically
    """
    job_manager = get_job_queue_manager()

    try:
        job_manager.start_job(job_id)
        job_manager.update_progress(job_id, 0.1, "Analyzing entities...")

        # Run AI analysis
        async with get_session() as session:
            service = MergeService(session, user_id=user_id)

            merged_data = await service.analyze_merge(
                entity_type,
                source_entity,
                target_entity
            )

        # Generate changes summary
        changes_summary = {
            "fields_from_source": 0,
            "fields_from_target": 0,
            "fields_merged": 0
        }

        for key in merged_data.keys():
            if key in source_entity and merged_data[key] == source_entity[key]:
                changes_summary["fields_from_source"] += 1
            elif key in target_entity and merged_data[key] == target_entity[key]:
                changes_summary["fields_from_target"] += 1
            else:
                changes_summary["fields_merged"] += 1

        logger.info(f"AI merge analysis complete: {changes_summary}")

        job_manager.update_progress(job_id, 0.6, "Analysis complete")

        # Decision point: auto-approve or wait for user?
        if auto_approve:
            # Execute merge immediately
            logger.info(f"Auto-approving merge for {entity_type} {source_id} + {target_id}")
            job_manager.update_progress(job_id, 0.7, "Auto-approving merge...")

            async with get_session() as session:
                service = MergeService(session, user_id=user_id)
                result = await service.execute_merge(
                    entity_type,
                    source_id,
                    target_id,
                    merged_data
                )

            job_manager.complete_job(job_id, {
                "status": "success",
                "auto_approved": True,
                "merged_data": merged_data,
                "changes_summary": changes_summary,
                "merge_result": result
            })
            logger.info(f"Merge auto-approved and executed: {result}")

        else:
            # Pause for user review
            logger.info(f"Pausing merge for user review: {entity_type} {source_id} + {target_id}")

            # Create Brief card
            brief_card = {
                "title": f"Merge Preview: {entity_type.replace('_', ' ').title()}",
                "description": f"Review merged {entity_type}. {changes_summary['fields_merged']} fields were combined.",
                "category": "work",
                "actions": [
                    {
                        "action_id": "approve",
                        "label": "Approve Merge",
                        "style": "primary",
                        "endpoint": f"/api/merge/resume/{job_id}"
                    },
                    {
                        "action_id": "edit",
                        "label": "Edit & Approve",
                        "style": "secondary",
                        "endpoint": f"/api/merge/resume/{job_id}"
                    },
                    {
                        "action_id": "cancel",
                        "label": "Cancel",
                        "style": "danger"
                    }
                ],
                "provenance": f"AI analyzed {entity_type} entities and generated merged version with {changes_summary['fields_merged']} combined fields"
            }

            # Pause job and create Brief card
            job_manager.pause_for_input(
                job_id,
                awaiting_data={
                    "merged_data": merged_data,
                    "changes_summary": changes_summary,
                    "entity_type": entity_type,
                    "source_id": source_id,
                    "target_id": target_id,
                    "source_entity": source_entity,
                    "target_entity": target_entity
                },
                brief_card=brief_card
            )

            logger.info(f"Merge paused for user review, Brief card created")

    except Exception as e:
        logger.error(f"Merge analysis failed: {e}", exc_info=True)
        job_manager.fail_job(job_id, str(e))


@router.post("/analyze")
async def analyze_merge(
    request: AnalyzeMergeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Analyze merge between two entities with AI

    Modes:
    - auto_approve=False (default): Pause for user review via Brief card
    - auto_approve=True: Execute merge immediately without waiting

    Returns:
        job_id for tracking progress
    """
    try:
        # Extract entity IDs if not provided
        source_id = request.source_id or request.source_entity.get('id') or request.source_entity.get('item_id')
        target_id = request.target_id or request.target_entity.get('id') or request.target_entity.get('item_id')

        if not source_id or not target_id:
            raise HTTPException(
                status_code=400,
                detail="Could not determine entity IDs. Please provide source_id and target_id."
            )

        # Create job immediately
        job_manager = get_job_queue_manager()

        entity_name = request.source_entity.get('name') or request.source_entity.get('title') or request.source_entity.get('item', 'Entity')

        job_id = job_manager.create_job(
            job_type=JobType.ANALYZE,
            title=f"Merge Analysis: {request.entity_type.replace('_', ' ').title()}",
            description=f"Analyzing {entity_name}",
            metadata={
                'entity_type': request.entity_type,
                'source_id': source_id,
                'target_id': target_id,
                'auto_approve': request.auto_approve
            }
        )

        # Queue background task
        background_tasks.add_task(
            run_merge_analysis_job,
            job_id,
            request.entity_type,
            request.source_entity,
            request.target_entity,
            source_id,
            target_id,
            request.auto_approve,
            current_user.id if current_user else None
        )

        logger.info(f"Merge analysis queued: {job_id} (source={source_id}, target={target_id}, auto_approve={request.auto_approve})")

        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Merge analysis queued",
            "auto_approve": request.auto_approve
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queueing merge analysis: {e}")
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


class ResumeMergeRequest(BaseModel):
    """Request to resume a paused merge job"""
    action: str  # "approve", "edit", "cancel"
    edited_data: Optional[dict] = None  # If action="edit", provide edited merged_data


@router.post("/resume/{job_id}")
async def resume_merge(
    job_id: str,
    request: ResumeMergeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Resume a paused merge job with user's decision

    Actions:
    - approve: Execute merge with AI-generated merged_data
    - edit: Execute merge with user-edited merged_data
    - cancel: Cancel the merge

    Returns:
        Updated job status
    """
    job_manager = get_job_queue_manager()

    try:
        # Get job
        job = job_manager.get_job(job_id)

        if job.status != "awaiting_input":
            raise HTTPException(
                status_code=400,
                detail=f"Job {job_id} is not awaiting input (status: {job.status})"
            )

        # Get awaiting data
        awaiting_data = job.awaiting_data
        if not awaiting_data:
            raise HTTPException(
                status_code=500,
                detail=f"Job {job_id} has no awaiting data"
            )

        # Extract data
        entity_type = awaiting_data["entity_type"]
        source_id = awaiting_data["source_id"]
        target_id = awaiting_data["target_id"]
        merged_data = awaiting_data["merged_data"]

        # Handle user action
        if request.action == "cancel":
            # Cancel merge
            job_manager.cancel_job(job_id)
            logger.info(f"User cancelled merge: {job_id}")

            return {
                "status": "cancelled",
                "message": "Merge cancelled by user"
            }

        elif request.action == "approve":
            # Resume with AI-generated merged_data
            logger.info(f"User approved merge: {job_id}")

            # Resume job
            job_manager.resume_with_input(job_id, {
                "action": "approve",
                "merged_data": merged_data
            })

            # Execute merge in background
            async def execute_approved_merge():
                try:
                    job_manager.update_progress(job_id, 0.7, "Executing merge...")

                    async with get_session() as session:
                        service = MergeService(session, user_id=current_user.id if current_user else None)
                        result = await service.execute_merge(
                            entity_type,
                            source_id,
                            target_id,
                            merged_data
                        )

                    job_manager.complete_job(job_id, {
                        "status": "success",
                        "user_approved": True,
                        "merged_data": merged_data,
                        "merge_result": result
                    })
                    logger.info(f"Merge executed successfully: {result}")

                except Exception as e:
                    logger.error(f"Merge execution failed: {e}", exc_info=True)
                    job_manager.fail_job(job_id, str(e))

            background_tasks.add_task(execute_approved_merge)

            return {
                "status": "resumed",
                "message": "Merge approved, executing...",
                "job_id": job_id
            }

        elif request.action == "edit":
            # Resume with user-edited merged_data
            if not request.edited_data:
                raise HTTPException(
                    status_code=400,
                    detail="edited_data is required when action='edit'"
                )

            logger.info(f"User approved merge with edits: {job_id}")

            # Resume job
            job_manager.resume_with_input(job_id, {
                "action": "edit",
                "edited_data": request.edited_data
            })

            # Execute merge with edited data in background
            async def execute_edited_merge():
                try:
                    job_manager.update_progress(job_id, 0.7, "Executing merge with edits...")

                    async with get_session() as session:
                        service = MergeService(session, user_id=current_user.id if current_user else None)
                        result = await service.execute_merge(
                            entity_type,
                            source_id,
                            target_id,
                            request.edited_data
                        )

                    job_manager.complete_job(job_id, {
                        "status": "success",
                        "user_edited": True,
                        "merged_data": request.edited_data,
                        "merge_result": result
                    })
                    logger.info(f"Merge executed with edits: {result}")

                except Exception as e:
                    logger.error(f"Merge execution failed: {e}", exc_info=True)
                    job_manager.fail_job(job_id, str(e))

            background_tasks.add_task(execute_edited_merge)

            return {
                "status": "resumed",
                "message": "Merge approved with edits, executing...",
                "job_id": job_id
            }

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {request.action}. Must be 'approve', 'edit', or 'cancel'"
            )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming merge: {e}")
        raise HTTPException(status_code=500, detail=str(e))
