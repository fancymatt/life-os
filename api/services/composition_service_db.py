"""
Composition Service (PostgreSQL)

Business logic for managing saved preset compositions using PostgreSQL.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from api.repositories.composition_repository import CompositionRepository
from api.models.db import Composition


class CompositionServiceDB:
    """Service for managing saved preset compositions (PostgreSQL-backed)"""

    def __init__(self, session: AsyncSession, user_id: Optional[int] = None):
        self.session = session
        self.user_id = user_id
        self.repository = CompositionRepository(session)

    def _composition_to_dict(self, composition: Composition) -> Dict[str, Any]:
        """Convert Composition model to dict"""
        return {
            "composition_id": composition.composition_id,
            "name": composition.name,
            "subject": composition.subject,
            "presets": composition.presets,
            "created_at": composition.created_at.isoformat() if composition.created_at else None,
            "updated_at": composition.updated_at.isoformat() if composition.updated_at else None,
        }

    async def list_compositions(self) -> List[Dict[str, Any]]:
        """List all compositions for the current user"""
        compositions = await self.repository.list_all(user_id=self.user_id)
        return [self._composition_to_dict(comp) for comp in compositions]

    async def get_composition(self, composition_id: str) -> Optional[Dict[str, Any]]:
        """Get composition by ID"""
        composition = await self.repository.get_by_id(composition_id)
        if not composition:
            return None
        if self.user_id and composition.user_id != self.user_id:
            return None
        return self._composition_to_dict(composition)

    async def save_composition(self, composition_id: str, name: str, subject: str, presets: List[dict]) -> Dict[str, Any]:
        """
        Save a composition (create or update)

        Args:
            composition_id: Composition identifier
            name: Composition name
            subject: Subject image path
            presets: List of preset dictionaries

        Returns:
            Saved composition data
        """
        # Check if composition already exists
        existing = await self.repository.get_by_id(composition_id)

        if existing:
            # Update existing composition
            if self.user_id and existing.user_id != self.user_id:
                raise ValueError("Cannot update another user's composition")

            existing.name = name
            existing.subject = subject
            existing.presets = presets
            existing.updated_at = datetime.utcnow()

            composition = await self.repository.update(existing)
        else:
            # Create new composition
            composition = Composition(
                composition_id=composition_id,
                name=name,
                subject=subject,
                presets=presets,
                user_id=self.user_id
            )
            composition = await self.repository.create(composition)

        await self.session.commit()
        return self._composition_to_dict(composition)

    async def delete_composition(self, composition_id: str) -> bool:
        """Delete composition"""
        composition = await self.repository.get_by_id(composition_id)
        if not composition:
            return False
        if self.user_id and composition.user_id != self.user_id:
            return False

        await self.repository.delete(composition)
        await self.session.commit()
        return True
