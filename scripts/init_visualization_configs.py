#!/usr/bin/env python3
"""
Initialize Default Visualization Configs

Creates default visualization configurations for standard entity types.
These configs define how different entities are rendered as preview images.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.visualization_config_service_db import VisualizationConfigServiceDB
from api.database import get_session
from api.logging_config import get_logger

logger = get_logger(__name__)


async def create_default_configs():
    """Create default visualization configs for all entity types"""

    async with get_session() as session:
        service = VisualizationConfigServiceDB(session, user_id=None)

        logger.info("🎨 Creating default visualization configs...")

        # Clothing Item Config
        try:
            logger.info("Creating config: Clothing Item - Product Photography")
            await service.create_config(
            entity_type="clothing_item",
            display_name="Product Photography (Default)",
            composition_style="product",
            framing="medium",
            angle="front",
            background="white",
            lighting="soft_even",
            additional_instructions="Display clothing items on a simple mannequin (for worn items) or as a styled flat lay (for accessories). Use pure white background for catalog consistency. Show item clearly with accurate colors and details.",
            image_size="1024x1024",
            model="gemini/gemini-2.5-flash-image",
            is_default=True
            )
            logger.info("✅ Clothing item config created")
        except Exception as e:
            logger.warning(f"⚠️  Failed to create clothing item config: {e}")

        # Character Config - Portrait Style
        try:
            logger.info("Creating config: Character - Portrait Style")
            await service.create_config(
            entity_type="character",
            display_name="Portrait Style (Default)",
            composition_style="portrait",
            framing="closeup",
            angle="eye_level",
            background="simple_scene",
            lighting="natural",
            additional_instructions="Create a character portrait showing face and upper body clearly. Use natural lighting and simple background that doesn't distract from the character. Focus on capturing facial features, expression, and overall appearance accurately.",
            image_size="1024x1024",
            model="gemini/gemini-2.5-flash-image",
            is_default=True
            )
            logger.info("Character config created\n")
        except Exception as e:
            logger.warning(f"Failed to create character config: {e}\n")

        # Outfit Config - Full Body
        try:
            logger.info("Creating config: Outfit - Full Body Display")
            await service.create_config(
                entity_type="outfit",
                display_name="Full Body Display (Default)",
                composition_style="mannequin",
                framing="full",
                angle="front",
                background="white",
                lighting="soft_even",
                additional_instructions="Display complete outfit on a featureless mannequin against pure white background. Show full body to capture all clothing items. Use even, professional lighting to show colors and fabrics accurately.",
                image_size="1024x1024",
                model="gemini/gemini-2.5-flash-image",
                is_default=True
            )
            logger.info("Outfit config created\n")
        except Exception as e:
            logger.warning(f"Failed to create outfit config: {e}\n")

        # Clothing Item Config - Flat Lay Alternative
        try:
            logger.info("Creating config: Clothing Item - Flat Lay Style")
            await service.create_config(
                entity_type="clothing_item",
                display_name="Flat Lay Style",
                composition_style="flat_lay",
                framing="medium",
                angle="top_down",
                background="white",
                lighting="soft_even",
                additional_instructions="Styled flat lay arrangement of the clothing item from overhead view. Item is laid flat and arranged artfully. Pure white background. Perfect for accessories, bags, and items that look better laid flat.",
                image_size="1024x1024",
                model="gemini/gemini-2.5-flash-image",
                is_default=False
            )
            logger.info("Clothing item flat lay config created\n")
        except Exception as e:
            logger.warning(f"Failed to create flat lay config: {e}\n")

        # Character Config - Full Body Alternative
        try:
            logger.info("Creating config: Character - Full Body Pose")
            await service.create_config(
                entity_type="character",
                display_name="Full Body Pose",
                composition_style="portrait",
                framing="full",
                angle="eye_level",
                background="simple_scene",
                lighting="natural",
                additional_instructions="Full body character pose showing complete appearance including clothing, body type, and stance. Natural lighting with simple background. Useful for character reference sheets and full costume visualization.",
                image_size="1024x1024",
                model="gemini/gemini-2.5-flash-image",
                is_default=False
            )
            logger.info("Character full body config created\n")
        except Exception as e:
            logger.warning(f"Failed to create character full body config: {e}\n")

        # Outfit Config - Lifestyle Alternative
        try:
            logger.info("Creating config: Outfit - Lifestyle Shot")
            await service.create_config(
                entity_type="outfit",
                display_name="Lifestyle Shot",
                composition_style="lifestyle",
                framing="full",
                angle="eye_level",
                background="detailed_scene",
                lighting="natural",
                additional_instructions="Lifestyle shot showing outfit in context with environmental scene. More natural and relatable than mannequin display. Shows how outfit looks when worn in real situations.",
                image_size="1024x1024",
                model="gemini/gemini-2.5-flash-image",
                is_default=False
            )
            logger.info("Outfit lifestyle config created\n")
        except Exception as e:
            logger.warning(f"Failed to create outfit lifestyle config: {e}\n")

        logger.info("Default visualization configs initialized!")
        logger.info("\nSummary:")
        summary = await service.get_entity_types_summary()
        for entity_type, count in summary.items():
            logger.info(f"  - {entity_type}: {count} configs")


if __name__ == "__main__":
    asyncio.run(create_default_configs())
