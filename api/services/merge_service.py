"""
Entity Merge Service

Handles merging duplicate entities across all entity types.
Workflow:
1. Find all references to target entity
2. AI analyzes both entities and generates merged version
3. Update all references to point to merged entity
4. Archive target entity with merged_into metadata
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_, and_
from uuid import UUID
import json

from api.logging_config import get_logger
from ai_tools.shared.router import Router

logger = get_logger(__name__)


class MergeService:
    """Service for merging duplicate entities"""

    def __init__(self, db_session: AsyncSession, user_id: Optional[int] = None):
        self.db = db_session
        self.user_id = user_id
        self.router = Router()

    async def find_references(
        self,
        entity_type: str,
        entity_id: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find all references to an entity across the system.

        Returns dict mapping reference type to list of references:
        {
            "stories": [{story_id, title, reference_type}],
            "images": [{image_id, file_path}],
            "compositions": [{composition_id, name}],
            ...
        }
        """
        references = {
            "stories": [],
            "images": [],
            "outfits": [],
            "compositions": [],
            "visualization_configs": []
        }

        # Import models here to avoid circular imports
        from api.models.db_models import (
            Story, Image, Outfit, Composition, VisualizationConfig
        )

        try:
            # Check stories (metadata might reference entities)
            if entity_type in ["character", "alteration"]:
                stmt = select(Story).where(
                    or_(
                        Story.character_id == entity_id,
                        Story.metadata.contains({entity_type + "_id": entity_id})
                    )
                )
                if self.user_id:
                    stmt = stmt.where(Story.user_id == self.user_id)

                result = await self.db.execute(stmt)
                stories = result.scalars().all()

                references["stories"] = [
                    {
                        "story_id": str(story.story_id),
                        "title": story.title,
                        "reference_type": "character" if story.character_id == entity_id else "metadata"
                    }
                    for story in stories
                ]

            # Check images (metadata references)
            stmt = select(Image).where(
                Image.metadata.contains({entity_type + "_id": entity_id})
            )
            if self.user_id:
                stmt = stmt.where(Image.user_id == self.user_id)

            result = await self.db.execute(stmt)
            images = result.scalars().all()

            references["images"] = [
                {
                    "image_id": str(img.image_id),
                    "file_path": img.file_path,
                    "created_at": img.created_at.isoformat() if img.created_at else None
                }
                for img in images
            ]

            logger.info(f"Found {len(references['images'])} image references for {entity_type} {entity_id}")

            # Additional reference checking can be added here for:
            # - Outfits
            # - Compositions
            # - Visualization configs
            # - etc.

            return references

        except Exception as e:
            logger.error(f"Error finding references for {entity_type} {entity_id}: {e}")
            raise

    async def analyze_merge(
        self,
        entity_type: str,
        source_entity: Dict[str, Any],
        target_entity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to analyze two entities and generate an intelligent merged version.

        Args:
            entity_type: Type of entity (character, clothing_item, etc.)
            source_entity: Entity to keep (this ID will remain)
            target_entity: Entity to merge in (this will be archived)

        Returns:
            Merged entity data with combined information
        """
        # Build prompt for AI analysis
        system_prompt = f"""You are an expert at merging duplicate {entity_type} entities.

Your task is to analyze two {entity_type} entities and create a merged version that:
1. Preserves ALL unique information from both entities
2. Combines descriptions intelligently (don't just concatenate)
3. Merges tags (union of both tag sets)
4. Combines metadata fields
5. Keeps the most complete/detailed version of each field

Return a JSON object with the merged entity data.
Include ALL fields from the entity type, using the better version from either source."""

        user_prompt = f"""Merge these two {entity_type} entities:

SOURCE ENTITY (ID will be kept):
{json.dumps(source_entity, indent=2)}

TARGET ENTITY (will be archived):
{json.dumps(target_entity, indent=2)}

Generate a merged {entity_type} that combines the best information from both.
Return ONLY valid JSON matching the {entity_type} schema."""

        try:
            # Use router to call AI with structured output
            response = await self.router.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model_name="gemini/gemini-2.0-flash-exp",  # Fast model for analysis
                temperature=0.3,  # Lower temperature for consistent merging
                max_tokens=2000
            )

            # Parse AI response
            merged_data = json.loads(response)

            logger.info(f"AI generated merged {entity_type} combining {len(source_entity)} and {len(target_entity)} fields")

            return merged_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI merge response: {e}")
            # Fallback: simple merge logic
            return self._simple_merge(source_entity, target_entity)
        except Exception as e:
            logger.error(f"Error in AI merge analysis: {e}")
            raise

    def _simple_merge(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback simple merge if AI fails.
        Takes the non-empty value from either entity, preferring source.
        """
        merged = source.copy()

        for key, value in target.items():
            # Skip IDs and timestamps
            if key.endswith('_id') or key.endswith('_at'):
                continue

            # If source doesn't have this field or it's empty, use target's
            if key not in merged or not merged[key]:
                merged[key] = value
            # Special handling for lists (merge)
            elif isinstance(value, list) and isinstance(merged[key], list):
                # Merge lists, remove duplicates
                merged[key] = list(set(merged[key] + value))
            # Special handling for dicts (merge)
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key].update(value)

        return merged

    async def execute_merge(
        self,
        entity_type: str,
        source_id: str,
        target_id: str,
        merged_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Execute the merge:
        1. Update source entity with merged data
        2. Update all references from target to source
        3. Archive target entity with merged_into metadata

        Returns dict with status and message
        """
        try:
            # Import repository classes
            from api.repositories.character_repository import CharacterRepository
            from api.repositories.clothing_item_repository import ClothingItemRepository
            from api.repositories.board_game_repository import BoardGameRepository

            # Get appropriate repository
            repo = None
            if entity_type == "character":
                repo = CharacterRepository(self.db)
            elif entity_type == "clothing_item":
                repo = ClothingItemRepository(self.db)
            elif entity_type == "board_game":
                repo = BoardGameRepository(self.db)
            # Add more entity types as needed

            if not repo:
                raise ValueError(f"Unsupported entity type for merging: {entity_type}")

            # 1. Update source entity with merged data
            await repo.update(source_id, merged_data)
            logger.info(f"Updated {entity_type} {source_id} with merged data")

            # 2. Update references (find and update all references from target to source)
            references = await self.find_references(entity_type, target_id)
            total_updated = 0

            # Update image references
            if references["images"]:
                from api.models.db_models import Image
                for img_ref in references["images"]:
                    stmt = (
                        update(Image)
                        .where(Image.image_id == UUID(img_ref["image_id"]))
                        .values(
                            metadata=Image.metadata.op('||')(
                                json.dumps({f"{entity_type}_id": source_id})
                            )
                        )
                    )
                    await self.db.execute(stmt)
                    total_updated += 1

            # Update story references
            if references["stories"]:
                from api.models.db_models import Story
                for story_ref in references["stories"]:
                    if story_ref["reference_type"] == "character":
                        stmt = (
                            update(Story)
                            .where(Story.story_id == UUID(story_ref["story_id"]))
                            .values(character_id=UUID(source_id))
                        )
                    else:
                        stmt = (
                            update(Story)
                            .where(Story.story_id == UUID(story_ref["story_id"]))
                            .values(
                                metadata=Story.metadata.op('||')(
                                    json.dumps({f"{entity_type}_id": source_id})
                                )
                            )
                        )
                    await self.db.execute(stmt)
                    total_updated += 1

            logger.info(f"Updated {total_updated} references from {target_id} to {source_id}")

            # 3. Archive target entity with merged_into metadata
            archive_metadata = {"merged_into": source_id}
            await repo.archive(target_id, metadata=archive_metadata)
            logger.info(f"Archived {entity_type} {target_id} with merged_into: {source_id}")

            await self.db.commit()

            return {
                "status": "success",
                "message": f"Successfully merged {entity_type}. Updated {total_updated} references.",
                "merged_entity_id": source_id,
                "archived_entity_id": target_id,
                "references_updated": total_updated
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error executing merge: {e}")
            raise
