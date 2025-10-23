"""
Character Service (PostgreSQL)

Database-backed implementation of character service using PostgreSQL.
Replaces JSON file storage with relational database.
"""

import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings
from api.models.db import Character, User
from api.repositories import CharacterRepository
from api.logging_config import get_logger

logger = get_logger(__name__)


class CharacterServiceDB:
    """PostgreSQL-based character service"""

    def __init__(self, session: AsyncSession, user_id: Optional[int] = None):
        """
        Initialize character service with database session

        Args:
            session: SQLAlchemy async session
            user_id: Optional user ID for filtering
        """
        self.session = session
        self.user_id = user_id
        self.repository = CharacterRepository(session)
        self.characters_dir = Path(settings.characters_dir)
        self.characters_dir.mkdir(parents=True, exist_ok=True)

    def _get_image_path(self, character_id: str) -> Path:
        """Get path to character reference image"""
        return self.characters_dir / f"{character_id}_ref.png"

    def _character_to_dict(self, character: Character) -> Dict[str, Any]:
        """Convert Character model to dict"""
        return {
            "character_id": character.character_id,
            "name": character.name,
            "visual_description": character.visual_description,
            "physical_description": character.physical_description,
            "personality": character.personality,
            "reference_image_path": character.reference_image_path,
            "tags": character.tags,
            "created_at": character.created_at.isoformat() if character.created_at else None,
            "updated_at": character.updated_at.isoformat() if character.updated_at else None,
            "metadata": character.meta,  # Note: 'meta' in DB, 'metadata' in API
            "age": character.age,
            "skin_tone": character.skin_tone,
            "face_description": character.face_description,
            "hair_description": character.hair_description,
            "body_description": character.body_description
        }

    async def create_character(
        self,
        name: str,
        visual_description: Optional[str] = None,
        personality: Optional[str] = None,
        reference_image_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        age: Optional[str] = None,
        skin_tone: Optional[str] = None,
        face_description: Optional[str] = None,
        hair_description: Optional[str] = None,
        body_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new character in database

        Args:
            name: Character name
            visual_description: Visual appearance description
            personality: Personality traits
            reference_image_path: Path to reference image
            tags: List of tags
            metadata: Additional metadata
            age: Apparent age or age group
            skin_tone: Skin tone description
            face_description: Facial description
            hair_description: Hair description
            body_description: Body/physique description

        Returns:
            Character data dict
        """
        character_id = str(uuid.uuid4())[:8]

        character = Character(
            character_id=character_id,
            name=name,
            visual_description=visual_description,
            personality=personality,
            physical_description=None,
            reference_image_path=reference_image_path,
            tags=tags or [],
            meta=metadata or {},  # Note: 'meta' in DB
            age=age,
            skin_tone=skin_tone,
            face_description=face_description,
            hair_description=hair_description,
            body_description=body_description,
            user_id=self.user_id
        )

        character = await self.repository.create(character)
        await self.session.commit()

        return self._character_to_dict(character)

    async def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a character by ID

        Args:
            character_id: Character ID

        Returns:
            Character data dict or None if not found
        """
        character = await self.repository.get_by_id(character_id)

        if not character:
            return None

        # Filter by user if specified
        if self.user_id and character.user_id != self.user_id:
            return None

        return self._character_to_dict(character)

    async def list_characters(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all characters (filtered by user if specified)

        Args:
            limit: Maximum number of characters to return
            offset: Number of characters to skip

        Returns:
            List of character data dicts
        """
        characters = await self.repository.get_all(
            user_id=self.user_id,
            limit=limit,
            offset=offset
        )
        return [self._character_to_dict(char) for char in characters]

    async def update_character(
        self,
        character_id: str,
        name: Optional[str] = None,
        visual_description: Optional[str] = None,
        personality: Optional[str] = None,
        physical_description: Optional[str] = None,
        reference_image_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        age: Optional[str] = None,
        skin_tone: Optional[str] = None,
        face_description: Optional[str] = None,
        hair_description: Optional[str] = None,
        body_description: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a character

        Args:
            character_id: Character ID
            name: New name (optional)
            visual_description: New visual description (optional)
            personality: New personality (optional)
            physical_description: Analyzed physical appearance (optional)
            reference_image_path: New reference image path (optional)
            tags: New tags (optional)
            metadata: New metadata (optional)
            age: Apparent age or age group (optional)
            skin_tone: Skin tone description (optional)
            face_description: Facial description (optional)
            hair_description: Hair description (optional)
            body_description: Body/physique description (optional)

        Returns:
            Updated character data dict or None if not found
        """
        character = await self.repository.get_by_id(character_id)

        if not character:
            return None

        # Check user permission
        if self.user_id and character.user_id != self.user_id:
            return None

        # Update fields if provided
        if name is not None:
            character.name = name
        if visual_description is not None:
            character.visual_description = visual_description
        if personality is not None:
            character.personality = personality
        if physical_description is not None:
            character.physical_description = physical_description
        if reference_image_path is not None:
            character.reference_image_path = reference_image_path
        if tags is not None:
            character.tags = tags
        if metadata is not None:
            character.meta.update(metadata)  # Note: 'meta' in DB

        # Update appearance fields if provided
        if age is not None:
            character.age = age
        if skin_tone is not None:
            character.skin_tone = skin_tone
        if face_description is not None:
            character.face_description = face_description
        if hair_description is not None:
            character.hair_description = hair_description
        if body_description is not None:
            character.body_description = body_description

        character.updated_at = datetime.utcnow()

        character = await self.repository.update(character)
        await self.session.commit()

        return self._character_to_dict(character)

    async def delete_character(self, character_id: str) -> bool:
        """
        Delete a character

        Args:
            character_id: Character ID

        Returns:
            True if deleted, False if not found
        """
        character = await self.repository.get_by_id(character_id)

        if not character:
            return False

        # Check user permission
        if self.user_id and character.user_id != self.user_id:
            return False

        # Delete from database
        success = await self.repository.delete(character_id)

        if success:
            await self.session.commit()

            # Delete reference image if exists
            image_file = self._get_image_path(character_id)
            if image_file.exists():
                image_file.unlink()

        return success

    def save_reference_image(self, character_id: str, image_data: bytes) -> str:
        """
        Save reference image for a character (file system operation)

        Args:
            character_id: Character ID
            image_data: Image binary data

        Returns:
            Path to saved image
        """
        image_path = self._get_image_path(character_id)

        with open(image_path, 'wb') as f:
            f.write(image_data)

        return str(image_path)

    def get_reference_image_path(self, character_id: str) -> Optional[str]:
        """
        Get reference image path for a character (file system check)

        Args:
            character_id: Character ID

        Returns:
            Image path or None if not found
        """
        image_path = self._get_image_path(character_id)

        if image_path.exists():
            return str(image_path)

        return None

    async def create_character_from_subject(
        self,
        subject_path: str,
        name: str,
        analysis_results: Optional[Dict[str, Any]] = None,
        personality: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Create a character from a subject image with optional analysis

        Args:
            subject_path: Path to subject image file
            name: Character name
            analysis_results: Optional comprehensive analysis results
            personality: Optional personality description
            tags: Optional tags

        Returns:
            Tuple of (character_data, visual_description)
        """
        # Generate visual description from analysis if available
        visual_description = None
        metadata = {}

        if analysis_results:
            # Extract key visual characteristics from analysis
            visual_parts = []

            # Outfit description
            if 'outfit' in analysis_results:
                outfit = analysis_results['outfit']
                if outfit.get('suggested_name'):
                    visual_parts.append(f"wearing {outfit['suggested_name']}")

            # Hair style and color
            hair_parts = []
            if 'hair_style' in analysis_results:
                hair_style = analysis_results['hair_style']
                if hair_style.get('suggested_name'):
                    hair_parts.append(hair_style['suggested_name'])

            if 'hair_color' in analysis_results:
                hair_color = analysis_results['hair_color']
                if hair_color.get('suggested_name'):
                    hair_parts.append(hair_color['suggested_name'])

            if hair_parts:
                visual_parts.append(f"with {' '.join(hair_parts)}")

            # Expression
            if 'expression' in analysis_results:
                expression = analysis_results['expression']
                if expression.get('suggested_name'):
                    visual_parts.append(f"{expression['suggested_name']} expression")

            # Makeup
            if 'makeup' in analysis_results:
                makeup = analysis_results['makeup']
                if makeup.get('suggested_name'):
                    visual_parts.append(f"{makeup['suggested_name']} makeup")

            # Accessories
            if 'accessories' in analysis_results:
                accessories = analysis_results['accessories']
                if accessories.get('suggested_name'):
                    visual_parts.append(f"with {accessories['suggested_name']}")

            if visual_parts:
                visual_description = ", ".join(visual_parts)

            # Store analysis metadata
            metadata['source_image'] = subject_path
            metadata['analyzed_at'] = datetime.utcnow().isoformat()

        # Create character
        character_data = await self.create_character(
            name=name,
            visual_description=visual_description,
            personality=personality,
            tags=tags,
            metadata=metadata
        )

        # Copy subject image as reference image
        subject_file = Path(subject_path)
        if subject_file.exists():
            dest_path = self._get_image_path(character_data['character_id'])
            shutil.copy2(subject_file, dest_path)

            # Update character with image path
            character_data = await self.update_character(
                character_data['character_id'],
                reference_image_path=str(dest_path)
            )

        return character_data, visual_description

    async def search_characters(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search characters with filters

        Args:
            query: Text search query
            tags: Filter by tags

        Returns:
            List of matching character data dicts
        """
        characters = await self.repository.search(
            query=query,
            user_id=self.user_id,
            tags=tags
        )

        return [self._character_to_dict(char) for char in characters]
