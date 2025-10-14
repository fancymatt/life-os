#!/usr/bin/env python3
"""
Generate analyzer tool from template

Creates the directory structure and files for a new analyzer tool.
"""

import sys
from pathlib import Path
from typing import Dict

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))


TOOL_TEMPLATE = '''#!/usr/bin/env python3
"""
{title}

{description}

Usage:
    python ai_tools/{name}/tool.py <image_path> [--save-as <preset_name>]
"""

import sys
from pathlib import Path
from typing import Optional, Union, List

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_capabilities.specs import {spec_class}, SpecMetadata
from ai_tools.shared.router import LLMRouter, RouterConfig
from ai_tools.shared.preset import PresetManager
from ai_tools.shared.cache import CacheManager
from dotenv import load_dotenv

load_dotenv()


class {class_name}:
    """
    {class_description}
    """

    def __init__(
        self,
        model: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None
    ):
        """
        Initialize {name}

        Args:
            model: Model to use (default from config)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Cache TTL in seconds (default: 7 days)
        """
        # Get model from config if not specified
        if model is None:
            config = RouterConfig()
            model = config.get_model_for_tool("{name}")

        self.router = LLMRouter(model=model)
        self.use_cache = use_cache
        self.cache_manager = CacheManager(default_ttl=cache_ttl) if cache_ttl else CacheManager()
        self.preset_manager = PresetManager()

        # Load prompt template
        template_path = Path(__file__).parent / "template.md"
        with open(template_path) as f:
            self.prompt_template = f.read()

    def analyze(
        self,
        image_path: Union[Path, str],
        skip_cache: bool = False,
        save_as_preset: Optional[str] = None,
        preset_notes: Optional[str] = None
    ) -> {spec_class}:
        """
        Analyze {subject}

        Args:
            image_path: Path to image file
            skip_cache: Skip cache lookup (default: False)
            save_as_preset: Save result as preset with this name
            preset_notes: Optional notes for the preset

        Returns:
            {spec_class} with analysis results
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {{image_path}}")

        # Check cache first (unless skipped)
        if self.use_cache and not skip_cache:
            cached = self.cache_manager.get_for_file(
                "{category}",
                image_path,
                {spec_class}
            )
            if cached:
                print(f"✅ Using cached analysis for {{image_path.name}}")

                # Save as preset if requested
                if save_as_preset:
                    preset_path = self.preset_manager.save(
                        "{category}",
                        save_as_preset,
                        cached,
                        notes=preset_notes
                    )
                    print(f"⭐ Saved as preset: {{save_as_preset}}")
                    print(f"   Location: {{preset_path}}")

                return cached

        # Perform analysis
        print(f"🔍 Analyzing {subject} in {{image_path.name}}...")

        try:
            result = self.router.call_structured(
                prompt=self.prompt_template,
                response_model={spec_class},
                images=[image_path],
                temperature=0.3
            )

            # Add metadata
            result._metadata = SpecMetadata(
                tool="{name}",
                tool_version="1.0.0",
                source_image=str(image_path),
                source_hash=self.cache_manager.compute_file_hash(image_path),
                model_used=self.router.model
            )

            # Cache the result
            if self.use_cache:
                self.cache_manager.set_for_file(
                    "{category}",
                    image_path,
                    result
                )
                print(f"💾 Cached analysis")

            # Save as preset if requested
            if save_as_preset:
                preset_path = self.preset_manager.save(
                    "{category}",
                    save_as_preset,
                    result,
                    notes=preset_notes
                )
                print(f"⭐ Saved as preset: {{save_as_preset}}")
                print(f"   Location: {{preset_path}}")

            return result

        except Exception as e:
            raise Exception(f"Failed to analyze {subject}: {{e}}")

    def analyze_from_preset(self, preset_name: str) -> {spec_class}:
        """Load analysis from a preset"""
        return self.preset_manager.load("{category}", preset_name, {spec_class})

    def save_to_preset(
        self,
        result: {spec_class},
        name: str,
        notes: Optional[str] = None
    ) -> Path:
        """Save analysis as a preset"""
        return self.preset_manager.save("{category}", name, result, notes=notes)

    def list_presets(self) -> List[str]:
        """List all presets"""
        return self.preset_manager.list("{category}")

    def get_cache_stats(self):
        """Get cache statistics"""
        return self.cache_manager.stats()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="{cli_description}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze image
  python tool.py image.jpg

  # Analyze and save as preset
  python tool.py image.jpg --save-as {example_preset} --notes "{example_notes}"

  # Skip cache
  python tool.py image.jpg --no-cache

  # List presets
  python tool.py --list
        """
    )

    parser.add_argument(
        'image',
        nargs='?',
        help='Path to image file'
    )

    parser.add_argument(
        '--save-as',
        help='Save result as preset with this name'
    )

    parser.add_argument(
        '--notes',
        help='Notes for the preset'
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Skip cache lookup'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all presets'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default from config)'
    )

    args = parser.parse_args()

    analyzer = {class_name}(model=args.model)

    # List presets
    if args.list:
        presets = analyzer.list_presets()
        print(f"\\n📋 {title} Presets ({{len(presets)}}):")
        for preset in presets:
            print(f"  - {{preset}}")
        return

    # Analyze image
    if not args.image:
        parser.error("Image path required (or use --list)")

    try:
        result = analyzer.analyze(
            args.image,
            skip_cache=args.no_cache,
            save_as_preset=args.save_as,
            preset_notes=args.notes
        )

        # Print results
        {print_results}

    except Exception as e:
        print(f"\\n❌ Error: {{e}}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''

INIT_TEMPLATE = '''"""{title}"""

from .tool import {class_name}

__all__ = ["{class_name}"]
'''


ANALYZERS = {
    "hair_style_analyzer": {
        "title": "Hair Style Analyzer",
        "spec_class": "HairStyleSpec",
        "category": "hair_styles",
        "subject": "hair style",
        "description": "Analyzes hair style structure including cut, length, layers, texture, volume, and styling.",
        "class_description": "Analyzes hair style structure (not color).",
        "cli_description": "Analyze hair style in images",
        "example_preset": "long-layered",
        "example_notes": "Long layered hairstyle",
        "print_results": '''print("\\n" + "="*70)
        print("Hair Style Analysis")
        print("="*70)
        print(f"\\nCut: {result.cut}")
        print(f"Length: {result.length}")
        print(f"Layers: {result.layers}")
        print(f"Texture: {result.texture}")
        print(f"Volume: {result.volume}")
        print(f"Parting: {result.parting}")
        print(f"Front Styling: {result.front_styling}")
        print(f"Overall Style: {result.overall_style}")
        print("\\n" + "="*70)''',
    },
    "hair_color_analyzer": {
        "title": "Hair Color Analyzer",
        "spec_class": "HairColorSpec",
        "category": "hair_colors",
        "subject": "hair color",
        "description": "Analyzes hair color including base color, undertones, highlights, lowlights, and coloring technique.",
        "class_description": "Analyzes hair color (not style structure).",
        "cli_description": "Analyze hair color in images",
        "example_preset": "ash-blonde",
        "example_notes": "Ash blonde with highlights",
        "print_results": '''print("\\n" + "="*70)
        print("Hair Color Analysis")
        print("="*70)
        print(f"\\nBase Color: {result.base_color}")
        print(f"Undertones: {result.undertones}")
        if result.highlights:
            print(f"Highlights: {result.highlights}")
        if result.lowlights:
            print(f"Lowlights: {result.lowlights}")
        if result.technique:
            print(f"Technique: {result.technique}")
        print(f"Dimension: {result.dimension}")
        print(f"Finish: {result.finish}")
        print("\\n" + "="*70)''',
    },
    "makeup_analyzer": {
        "title": "Makeup Analyzer",
        "spec_class": "MakeupSpec",
        "category": "makeup",
        "subject": "makeup",
        "description": "Analyzes makeup including complexion (foundation, blush, contour), eyes (shadow, liner, mascara), lips, and overall style.",
        "class_description": "Analyzes makeup application and style.",
        "cli_description": "Analyze makeup in images",
        "example_preset": "natural-makeup",
        "example_notes": "Natural everyday makeup",
        "print_results": '''print("\\n" + "="*70)
        print("Makeup Analysis")
        print("="*70)
        print(f"\\nComplexion: {result.complexion}")
        print(f"Eyes: {result.eyes}")
        print(f"Lips: {result.lips}")
        print(f"Overall Style: {result.overall_style}")
        print(f"Intensity: {result.intensity}")
        print(f"\\nColor Palette ({len(result.color_palette)}):")
        print(f"  {', '.join(result.color_palette)}")
        print("\\n" + "="*70)''',
    },
    "expression_analyzer": {
        "title": "Expression Analyzer",
        "spec_class": "ExpressionSpec",
        "category": "expressions",
        "subject": "facial expression",
        "description": "Analyzes facial expression including primary emotion, intensity, mouth/eyes/eyebrows position, gaze direction.",
        "class_description": "Analyzes facial expressions and emotional state.",
        "cli_description": "Analyze facial expression in images",
        "example_preset": "confident-smile",
        "example_notes": "Confident smiling expression",
        "print_results": '''print("\\n" + "="*70)
        print("Expression Analysis")
        print("="*70)
        print(f"\\nPrimary Emotion: {result.primary_emotion}")
        print(f"Intensity: {result.intensity}")
        print(f"Mouth: {result.mouth}")
        print(f"Eyes: {result.eyes}")
        print(f"Eyebrows: {result.eyebrows}")
        print(f"Gaze Direction: {result.gaze_direction}")
        print(f"Overall Mood: {result.overall_mood}")
        print("\\n" + "="*70)''',
    },
    "accessories_analyzer": {
        "title": "Accessories Analyzer",
        "spec_class": "AccessoriesSpec",
        "category": "accessories",
        "subject": "accessories",
        "description": "Analyzes accessories including jewelry, bags, belts, scarves, hats, watches, and overall styling approach.",
        "class_description": "Analyzes accessories and styling details.",
        "cli_description": "Analyze accessories in images",
        "example_preset": "minimal-jewelry",
        "example_notes": "Minimal jewelry style",
        "print_results": '''print("\\n" + "="*70)
        print("Accessories Analysis")
        print("="*70)
        if result.jewelry:
            print(f"\\nJewelry ({len(result.jewelry)}):")
            for item in result.jewelry:
                print(f"  - {item}")
        if result.bags:
            print(f"\\nBags: {result.bags}")
        if result.belts:
            print(f"Belts: {result.belts}")
        if result.scarves:
            print(f"Scarves: {result.scarves}")
        if result.hats:
            print(f"Hats: {result.hats}")
        if result.watches:
            print(f"Watches: {result.watches}")
        if result.other:
            print(f"\\nOther ({len(result.other)}):")
            for item in result.other:
                print(f"  - {item}")
        print(f"\\nOverall Style: {result.overall_style}")
        print("\\n" + "="*70)''',
    },
}


def generate_analyzer(name: str, config: Dict[str, str]):
    """Generate analyzer tool"""
    class_name = ''.join(word.capitalize() for word in name.split('_'))

    # Create directory
    tool_dir = Path(f"ai_tools/{name}")
    tool_dir.mkdir(parents=True, exist_ok=True)

    # Generate tool.py
    tool_code = TOOL_TEMPLATE.format(
        name=name,
        title=config["title"],
        description=config["description"],
        spec_class=config["spec_class"],
        class_name=class_name,
        class_description=config["class_description"],
        category=config["category"],
        subject=config["subject"],
        cli_description=config["cli_description"],
        example_preset=config["example_preset"],
        example_notes=config["example_notes"],
        print_results=config["print_results"]
    )

    (tool_dir / "tool.py").write_text(tool_code)
    (tool_dir / "tool.py").chmod(0o755)

    # Generate __init__.py
    init_code = INIT_TEMPLATE.format(
        title=config["title"],
        class_name=class_name
    )
    (tool_dir / "__init__.py").write_text(init_code)

    print(f"✅ Generated {name}")
    print(f"   Created: {tool_dir}/tool.py")
    print(f"   Created: {tool_dir}/__init__.py")
    print(f"   TODO: Create {tool_dir}/template.md")


if __name__ == "__main__":
    for name, config in ANALYZERS.items():
        generate_analyzer(name, config)
