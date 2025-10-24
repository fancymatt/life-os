"""
Clothing Items Service (PostgreSQL)

Database-backed implementation of clothing items service using PostgreSQL.
Replaces JSON file storage with relational database.
"""

import uuid
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings
from api.models.db import ClothingItem
from api.repositories import ClothingItemRepository
from api.logging_config import get_logger

# Add project to path for importing ItemVisualizer
sys.path.insert(0, str(settings.base_dir))
from ai_tools.item_visualizer.tool import ItemVisualizer

logger = get_logger(__name__)


class ClothingItemServiceDB:
    """PostgreSQL-based clothing items service"""

    def __init__(self, session: AsyncSession, user_id: Optional[int] = None):
        """
        Initialize clothing items service with database session

        Args:
            session: SQLAlchemy async session
            user_id: Optional user ID for filtering
        """
        self.session = session
        self.user_id = user_id
        self.repository = ClothingItemRepository(session)
        self.visualizer = ItemVisualizer()

    def _clothing_item_to_dict(self, item: ClothingItem) -> Dict[str, Any]:
        """Convert ClothingItem model to dict"""
        return {
            "item_id": item.item_id,
            "category": item.category,
            "item": item.item,
            "fabric": item.fabric,
            "color": item.color,
            "details": item.details,
            "source_image": item.source_image,
            "preview_image_path": item.preview_image_path,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }

    async def list_clothing_items(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all clothing items, optionally filtered by category

        Args:
            category: Optional category filter (e.g., "tops", "bottoms")
            limit: Maximum number of items to return
            offset: Number of items to skip
            include_archived: If True, include archived items. Default False.

        Returns:
            List of clothing item dicts
        """
        # Get items with pagination (repository handles filtering and pagination at database level)
        items = await self.repository.get_all(
            user_id=self.user_id,
            category=category,
            limit=limit,
            offset=offset,
            include_archived=include_archived
        )

        # Convert to dicts
        return [self._clothing_item_to_dict(item) for item in items]

    async def get_clothing_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single clothing item by ID

        Args:
            item_id: UUID of the clothing item

        Returns:
            Clothing item dict or None if not found
        """
        item = await self.repository.get_by_id(item_id)

        if not item:
            return None

        # Filter by user if specified
        if self.user_id and item.user_id != self.user_id:
            return None

        return self._clothing_item_to_dict(item)

    async def create_clothing_item(
        self,
        category: str,
        item: str,
        fabric: str,
        color: str,
        details: str,
        source_image: Optional[str] = None,
        generate_preview: bool = False,
        background_tasks = None
    ) -> Dict[str, Any]:
        """
        Create a new clothing item

        Args:
            category: Body zone category
            item: Garment type
            fabric: Material and texture
            color: Color description
            details: Construction details
            source_image: Optional source image path (original image item was extracted from)
            generate_preview: Whether to generate preview image
            background_tasks: Optional FastAPI BackgroundTasks for async preview generation

        Returns:
            Created clothing item dict
        """
        item_id = str(uuid.uuid4())

        clothing_item = ClothingItem(
            item_id=item_id,
            category=category,
            item=item,
            fabric=fabric,
            color=color,
            details=details,
            source_image=source_image,
            user_id=self.user_id
        )

        clothing_item = await self.repository.create(clothing_item)
        await self.session.commit()

        logger.info(f"Created clothing item: {item} ({category})", extra={'extra_fields': {
            'item_id': item_id,
            'category': category,
            'item': item
        }})

        # Generate preview if requested
        if generate_preview:
            if background_tasks is not None:
                # Run preview generation in background
                background_tasks.add_task(
                    self._generate_preview_safe,
                    item_id
                )
                logger.info(f"Queued preview generation for new clothing item {item_id}")
            else:
                # Fallback to synchronous generation
                try:
                    await self.generate_preview(item_id)
                except Exception as e:
                    logger.warning(f"Preview generation failed: {e}", extra={'extra_fields': {
                        'item_id': item_id,
                        'error': str(e)
                    }})

        return self._clothing_item_to_dict(clothing_item)

    async def update_clothing_item(
        self,
        item_id: str,
        category: Optional[str] = None,
        item: Optional[str] = None,
        fabric: Optional[str] = None,
        color: Optional[str] = None,
        details: Optional[str] = None,
        source_image: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a clothing item

        Args:
            item_id: UUID of the clothing item
            category: Optional new category
            item: Optional new item type
            fabric: Optional new fabric
            color: Optional new color
            details: Optional new details
            source_image: Optional new source image

        Returns:
            Updated clothing item dict or None if not found
        """
        clothing_item = await self.repository.get_by_id(item_id)

        if not clothing_item:
            return None

        # Check user permission
        if self.user_id and clothing_item.user_id != self.user_id:
            return None

        # Update fields if provided
        if category is not None:
            clothing_item.category = category
        if item is not None:
            clothing_item.item = item
        if fabric is not None:
            clothing_item.fabric = fabric
        if color is not None:
            clothing_item.color = color
        if details is not None:
            clothing_item.details = details
        if source_image is not None:
            clothing_item.source_image = source_image

        clothing_item.updated_at = datetime.utcnow()

        clothing_item = await self.repository.update(clothing_item)
        await self.session.commit()

        logger.info(f"Updated clothing item: {item_id}", extra={'extra_fields': {
            'item_id': item_id
        }})

        return self._clothing_item_to_dict(clothing_item)

    async def delete_clothing_item(self, item_id: str) -> bool:
        """
        Delete a clothing item

        Args:
            item_id: UUID of the clothing item

        Returns:
            True if deleted, False if not found
        """
        clothing_item = await self.repository.get_by_id(item_id)

        if not clothing_item:
            return False

        # Check user permission
        if self.user_id and clothing_item.user_id != self.user_id:
            return False

        success = await self.repository.delete(item_id)

        if success:
            await self.session.commit()
            logger.info(f"Deleted clothing item: {item_id}", extra={'extra_fields': {
                'item_id': item_id
            }})

        return success

    async def archive_clothing_item(self, item_id: str) -> bool:
        """
        Archive a clothing item (soft delete)

        Args:
            item_id: UUID of the clothing item

        Returns:
            True if archived, False if not found
        """
        clothing_item = await self.repository.get_by_id(item_id)

        if not clothing_item:
            return False

        # Check user permission
        if self.user_id and clothing_item.user_id != self.user_id:
            return False

        success = await self.repository.archive(item_id)

        if success:
            await self.session.commit()
            logger.info(f"Archived clothing item: {item_id}", extra={'extra_fields': {
                'item_id': item_id
            }})

        return success

    async def unarchive_clothing_item(self, item_id: str) -> bool:
        """
        Unarchive a clothing item

        Args:
            item_id: UUID of the clothing item

        Returns:
            True if unarchived, False if not found
        """
        clothing_item = await self.repository.get_by_id(item_id)

        if not clothing_item:
            return False

        # Check user permission
        if self.user_id and clothing_item.user_id != self.user_id:
            return False

        success = await self.repository.unarchive(item_id)

        if success:
            await self.session.commit()
            logger.info(f"Unarchived clothing item: {item_id}", extra={'extra_fields': {
                'item_id': item_id
            }})

        return success

    async def get_categories_summary(self) -> Dict[str, int]:
        """
        Get count of items per category

        Returns:
            Dict mapping category name to count
        """
        # Use repository method to get aggregated data
        categories = await self.repository.get_categories(user_id=self.user_id)

        # Convert list of tuples to dict
        return {category: count for category, count in categories}

    async def count_clothing_items(
        self,
        category: Optional[str] = None,
        include_archived: bool = False
    ) -> int:
        """
        Count total clothing items (filtered by user and optionally by category)

        Args:
            category: Optional category filter
            include_archived: If True, include archived items. Default False.

        Returns:
            Total number of clothing items
        """
        return await self.repository.count(
            user_id=self.user_id,
            category=category,
            include_archived=include_archived
        )

    def _generate_preview_safe(self, item_id: str):
        """
        Safe wrapper for preview generation with error logging

        Args:
            item_id: UUID of the clothing item
        """
        try:
            # Note: This is called from background_tasks which doesn't support async
            # We'll need to handle this differently for async version
            import asyncio
            asyncio.create_task(self.generate_preview(item_id))
        except Exception as e:
            logger.warning(f"Background preview generation failed for {item_id}: {e}", extra={'extra_fields': {
                'item_id': item_id,
                'error': str(e)
            }})

    async def modify_clothing_item(
        self,
        item_id: str,
        instruction: str
    ) -> Optional[Dict[str, Any]]:
        """
        Modify a clothing item using AI based on natural language instruction

        Args:
            item_id: UUID of the clothing item
            instruction: Natural language modification request (e.g., "Make these shoulder-length", "Change to red")

        Returns:
            Modified clothing item dict or None if not found
        """
        from ai_tools.clothing_modifier.tool import ClothingModifier

        # Load existing item
        clothing_item = await self.repository.get_by_id(item_id)
        if not clothing_item:
            return None

        # Check user permission
        if self.user_id and clothing_item.user_id != self.user_id:
            return None

        logger.info(f"Modifying clothing item {item_id} with instruction: {instruction}", extra={'extra_fields': {
            'item_id': item_id,
            'instruction': instruction
        }})

        # Use AI to modify the item
        modifier = ClothingModifier()
        item_dict = {
            'item': clothing_item.item,
            'category': clothing_item.category,
            'color': clothing_item.color,
            'fabric': clothing_item.fabric,
            'details': clothing_item.details,
            'visual_description': getattr(clothing_item, 'visual_description', '')
        }

        try:
            modified_data = modifier.modify(item_dict, instruction)

            # Update the item with modified data
            clothing_item.item = modified_data.get('item', clothing_item.item)
            clothing_item.color = modified_data.get('color', clothing_item.color)
            clothing_item.fabric = modified_data.get('fabric', clothing_item.fabric)
            clothing_item.details = modified_data.get('details', clothing_item.details)
            if 'visual_description' in modified_data:
                clothing_item.visual_description = modified_data['visual_description']

            # Mark as manually modified
            clothing_item.manually_modified = True
            clothing_item.updated_at = datetime.utcnow()

            clothing_item = await self.repository.update(clothing_item)
            await self.session.commit()

            logger.info(f"Successfully modified clothing item {item_id}", extra={'extra_fields': {
                'item_id': item_id
            }})

            return self._clothing_item_to_dict(clothing_item)

        except Exception as e:
            logger.error(f"Failed to modify clothing item {item_id}: {e}", extra={'extra_fields': {
                'item_id': item_id,
                'error': str(e)
            }})
            raise

    async def create_variant(
        self,
        item_id: str,
        instruction: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a variant of a clothing item with AI-based modifications

        Args:
            item_id: UUID of the source clothing item
            instruction: Natural language modification request

        Returns:
            New variant clothing item dict or None if source not found
        """
        from ai_tools.clothing_modifier.tool import ClothingModifier

        # Load source item
        source_item = await self.repository.get_by_id(item_id)
        if not source_item:
            return None

        # Check user permission
        if self.user_id and source_item.user_id != self.user_id:
            return None

        logger.info(f"Creating variant of clothing item {item_id} with instruction: {instruction}", extra={'extra_fields': {
            'source_item_id': item_id,
            'instruction': instruction
        }})

        # Use AI to modify the item
        modifier = ClothingModifier()
        item_dict = {
            'item': source_item.item,
            'category': source_item.category,
            'color': source_item.color,
            'fabric': source_item.fabric,
            'details': source_item.details,
            'visual_description': getattr(source_item, 'visual_description', '')
        }

        try:
            modified_data = modifier.modify(item_dict, instruction)

            # Create new item as variant
            variant_id = str(uuid.uuid4())
            variant_item = ClothingItem(
                item_id=variant_id,
                category=modified_data.get('category', source_item.category),
                item=f"{modified_data.get('item', source_item.item)} (Variant)",
                fabric=modified_data.get('fabric', source_item.fabric),
                color=modified_data.get('color', source_item.color),
                details=modified_data.get('details', source_item.details),
                source_image=source_item.source_image,
                source_entity_id=item_id,  # Track the source
                manually_modified=False,  # Variant is AI-generated, not manually modified
                user_id=self.user_id
            )

            if 'visual_description' in modified_data:
                variant_item.visual_description = modified_data['visual_description']

            variant_item = await self.repository.create(variant_item)
            await self.session.commit()

            logger.info(f"Successfully created variant {variant_id} from {item_id}", extra={'extra_fields': {
                'variant_id': variant_id,
                'source_item_id': item_id
            }})

            return self._clothing_item_to_dict(variant_item)

        except Exception as e:
            logger.error(f"Failed to create variant of {item_id}: {e}", extra={'extra_fields': {
                'item_id': item_id,
                'error': str(e)
            }})
            raise

    async def generate_preview(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate a preview image for a clothing item using configured visualization settings

        Args:
            item_id: UUID of the clothing item

        Returns:
            Updated clothing item dict with preview_image_path, or None if not found
        """
        # Load existing item
        clothing_item = await self.repository.get_by_id(item_id)
        if not clothing_item:
            return None

        # Check user permission
        if self.user_id and clothing_item.user_id != self.user_id:
            return None

        logger.info(f"Generating preview for clothing item: {clothing_item.item} ({clothing_item.category})", extra={'extra_fields': {
            'item_id': item_id,
            'item': clothing_item.item,
            'category': clothing_item.category
        }})

        try:
            # Import here to avoid circular dependency
            from ai_capabilities.specs import ClothingItemEntity, ClothingCategory, VisualizationConfigEntity
            from api.services.visualization_config_service_db import VisualizationConfigServiceDB
            from api.database import get_session

            # Create ClothingItemEntity from database model
            item_entity = ClothingItemEntity(
                item_id=clothing_item.item_id,
                category=ClothingCategory(clothing_item.category),
                item=clothing_item.item,
                fabric=clothing_item.fabric,
                color=clothing_item.color,
                details=clothing_item.details,
                source_image=clothing_item.source_image,
                created_at=clothing_item.created_at
            )

            # Load default visualization config for clothing items from database
            async with get_session() as viz_session:
                config_service = VisualizationConfigServiceDB(viz_session, user_id=None)
                config_dict = await config_service.get_default_config("clothing_item")

            if config_dict:
                config = VisualizationConfigEntity(**config_dict)
                logger.debug(f"Using config: {config.display_name}")
            else:
                # Fallback to None if no config exists (visualizer will use defaults)
                config = None
                logger.debug("Using default visualization settings (no config found)")

            # Generate preview using ItemVisualizer
            # Save to output directory so nginx can serve it
            # Use consistent filename (cache busting handled by query param ?t=timestamp)
            preview_path = self.visualizer.visualize(
                entity=item_entity,
                entity_type="clothing_item",
                config=config,
                output_dir=settings.output_dir / "clothing_items",
                filename=f"{item_id}_preview"
            )

            # Convert to web-accessible URL path
            # /app/output/clothing_items/xyz.png -> /output/clothing_items/xyz.png
            web_path = f"/output/clothing_items/{preview_path.name}"

            # No need to delete old preview - we're overwriting the same file

            # Update item with preview path
            clothing_item.preview_image_path = web_path
            clothing_item.updated_at = datetime.utcnow()

            clothing_item = await self.repository.update(clothing_item)
            await self.session.commit()

            logger.info(f"Preview generated: {web_path}", extra={'extra_fields': {
                'item_id': item_id,
                'preview_path': web_path
            }})

            return self._clothing_item_to_dict(clothing_item)

        except Exception as e:
            logger.error(f"Failed to generate preview for {item_id}: {e}", extra={'extra_fields': {
                'item_id': item_id,
                'error': str(e)
            }})
            raise
