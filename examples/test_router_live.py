#!/usr/bin/env python3
"""
Quick test of the LLMRouter with real API calls

Demonstrates:
- Basic text generation
- Structured output (JSON -> Pydantic)
- Image analysis (if image provided)
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_tools.shared.router import LLMRouter
from ai_capabilities.specs import OutfitSpec, VisualStyleSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_basic_text_call():
    """Test basic text generation"""
    print("\n" + "="*70)
    print("Test 1: Basic Text Generation")
    print("="*70)

    # Use "gemini/" prefix for Google AI Studio (uses GEMINI_API_KEY)
    # Or use "gpt-4o" for OpenAI (uses OPENAI_API_KEY)
    router = LLMRouter(model="gemini/gemini-2.0-flash-exp")

    prompt = "Describe a professional business outfit in one sentence."
    response = router.call(prompt)

    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print("✅ Basic text generation works!")


def test_structured_output():
    """Test structured output (JSON -> Pydantic)"""
    print("\n" + "="*70)
    print("Test 2: Structured Output (Outfit Analysis)")
    print("="*70)

    router = LLMRouter(model="gemini/gemini-2.0-flash-exp")

    prompt = """
    Analyze this outfit description and extract structured details:

    "A charcoal gray wool suit jacket with notch lapels, two buttons, and slim fit.
    Paired with a crisp white cotton dress shirt with point collar and French cuffs.
    The overall style is modern professional with a contemporary minimalist aesthetic."

    Extract the clothing items, style genre, formality level, and aesthetic.
    """

    try:
        outfit = router.call_structured(prompt, OutfitSpec)

        print(f"\n✅ Structured output parsing works!")
        print(f"\nParsed Outfit:")
        print(f"  Style Genre: {outfit.style_genre}")
        print(f"  Formality: {outfit.formality}")
        print(f"  Aesthetic: {outfit.aesthetic}")
        print(f"  Items: {len(outfit.clothing_items)}")
        for item in outfit.clothing_items:
            print(f"    - {item.item}: {item.color} {item.fabric}")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_visual_style_analysis():
    """Test analyzing a visual/photographic style"""
    print("\n" + "="*70)
    print("Test 3: Visual Style Analysis")
    print("="*70)

    router = LLMRouter(model="gemini/gemini-2.0-flash-exp")

    prompt = """
    Analyze this photography style description:

    "A professional headshot with three-point lighting setup. Soft, diffused light
    from the front with warm color grading. Shot at eye level with a plain white
    backdrop. The overall mood is professional and approachable, typical of
    corporate photography."

    Extract the lighting setup, color grading, composition, mood, and photography style.
    """

    try:
        style = router.call_structured(prompt, VisualStyleSpec)

        print(f"\n✅ Visual style analysis works!")
        print(f"\nParsed Style:")
        print(f"  Lighting: {style.lighting_setup}")
        print(f"  Color Grading: {style.color_grading}")
        print(f"  Mood: {style.mood}")
        print(f"  Photography Style: {style.photography_style}")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_with_image(image_path: Path):
    """Test image analysis (requires image file)"""
    print("\n" + "="*70)
    print("Test 4: Image Analysis")
    print("="*70)

    if not image_path.exists():
        print(f"⚠️  Image not found: {image_path}")
        print("Skipping image test.")
        return

    router = LLMRouter(model="gemini/gemini-2.0-flash-exp")

    prompt = "Describe the outfit in this image in detail."

    try:
        response = router.call(prompt, images=[image_path])

        print(f"\n✅ Image analysis works!")
        print(f"\nImage: {image_path.name}")
        print(f"Analysis: {response[:200]}...")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("AI-Studio Router Live Tests")
    print("="*70)
    print("\nThese tests make REAL API calls and will consume credits!")
    print("Make sure you have API keys in your .env file.")

    try:
        # Test 1: Basic text
        test_basic_text_call()

        # Test 2: Structured output
        test_structured_output()

        # Test 3: Visual style analysis
        test_visual_style_analysis()

        # Test 4: Image (if available)
        # You can provide your own image path here
        # test_with_image(Path("path/to/your/image.jpg"))

        print("\n" + "="*70)
        print("✅ All tests passed! Router is working with real APIs.")
        print("="*70)

    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ Tests failed: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
