#!/usr/bin/env python3
"""
Style Transfer Generator

Transfer visual style from one image to another while preserving the subject.

Usage:
    python ai_tools/style_transfer_generator/tool.py <subject> --style <style_preset>
"""

import sys
from pathlib import Path
from typing import Optional, Union
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.modular_image_generator.tool import ModularImageGenerator
from dotenv import load_dotenv
from api.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()


class StyleTransferGenerator(ModularImageGenerator):
    """
    Specialized generator for style transfer.

    Transfers visual style to subject while preserving identity.
    """

    def transfer_style(
        self,
        subject_image: Union[Path, str],
        style: str,
        strength: float = 0.8,
        output_dir: str = "output/style_transfer"
    ):
        """
        Transfer style to subject image

        Args:
            subject_image: Source image
            style: Visual style preset name
            strength: Style transfer strength (0.0-1.0)
            output_dir: Output directory

        Returns:
            ImageGenerationResult
        """
        logger.info(f"\n{'='*70}")
        logger.info("STYLE TRANSFER")
        logger.info(f"{'='*70}\n")
        logger.info(f"Subject: {Path(subject_image).name}")
        logger.info(f"Style: {style}")
        logger.info(f"Strength: {strength}")

        # Use modular generator with only visual style
        return self.generate(
            subject_image=subject_image,
            visual_style=style,
            output_dir=output_dir,
            temperature=strength
        )


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Transfer visual style to subject image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transfer style
  python tool.py subject.jpg --style film-noir

  # Adjust strength
  python tool.py subject.jpg --style vintage-warm --strength 0.9

  # Custom output
  python tool.py subject.jpg --style modern-clean --output output/custom/
        """
    )

    parser.add_argument('subject', help='Subject image path')
    parser.add_argument('--style', required=True, help='Visual style preset name')
    parser.add_argument('--strength', type=float, default=0.8, help='Transfer strength (default: 0.8)')
    parser.add_argument('--output', default='output/style_transfer', help='Output directory')
    parser.add_argument('--model', help='Model to use (default from config)')

    args = parser.parse_args()

    try:
        generator = StyleTransferGenerator(model=args.model)
        result = generator.transfer_style(
            subject_image=args.subject,
            style=args.style,
            strength=args.strength,
            output_dir=args.output
        )

        logger.info(f"\n{'='*70}")
        logger.info("STYLE TRANSFER COMPLETE")
        logger.info(f"{'='*70}\n")

    except Exception as e:
        logger.error(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
