"""
Brief Card Service

File-based storage for Brief cards (Phase 8 foundation).
Future: Move to database for persistence.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import json
import aiofiles
from api.models.jobs import BriefCard, BriefCardAction
from api.logging_config import get_logger
from api.config import settings

logger = get_logger(__name__)


class BriefCardService:
    """
    Manage Brief cards - surface job results/decisions to user

    Foundation for Phase 8 Daily Brief system.
    Uses file-based storage to persist across API restarts.
    """

    def __init__(self):
        self._cards: Dict[str, BriefCard] = {}
        self._storage_dir = settings.base_dir / "data" / "brief_cards"
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._load_cards()

    def _load_cards(self):
        """Load all cards from disk on startup"""
        try:
            for card_file in self._storage_dir.glob("*.json"):
                with open(card_file, 'r') as f:
                    card_data = json.load(f)
                    card = BriefCard(**card_data)
                    self._cards[card.card_id] = card
            logger.info(f"Loaded {len(self._cards)} Brief cards from disk")
        except Exception as e:
            logger.error(f"Error loading Brief cards: {e}")

    def _save_card(self, card: BriefCard):
        """Save a card to disk"""
        try:
            card_file = self._storage_dir / f"{card.card_id}.json"
            with open(card_file, 'w') as f:
                json.dump(card.dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving Brief card {card.card_id}: {e}")

    def _delete_card_file(self, card_id: str):
        """Delete a card file from disk"""
        try:
            card_file = self._storage_dir / f"{card_id}.json"
            if card_file.exists():
                card_file.unlink()
        except Exception as e:
            logger.error(f"Error deleting Brief card file {card_id}: {e}")

    def create_card(
        self,
        job_id: str,
        title: str,
        description: str,
        actions: List[BriefCardAction],
        data: Optional[Dict[str, Any]] = None,
        category: str = "work",
        provenance: Optional[str] = None
    ) -> BriefCard:
        """
        Create a new Brief card

        Args:
            job_id: Associated job ID
            title: Card title (e.g., "Merge Preview Ready")
            description: Card description
            actions: List of action buttons
            data: Optional data payload for UI
            category: "work", "creative", "life", "maintenance"
            provenance: Full reasoning for why this surfaced

        Returns:
            Created BriefCard
        """
        card = BriefCard(
            job_id=job_id,
            title=title,
            description=description,
            actions=actions,
            data=data,
            category=category,
            provenance=provenance
        )

        self._cards[card.card_id] = card
        self._save_card(card)
        logger.info(f"Created Brief card: {card.card_id} for job {job_id}")
        return card

    def get_card(self, card_id: str) -> Optional[BriefCard]:
        """Get a Brief card by ID"""
        return self._cards.get(card_id)

    def get_card_by_job(self, job_id: str) -> Optional[BriefCard]:
        """Get Brief card associated with a job"""
        for card in self._cards.values():
            if card.job_id == job_id and not card.dismissed:
                return card
        return None

    def list_cards(
        self,
        category: Optional[str] = None,
        include_dismissed: bool = False
    ) -> List[BriefCard]:
        """
        List all Brief cards

        Args:
            category: Filter by category (work/creative/life/maintenance)
            include_dismissed: Include dismissed cards

        Returns:
            List of BriefCard objects sorted by created_at (newest first)
        """
        cards = list(self._cards.values())

        # Filter dismissed
        if not include_dismissed:
            cards = [c for c in cards if not c.dismissed]

        # Filter category
        if category:
            cards = [c for c in cards if c.category == category]

        # Sort by created_at (newest first)
        cards.sort(key=lambda c: c.created_at, reverse=True)

        return cards

    def respond_to_card(
        self,
        card_id: str,
        response: Dict[str, Any]
    ) -> BriefCard:
        """
        Record user response to a Brief card

        Args:
            card_id: Card ID
            response: User's response data

        Returns:
            Updated BriefCard

        Raises:
            ValueError: If card not found
        """
        card = self._cards.get(card_id)
        if not card:
            raise ValueError(f"Brief card not found: {card_id}")

        card.response = response
        card.responded_at = datetime.now()
        self._save_card(card)

        logger.info(f"User responded to Brief card {card_id}: {response}")
        return card

    def dismiss_card(self, card_id: str) -> BriefCard:
        """
        Dismiss a Brief card

        Args:
            card_id: Card ID

        Returns:
            Updated BriefCard

        Raises:
            ValueError: If card not found
        """
        card = self._cards.get(card_id)
        if not card:
            raise ValueError(f"Brief card not found: {card_id}")

        card.dismissed = True
        card.responded_at = datetime.now()
        self._save_card(card)

        logger.info(f"Dismissed Brief card: {card_id}")
        return card

    def snooze_card(self, card_id: str, until: datetime) -> BriefCard:
        """
        Snooze a Brief card until a specific time

        Args:
            card_id: Card ID
            until: Snooze until this datetime

        Returns:
            Updated BriefCard

        Raises:
            ValueError: If card not found
        """
        card = self._cards.get(card_id)
        if not card:
            raise ValueError(f"Brief card not found: {card_id}")

        card.snoozed_until = until
        self._save_card(card)

        logger.info(f"Snoozed Brief card {card_id} until {until}")
        return card

    def clear_all_cards(self):
        """Clear all cards (for testing)"""
        # Delete all card files
        for card_file in self._storage_dir.glob("*.json"):
            card_file.unlink()
        self._cards.clear()
        logger.info("Cleared all Brief cards")


# Global singleton instance
_brief_service = None


def get_brief_service() -> BriefCardService:
    """Get the global BriefCardService instance"""
    global _brief_service
    if _brief_service is None:
        _brief_service = BriefCardService()
    return _brief_service
