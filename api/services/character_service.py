"""
Character Service

Handles character entity storage, retrieval, and management.
"""

import json
import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from api.config import settings


class CharacterService:
    """Service for managing character entities"""

    def __init__(self):
        """Initialize character service"""
        self.characters_dir = Path(settings.characters_dir)
        self.characters_dir.mkdir(parents=True, exist_ok=True)

    def _get_character_path(self, character_id: str) -> Path:
        """Get path to character JSON file"""
        return self.characters_dir / f"{character_id}.json"

    def _get_image_path(self, character_id: str) -> Path:
        """Get path to character reference image"""
        return self.characters_dir / f"{character_id}_ref.png"

    def create_character(
        self,
        name: str,
        visual_description: Optional[str] = None,
        personality: Optional[str] = None,
        reference_image_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        # Detailed appearance fields
        age: Optional[str] = None,
        skin_tone: Optional[str] = None,
        face_description: Optional[str] = None,
        hair_description: Optional[str] = None,
        body_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new character

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

        character_data = {
            "character_id": character_id,
            "name": name,
            "visual_description": visual_description,
            "personality": personality,
            "physical_description": None,  # Analyzed physical appearance (auto-generated)
            "reference_image_path": reference_image_path,
            "tags": tags or [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            # Detailed appearance fields
            "age": age,
            "skin_tone": skin_tone,
            "face_description": face_description,
            "hair_description": hair_description,
            "body_description": body_description
        }

        # Save character data
        character_file = self._get_character_path(character_id)
        with open(character_file, 'w') as f:
            json.dump(character_data, f, indent=2)

        return character_data

    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a character by ID

        Args:
            character_id: Character ID

        Returns:
            Character data dict or None if not found
        """
        character_file = self._get_character_path(character_id)

        if not character_file.exists():
            return None

        with open(character_file, 'r') as f:
            return json.load(f)

    def list_characters(self) -> List[Dict[str, Any]]:
        """
        List all characters

        Returns:
            List of character data dicts
        """
        characters = []

        for file_path in self.characters_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    character_data = json.load(f)
                    characters.append(character_data)
            except Exception as e:
                print(f"Error loading character {file_path}: {e}")
                continue

        # Sort by created_at (newest first)
        characters.sort(
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )

        return characters

    def update_character(
        self,
        character_id: str,
        name: Optional[str] = None,
        visual_description: Optional[str] = None,
        personality: Optional[str] = None,
        physical_description: Optional[str] = None,
        reference_image_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        # Detailed appearance fields
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
        character_data = self.get_character(character_id)

        if not character_data:
            return None

        # Update fields if provided
        if name is not None:
            character_data['name'] = name
        if visual_description is not None:
            character_data['visual_description'] = visual_description
        if personality is not None:
            character_data['personality'] = personality
        if physical_description is not None:
            character_data['physical_description'] = physical_description
        if reference_image_path is not None:
            character_data['reference_image_path'] = reference_image_path
        if tags is not None:
            character_data['tags'] = tags
        if metadata is not None:
            character_data['metadata'].update(metadata)

        # Update appearance fields if provided
        if age is not None:
            character_data['age'] = age
        if skin_tone is not None:
            character_data['skin_tone'] = skin_tone
        if face_description is not None:
            character_data['face_description'] = face_description
        if hair_description is not None:
            character_data['hair_description'] = hair_description
        if body_description is not None:
            character_data['body_description'] = body_description

        character_data['updated_at'] = datetime.utcnow().isoformat()

        # Save updated data
        character_file = self._get_character_path(character_id)
        with open(character_file, 'w') as f:
            json.dump(character_data, f, indent=2)

        return character_data

    def delete_character(self, character_id: str) -> bool:
        """
        Delete a character

        Args:
            character_id: Character ID

        Returns:
            True if deleted, False if not found
        """
        character_file = self._get_character_path(character_id)
        image_file = self._get_image_path(character_id)

        if not character_file.exists():
            return False

        # Delete character file
        character_file.unlink()

        # Delete reference image if exists
        if image_file.exists():
            image_file.unlink()

        return True

    def save_reference_image(self, character_id: str, image_data: bytes) -> str:
        """
        Save reference image for a character

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
        Get reference image path for a character

        Args:
            character_id: Character ID

        Returns:
            Image path or None if not found
        """
        image_path = self._get_image_path(character_id)

        if image_path.exists():
            return str(image_path)

        return None

    def create_character_from_subject(
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
        character_data = self.create_character(
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
            character_data = self.update_character(
                character_data['character_id'],
                reference_image_path=str(dest_path)
            )

        return character_data, visual_description
