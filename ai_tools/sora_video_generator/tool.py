#!/usr/bin/env python3
"""
Sora Video Generator

Generate videos using OpenAI's Sora API.

Usage:
    python ai_tools/sora_video_generator/tool.py "person walking on beach" \
        --duration 4 \
        --size 720x1280
"""

import sys
import os
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import VideoGenerationResult, VideoGenerationRequest, VideoModel
from ai_tools.video_prompt_enhancer.tool import VideoPromptEnhancer
from dotenv import load_dotenv

load_dotenv()


class SoraVideoGenerator:
    """
    Generate videos using Sora API.

    Features:
    - Automatic prompt enhancement
    - Multiple aspect ratios
    - Duration control (4-12 seconds)
    - Pro and standard models
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Sora video generator

        Args:
            api_key: OpenAI API key (default: from OPENAI_API_KEY env)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package required: pip install openai")

        self.enhancer = VideoPromptEnhancer()

    def generate(
        self,
        prompt: str,
        model: str = "sora-2-pro",
        size: str = "720x1280",  # 9:16 portrait
        seconds: int = 4,
        skip_enhancement: bool = False,
        output_dir: str = "output/videos"
    ) -> VideoGenerationResult:
        """
        Generate video with Sora

        Args:
            prompt: Video description
            model: Model to use (sora-2, sora-2-pro)
            size: Resolution (720x1280=9:16, 1792x1024=16:9, 1024x1792=9:16 tall)
            seconds: Duration in seconds (4-12)
            skip_enhancement: Skip prompt enhancement
            output_dir: Output directory

        Returns:
            VideoGenerationResult
        """
        print(f"\n{'='*70}")
        print("SORA VIDEO GENERATION")
        print(f"{'='*70}\n")

        # Enhance prompt if needed
        if skip_enhancement:
            enhanced_prompt = prompt
            print(f"Prompt: {prompt}")
        else:
            print(f"Original prompt: {prompt}")
            enhanced_prompt = self.enhancer.enhance(prompt)
            print(f"Enhanced prompt: {enhanced_prompt}")

        print(f"\nModel: {model}")
        print(f"Size: {size}")
        print(f"Duration: {seconds}s")

        # Calculate cost
        cost_per_second = 0.50 if model == "sora-2-pro" else 0.125
        estimated_cost = seconds * cost_per_second

        print(f"Estimated cost: ${estimated_cost:.2f}")
        print(f"\n🎬 Generating video...")

        # Generate video
        start_time = datetime.now()

        try:
            response = self.client.videos.generate(
                model=model,
                prompt=enhanced_prompt,
                size=size,
                seconds=seconds
            )

            # Wait for video to be ready
            video_id = response.id
            print(f"Video ID: {video_id}")
            print(f"⏳ Waiting for video to be ready...")

            while True:
                status = self.client.videos.retrieve(video_id)
                if status.status == "completed":
                    break
                elif status.status == "failed":
                    raise Exception(f"Video generation failed: {status.error}")
                time.sleep(2)
                print(".", end="", flush=True)

            print("\n✅ Video ready")

            # Download video
            video_bytes = self.client.videos.content(video_id)

            # Save video
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sora_{timestamp}.mp4"
            file_path = output_path / filename

            with open(file_path, 'wb') as f:
                f.write(video_bytes)

            file_size_mb = len(video_bytes) / (1024 * 1024)
            generation_time = (datetime.now() - start_time).total_seconds()

            print(f"\n✅ Saved: {file_path}")
            print(f"   Size: {file_size_mb:.1f} MB")
            print(f"   Time: {generation_time:.1f}s")
            print(f"   Cost: ${estimated_cost:.2f}")

            # Create result
            request = VideoGenerationRequest(
                prompt=prompt,
                enhanced_prompt=enhanced_prompt if not skip_enhancement else None,
                model=VideoModel.SORA_2_PRO if model == "sora-2-pro" else VideoModel.SORA_2,
                size=size,
                seconds=seconds,
                skip_enhancement=skip_enhancement
            )

            result = VideoGenerationResult(
                file_path=str(file_path),
                video_id=video_id,
                request=request,
                model_used=model,
                file_size_mb=file_size_mb,
                generation_time=generation_time,
                cost_estimate=estimated_cost
            )

            return result

        except Exception as e:
            raise Exception(f"Failed to generate video: {e}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate videos with Sora",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 9:16 portrait video
  python tool.py "person walking on beach" --size 720x1280

  # Generate 16:9 landscape video
  python tool.py "city skyline at sunset" --size 1792x1024 --duration 8

  # Use standard model (cheaper)
  python tool.py "forest scene" --model sora-2 --duration 4

  # Skip prompt enhancement
  python tool.py "detailed prompt here" --skip-enhancement

Sizes:
  - 720x1280: 9:16 portrait (mobile)
  - 1792x1024: 16:9 landscape (desktop)
  - 1024x1792: 9:16 tall portrait

Models:
  - sora-2: $0.125/second
  - sora-2-pro: $0.50/second
        """
    )

    parser.add_argument(
        'prompt',
        help='Video description'
    )

    parser.add_argument(
        '--model',
        default='sora-2-pro',
        choices=['sora-2', 'sora-2-pro'],
        help='Model to use (default: sora-2-pro)'
    )

    parser.add_argument(
        '--size',
        default='720x1280',
        help='Video size (default: 720x1280 for 9:16 portrait)'
    )

    parser.add_argument(
        '--duration',
        type=int,
        default=4,
        choices=range(4, 13),
        help='Duration in seconds (4-12, default: 4)'
    )

    parser.add_argument(
        '--skip-enhancement',
        action='store_true',
        help='Skip automatic prompt enhancement'
    )

    parser.add_argument(
        '--output',
        default='output/videos',
        help='Output directory (default: output/videos)'
    )

    args = parser.parse_args()

    try:
        generator = SoraVideoGenerator()
        result = generator.generate(
            prompt=args.prompt,
            model=args.model,
            size=args.size,
            seconds=args.duration,
            skip_enhancement=args.skip_enhancement,
            output_dir=args.output
        )

        print(f"\n{'='*70}")
        print("VIDEO GENERATION COMPLETE")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
