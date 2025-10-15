"""Analyzer Service

Wraps existing analyzer tools for API access.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.outfit_analyzer.tool import OutfitAnalyzer
from ai_tools.visual_style_analyzer.tool import VisualStyleAnalyzer
from ai_tools.art_style_analyzer.tool import ArtStyleAnalyzer
from ai_tools.hair_style_analyzer.tool import HairStyleAnalyzer
from ai_tools.hair_color_analyzer.tool import HairColorAnalyzer
from ai_tools.makeup_analyzer.tool import MakeupAnalyzer
from ai_tools.expression_analyzer.tool import ExpressionAnalyzer
from ai_tools.accessories_analyzer.tool import AccessoriesAnalyzer
from ai_tools.comprehensive_analyzer.tool import ComprehensiveAnalyzer


class AnalyzerService:
    """Service for running image analyzers"""

    # Analyzer registry with metadata
    ANALYZERS = {
        "outfit": {
            "class": OutfitAnalyzer,
            "description": "Analyze outfit including clothing items, style, formality",
            "category": "analyzer",
            "cost": 0.001,
            "avg_time": 3.0
        },
        "visual-style": {
            "class": VisualStyleAnalyzer,
            "description": "Analyze photograph composition (subject action, setting, framing, lighting, mood)",
            "category": "analyzer",
            "cost": 0.001,
            "avg_time": 3.0
        },
        "art-style": {
            "class": ArtStyleAnalyzer,
            "description": "Analyze artistic style, medium, and technique",
            "category": "analyzer",
            "cost": 0.001,
            "avg_time": 3.0
        },
        "hair-style": {
            "class": HairStyleAnalyzer,
            "description": "Analyze hair structure (cut, length, layers, texture)",
            "category": "analyzer",
            "cost": 0.001,
            "avg_time": 3.0
        },
        "hair-color": {
            "class": HairColorAnalyzer,
            "description": "Analyze hair color, undertones, highlights",
            "category": "analyzer",
            "cost": 0.001,
            "avg_time": 3.0
        },
        "makeup": {
            "class": MakeupAnalyzer,
            "description": "Analyze makeup application and style",
            "category": "analyzer",
            "cost": 0.001,
            "avg_time": 3.0
        },
        "expression": {
            "class": ExpressionAnalyzer,
            "description": "Analyze facial expression and emotion",
            "category": "analyzer",
            "cost": 0.001,
            "avg_time": 3.0
        },
        "accessories": {
            "class": AccessoriesAnalyzer,
            "description": "Analyze accessories (jewelry, bags, etc.)",
            "category": "analyzer",
            "cost": 0.001,
            "avg_time": 3.0
        },
        "comprehensive": {
            "class": ComprehensiveAnalyzer,
            "description": "Run all analyzers at once",
            "category": "analyzer",
            "cost": 0.008,
            "avg_time": 20.0
        }
    }

    def __init__(self):
        """Initialize analyzer service"""
        self._analyzer_instances = {}

    def _get_analyzer(self, analyzer_name: str, auto_visualize: bool = False):
        """
        Get or create analyzer instance

        Args:
            analyzer_name: Name of the analyzer
            auto_visualize: Whether to enable auto-visualization (default: False for API usage)
        """
        # Use a cache key that includes auto_visualize setting
        cache_key = f"{analyzer_name}_{auto_visualize}"

        if cache_key not in self._analyzer_instances:
            if analyzer_name not in self.ANALYZERS:
                raise ValueError(f"Unknown analyzer: {analyzer_name}")

            analyzer_class = self.ANALYZERS[analyzer_name]["class"]

            # For OutfitAnalyzer, pass auto_visualize parameter
            if analyzer_name == "outfit":
                self._analyzer_instances[cache_key] = analyzer_class(auto_visualize=auto_visualize)
            else:
                self._analyzer_instances[cache_key] = analyzer_class()

        return self._analyzer_instances[cache_key]

    def analyze(
        self,
        analyzer_name: str,
        image_path: Path,
        save_as_preset: Optional[str] = None,
        skip_cache: bool = False,
        background_tasks = None
    ) -> Dict[str, Any]:
        """
        Run analyzer on image

        Args:
            analyzer_name: Name of analyzer to use
            image_path: Path to image file
            save_as_preset: Optional preset name to save as
            skip_cache: Whether to skip cache
            background_tasks: Optional FastAPI BackgroundTasks for async visualization

        Returns:
            Analysis result dict
        """
        # Disable auto-visualization for outfit analyzer when using background tasks
        auto_visualize = (background_tasks is None) and (analyzer_name == "outfit")
        analyzer = self._get_analyzer(analyzer_name, auto_visualize=auto_visualize)

        # For comprehensive analyzer, use different method
        if analyzer_name == "comprehensive":
            result = analyzer.analyze(
                image_path,
                skip_cache=skip_cache,
                save_all_presets=(save_as_preset is not None),
                preset_prefix=save_as_preset
            )
        else:
            result = analyzer.analyze(
                image_path,
                skip_cache=skip_cache,
                save_as_preset=save_as_preset
            )

        # Convert Pydantic model to dict and include metadata
        if hasattr(result, 'model_dump'):
            data = result.model_dump()
        elif hasattr(result, 'dict'):
            data = result.dict()
        else:
            data = result if isinstance(result, dict) else {}

        # Manually add metadata if it exists (Pydantic excludes private fields like _metadata)
        if hasattr(result, '_metadata') and result._metadata:
            if hasattr(result._metadata, 'model_dump'):
                data['_metadata'] = result._metadata.model_dump()
            elif hasattr(result._metadata, 'dict'):
                data['_metadata'] = result._metadata.dict()
            else:
                data['_metadata'] = result._metadata

        # Queue visualization generation if we saved a preset and have background tasks
        if (background_tasks is not None and
            save_as_preset and
            "_metadata" in data and
            "preset_id" in data["_metadata"]):

            from ai_tools.outfit_visualizer.tool import OutfitVisualizer
            from ai_tools.shared.visualizer import PresetVisualizer
            from ai_tools.shared.preset import PresetManager
            from ai_capabilities.specs import (
                OutfitSpec,
                VisualStyleSpec,
                ArtStyleSpec,
                HairStyleSpec,
                HairColorSpec,
                MakeupSpec,
                ExpressionSpec,
                AccessoriesSpec
            )

            preset_id = data["_metadata"]["preset_id"]

            # Map analyzer names to category names and spec classes
            analyzer_category_map = {
                "outfit": ("outfits", OutfitSpec),
                "visual-style": ("visual_styles", VisualStyleSpec),
                "art-style": ("art_styles", ArtStyleSpec),
                "hair-style": ("hair_styles", HairStyleSpec),
                "hair-color": ("hair_colors", HairColorSpec),
                "makeup": ("makeup", MakeupSpec),
                "expression": ("expressions", ExpressionSpec),
                "accessories": ("accessories", AccessoriesSpec)
            }

            if analyzer_name in analyzer_category_map:
                category, spec_class = analyzer_category_map[analyzer_name]

                def generate_visualization():
                    """Background task to generate preset visualization"""
                    try:
                        preset_manager = PresetManager()
                        preset_dir = preset_manager._get_preset_dir(category)

                        if analyzer_name == "outfit":
                            # Use outfit-specific visualizer
                            visualizer = OutfitVisualizer()
                            spec = spec_class(**data)
                            visualizer.visualize(
                                outfit=spec,
                                output_dir=preset_dir,
                                preset_id=preset_id
                            )
                        else:
                            # Use generic visualizer for all other types
                            visualizer = PresetVisualizer()
                            spec = spec_class(**data)
                            visualizer.visualize(
                                spec_type=category,
                                spec=spec,
                                output_dir=preset_dir,
                                preset_id=preset_id
                            )

                        print(f"✅ Generated preview for {preset_id}")
                    except Exception as e:
                        print(f"⚠️  Preview generation failed: {e}")

                background_tasks.add_task(generate_visualization)
                print(f"🎨 Queued preview generation for {preset_id}")

        return data

    def list_analyzers(self) -> list:
        """List all available analyzers"""
        return [
            {
                "name": name,
                "description": info["description"],
                "category": info["category"],
                "estimated_cost": info["cost"],
                "avg_time_seconds": info["avg_time"]
            }
            for name, info in self.ANALYZERS.items()
        ]

    def get_analyzer_info(self, analyzer_name: str) -> Dict[str, Any]:
        """Get information about a specific analyzer"""
        if analyzer_name not in self.ANALYZERS:
            raise ValueError(f"Unknown analyzer: {analyzer_name}")

        info = self.ANALYZERS[analyzer_name]
        return {
            "name": analyzer_name,
            "description": info["description"],
            "category": info["category"],
            "estimated_cost": info["cost"],
            "avg_time_seconds": info["avg_time"]
        }

    def validate_analyzer(self, analyzer_name: str) -> bool:
        """Check if analyzer exists"""
        return analyzer_name in self.ANALYZERS
