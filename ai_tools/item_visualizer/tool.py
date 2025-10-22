"""
Item Visualizer Tool

Generic visualization tool for any entity type. Uses configurable visualization
settings to generate preview images with consistent style and composition.

Features:
- Configurable composition, framing, lighting, and background
- Art style integration
- Reference image support
- Works with any entity type
"""

from pathlib import Path
from typing import Optional, Union, Dict, Any
from datetime import datetime
import sys
import json
import base64

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import (
    VisualizationConfigEntity,
    ArtStyleSpec,
    ClothingItemEntity,
    CharacterAppearanceSpec,
    OutfitSpec
)
from ai_tools.shared.router import LLMRouter


class ItemVisualizer:
    """
    Generic visualization tool for any entity type.

    Uses VisualizationConfigEntity to control how items are rendered,
    allowing consistent visualization across different entity types.
    """

    def __init__(self, config: Optional[VisualizationConfigEntity] = None):
        """
        Initialize the item visualizer

        Args:
            config: Optional default visualization config
        """
        self.default_config = config
        self.router = LLMRouter()

    def _load_art_style(self, art_style_id: str) -> Optional[ArtStyleSpec]:
        """
        Load an art style preset by ID

        Args:
            art_style_id: UUID of art style preset

        Returns:
            ArtStyleSpec or None if not found
        """
        try:
            from api.config import settings
            art_style_path = settings.presets_dir / "art_styles" / f"{art_style_id}.json"

            if not art_style_path.exists():
                print(f"⚠️  Art style {art_style_id} not found")
                return None

            with open(art_style_path, 'r') as f:
                data = json.load(f)
                # Remove metadata if present
                data.pop('_metadata', None)
                return ArtStyleSpec(**data)
        except Exception as e:
            print(f"⚠️  Failed to load art style {art_style_id}: {e}")
            return None

    def _load_reference_image(self, reference_path: str) -> Optional[str]:
        """
        Load reference image and encode as base64

        Args:
            reference_path: URL path to reference image (e.g., /uploads/file.png)

        Returns:
            Base64 encoded image or None
        """
        try:
            from api.config import settings

            # Convert URL path to filesystem path
            if reference_path.startswith('/uploads/'):
                ref_img_name = reference_path[len('/uploads/'):]
                full_path = settings.upload_dir / ref_img_name
            elif reference_path.startswith('/output/'):
                ref_img_name = reference_path[len('/output/'):]
                full_path = settings.output_dir / ref_img_name
            elif reference_path.startswith('/'):
                # Strip leading slash for relative path
                full_path = settings.base_dir / reference_path[1:]
            else:
                # Already relative path
                full_path = settings.base_dir / reference_path

            if not full_path.exists():
                print(f"⚠️  Reference image not found: {reference_path}")
                print(f"   Tried filesystem path: {full_path}")
                return None

            with open(full_path, 'rb') as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            print(f"⚠️  Failed to load reference image: {e}")
            return None

    def _entity_to_description(self, entity: Any, entity_type: str) -> str:
        """
        Convert entity to natural language description

        Args:
            entity: The entity object
            entity_type: Type of entity (for formatting)

        Returns:
            Formatted description string
        """
        if isinstance(entity, ClothingItemEntity):
            return f"""CLOTHING ITEM:
Type: {entity.item}
Category: {entity.category}
Fabric: {entity.fabric}
Color: {entity.color}
Details: {entity.details}"""

        elif isinstance(entity, CharacterAppearanceSpec):
            return f"""CHARACTER:
Age: {entity.age}
Skin Tone: {entity.skin_tone}
Face: {entity.face_description}
Hair: {entity.hair_description}
Body: {entity.body_description}"""

        elif isinstance(entity, OutfitSpec):
            items_desc = "\n".join([f"- {item.item}: {item.color} {item.fabric}, {item.details}"
                                   for item in entity.clothing_items])
            return f"""OUTFIT: {entity.suggested_name}
Style: {entity.style_genre}
Formality: {entity.formality}
Aesthetic: {entity.aesthetic}

Items:
{items_desc}"""

        elif isinstance(entity, dict):
            # Generic dict handling - format key-value pairs
            lines = []
            for key, value in entity.items():
                if not key.startswith('_') and value is not None:
                    lines.append(f"{key}: {value}")
            return "\n".join(lines)

        else:
            # Fallback: use entity's __dict__
            return str(entity)

    def _construct_prompt(
        self,
        entity: Any,
        entity_type: str,
        config: VisualizationConfigEntity,
        art_style: Optional[ArtStyleSpec] = None,
        reference_image_b64: Optional[str] = None
    ) -> str:
        """
        Construct visualization prompt from all inputs

        Args:
            entity: The entity to visualize
            entity_type: Type of entity
            config: Visualization configuration
            art_style: Optional art style to apply
            reference_image_b64: Optional reference image (base64)

        Returns:
            Complete prompt for image generation
        """
        # Start with entity description
        entity_desc = self._entity_to_description(entity, entity_type)

        # Build composition instructions
        composition_instructions = f"""
COMPOSITION SETTINGS:
- Style: {config.composition_style.value}
- Framing: {config.framing.value}
- Camera Angle: {config.angle.value}
- Background: {config.background.value}
- Lighting: {config.lighting.value}
"""

        # Add art style if provided
        art_style_instructions = ""
        if art_style:
            art_style_instructions = f"""
ART STYLE:
- Medium: {art_style.medium}
- Technique: {art_style.technique}
- Color Palette: {', '.join(art_style.color_palette)}
- Texture: {art_style.texture}
- Mood: {art_style.mood}
- Detail Level: {art_style.level_of_detail}
"""

        # Add reference image note if provided
        reference_note = ""
        if reference_image_b64:
            reference_note = "\nREFERENCE IMAGE PROVIDED: Use the attached reference image as a guide for composition, framing, and overall visual approach.\n"

        # Add additional instructions
        additional = ""
        if config.additional_instructions:
            additional = f"\nADDITIONAL INSTRUCTIONS:\n{config.additional_instructions}\n"

        # Construct complete prompt
        prompt = f"""Create a high-quality visualization of the following item.

{entity_desc}

{composition_instructions}
{art_style_instructions}
{reference_note}
{additional}

CRITICAL REQUIREMENTS:
- The visualization must accurately represent the item described above
- Follow the composition settings exactly (framing, angle, background, lighting)
{f"- Apply the specified art style consistently ({art_style.suggested_name})" if art_style else ""}
- Ensure professional, clean presentation suitable for a catalog or portfolio
- Image size: {config.image_size}

Generate a single, high-quality preview image that clearly shows the item."""

        return prompt

    def visualize(
        self,
        entity: Any,
        entity_type: str,
        config: Optional[VisualizationConfigEntity] = None,
        output_dir: Union[Path, str] = None,
        filename: Optional[str] = None
    ) -> Path:
        """
        Generate a visualization of an entity

        Args:
            entity: The entity to visualize (ClothingItemEntity, CharacterAppearanceSpec, dict, etc.)
            entity_type: Type of entity (e.g., "clothing_item", "character", "outfit")
            config: Visualization configuration (uses default if not provided)
            output_dir: Directory to save visualization
            filename: Optional output filename (without extension)

        Returns:
            Path to generated visualization
        """
        # Use provided config or default
        if config is None:
            if self.default_config is None:
                raise ValueError("No visualization config provided and no default config set")
            config = self.default_config

        # Set output directory
        if output_dir is None:
            from api.config import settings
            output_dir = settings.base_dir / "data" / entity_type.replace('_', '-') + "s"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load art style if specified
        art_style = None
        if config.art_style_id:
            art_style = self._load_art_style(config.art_style_id)

        # Load reference image if specified
        reference_image_b64 = None
        if config.reference_image_path:
            reference_image_b64 = self._load_reference_image(config.reference_image_path)

        # Determine reference image path for Gemini generation
        # ONLY use config.reference_image_path - config should be self-contained
        # Do NOT fall back to entity.source_image (config applies to all entities of this type)
        reference_image_path = None
        if config.reference_image_path:
            from api.config import settings

            # Convert URL path to filesystem path
            # URL format: /uploads/filename.png -> filesystem: settings.upload_dir / filename.png
            # NOTE: Use ref_img_name to avoid shadowing the filename parameter!
            path_str = config.reference_image_path
            if path_str.startswith('/uploads/'):
                ref_img_name = path_str[len('/uploads/'):]
                reference_image_path = settings.upload_dir / ref_img_name
            elif path_str.startswith('/output/'):
                ref_img_name = path_str[len('/output/'):]
                reference_image_path = settings.output_dir / ref_img_name
            elif path_str.startswith('/'):
                # Strip leading slash for relative path
                reference_image_path = settings.base_dir / path_str[1:]
            else:
                # Already relative path
                reference_image_path = settings.base_dir / path_str

            # Verify reference image exists
            if not reference_image_path.exists():
                print(f"⚠️  Reference image not found: {config.reference_image_path}")
                print(f"   Tried filesystem path: {reference_image_path}")
                reference_image_path = None

        # Construct prompt
        prompt = self._construct_prompt(
            entity=entity,
            entity_type=entity_type,
            config=config,
            art_style=art_style,
            reference_image_b64=reference_image_b64
        )

        print(f"\n🎨 Generating visualization for {entity_type}...")
        print(f"   Config: {config.display_name}")
        if art_style:
            print(f"   Art Style: {art_style.suggested_name}")
        if reference_image_path:
            print(f"   Reference Image: {reference_image_path}")

        try:
            # Truncate prompt if too long
            if len(prompt) > 3900:
                prompt = prompt[:3900] + "..."

            # Generate image
            image_bytes = self.router.generate_image(
                prompt=prompt,
                image_path=reference_image_path,  # Pass reference image for Gemini
                model=config.model,
                provider="gemini",  # Extract provider from model string if needed
                size=config.image_size
            )

            # Generate output filename
            if filename:
                output_filename = f"{filename}.png"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{entity_type}_viz_{timestamp}.png"

            output_path = output_dir / output_filename

            # Save generated image
            with open(output_path, 'wb') as f:
                f.write(image_bytes)

            print(f"✅ Visualization saved: {output_path}")

            return output_path

        except Exception as e:
            raise Exception(f"Failed to generate visualization: {e}")


def main():
    """CLI interface for item visualizer"""
    import argparse
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Generate visualizations for any entity type",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Visualize a clothing item with default config
  python tool.py --entity-type clothing_item --entity-file data/clothing_items/abc123.json

  # Visualize with custom config
  python tool.py --entity-type clothing_item --entity-file data/clothing_items/abc123.json --config-file data/viz_configs/default_clothing.json
        """
    )

    parser.add_argument(
        '--entity-type',
        required=True,
        help='Type of entity (e.g., clothing_item, character, outfit)'
    )

    parser.add_argument(
        '--entity-file',
        required=True,
        help='Path to entity JSON file'
    )

    parser.add_argument(
        '--config-file',
        help='Path to visualization config JSON file'
    )

    parser.add_argument(
        '--output',
        help='Output directory'
    )

    args = parser.parse_args()

    try:
        # Load entity
        with open(args.entity_file, 'r') as f:
            entity_data = json.load(f)

        # Load config if provided
        config = None
        if args.config_file:
            with open(args.config_file, 'r') as f:
                config_data = json.load(f)
                config = VisualizationConfigEntity(**config_data)

        # Create visualizer
        visualizer = ItemVisualizer(config=config)

        # Generate visualization
        output_path = visualizer.visualize(
            entity=entity_data,
            entity_type=args.entity_type,
            output_dir=args.output
        )

        print(f"\n✅ Visualization complete!")
        print(f"   Output: {output_path}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
