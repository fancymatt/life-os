"""
Brief Card Routes

API endpoints for Brief cards (Phase 8 foundation).

Brief cards surface decisions and results to users:
- Jobs awaiting input (merge preview, agent approvals)
- Completed background tasks
- Suggested actions from Auto-Prep/Auto-Tidy

Foundation for Phase 8 Daily Brief system.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from api.services.brief_service import get_brief_service
from api.models.jobs import BriefCard
from api.logging_config import get_logger
from api.database import get_session
from api.services.merge_service import MergeService

router = APIRouter()
logger = get_logger(__name__)


class RespondToBriefCardRequest(BaseModel):
    """Request to respond to a Brief card"""
    response: Dict[str, Any]  # User's response (e.g., {"action": "approve", "edited_data": {...}})


class SnoozeCardRequest(BaseModel):
    """Request to snooze a Brief card"""
    until: datetime  # Snooze until this time


@router.get("/", response_model=List[BriefCard])
async def list_brief_cards(
    category: Optional[str] = None,
    include_dismissed: bool = False
):
    """
    List all Brief cards

    Query Parameters:
    - category: Filter by category (work/creative/life/maintenance)
    - include_dismissed: Include dismissed cards (default: False)

    Returns:
        List of BriefCard objects sorted by created_at (newest first)
    """
    brief_service = get_brief_service()
    cards = brief_service.list_cards(
        category=category,
        include_dismissed=include_dismissed
    )

    logger.info(f"Listed {len(cards)} Brief cards (category={category}, include_dismissed={include_dismissed})")
    return cards


@router.get("/{card_id}", response_model=BriefCard)
async def get_brief_card(card_id: str):
    """
    Get a specific Brief card by ID

    Returns:
        BriefCard object
    """
    brief_service = get_brief_service()
    card = brief_service.get_card(card_id)

    if not card:
        raise HTTPException(status_code=404, detail=f"Brief card not found: {card_id}")

    return card


@router.post("/{card_id}/respond", response_model=BriefCard)
async def respond_to_brief_card(
    card_id: str,
    request: RespondToBriefCardRequest,
    background_tasks: BackgroundTasks
):
    """
    Respond to a Brief card

    Records user's response and executes the associated action (e.g., merge).

    Body:
    {
        "response": {
            "action": "approve",
            "edited_data": {...}  // Optional edited data
        }
    }

    Returns:
        Updated BriefCard
    """
    brief_service = get_brief_service()

    try:
        # Record the response
        card = brief_service.respond_to_card(card_id, request.response)
        logger.info(f"User responded to Brief card {card_id}: {request.response.get('action', 'unknown')}")

        # Handle the action
        action = request.response.get("action")
        from api.services.job_queue import get_job_queue_manager
        job_manager = get_job_queue_manager()

        if action == "approve":
            # Execute the merge
            job = job_manager.get_job(card.job_id)

            if job and job.status == "awaiting_input":
                # Extract merge parameters from awaiting_data
                awaiting_data = job.awaiting_data
                entity_type = awaiting_data.get("entity_type")
                source_id = awaiting_data.get("source_id")
                target_id = awaiting_data.get("target_id")
                merged_data = awaiting_data.get("merged_data")

                if all([entity_type, source_id, target_id, merged_data]):
                    # Execute merge in background
                    async def execute_merge():
                        try:
                            logger.info(f"Executing approved merge for job {card.job_id}: {entity_type} {source_id} -> {target_id}")
                            async with get_session() as session:
                                service = MergeService(session, user_id=None)
                                result = await service.execute_merge(
                                    entity_type, source_id, target_id, merged_data
                                )
                            job_manager.complete_job(card.job_id, {
                                "status": "success",
                                "user_approved": True,
                                "merge_result": result
                            })
                            logger.info(f"Merge completed successfully for job {card.job_id}")
                        except Exception as e:
                            logger.error(f"Merge failed for job {card.job_id}: {e}")
                            job_manager.fail_job(card.job_id, str(e))

                    # Resume job and start merge
                    job_manager.resume_with_input(card.job_id, {"action": "approve"})
                    background_tasks.add_task(execute_merge)

                    # Dismiss the card now that action is taken
                    brief_service.dismiss_card(card_id)
                    logger.info(f"Started merge execution and dismissed Brief card {card_id}")

        elif action == "cancel":
            # Cancel the job and dismiss the card
            try:
                job = job_manager.get_job(card.job_id)
                if job and job.status == "awaiting_input":
                    # Cancel the job
                    job_manager.cancel_job(card.job_id)
                    logger.info(f"Cancelled job {card.job_id} per user request")
            except ValueError:
                # Job not found or already completed - that's okay
                pass

            # Dismiss the card
            brief_service.dismiss_card(card_id)
            logger.info(f"Cancelled merge and dismissed Brief card {card_id}")

        elif action == "edit":
            # For edit action, we could implement editing in the future
            # For now, just dismiss the card
            brief_service.dismiss_card(card_id)
            logger.info(f"Edit action received, dismissed Brief card {card_id}")

        return card

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{card_id}/dismiss", response_model=BriefCard)
async def dismiss_brief_card(card_id: str):
    """
    Dismiss a Brief card without responding

    Marks card as dismissed (hides from active Brief).

    Returns:
        Updated BriefCard
    """
    brief_service = get_brief_service()

    try:
        card = brief_service.dismiss_card(card_id)
        logger.info(f"Dismissed Brief card: {card_id}")
        return card

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{card_id}/snooze", response_model=BriefCard)
async def snooze_brief_card(
    card_id: str,
    request: SnoozeCardRequest
):
    """
    Snooze a Brief card until a specific time

    Temporarily hides card from active Brief until specified time.

    Body:
    {
        "until": "2025-10-25T09:00:00Z"
    }

    Returns:
        Updated BriefCard
    """
    brief_service = get_brief_service()

    try:
        card = brief_service.snooze_card(card_id, request.until)
        logger.info(f"Snoozed Brief card {card_id} until {request.until}")
        return card

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
