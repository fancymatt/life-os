#!/usr/bin/env python3
"""
Modular Image Generator

Generate images by combining any modular specs:
- Outfit
- Visual Style
- Art Style
- Hair Style
- Hair Color
- Makeup
- Expression
- Accessories

Usage:
    python ai_tools/modular_image_generator/tool.py <subject_image> \
        [--outfit <preset>] \
        [--visual-style <preset>] \
        [--art-style <preset>] \
        [--hair-style <preset>] \
        [--hair-color <preset>] \
        [--makeup <preset>] \
        [--expression <preset>] \
        [--accessories <preset>]
"""

import sys
from pathlib import Path
from typing import Optional, Union
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import (
    OutfitSpec,
    VisualStyleSpec,
    ArtStyleSpec,
    HairStyleSpec,
    HairColorSpec,
    MakeupSpec,
    ExpressionSpec,
    AccessoriesSpec,
    ImageGenerationResult,
    ImageGenerationRequest
)
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.preset import PresetManager
from dotenv import load_dotenv

load_dotenv()


class ModularImageGenerator:
    """
    Generate images using modular specs.

    Can combine any number of specs to create a custom image.
    """

    def __init__(self, model: Optional[str] = None):
        """
        Initialize modular image generator

        Args:
            model: Model to use (default from config)
        """
        if model is None:
            config = RouterConfig()
            model = config.get_model_for_tool("modular_image_generator")

        self.router = LLMRouter(model=model)
        self.preset_manager = PresetManager()

    def _merge_outfits(self, outfit_specs: list) -> OutfitSpec:
        """
        Merge multiple outfit specs into one amalgamated outfit

        Args:
            outfit_specs: List of OutfitSpec objects

        Returns:
            Merged OutfitSpec with all clothing items
        """
        if not outfit_specs:
            return None

        if len(outfit_specs) == 1:
            return outfit_specs[0]

        # Combine all clothing items from all outfits
        all_clothing_items = []
        for outfit in outfit_specs:
            all_clothing_items.extend(outfit.clothing_items)

        # Take suggested name from first outfit, or create amalgamated name
        names = [o.suggested_name for o in outfit_specs if o.suggested_name]
        if len(names) > 1:
            suggested_name = "Amalgamated Outfit"
        elif names:
            suggested_name = names[0]
        else:
            suggested_name = "Custom Outfit"

        # Combine style genres, formality levels, and aesthetics
        style_genres = [o.style_genre for o in outfit_specs if o.style_genre]
        formality_levels = [o.formality for o in outfit_specs if o.formality]
        aesthetics = [o.aesthetic for o in outfit_specs if o.aesthetic]

        # Use the most specific values, or combine if multiple
        style_genre = ", ".join(set(style_genres)) if style_genres else None
        formality = formality_levels[0] if formality_levels else None
        aesthetic = ", ".join(set(aesthetics)) if aesthetics else None

        print(f"🔀 Merged {len(outfit_specs)} outfits into one ({len(all_clothing_items)} total items)")

        return OutfitSpec(
            suggested_name=suggested_name,
            clothing_items=all_clothing_items,
            style_genre=style_genre,
            formality=formality,
            aesthetic=aesthetic
        )

    def generate(
        self,
        subject_image: Union[Path, str],
        outfit: Optional[Union[str, list, OutfitSpec]] = None,
        visual_style: Optional[Union[str, VisualStyleSpec]] = None,
        art_style: Optional[Union[str, ArtStyleSpec]] = None,
        hair_style: Optional[Union[str, HairStyleSpec]] = None,
        hair_color: Optional[Union[str, HairColorSpec]] = None,
        makeup: Optional[Union[str, MakeupSpec]] = None,
        expression: Optional[Union[str, ExpressionSpec]] = None,
        accessories: Optional[Union[str, AccessoriesSpec]] = None,
        output_dir: str = "output/generated",
        temperature: float = 0.8
    ) -> ImageGenerationResult:
        """
        Generate image with modular specs

        Args:
            subject_image: Source image path
            outfit: Outfit preset name, list of preset names, or OutfitSpec
            visual_style: Visual style preset name or VisualStyleSpec
            art_style: Art style preset name or ArtStyleSpec
            hair_style: Hair style preset name or HairStyleSpec
            hair_color: Hair color preset name or HairColorSpec
            makeup: Makeup preset name or MakeupSpec
            expression: Expression preset name or ExpressionSpec
            accessories: Accessories preset name or AccessoriesSpec
            output_dir: Output directory
            temperature: Generation temperature

        Returns:
            ImageGenerationResult
        """
        subject_image = Path(subject_image)

        if not subject_image.exists():
            raise FileNotFoundError(f"Subject image not found: {subject_image}")

        print(f"\n{'='*70}")
        print("MODULAR IMAGE GENERATION")
        print(f"{'='*70}\n")
        print(f"Subject: {subject_image.name}")

        # Debug: Check what we received
        print(f"🔍 DEBUG: outfit parameter type: {type(outfit)}, value: {outfit}")

        # Load specs from presets if needed
        # Special handling for outfit - can be a list of IDs
        if isinstance(outfit, list):
            print(f"📦 Loading {len(outfit)} outfits for amalgamation...")
            outfit_specs = []
            for outfit_id in outfit:
                spec = self._load_spec(outfit_id, "outfits", OutfitSpec, "Outfit")
                if spec:
                    outfit_specs.append(spec)
            outfit_spec = self._merge_outfits(outfit_specs) if outfit_specs else None
        else:
            outfit_spec = self._load_spec(outfit, "outfits", OutfitSpec, "Outfit")

        visual_style_spec = self._load_spec(visual_style, "visual_styles", VisualStyleSpec, "Visual Style")
        art_style_spec = self._load_spec(art_style, "art_styles", ArtStyleSpec, "Art Style")
        hair_style_spec = self._load_spec(hair_style, "hair_styles", HairStyleSpec, "Hair Style")
        hair_color_spec = self._load_spec(hair_color, "hair_colors", HairColorSpec, "Hair Color")
        makeup_spec = self._load_spec(makeup, "makeup", MakeupSpec, "Makeup")
        expression_spec = self._load_spec(expression, "expressions", ExpressionSpec, "Expression")
        accessories_spec = self._load_spec(accessories, "accessories", AccessoriesSpec, "Accessories")

        # Build prompt from specs
        prompt = self._build_prompt(
            outfit_spec,
            visual_style_spec,
            art_style_spec,
            hair_style_spec,
            hair_color_spec,
            makeup_spec,
            expression_spec,
            accessories_spec
        )

        print(f"\n🎨 Generating image with Gemini 2.5 Flash...")
        print(f"   Temperature: {temperature}")

        # Generate image
        start_time = datetime.now()

        image_bytes = self.router.generate_image(
            prompt=prompt,
            image_path=subject_image,
            model=self.router.model,
            provider="gemini",
            temperature=temperature
        )

        generation_time = (datetime.now() - start_time).total_seconds()

        # Save image
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{subject_image.stem}_modular_{timestamp}.png"
        file_path = output_path / filename

        with open(file_path, 'wb') as f:
            f.write(image_bytes)

        print(f"\n✅ Generated: {file_path}")
        print(f"   Time: {generation_time:.1f}s")
        print(f"   Cost: ~$0.04")

        # Create result
        request = ImageGenerationRequest(
            subject_image=str(subject_image),
            outfit=outfit_spec,
            visual_style=visual_style_spec,
            hair_style=hair_style_spec,
            hair_color=hair_color_spec,
            makeup=makeup_spec,
            expression=expression_spec,
            accessories=accessories_spec
        )

        result = ImageGenerationResult(
            file_path=str(file_path),
            request=request,
            model_used=self.router.model,
            timestamp=datetime.now(),
            cost_estimate=0.04,
            generation_time=generation_time
        )

        return result

    def _load_spec(self, spec_or_name, category, spec_class, label):
        """Load spec from preset if needed"""
        if spec_or_name is None:
            return None

        if isinstance(spec_or_name, str):
            print(f"📦 Loading {label}: {spec_or_name}")
            return self.preset_manager.load(category, spec_or_name, spec_class)
        else:
            print(f"✓ Using provided {label} spec")
            return spec_or_name

    def _build_prompt(
        self,
        outfit: Optional[OutfitSpec],
        visual_style: Optional[VisualStyleSpec],
        art_style: Optional[ArtStyleSpec],
        hair_style: Optional[HairStyleSpec],
        hair_color: Optional[HairColorSpec],
        makeup: Optional[MakeupSpec],
        expression: Optional[ExpressionSpec],
        accessories: Optional[AccessoriesSpec]
    ) -> str:
        """Build generation prompt from specs"""
        sections = []

        # Subject instruction
        sections.append("Generate a 9:16 portrait format image of the person shown in the reference image.")

        # VISUAL STYLE FIRST - This defines the entire composition and must be followed exactly
        if visual_style:
            style_section = "**PHOTOGRAPH COMPOSITION - FOLLOW EXACTLY:**\n\n"

            # Subject pose and interaction - MOST CRITICAL
            style_section += f"**SUBJECT POSE & ACTION (MANDATORY):**\n{visual_style.subject_action}\n\n"

            # Camera framing
            style_section += f"**FRAMING:** {visual_style.framing}\n"
            style_section += f"**CAMERA ANGLE:** {visual_style.camera_angle}\n\n"

            # Environment/setting
            style_section += f"**SETTING & BACKGROUND:**\n{visual_style.setting}\n\n"

            # Lighting
            style_section += f"**LIGHTING:**\n{visual_style.lighting}\n\n"

            # Mood
            style_section += f"**MOOD & ATMOSPHERE:**\n{visual_style.mood}\n\n"

            style_section += "**CRITICAL: The subject's pose, body position, gaze direction, and interaction with the environment described above are MANDATORY and must be reproduced exactly as specified. Do not default to a standard camera-facing pose.**"

            sections.append(style_section)

        # Outfit
        if outfit:
            # Emphasize that ALL items should be worn simultaneously with numbered list
            num_items = len(outfit.clothing_items)
            outfit_desc = f"**MANDATORY CLOTHING REQUIREMENTS - ALL {num_items} ITEMS MUST APPEAR:**\n\n"
            outfit_desc += f"The person MUST be wearing ALL {num_items} of the following distinct clothing items simultaneously, layered together:\n\n"

            for idx, item in enumerate(outfit.clothing_items, 1):
                outfit_desc += f"{idx}. {item.item} - {item.color} {item.fabric}\n"

            outfit_desc += f"\n**Overall Style:** {outfit.style_genre}, {outfit.formality}"
            outfit_desc += f"\n\n**CRITICAL REQUIREMENTS:**"
            outfit_desc += f"\n- This is an amalgamated outfit containing {num_items} distinct items"
            outfit_desc += f"\n- Each numbered item above is a SEPARATE, DISTINCT piece of clothing"
            outfit_desc += f"\n- ALL {num_items} items must be visible in the image, layered appropriately"
            outfit_desc += f"\n- Multiple jackets/layers should be stacked on top of each other"
            outfit_desc += f"\n- All accessories and items must be clearly visible"
            outfit_desc += f"\n- Do NOT omit any items - every single numbered item is mandatory"
            sections.append(outfit_desc)

        # Hair style
        if hair_style:
            hair_desc = f"Hair style: {hair_style.overall_style}. "
            hair_desc += f"{hair_style.length}, {hair_style.texture}, {hair_style.volume} volume."
            sections.append(hair_desc)

        # Hair color
        if hair_color:
            color_desc = f"Hair color: {hair_color.base_color} with {hair_color.undertones} undertones."
            if hair_color.highlights:
                color_desc += f" {hair_color.highlights}."
            sections.append(color_desc)

        # Makeup
        if makeup:
            makeup_desc = f"Makeup: {makeup.overall_style} ({makeup.intensity}). "
            makeup_desc += f"Complexion: {makeup.complexion}. Eyes: {makeup.eyes}. Lips: {makeup.lips}."
            sections.append(makeup_desc)

        # Expression
        if expression:
            expr_desc = f"Expression: {expression.primary_emotion} ({expression.intensity}). "
            expr_desc += f"Mouth: {expression.mouth}. Eyes: {expression.eyes}. "
            expr_desc += f"Gaze: {expression.gaze_direction}."
            sections.append(expr_desc)

        # Accessories
        if accessories:
            if accessories.jewelry or accessories.bags or accessories.other:
                acc_desc = "Accessories: "
                if accessories.jewelry:
                    acc_desc += f"{', '.join(accessories.jewelry)}. "
                if accessories.bags:
                    acc_desc += f"Bag: {accessories.bags}. "
                sections.append(acc_desc.strip())

        # Art style
        if art_style:
            art_desc = f"Artistic style: {art_style.artistic_movement}. "
            art_desc += f"Rendered as {art_style.medium} with {art_style.technique}. "
            art_desc += f"Texture: {art_style.texture}. Mood: {art_style.mood}."
            sections.append(art_desc)

        return "\n\n".join(sections)

    async def agenerate(
        self,
        subject_image: Union[Path, str],
        outfit: Optional[Union[str, list, OutfitSpec]] = None,
        visual_style: Optional[Union[str, VisualStyleSpec]] = None,
        art_style: Optional[Union[str, ArtStyleSpec]] = None,
        hair_style: Optional[Union[str, HairStyleSpec]] = None,
        hair_color: Optional[Union[str, HairColorSpec]] = None,
        makeup: Optional[Union[str, MakeupSpec]] = None,
        expression: Optional[Union[str, ExpressionSpec]] = None,
        accessories: Optional[Union[str, AccessoriesSpec]] = None,
        output_dir: str = "output/generated",
        temperature: float = 0.8
    ) -> ImageGenerationResult:
        """
        Async version: Generate image with modular specs

        Args:
            subject_image: Source image path
            outfit: Outfit preset name, list of preset names, or OutfitSpec
            visual_style: Visual style preset name or VisualStyleSpec
            art_style: Art style preset name or ArtStyleSpec
            hair_style: Hair style preset name or HairStyleSpec
            hair_color: Hair color preset name or HairColorSpec
            makeup: Makeup preset name or MakeupSpec
            expression: Expression preset name or ExpressionSpec
            accessories: Accessories preset name or AccessoriesSpec
            output_dir: Output directory
            temperature: Generation temperature

        Returns:
            ImageGenerationResult
        """
        import aiofiles

        subject_image = Path(subject_image)

        if not subject_image.exists():
            raise FileNotFoundError(f"Subject image not found: {subject_image}")

        print(f"\n{'='*70}")
        print("MODULAR IMAGE GENERATION (ASYNC)")
        print(f"{'='*70}\n")
        print(f"Subject: {subject_image.name}")

        # Debug: Check what we received
        print(f"🔍 DEBUG: outfit parameter type: {type(outfit)}, value: {outfit}")

        # Load specs from presets if needed
        # Special handling for outfit - can be a list of IDs
        if isinstance(outfit, list):
            print(f"📦 Loading {len(outfit)} outfits for amalgamation...")
            outfit_specs = []
            for outfit_id in outfit:
                spec = self._load_spec(outfit_id, "outfits", OutfitSpec, "Outfit")
                if spec:
                    outfit_specs.append(spec)
            outfit_spec = self._merge_outfits(outfit_specs) if outfit_specs else None
        else:
            outfit_spec = self._load_spec(outfit, "outfits", OutfitSpec, "Outfit")

        visual_style_spec = self._load_spec(visual_style, "visual_styles", VisualStyleSpec, "Visual Style")
        art_style_spec = self._load_spec(art_style, "art_styles", ArtStyleSpec, "Art Style")
        hair_style_spec = self._load_spec(hair_style, "hair_styles", HairStyleSpec, "Hair Style")
        hair_color_spec = self._load_spec(hair_color, "hair_colors", HairColorSpec, "Hair Color")
        makeup_spec = self._load_spec(makeup, "makeup", MakeupSpec, "Makeup")
        expression_spec = self._load_spec(expression, "expressions", ExpressionSpec, "Expression")
        accessories_spec = self._load_spec(accessories, "accessories", AccessoriesSpec, "Accessories")

        # Build prompt from specs
        prompt = self._build_prompt(
            outfit_spec,
            visual_style_spec,
            art_style_spec,
            hair_style_spec,
            hair_color_spec,
            makeup_spec,
            expression_spec,
            accessories_spec
        )

        print(f"\n🎨 Generating image with Gemini 2.5 Flash (async)...")
        print(f"   Temperature: {temperature}")

        # Generate image (async)
        start_time = datetime.now()

        image_bytes = await self.router.agenerate_image(
            prompt=prompt,
            image_path=subject_image,
            model=self.router.model,
            provider="gemini",
            temperature=temperature
        )

        generation_time = (datetime.now() - start_time).total_seconds()

        # Save image
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{subject_image.stem}_modular_{timestamp}.png"
        file_path = output_path / filename

        # Use aiofiles for async file writing
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(image_bytes)

        print(f"\n✅ Generated: {file_path}")
        print(f"   Time: {generation_time:.1f}s")
        print(f"   Cost: ~$0.04")

        # Create result
        request = ImageGenerationRequest(
            subject_image=str(subject_image),
            outfit=outfit_spec,
            visual_style=visual_style_spec,
            hair_style=hair_style_spec,
            hair_color=hair_color_spec,
            makeup=makeup_spec,
            expression=expression_spec,
            accessories=accessories_spec
        )

        result = ImageGenerationResult(
            file_path=str(file_path),
            request=request,
            model_used=self.router.model,
            timestamp=datetime.now(),
            cost_estimate=0.04,
            generation_time=generation_time
        )

        return result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate images with modular specs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Just change outfit
  python tool.py subject.jpg --outfit casual-outfit

  # Change outfit and visual style
  python tool.py subject.jpg --outfit formal-suit --visual-style film-noir

  # Full transformation
  python tool.py subject.jpg \
    --outfit summer-dress \
    --visual-style vintage-style \
    --hair-style long-wavy \
    --hair-color blonde-highlights \
    --makeup natural-glam \
    --expression confident-smile

  # Custom output directory
  python tool.py subject.jpg --outfit outfit1 --output output/custom/
        """
    )

    parser.add_argument(
        'subject',
        help='Subject image path'
    )

    parser.add_argument('--outfit', help='Outfit preset name')
    parser.add_argument('--visual-style', help='Visual style preset name')
    parser.add_argument('--art-style', help='Art style preset name')
    parser.add_argument('--hair-style', help='Hair style preset name')
    parser.add_argument('--hair-color', help='Hair color preset name')
    parser.add_argument('--makeup', help='Makeup preset name')
    parser.add_argument('--expression', help='Expression preset name')
    parser.add_argument('--accessories', help='Accessories preset name')

    parser.add_argument(
        '--output',
        default='output/generated',
        help='Output directory (default: output/generated)'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        default=0.8,
        help='Generation temperature (default: 0.8)'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default from config)'
    )

    args = parser.parse_args()

    try:
        generator = ModularImageGenerator(model=args.model)
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

        print(f"\n{'='*70}")
        print("GENERATION COMPLETE")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
