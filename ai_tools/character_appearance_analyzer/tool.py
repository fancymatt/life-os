#!/usr/bin/env python3
"""
Character Appearance Analyzer

Extracts detailed physical appearance description from character images.
Used to provide consistent character descriptions for story illustrations.
"""

import sys
from pathlib import Path
from typing import Optional, Union

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_capabilities.specs import CharacterAppearanceSpec
from dotenv import load_dotenv
from api.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()


class CharacterAppearanceAnalyzer:
    """
    Analyzes character images to extract detailed physical appearance descriptions.

    Optimized for creating consistent character descriptions for story illustrations.
    """

    def __init__(self, model: Optional[str] = None, temperature: Optional[float] = None):
        """
        Initialize character appearance analyzer

        Args:
            model: Model to use (default from config)
            temperature: Temperature to use (default from config)
        """
        config = RouterConfig()

        if model is None:
            model = config.get_model_for_tool("character_appearance_analyzer")

        if temperature is None:
            # Load temperature from config
            temperature = config.config.get('tool_settings', {}).get(
                'character_appearance_analyzer', {}
            ).get('temperature', 0.7)

        self.router = LLMRouter(model=model)
        self.temperature = temperature

        # Store template paths (but don't load yet - load fresh on each call)
        self.custom_template_path = Path(__file__).parent.parent.parent / "data" / "tool_configs" / "character_appearance_analyzer_template.md"
        self.base_template_path = Path(__file__).parent / "template.md"

    def _load_template(self) -> str:
        """Load the latest template (reloaded on each call to pick up edits)"""
        if self.custom_template_path.exists():
            template_path = self.custom_template_path
        else:
            template_path = self.base_template_path

        with open(template_path, 'r') as f:
            return f.read()

    def analyze(
        self,
        image_path: Union[Path, str]
    ) -> CharacterAppearanceSpec:
        """
        Analyze character appearance from image

        Args:
            image_path: Path to character image

        Returns:
            CharacterAppearanceSpec with detailed appearance information
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info(f"\n{'='*70}")
        logger.info(f"CHARACTER APPEARANCE ANALYSIS")
        logger.info(f"{'='*70}\n")
        logger.info(f"Image: {image_path.name}")

        # Load template fresh (picks up any edits immediately)
        prompt_template = self._load_template()

        # Use the template (no call_structured, just call with response_format)
        result = self.router.call_structured(
            prompt=prompt_template,
            response_model=CharacterAppearanceSpec,
            images=[image_path],
            temperature=self.temperature
        )

        logger.info(f"\nAnalysis complete")
        logger.info(f"\n📝 Summary:")
        logger.info(f"   Age: {result.age}")
        logger.info(f"   Hair: {result.hair_description}")
        logger.info(f"   Skin: {result.skin_tone}")

        return result

    async def aanalyze(
        self,
        image_path: Union[Path, str]
    ) -> CharacterAppearanceSpec:
        """
        Async version: Analyze character appearance from image

        Args:
            image_path: Path to character image

        Returns:
            CharacterAppearanceSpec with detailed appearance information
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info(f"\n{'='*70}")
        logger.info(f"CHARACTER APPEARANCE ANALYSIS (ASYNC)")
        logger.info(f"{'='*70}\n")
        logger.info(f"Image: {image_path.name}")

        # Load template fresh (picks up any edits immediately)
        prompt_template = self._load_template()

        # Use the template (no call_structured, just call with response_format)
        result = await self.router.acall_structured(
            prompt=prompt_template,
            response_model=CharacterAppearanceSpec,
            images=[image_path],
            temperature=self.temperature
        )

        logger.info(f"\nAnalysis complete")
        logger.info(f"\n📝 Summary:")
        logger.info(f"   Age: {result.age}")
        logger.info(f"   Hair: {result.hair_description}")
        logger.info(f"   Skin: {result.skin_tone}")

        return result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze character physical appearance from image",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'image',
        help='Path to character image'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default from config)'
    )

    args = parser.parse_args()

    try:
        analyzer = CharacterAppearanceAnalyzer(model=args.model)
        result = analyzer.analyze(args.image)

        # Print detailed results
        logger.info(f"\n{'='*70}")
        logger.info("DETAILED ANALYSIS")
        logger.info(f"{'='*70}\n")
        logger.info(f"Age: {result.age}")
        logger.info(f"Skin Tone: {result.skin_tone}")
        logger.info(f"\nFace: {result.face_description}")
        logger.info(f"\nHair: {result.hair_description}")
        logger.info(f"\nBody: {result.body_description}")
        logger.info(f"\n{'='*70}\n")

    except Exception as e:
        logger.error(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
