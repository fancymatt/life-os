#!/usr/bin/env python3
"""
Combined Transformation

Apply multiple transformations to an image at once.

Alias for modular_image_generator with preset combinations.

Usage:
    python ai_tools/combined_transformation/tool.py <subject> \
        --outfit <preset> \
        --visual-style <preset> \
        --hair-style <preset>
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.modular_image_generator.tool import ModularImageGenerator
from dotenv import load_dotenv
from api.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()


class CombinedTransformation(ModularImageGenerator):
    """
    Apply multiple transformations at once.

    This is an alias for ModularImageGenerator with a focus on
    combining multiple specs for complete transformations.
    """
    pass


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Apply multiple transformations to an image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Outfit + Style
  python tool.py subject.jpg \
    --outfit casual-outfit \
    --visual-style film-noir

  # Full transformation
  python tool.py subject.jpg \
    --outfit formal-suit \
    --visual-style vintage-style \
    --hair-style slicked-back \
    --makeup minimal

  # With art style
  python tool.py subject.jpg \
    --outfit modern-outfit \
    --art-style impressionist \
    --expression confident
        """
    )

    parser.add_argument('subject', help='Subject image path')
    parser.add_argument('--outfit', help='Outfit preset name')
    parser.add_argument('--visual-style', help='Visual style preset name')
    parser.add_argument('--art-style', help='Art style preset name')
    parser.add_argument('--hair-style', help='Hair style preset name')
    parser.add_argument('--hair-color', help='Hair color preset name')
    parser.add_argument('--makeup', help='Makeup preset name')
    parser.add_argument('--expression', help='Expression preset name')
    parser.add_argument('--accessories', help='Accessories preset name')
    parser.add_argument('--output', default='output/combined', help='Output directory')
    parser.add_argument('--temperature', type=float, default=0.8, help='Temperature')
    parser.add_argument('--model', help='Model to use (default from config)')

    args = parser.parse_args()

    try:
        generator = CombinedTransformation(model=args.model)

        logger.info(f"\n{'='*70}")
        logger.info("COMBINED TRANSFORMATION")
        logger.info(f"{'='*70}\n")

        result = generator.generate(
            subject_image=args.subject,
            outfit=args.outfit,
            visual_style=args.visual_style,
            art_style=args.art_style,
            hair_style=args.hair_style,
            hair_color=args.hair_color,
            makeup=args.makeup,
            expression=args.expression,
            accessories=args.accessories,
            output_dir=args.output,
            temperature=args.temperature
        )

        logger.info(f"\n{'='*70}")
        logger.info("COMBINED TRANSFORMATION COMPLETE")
        logger.info(f"{'='*70}\n")

    except Exception as e:
        logger.error(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
