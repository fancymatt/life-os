#!/usr/bin/env python3
"""
Initialize Default Visualization Configs

Creates default visualization configurations for standard entity types.
These configs define how different entities are rendered as preview images.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.visualization_config_service import VisualizationConfigService


def create_default_configs():
    """Create default visualization configs for all entity types"""

    service = VisualizationConfigService()

    print("🎨 Creating default visualization configs...\n")

    # Clothing Item Config
    try:
        print("Creating config: Clothing Item - Product Photography")
        service.create_config(
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
        print("✅ Clothing item config created\n")
    except Exception as e:
        print(f"⚠️  Failed to create clothing item config: {e}\n")

    # Character Config - Portrait Style
    try:
        print("Creating config: Character - Portrait Style")
        service.create_config(
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
        print("✅ Character config created\n")
    except Exception as e:
        print(f"⚠️  Failed to create character config: {e}\n")

    # Outfit Config - Full Body
    try:
        print("Creating config: Outfit - Full Body Display")
        service.create_config(
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
        print("✅ Outfit config created\n")
    except Exception as e:
        print(f"⚠️  Failed to create outfit config: {e}\n")

    # Clothing Item Config - Flat Lay Alternative
    try:
        print("Creating config: Clothing Item - Flat Lay Style")
        service.create_config(
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
        print("✅ Clothing item flat lay config created\n")
    except Exception as e:
        print(f"⚠️  Failed to create flat lay config: {e}\n")

    # Character Config - Full Body Alternative
    try:
        print("Creating config: Character - Full Body Pose")
        service.create_config(
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
        print("✅ Character full body config created\n")
    except Exception as e:
        print(f"⚠️  Failed to create character full body config: {e}\n")

    # Outfit Config - Lifestyle Alternative
    try:
        print("Creating config: Outfit - Lifestyle Shot")
        service.create_config(
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
        print("✅ Outfit lifestyle config created\n")
    except Exception as e:
        print(f"⚠️  Failed to create outfit lifestyle config: {e}\n")

    print("✅ Default visualization configs initialized!")
    print("\nSummary:")
    summary = service.get_entity_types_summary()
    for entity_type, count in summary.items():
        print(f"  - {entity_type}: {count} configs")


if __name__ == "__main__":
    create_default_configs()
