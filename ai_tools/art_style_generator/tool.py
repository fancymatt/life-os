#!/usr/bin/env python3
"""
Art Style Generator

Generate images with artistic style treatments.

Usage:
    python ai_tools/art_style_generator/tool.py <subject> --art-style <art_preset>
"""

import sys
from pathlib import Path
from typing import Optional, Union

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.modular_image_generator.tool import ModularImageGenerator
from dotenv import load_dotenv
from api.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()


class ArtStyleGenerator(ModularImageGenerator):
    """
    Specialized generator for artistic style.

    Renders subject in various artistic styles (oil painting, watercolor, etc.)
    """

    def generate_art(
        self,
        subject_image: Union[Path, str],
        art_style: str,
        output_dir: str = "output/art_style"
    ):
        """
        Generate image with artistic style

        Args:
            subject_image: Source image
            art_style: Art style preset name
            output_dir: Output directory

        Returns:
            ImageGenerationResult
        """
        logger.info(f"\n{'='*70}")
        logger.info("ART STYLE GENERATION")
        logger.info(f"{'='*70}\n")
        logger.info(f"Subject: {Path(subject_image).name}")
        logger.info(f"Art Style: {art_style}")

        # Use modular generator with only art style
        return self.generate(
            subject_image=subject_image,
            art_style=art_style,
            output_dir=output_dir
        )


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate images with artistic style",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with art style
  python tool.py subject.jpg --art-style impressionist

  # Oil painting style
  python tool.py subject.jpg --art-style oil-painting

  # Custom output
  python tool.py subject.jpg --art-style watercolor --output output/custom/
        """
    )

    parser.add_argument('subject', help='Subject image path')
    parser.add_argument('--art-style', required=True, help='Art style preset name')
    parser.add_argument('--output', default='output/art_style', help='Output directory')
    parser.add_argument('--model', help='Model to use (default from config)')

    args = parser.parse_args()

    try:
        generator = ArtStyleGenerator(model=args.model)
        result = generator.generate_art(
            subject_image=args.subject,
            art_style=args.art_style,
            output_dir=args.output
        )

        logger.info(f"\n{'='*70}")
        logger.info("ART STYLE GENERATION COMPLETE")
        logger.info(f"{'='*70}\n")

    except Exception as e:
        logger.error(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
