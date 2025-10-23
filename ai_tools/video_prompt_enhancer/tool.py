#!/usr/bin/env python3
"""
Video Prompt Enhancer

Enhance video generation prompts using GPT-4o or GPT-5.

Takes a simple prompt and enhances it with detailed descriptions for better video generation.

Usage:
    python ai_tools/video_prompt_enhancer/tool.py "person walking on beach"
"""

import sys
from pathlib import Path
from typing import Optional

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.shared.router import LLMRouter, RouterConfig
from dotenv import load_dotenv
from api.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()


ENHANCEMENT_TEMPLATE = """You are a video prompt enhancement specialist. Your task is to take a simple video prompt and expand it into a detailed, cinematic description optimized for AI video generation.

Original prompt: "{original_prompt}"

Enhance this prompt by:
1. Adding specific camera movements and angles
2. Including lighting and atmosphere details
3. Describing motion and timing
4. Adding environmental details
5. Specifying mood and emotion
6. Including technical aspects (frame rate feel, cinematography style)

Keep the enhanced prompt under 500 characters and focused on visual, actionable details.

Return ONLY the enhanced prompt, nothing else."""


class VideoPromptEnhancer:
    """
    Enhance video prompts using LLM.

    Takes simple prompts and expands them for better video generation.
    """

    def __init__(self, model: Optional[str] = None):
        """
        Initialize video prompt enhancer

        Args:
            model: Model to use (default from config or gpt-4o)
        """
        if model is None:
            try:
                config = RouterConfig()
                model = config.get_model_for_tool("video_prompt_enhancer")
            except:
                model = "gpt-4o"

        self.router = LLMRouter(model=model)

    def enhance(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Enhance a video prompt

        Args:
            prompt: Original simple prompt
            temperature: Generation temperature (default: 0.7)

        Returns:
            Enhanced prompt string
        """
        logger.info(f"\n{'='*70}")
        logger.info("VIDEO PROMPT ENHANCEMENT")
        logger.info(f"{'='*70}\n")
        logger.info(f"Original: {prompt}")
        logger.info(f"Model: {self.router.model}")

        enhancement_prompt = ENHANCEMENT_TEMPLATE.format(original_prompt=prompt)

        enhanced = self.router.call(
            prompt=enhancement_prompt,
            temperature=temperature
        )

        # Clean up response
        enhanced = enhanced.strip().strip('"').strip("'")

        logger.info(f"\n{'='*70}")
        logger.info(f"Enhanced: {enhanced}")
        logger.info(f"{'='*70}\n")

        return enhanced


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhance video generation prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enhance a prompt
  python tool.py "person walking on beach"

  # With custom model
  python tool.py "city at night" --model gpt-4o

  # Adjust creativity
  python tool.py "forest scene" --temperature 0.9
        """
    )

    parser.add_argument(
        'prompt',
        help='Original video prompt to enhance'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default: gpt-4o)'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='Generation temperature (default: 0.7)'
    )

    args = parser.parse_args()

    try:
        enhancer = VideoPromptEnhancer(model=args.model)
        enhanced = enhancer.enhance(args.prompt, temperature=args.temperature)

        # Print for easy copying
        logger.info("\n📋 Copy enhanced prompt:")
        logger.info(f"\n{enhanced}\n")

    except Exception as e:
        logger.error(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
