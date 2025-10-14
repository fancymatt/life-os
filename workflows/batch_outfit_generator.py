#!/usr/bin/env python3
"""
Batch Outfit Generator Workflow

Generates multiple images by combining:
- N subject images
- M outfit presets
- K visual style presets

Total generations: N × M × K

Features:
- Progress tracking
- Cost estimation
- Error handling and retry
- Organized output structure
- Summary reports

Usage:
    python batch_outfit_generator.py \
        --subjects path/to/subjects/*.jpg \
        --outfits outfit1,outfit2,outfit3 \
        --styles style1,style2 \
        --output output/batch

This generates: subjects × outfits × styles images
"""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_tools.outfit_generator.tool import OutfitGenerator
from ai_tools.shared.preset import PresetManager
from dotenv import load_dotenv

load_dotenv()


class BatchGenerationStats:
    """Track batch generation statistics"""

    def __init__(self):
        self.total = 0
        self.completed = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = None
        self.end_time = None
        self.errors = []

    def to_dict(self):
        elapsed = None
        if self.start_time and self.end_time:
            elapsed = (self.end_time - self.start_time).total_seconds()

        return {
            "total": self.total,
            "completed": self.completed,
            "failed": self.failed,
            "skipped": self.skipped,
            "success_rate": f"{(self.completed / self.total * 100):.1f}%" if self.total > 0 else "0%",
            "elapsed_seconds": elapsed,
            "errors": self.errors[:10]  # First 10 errors
        }


class BatchOutfitGenerator:
    """
    Batch generator for outfit transformations

    Generates all combinations of subjects × outfits × styles
    """

    def __init__(
        self,
        output_dir: Path = Path("output/batch"),
        skip_existing: bool = True,
        cost_per_image: float = 0.04
    ):
        """
        Initialize batch generator

        Args:
            output_dir: Base output directory
            skip_existing: Skip if output already exists
            cost_per_image: Cost per image generation (default: $0.04)
        """
        self.output_dir = output_dir
        self.skip_existing = skip_existing
        self.cost_per_image = cost_per_image
        self.generator = OutfitGenerator()
        self.preset_manager = PresetManager()
        self.stats = BatchGenerationStats()

    def validate_presets(
        self,
        outfit_names: List[str],
        style_names: Optional[List[str]] = None
    ):
        """Validate that all presets exist"""
        print("\n📋 Validating presets...")

        # Check outfits
        available_outfits = self.preset_manager.list("outfits")
        missing_outfits = [o for o in outfit_names if o not in available_outfits]

        if missing_outfits:
            print(f"❌ Missing outfit presets: {', '.join(missing_outfits)}")
            print(f"   Available: {', '.join(available_outfits)}")
            return False

        # Check styles
        if style_names:
            available_styles = self.preset_manager.list("visual_styles")
            missing_styles = [s for s in style_names if s not in available_styles]

            if missing_styles:
                print(f"❌ Missing style presets: {', '.join(missing_styles)}")
                print(f"   Available: {', '.join(available_styles)}")
                return False

        print(f"✅ All presets valid")
        print(f"   Outfits: {len(outfit_names)}")
        if style_names:
            print(f"   Styles: {len(style_names)}")

        return True

    def generate_batch(
        self,
        subject_images: List[Path],
        outfit_names: List[str],
        style_names: Optional[List[str]] = None,
        temperature: float = 0.8
    ):
        """
        Generate batch of images

        Args:
            subject_images: List of subject image paths
            outfit_names: List of outfit preset names
            style_names: Optional list of style preset names
            temperature: Generation temperature

        Returns:
            BatchGenerationStats
        """
        # Validate inputs
        if not subject_images:
            raise ValueError("No subject images provided")

        if not outfit_names:
            raise ValueError("No outfit presets provided")

        # Validate presets exist
        if not self.validate_presets(outfit_names, style_names):
            raise ValueError("Preset validation failed")

        # Calculate totals
        styles_to_use = style_names if style_names else [None]
        self.stats.total = len(subject_images) * len(outfit_names) * len(styles_to_use)
        estimated_cost = self.stats.total * self.cost_per_image

        # Print summary
        print("\n" + "=" * 70)
        print("BATCH GENERATION PLAN")
        print("=" * 70)
        print(f"\nSubjects: {len(subject_images)}")
        for i, subject in enumerate(subject_images[:5], 1):
            print(f"  {i}. {subject.name}")
        if len(subject_images) > 5:
            print(f"  ... and {len(subject_images) - 5} more")

        print(f"\nOutfits: {len(outfit_names)}")
        for outfit in outfit_names:
            print(f"  - {outfit}")

        if style_names:
            print(f"\nStyles: {len(style_names)}")
            for style in style_names:
                print(f"  - {style}")
        else:
            print(f"\nStyles: None (using default black background)")

        print(f"\n📊 Total generations: {self.stats.total}")
        print(f"💰 Estimated cost: ${estimated_cost:.2f}")
        print(f"📁 Output: {self.output_dir}")

        input(f"\nPress Enter to continue (or Ctrl+C to cancel)...")

        # Start generation
        print("\n" + "=" * 70)
        print("STARTING BATCH GENERATION")
        print("=" * 70)

        self.stats.start_time = datetime.now()
        current = 0

        for subject in subject_images:
            for outfit in outfit_names:
                for style in styles_to_use:
                    current += 1

                    # Build output path
                    subject_name = subject.stem
                    style_name = style if style else "default"
                    output_subdir = self.output_dir / subject_name / outfit
                    output_path = output_subdir / f"{style_name}.png"

                    # Skip if exists
                    if self.skip_existing and output_path.exists():
                        print(f"\n[{current}/{self.stats.total}] ⏭️  Skipping (exists)")
                        print(f"   {subject.name} × {outfit} × {style_name}")
                        self.stats.skipped += 1
                        continue

                    # Generate
                    print(f"\n[{current}/{self.stats.total}] 🎨 Generating...")
                    print(f"   Subject: {subject.name}")
                    print(f"   Outfit: {outfit}")
                    if style:
                        print(f"   Style: {style}")

                    try:
                        result = self.generator.generate(
                            subject_image=subject,
                            outfit=outfit,
                            visual_style=style,
                            output_dir=str(output_subdir),
                            temperature=temperature
                        )

                        # Rename to standard name
                        generated_path = Path(result.file_path)
                        if generated_path.exists() and generated_path != output_path:
                            generated_path.rename(output_path)

                        print(f"   ✅ Saved: {output_path.relative_to(self.output_dir)}")
                        self.stats.completed += 1

                    except Exception as e:
                        print(f"   ❌ Failed: {e}")
                        self.stats.failed += 1
                        self.stats.errors.append({
                            "subject": subject.name,
                            "outfit": outfit,
                            "style": style,
                            "error": str(e)
                        })

        self.stats.end_time = datetime.now()

        # Print summary
        self._print_summary()

        # Save report
        self._save_report()

        return self.stats

    def _print_summary(self):
        """Print generation summary"""
        print("\n" + "=" * 70)
        print("BATCH GENERATION COMPLETE")
        print("=" * 70)

        elapsed = (self.stats.end_time - self.stats.start_time).total_seconds()

        print(f"\n📊 Results:")
        print(f"   Total: {self.stats.total}")
        print(f"   ✅ Completed: {self.stats.completed}")
        print(f"   ❌ Failed: {self.stats.failed}")
        print(f"   ⏭️  Skipped: {self.stats.skipped}")
        print(f"   Success Rate: {(self.stats.completed / self.stats.total * 100):.1f}%")

        print(f"\n⏱️  Time:")
        print(f"   Elapsed: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
        if self.stats.completed > 0:
            print(f"   Per image: {elapsed/self.stats.completed:.1f}s")

        print(f"\n💰 Cost:")
        actual_cost = self.stats.completed * self.cost_per_image
        print(f"   Estimated: ${self.stats.total * self.cost_per_image:.2f}")
        print(f"   Actual: ${actual_cost:.2f}")

        if self.stats.failed > 0:
            print(f"\n❌ Errors ({self.stats.failed}):")
            for error in self.stats.errors[:5]:
                print(f"   - {error['subject']} × {error['outfit']}: {error['error'][:80]}")
            if len(self.stats.errors) > 5:
                print(f"   ... and {len(self.stats.errors) - 5} more")

        print(f"\n📁 Output: {self.output_dir}")

    def _save_report(self):
        """Save generation report"""
        report_path = self.output_dir / "_batch_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": self.stats.end_time.isoformat(),
            "statistics": self.stats.to_dict(),
            "output_directory": str(self.output_dir)
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved: {report_path}")


def main():
    """CLI interface for batch generation"""
    import argparse
    import glob

    parser = argparse.ArgumentParser(
        description="Batch outfit generation workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all combinations
  python batch_outfit_generator.py \\
    --subjects photos/*.jpg \\
    --outfits casual,formal,street \\
    --styles film-noir,vintage \\
    --output output/batch

  # Generate with single style
  python batch_outfit_generator.py \\
    --subjects person1.jpg person2.jpg \\
    --outfits summer-dress \\
    --style beach-sunset

  # Generate without style (black background)
  python batch_outfit_generator.py \\
    --subjects subject.jpg \\
    --outfits outfit1,outfit2,outfit3
        """
    )

    parser.add_argument(
        '--subjects',
        nargs='+',
        required=True,
        help='Subject images (supports glob patterns)'
    )

    parser.add_argument(
        '--outfits',
        required=True,
        help='Comma-separated outfit preset names'
    )

    parser.add_argument(
        '--styles',
        help='Comma-separated style preset names (optional)'
    )

    parser.add_argument(
        '--output',
        default='output/batch',
        help='Output directory (default: output/batch)'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        default=0.8,
        help='Generation temperature (default: 0.8)'
    )

    parser.add_argument(
        '--no-skip',
        action='store_true',
        help='Regenerate even if output exists'
    )

    parser.add_argument(
        '--cost',
        type=float,
        default=0.04,
        help='Cost per image (default: $0.04)'
    )

    args = parser.parse_args()

    try:
        # Parse subjects (expand globs)
        subject_paths = []
        for pattern in args.subjects:
            matches = glob.glob(pattern)
            if matches:
                subject_paths.extend([Path(p) for p in matches])
            else:
                # Not a glob, treat as literal path
                subject_paths.append(Path(pattern))

        # Validate subjects exist
        subject_paths = [p for p in subject_paths if p.exists()]
        if not subject_paths:
            print("❌ No valid subject images found")
            sys.exit(1)

        # Parse outfits
        outfit_names = [o.strip() for o in args.outfits.split(',')]

        # Parse styles
        style_names = None
        if args.styles:
            style_names = [s.strip() for s in args.styles.split(',')]

        # Create generator
        batch_gen = BatchOutfitGenerator(
            output_dir=Path(args.output),
            skip_existing=not args.no_skip,
            cost_per_image=args.cost
        )

        # Run batch
        stats = batch_gen.generate_batch(
            subject_images=subject_paths,
            outfit_names=outfit_names,
            style_names=style_names,
            temperature=args.temperature
        )

        # Exit with appropriate code
        if stats.failed > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
