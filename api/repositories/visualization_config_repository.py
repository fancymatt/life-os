"""
Visualization Config Repository

Handles database operations for VisualizationConfig entities.
Provides clean separation between business logic and data access.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.db import VisualizationConfig
from api.logging_config import get_logger

logger = get_logger(__name__)


class VisualizationConfigRepository:
    """Repository for VisualizationConfig database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, config_id: str) -> Optional[VisualizationConfig]:
        """Get visualization config by ID"""
        result = await self.session.execute(
            select(VisualizationConfig).where(VisualizationConfig.config_id == config_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        entity_type: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[VisualizationConfig]:
        """Get all visualization configs, optionally filtered by entity_type and user with pagination support"""
        query = select(VisualizationConfig).order_by(VisualizationConfig.updated_at.desc())

        if entity_type is not None:
            query = query.where(VisualizationConfig.entity_type == entity_type)

        if user_id is not None:
            query = query.where(VisualizationConfig.user_id == user_id)

        # Exclude archived by default
        if not include_archived:
            query = query.where(VisualizationConfig.archived == False)

        if limit is not None:
            query = query.limit(limit)

        query = query.offset(offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_default_for_entity_type(self, entity_type: str) -> Optional[VisualizationConfig]:
        """Get the default visualization config for an entity type"""
        result = await self.session.execute(
            select(VisualizationConfig)
            .where(VisualizationConfig.entity_type == entity_type)
            .where(VisualizationConfig.is_default == True)
            .limit(1)
        )
        config = result.scalar_one_or_none()

        # If no default found, return the first config for this entity type
        if not config:
            result = await self.session.execute(
                select(VisualizationConfig)
                .where(VisualizationConfig.entity_type == entity_type)
                .order_by(VisualizationConfig.created_at.asc())
                .limit(1)
            )
            config = result.scalar_one_or_none()

        return config

    async def create(self, config: VisualizationConfig) -> VisualizationConfig:
        """Create new visualization config"""
        self.session.add(config)
        await self.session.flush()  # Get the ID without committing

        logger.info(f"Created visualization config in database: {config.display_name} ({config.config_id})")
        return config

    async def update(self, config: VisualizationConfig) -> VisualizationConfig:
        """Update existing visualization config"""
        await self.session.merge(config)
        await self.session.flush()

        logger.info(f"Updated visualization config in database: {config.display_name} ({config.config_id})")
        return config

    async def delete(self, config_id: str) -> bool:
        """Archive visualization config by ID (soft delete)"""
        return await self.archive(config_id)

    async def archive(self, config_id: str) -> bool:
        """Archive visualization config by ID (soft delete)"""
        config = await self.get_by_id(config_id)

        if not config:
            return False

        config.archived = True
        config.archived_at = datetime.utcnow()
        await self.session.flush()

        logger.info(f"Archived visualization config in database: {config_id}")
        return True

    async def unarchive(self, config_id: str) -> bool:
        """Unarchive visualization config by ID"""
        config = await self.get_by_id(config_id)

        if not config:
            return False

        config.archived = False
        config.archived_at = None
        await self.session.flush()

        logger.info(f"Unarchived visualization config in database: {config_id}")
        return True

    async def unmark_all_defaults_for_entity_type(
        self,
        entity_type: str,
        exclude_config_id: Optional[str] = None
    ) -> int:
        """
        Unmark all default configs for an entity type

        Args:
            entity_type: Entity type to unmark defaults for
            exclude_config_id: Optional config ID to exclude from unmarking

        Returns:
            Number of configs unmarked
        """
        query = select(VisualizationConfig).where(
            VisualizationConfig.entity_type == entity_type,
            VisualizationConfig.is_default == True
        )

        if exclude_config_id:
            query = query.where(VisualizationConfig.config_id != exclude_config_id)

        result = await self.session.execute(query)
        configs_to_unmark = list(result.scalars().all())

        for config in configs_to_unmark:
            config.is_default = False

        await self.session.flush()

        logger.info(f"Unmarked {len(configs_to_unmark)} default configs for entity_type: {entity_type}")
        return len(configs_to_unmark)

    async def exists(self, config_id: str) -> bool:
        """Check if visualization config exists"""
        config = await self.get_by_id(config_id)
        return config is not None

    async def count(
        self,
        entity_type: Optional[str] = None,
        user_id: Optional[int] = None,
        include_archived: bool = False
    ) -> int:
        """Count visualization configs, optionally filtered by entity_type and user"""
        from sqlalchemy import func

        query = select(func.count()).select_from(VisualizationConfig)

        if entity_type is not None:
            query = query.where(VisualizationConfig.entity_type == entity_type)

        if user_id is not None:
            query = query.where(VisualizationConfig.user_id == user_id)

        # Exclude archived by default
        if not include_archived:
            query = query.where(VisualizationConfig.archived == False)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_entity_types_summary(self) -> dict:
        """Get count of configs per entity type (excluding archived)"""
        from sqlalchemy import func

        query = select(
            VisualizationConfig.entity_type,
            func.count(VisualizationConfig.id).label('count')
        ).where(
            VisualizationConfig.archived == False
        ).group_by(VisualizationConfig.entity_type)

        result = await self.session.execute(query)
        rows = result.all()

        return {row.entity_type: row.count for row in rows}
