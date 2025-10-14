"""Generator Service

Wraps existing generator tools for API access.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.modular_image_generator.tool import ModularImageGenerator
from ai_tools.outfit_generator.tool import OutfitGenerator
from ai_tools.style_transfer_generator.tool import StyleTransferGenerator
from ai_tools.art_style_generator.tool import ArtStyleGenerator
from ai_tools.combined_transformation.tool import CombinedTransformation


class GeneratorService:
    """Service for running image generators"""

    # Generator registry
    GENERATORS = {
        "modular": {
            "class": ModularImageGenerator,
            "description": "Generate with any combination of modular specs",
            "category": "generator",
            "cost": 0.04,
            "avg_time": 10.0
        },
        "outfit": {
            "class": OutfitGenerator,
            "description": "Generate with outfit and style",
            "category": "generator",
            "cost": 0.04,
            "avg_time": 10.0
        },
        "style-transfer": {
            "class": StyleTransferGenerator,
            "description": "Transfer visual style to subject",
            "category": "generator",
            "cost": 0.04,
            "avg_time": 10.0
        },
        "art-style": {
            "class": ArtStyleGenerator,
            "description": "Generate with artistic style",
            "category": "generator",
            "cost": 0.04,
            "avg_time": 10.0
        },
        "combined": {
            "class": CombinedTransformation,
            "description": "Multi-spec transformation",
            "category": "generator",
            "cost": 0.04,
            "avg_time": 10.0
        }
    }

    def __init__(self):
        """Initialize generator service"""
        self._generator_instances = {}

    def _get_generator(self, generator_name: str):
        """Get or create generator instance"""
        if generator_name not in self._generator_instances:
            if generator_name not in self.GENERATORS:
                raise ValueError(f"Unknown generator: {generator_name}")

            generator_class = self.GENERATORS[generator_name]["class"]
            self._generator_instances[generator_name] = generator_class()

        return self._generator_instances[generator_name]

    def generate(
        self,
        generator_name: str,
        subject_image: Path,
        output_dir: Path,
        **specs
    ) -> Dict[str, Any]:
        """
        Generate image

        Args:
            generator_name: Name of generator to use
            subject_image: Path to subject image
            output_dir: Output directory
            **specs: Generator-specific specs (outfit, visual_style, etc.)

        Returns:
            Generation result dict
        """
        generator = self._get_generator(generator_name)

        # Use modular generator for most cases
        if generator_name in ["modular", "outfit", "combined"]:
            result = generator.generate(
                subject_image=subject_image,
                output_dir=str(output_dir),
                **specs
            )
        elif generator_name == "style-transfer":
            result = generator.transfer_style(
                subject_image=subject_image,
                style=specs.get("visual_style"),
                strength=specs.get("temperature", 0.8),
                output_dir=str(output_dir)
            )
        elif generator_name == "art-style":
            result = generator.generate_art(
                subject_image=subject_image,
                art_style=specs.get("art_style"),
                output_dir=str(output_dir)
            )

        # Convert result to dict
        if hasattr(result, 'model_dump'):
            return result.model_dump()
        elif hasattr(result, 'dict'):
            return result.dict()
        else:
            return result

    def list_generators(self) -> list:
        """List all available generators"""
        return [
            {
                "name": name,
                "description": info["description"],
                "category": info["category"],
                "estimated_cost": info["cost"],
                "avg_time_seconds": info["avg_time"]
            }
            for name, info in self.GENERATORS.items()
        ]

    def get_generator_info(self, generator_name: str) -> Dict[str, Any]:
        """Get information about a specific generator"""
        if generator_name not in self.GENERATORS:
            raise ValueError(f"Unknown generator: {generator_name}")

        info = self.GENERATORS[generator_name]
        return {
            "name": generator_name,
            "description": info["description"],
            "category": info["category"],
            "estimated_cost": info["cost"],
            "avg_time_seconds": info["avg_time"]
        }

    def validate_generator(self, generator_name: str) -> bool:
        """Check if generator exists"""
        return generator_name in self.GENERATORS
