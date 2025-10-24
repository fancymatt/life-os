"""
Brief Card Routes

API endpoints for Brief cards (Phase 8 foundation).

Brief cards surface decisions and results to users:
- Jobs awaiting input (merge preview, agent approvals)
- Completed background tasks
- Suggested actions from Auto-Prep/Auto-Tidy

Foundation for Phase 8 Daily Brief system.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from api.services.brief_service import get_brief_service
from api.models.jobs import BriefCard
from api.logging_config import get_logger

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
    request: RespondToBriefCardRequest
):
    """
    Respond to a Brief card

    Records user's response and marks card as responded.

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
        card = brief_service.respond_to_card(card_id, request.response)
        logger.info(f"User responded to Brief card {card_id}: {request.response.get('action', 'unknown')}")
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
