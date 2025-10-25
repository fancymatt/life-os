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
from ai_tools.entity_merger.tool import EntityMerger

logger = get_logger(__name__)


class MergeService:
    """Service for merging duplicate entities"""

    def __init__(self, db_session: AsyncSession, user_id: Optional[int] = None):
        self.db = db_session
        self.user_id = user_id
        self.merger = EntityMerger()  # Uses model from config

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
        from api.models.db import ImageEntityRelationship
        from sqlalchemy import select

        references = {
            "stories": [],
            "images": [],
            "outfits": [],
            "compositions": [],
            "visualization_configs": []
        }

        # Find image relationships
        try:
            stmt = select(ImageEntityRelationship).where(
                ImageEntityRelationship.entity_type == entity_type,
                ImageEntityRelationship.entity_id == entity_id
            )
            result = await self.db.execute(stmt)
            image_rels = result.scalars().all()

            for rel in image_rels:
                references["images"].append({
                    "relationship_id": rel.id,
                    "image_id": rel.image_id,
                    "role": rel.role
                })

            logger.info(f"Found {len(image_rels)} image references for {entity_type} {entity_id}")
        except Exception as e:
            logger.warning(f"Error finding image references: {e}")

        return references

    async def analyze_merge(
        self,
        entity_type: str,
        source_entity: Dict[str, Any],
        target_entity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to analyze two entities and generate an intelligent merged version.

        Uses the entity_merger tool with template-based prompting.
        Template can be customized in data/tool_configs/entity_merger_template.md

        Args:
            entity_type: Type of entity (character, clothing_item, etc.)
            source_entity: Entity to keep (this ID will remain)
            target_entity: Entity to merge in (this will be archived)

        Returns:
            Merged entity data with combined information
        """
        # Use EntityMerger tool (supports template override and model config)
        merged_data = self.merger.merge(
            entity_type=entity_type,
            source_entity=source_entity,
            target_entity=target_entity
        )

        return merged_data

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

            # Normalize entity type (handle plurals from frontend)
            normalized_type = entity_type.rstrip('s')  # "clothing_items" → "clothing_item"

            # Get appropriate repository
            repo = None
            if normalized_type in ["character"]:
                repo = CharacterRepository(self.db)
            elif normalized_type in ["clothing_item"]:
                repo = ClothingItemRepository(self.db)
            elif normalized_type in ["board_game"]:
                repo = BoardGameRepository(self.db)
            # Add more entity types as needed

            if not repo:
                raise ValueError(f"Unsupported entity type for merging: {entity_type}")

            # 1. Update source entity with merged data
            # Fetch the source entity ORM object
            source_entity_obj = await repo.get_by_id(source_id)
            if not source_entity_obj:
                raise ValueError(f"Source {entity_type} {source_id} not found")

            # Field length limits (from database schema)
            # These prevent StringDataRightTruncationError
            field_limits = {
                'item': 500,
                'color': 255,
                'name': 255,
                'visual_description': None,  # Text field
                'fabric': None,  # Text field
                'details': None,  # Text field
            }

            # Update fields from merged_data
            for key, value in merged_data.items():
                if hasattr(source_entity_obj, key) and key not in ['id', 'created_at', 'item_id', 'character_id', 'game_id']:
                    # Truncate string fields that exceed schema limits
                    if isinstance(value, str) and key in field_limits and field_limits[key] is not None:
                        max_len = field_limits[key]
                        if len(value) > max_len:
                            logger.warning(f"Truncating {key} from {len(value)} to {max_len} chars")
                            value = value[:max_len]
                    setattr(source_entity_obj, key, value)

            # Save updated entity
            await repo.update(source_entity_obj)
            logger.info(f"Updated {entity_type} {source_id} with merged data")

            # 2. Update references (find and update all references from target to source)
            references = await self.find_references(entity_type, target_id)
            total_updated = 0

            # Update image entity relationships
            if references["images"]:
                from api.models.db import ImageEntityRelationship
                from sqlalchemy import delete

                for img_ref in references["images"]:
                    # Check if source already has a relationship with this image+role
                    existing_stmt = select(ImageEntityRelationship).where(
                        ImageEntityRelationship.image_id == img_ref["image_id"],
                        ImageEntityRelationship.entity_type == entity_type,
                        ImageEntityRelationship.entity_id == source_id,
                        ImageEntityRelationship.role == img_ref["role"]
                    )
                    existing_result = await self.db.execute(existing_stmt)
                    existing_rel = existing_result.scalar_one_or_none()

                    if existing_rel:
                        # Source already has this relationship, delete the duplicate from target
                        delete_stmt = delete(ImageEntityRelationship).where(
                            ImageEntityRelationship.id == img_ref["relationship_id"]
                        )
                        await self.db.execute(delete_stmt)
                        logger.info(f"Deleted duplicate relationship {img_ref['relationship_id']} (already exists for source)")
                    else:
                        # Update the relationship to point to source_id instead of target_id
                        stmt = (
                            update(ImageEntityRelationship)
                            .where(ImageEntityRelationship.id == img_ref["relationship_id"])
                            .values(entity_id=source_id)
                        )
                        await self.db.execute(stmt)
                    total_updated += 1
                logger.info(f"Updated {len(references['images'])} image relationships")

            # Update story references
            if references["stories"]:
                from api.models.db import Story
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

            # 3. Archive target entity
            # Note: Some entities (Character, BoardGame) have 'meta' field,
            # but others (ClothingItem) do not. Set merged_into if supported.
            target_entity_obj = await repo.get_by_id(target_id)
            if target_entity_obj:
                # Set metadata if the entity supports it
                if hasattr(target_entity_obj, 'meta'):
                    if target_entity_obj.meta is None:
                        target_entity_obj.meta = {}
                    target_entity_obj.meta['merged_into'] = source_id
                    logger.info(f"Set merged_into metadata for {entity_type} {target_id}")
                await repo.archive(target_id)
                logger.info(f"Archived {entity_type} {target_id}")

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
