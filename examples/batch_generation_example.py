#!/usr/bin/env python3
"""
Batch Generation Example

Demonstrates how to generate multiple outfit variations using the batch workflow.

Usage:
    python examples/batch_generation_example.py
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflows.batch_outfit_generator import BatchOutfitGenerator
from dotenv import load_dotenv

load_dotenv()


def example_simple_batch():
    """
    Simple batch: 1 subject × 1 outfit × 1 style = 1 image
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Batch (1 × 1 × 1)")
    print("=" * 70)

    batch_gen = BatchOutfitGenerator(
        output_dir=Path("output/examples/simple"),
        skip_existing=True,
        cost_per_image=0.04
    )

    # Generate single variation
    stats = batch_gen.generate_batch(
        subject_images=[Path("shopping.webp")],
        outfit_names=["example-outfit"],
        style_names=["shopping-style"],
        temperature=0.8
    )

    print(f"\n✅ Generated {stats.completed} images")


def example_multiple_styles():
    """
    Multiple styles: 1 subject × 1 outfit × 3 styles = 3 images
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multiple Styles (1 × 1 × 3)")
    print("=" * 70)

    batch_gen = BatchOutfitGenerator(
        output_dir=Path("output/examples/styles"),
        skip_existing=True
    )

    # First create some style presets
    # (In real usage, you'd analyze different images to create these)

    stats = batch_gen.generate_batch(
        subject_images=[Path("shopping.webp")],
        outfit_names=["example-outfit"],
        style_names=["shopping-style"],  # Would have multiple styles here
        temperature=0.8
    )

    print(f"\n✅ Generated {stats.completed} images")


def example_multiple_outfits():
    """
    Multiple outfits: 1 subject × 3 outfits × 1 style = 3 images
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Multiple Outfits (1 × 3 × 1)")
    print("=" * 70)

    batch_gen = BatchOutfitGenerator(
        output_dir=Path("output/examples/outfits"),
        skip_existing=True
    )

    # First create some outfit presets
    # (In real usage, you'd analyze different images to create these)

    stats = batch_gen.generate_batch(
        subject_images=[Path("shopping.webp")],
        outfit_names=["example-outfit"],  # Would have multiple outfits here
        style_names=["shopping-style"],
        temperature=0.8
    )

    print(f"\n✅ Generated {stats.completed} images")


def example_full_matrix():
    """
    Full matrix: 2 subjects × 2 outfits × 2 styles = 8 images
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Full Matrix (2 × 2 × 2 = 8 images)")
    print("=" * 70)

    batch_gen = BatchOutfitGenerator(
        output_dir=Path("output/examples/matrix"),
        skip_existing=True
    )

    # In real usage:
    # - subject_images would be multiple different people
    # - outfit_names would be different outfit presets
    # - style_names would be different visual style presets

    stats = batch_gen.generate_batch(
        subject_images=[Path("shopping.webp")],  # Would have 2+ subjects
        outfit_names=["example-outfit"],  # Would have 2+ outfits
        style_names=["shopping-style"],  # Would have 2+ styles
        temperature=0.8
    )

    print(f"\n✅ Generated {stats.completed} images")
    print(f"💰 Total cost: ${stats.completed * 0.04:.2f}")


def main():
    """Run batch generation examples"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch generation examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run simple example (1 image)
  python examples/batch_generation_example.py --example simple

  # Run full matrix example (8 images)
  python examples/batch_generation_example.py --example matrix

  # Run all examples
  python examples/batch_generation_example.py --all
        """
    )

    parser.add_argument(
        '--example',
        choices=['simple', 'styles', 'outfits', 'matrix'],
        help='Which example to run'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all examples'
    )

    args = parser.parse_args()

    try:
        if args.all:
            example_simple_batch()
            example_multiple_styles()
            example_multiple_outfits()
            example_full_matrix()
        elif args.example == 'simple':
            example_simple_batch()
        elif args.example == 'styles':
            example_multiple_styles()
        elif args.example == 'outfits':
            example_multiple_outfits()
        elif args.example == 'matrix':
            example_full_matrix()
        else:
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
