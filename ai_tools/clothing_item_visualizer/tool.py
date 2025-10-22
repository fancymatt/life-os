"""
Clothing Item Visualizer Tool

Creates standalone visualizations of individual clothing items from their specifications.
Generates clean reference images showing the item on a mannequin or as a flat lay.

Features:
- Pure text-to-image generation from item specs
- Square format on white background
- Automatic generation when items are created
- Reference images for verification
"""

from pathlib import Path
from typing import Optional, Union
from datetime import datetime
import sys
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import ClothingItemEntity
from ai_tools.shared.router import LLMRouter, RouterConfig


class ClothingItemVisualizer:
    """
    Generates standalone visualizations of individual clothing items

    Creates clean, reference-quality images showing clothing items on
    mannequins or as styled flat lays on white backgrounds.
    """

    def __init__(self, model: Optional[str] = None):
        """
        Initialize the clothing item visualizer

        Args:
            model: Model to use for generation (default: gemini-2.5-flash-image)
        """
        # Use Gemini for image generation (better quality and cost)
        self.model = model or "gemini/gemini-2.5-flash-image"
        self.router = LLMRouter(model=self.model)

        # Load prompt template
        self.template_path = Path(__file__).parent / "template.md"
        with open(self.template_path, 'r') as f:
            self.prompt_template = f.read()

    def _construct_item_description(self, item: ClothingItemEntity) -> str:
        """
        Construct detailed description from clothing item spec

        Args:
            item: The clothing item entity

        Returns:
            Formatted description text
        """
        parts = []

        parts.append(f"CATEGORY: {item.category.upper()}")
        parts.append(f"ITEM: {item.item}")
        parts.append(f"COLOR: {item.color}")
        parts.append(f"FABRIC: {item.fabric}")
        parts.append(f"\nDETAILS: {item.details}")

        return "\n".join(parts)

    def _construct_generation_prompt(self, item: ClothingItemEntity) -> str:
        """
        Construct the complete generation prompt

        Args:
            item: Clothing item entity

        Returns:
            Complete prompt for image generation
        """
        item_description = self._construct_item_description(item)

        prompt = f"""{self.prompt_template}

{item_description}

Create a professional, clean visualization of this single clothing item. Display it on a simple mannequin (for worn items) or as a styled flat lay (for accessories), against a pure white background.

**CRITICAL COLOR ACCURACY:**
The color must exactly match the specification above: {item.color}. Pay careful attention to getting the color and all details correct.

The visualization should clearly show the item's fabric, color, and construction details."""

        return prompt

    def visualize(
        self,
        item: Union[ClothingItemEntity, dict, str],
        output_dir: Union[Path, str] = None,
        item_id: Optional[str] = None
    ) -> Path:
        """
        Generate a visualization of a clothing item

        Args:
            item: ClothingItemEntity object, dict, or item_id
            output_dir: Directory to save visualization (default: data/clothing_items)
            item_id: Optional item ID for filename

        Returns:
            Path to generated visualization
        """
        # Handle different input types
        if isinstance(item, str):
            # Load from file
            from api.config import settings
            item_path = settings.base_dir / "data" / "clothing_items" / f"{item}.json"
            with open(item_path, 'r') as f:
                data = json.load(f)
            item = ClothingItemEntity(**data)
            item_id = item_id or item.item_id
        elif isinstance(item, dict):
            item = ClothingItemEntity(**item)
            item_id = item_id or item.get('item_id')

        # Default output directory
        if output_dir is None:
            from api.config import settings
            output_dir = settings.base_dir / "data" / "clothing_items"

        output_dir = Path(output_dir)

        # Construct generation prompt
        prompt = self._construct_generation_prompt(item)

        print(f"\n🎨 Generating clothing item visualization...")
        print(f"   Category: {item.category}")
        print(f"   Item: {item.item}")
        print(f"   Color: {item.color}")

        try:
            # Truncate prompt if too long
            if len(prompt) > 3900:
                prompt = prompt[:3900] + "..."

            # Generate image using Gemini
            image_bytes = self.router.generate_image(
                prompt=prompt,
                model=self.model,
                provider="gemini",
                size="1024x1024"  # Square format
            )

            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate output filename
            if item_id:
                filename = f"{item_id}_preview.png"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"item_viz_{timestamp}.png"

            output_path = output_dir / filename

            # Save generated image
            with open(output_path, 'wb') as f:
                f.write(image_bytes)

            print(f"✅ Visualization saved: {output_path}")

            return output_path

        except Exception as e:
            raise Exception(f"Failed to generate visualization: {e}")


def main():
    """CLI interface for clothing item visualizer"""
    import argparse
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Generate standalone clothing item visualizations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Visualize from item ID
  python tool.py --item abc123-def456

  # Visualize from item file
  python tool.py --file data/clothing_items/abc123.json

  # Specify output directory
  python tool.py --item abc123 --output output/my_viz
        """
    )

    parser.add_argument(
        '--item',
        help='Item ID to visualize'
    )

    parser.add_argument(
        '--file',
        help='Path to item JSON file'
    )

    parser.add_argument(
        '--output',
        help='Output directory (default: data/clothing_items)'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default: gemini-2.5-flash-image)'
    )

    args = parser.parse_args()

    if not args.item and not args.file:
        parser.error("Either --item or --file must be specified")

    try:
        visualizer = ClothingItemVisualizer(model=args.model)

        if args.file:
            with open(args.file, 'r') as f:
                data = json.load(f)
            item = ClothingItemEntity(**data)
            item_id = data.get('item_id')
        else:
            item = args.item
            item_id = args.item

        output_path = visualizer.visualize(
            item=item,
            output_dir=args.output,
            item_id=item_id
        )

        print(f"\n✅ Visualization complete!")
        print(f"   Output: {output_path}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
