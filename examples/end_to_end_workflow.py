#!/usr/bin/env python3
"""
End-to-End AI-Studio Workflow

Demonstrates the complete workflow:
1. Analyze outfit from image
2. Analyze visual style from image
3. Generate new image using presets
4. Show modularity: mix outfit from image A with style from image B

Usage:
    python end_to_end_workflow.py source_image.jpg [--generate]
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_tools.outfit_analyzer.tool import OutfitAnalyzer
from ai_tools.visual_style_analyzer.tool import VisualStyleAnalyzer
from ai_tools.outfit_generator.tool import OutfitGenerator
from dotenv import load_dotenv

load_dotenv()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="End-to-end AI-Studio workflow demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'source_image',
        help='Source image to analyze'
    )

    parser.add_argument(
        '--subject-image',
        help='Subject image for generation (default: use source_image)'
    )

    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate new image using DALL-E (costs money!)'
    )

    parser.add_argument(
        '--outfit-preset',
        help='Existing outfit preset to use (skips analysis)'
    )

    parser.add_argument(
        '--style-preset',
        help='Existing style preset to use (skips analysis)'
    )

    args = parser.parse_args()

    source_image = Path(args.source_image)
    subject_image = Path(args.subject_image) if args.subject_image else source_image

    if not source_image.exists():
        print(f"❌ Error: Source image not found: {source_image}")
        sys.exit(1)

    print("=" * 80)
    print("AI-STUDIO END-TO-END WORKFLOW")
    print("=" * 80)

    # Phase 1: Analyze Outfit
    print("\n" + "=" * 80)
    print("PHASE 1: OUTFIT ANALYSIS")
    print("=" * 80)

    outfit_analyzer = OutfitAnalyzer()

    if args.outfit_preset:
        print(f"\n📦 Using existing outfit preset: {args.outfit_preset}")
        outfit = outfit_analyzer.analyze_from_preset(args.outfit_preset)
    else:
        print(f"\n🔍 Analyzing outfit in {source_image.name}...")
        outfit = outfit_analyzer.analyze(
            source_image,
            save_as_preset="workflow-outfit",
            preset_notes="Generated from end-to-end workflow example"
        )

    print(f"\n✅ Outfit Analysis Complete:")
    print(f"   Style: {outfit.style_genre}")
    print(f"   Formality: {outfit.formality}")
    print(f"   Aesthetic: {outfit.aesthetic}")
    print(f"   Items: {len(outfit.clothing_items)}")
    for item in outfit.clothing_items[:3]:
        print(f"     - {item.item} ({item.color})")
    if len(outfit.clothing_items) > 3:
        print(f"     ... and {len(outfit.clothing_items) - 3} more")

    # Phase 2: Analyze Visual Style
    print("\n" + "=" * 80)
    print("PHASE 2: VISUAL STYLE ANALYSIS")
    print("=" * 80)

    style_analyzer = VisualStyleAnalyzer()

    if args.style_preset:
        print(f"\n📦 Using existing style preset: {args.style_preset}")
        style = style_analyzer.analyze_from_preset(args.style_preset)
    else:
        print(f"\n🔍 Analyzing visual style in {source_image.name}...")
        style = style_analyzer.analyze(
            source_image,
            save_as_preset="workflow-style",
            preset_notes="Generated from end-to-end workflow example"
        )

    print(f"\n✅ Visual Style Analysis Complete:")
    print(f"   Photographic Style: {style.photographic_style}")
    print(f"   Artistic Style: {style.artistic_style}")
    print(f"   Mood: {style.mood}")
    print(f"   Era: {style.era_aesthetic}")
    print(f"   Color Palette: {', '.join(style.color_palette[:5])}")
    print(f"   Lighting: {style.lighting[:80]}...")

    # Phase 3: Presets Available
    print("\n" + "=" * 80)
    print("PHASE 3: PRESETS READY")
    print("=" * 80)

    print("\n📦 Analyzed presets are now available:")
    print(f"   Outfit: presets/outfits/workflow-outfit.json")
    print(f"   Style:  presets/visual_styles/workflow-style.json")
    print("\n💡 These can be:")
    print("   - Manually edited to refine the analysis")
    print("   - Mixed and matched (outfit from A, style from B)")
    print("   - Reused across multiple generations")

    # Phase 4: Generation (optional)
    if args.generate:
        print("\n" + "=" * 80)
        print("PHASE 4: IMAGE GENERATION")
        print("=" * 80)

        print(f"\n🎨 Generating new image...")
        print(f"   Subject: {subject_image.name}")
        print(f"   Outfit: workflow-outfit preset")
        print(f"   Style: workflow-style preset")
        print(f"\n⚠️  This will call DALL-E 3 and cost approximately $0.04")

        try:
            generator = OutfitGenerator()

            result = generator.generate(
                subject_image=subject_image,
                outfit="workflow-outfit",
                visual_style="workflow-style",
                output_dir="output/workflow"
            )

            print(f"\n✅ Generation Complete!")
            print(f"   Output: {result.file_path}")
            print(f"   Model: {result.model_used}")
            print(f"   Timestamp: {result.timestamp}")

            print("\n" + "=" * 80)
            print("COMPLETE WORKFLOW SUCCESS! 🎉")
            print("=" * 80)

        except Exception as e:
            print(f"\n❌ Generation failed: {e}")
            print("\nNote: This requires OPENAI_API_KEY in your .env file")
            sys.exit(1)

    else:
        print("\n" + "=" * 80)
        print("WORKFLOW ANALYSIS COMPLETE")
        print("=" * 80)

        print("\n✅ Outfit and style analyzed and saved as presets")
        print("\nTo generate an image, run:")
        print(f"  python {Path(__file__).name} {source_image} --generate")
        print("\nOr use the outfit-generator directly:")
        print(f"  python ai_tools/outfit_generator/tool.py {subject_image} \\")
        print(f"    --outfit workflow-outfit \\")
        print(f"    --style workflow-style")

    print("\n" + "=" * 80)
    print("MODULARITY DEMONSTRATION")
    print("=" * 80)

    print("\n💡 The power of AI-Studio's modular architecture:")
    print("\n1. Analyze multiple images:")
    print("   - Outfit from image A → casual-outfit preset")
    print("   - Style from image B  → film-noir preset")
    print("\n2. Mix and match presets:")
    print("   python ai_tools/outfit_generator/tool.py subject.jpg \\")
    print("     --outfit casual-outfit \\")
    print("     --style film-noir")
    print("\n3. Manual refinement:")
    print("   - Edit presets/outfits/casual-outfit.json")
    print("   - Adjust colors, fabrics, details")
    print("   - Regenerate with refined specs")
    print("\n4. Batch operations:")
    print("   - 10 subjects × 5 outfits × 3 styles = 150 variations")
    print("   - All using cached analyses and editable presets")


if __name__ == "__main__":
    main()
