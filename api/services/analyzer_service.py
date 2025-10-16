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
from ai_tools.character_appearance_analyzer.tool import CharacterAppearanceAnalyzer
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
        "character-appearance": {
            "class": CharacterAppearanceAnalyzer,
            "description": "Analyze character physical appearance (age, gender, ethnicity, features)",
            "category": "analyzer",
            "cost": 0.002,
            "avg_time": 4.0
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
        background_tasks = None,
        selected_analyses: Optional[dict] = None
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
                preset_prefix=None,  # No longer used - each preset gets AI-generated name
                selected_analyses=selected_analyses
            )
        else:
            # For individual analyzers, analyze first without saving
            result = analyzer.analyze(
                image_path,
                skip_cache=skip_cache,
                save_as_preset=None  # Don't save yet
            )

            # If user wanted to save, use the AI-generated suggested_name
            if save_as_preset:
                suggested_name = getattr(result, 'suggested_name', None)
                if suggested_name:
                    # Map analyzer names to category names
                    category_map = {
                        "outfit": "outfits",
                        "visual-style": "visual_styles",
                        "art-style": "art_styles",
                        "hair-style": "hair_styles",
                        "hair-color": "hair_colors",
                        "makeup": "makeup",
                        "expression": "expressions",
                        "accessories": "accessories",
                        "character-appearance": "character_appearance"
                    }

                    # Save using PresetManager directly
                    from ai_tools.shared.preset import PresetManager
                    preset_manager = PresetManager()
                    category = category_map.get(analyzer_name)

                    if category:
                        preset_path, preset_id = preset_manager.save(
                            category,
                            result,
                            display_name=suggested_name
                        )
                        # Update metadata
                        if result._metadata:
                            result._metadata.preset_id = preset_id
                            result._metadata.display_name = suggested_name
                        print(f"⭐ Saved as preset: {suggested_name} (ID: {preset_id})")

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

        # For comprehensive analyzer, convert all Pydantic models in results to dicts
        if analyzer_name == "comprehensive" and "results" in data:
            for result_type, result_data in data["results"].items():
                if result_data and not isinstance(result_data, dict):
                    # Convert Pydantic model to dict
                    if hasattr(result_data, 'model_dump'):
                        result_dict = result_data.model_dump()
                    elif hasattr(result_data, 'dict'):
                        result_dict = result_data.dict()
                    else:
                        continue

                    # Add metadata if it exists on the object
                    if hasattr(result_data, '_metadata') and result_data._metadata:
                        if hasattr(result_data._metadata, 'model_dump'):
                            result_dict['_metadata'] = result_data._metadata.model_dump()
                        elif hasattr(result_data._metadata, 'dict'):
                            result_dict['_metadata'] = result_data._metadata.dict()

                    # Replace the Pydantic model with the dict
                    data["results"][result_type] = result_dict

        # Queue visualization generation if we saved a preset and have background tasks
        if background_tasks is not None and save_as_preset:
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

            # Map analyzer names to category names and spec classes
            # Note: comprehensive analyzer uses underscores (visual_style), individual analyzers use hyphens (visual-style)
            analyzer_category_map = {
                "outfit": ("outfits", OutfitSpec),
                "visual-style": ("visual_styles", VisualStyleSpec),
                "visual_style": ("visual_styles", VisualStyleSpec),  # Comprehensive analyzer format
                "art-style": ("art_styles", ArtStyleSpec),
                "art_style": ("art_styles", ArtStyleSpec),  # Comprehensive analyzer format
                "hair-style": ("hair_styles", HairStyleSpec),
                "hair_style": ("hair_styles", HairStyleSpec),  # Comprehensive analyzer format
                "hair-color": ("hair_colors", HairColorSpec),
                "hair_color": ("hair_colors", HairColorSpec),  # Comprehensive analyzer format
                "makeup": ("makeup", MakeupSpec),
                "expression": ("expressions", ExpressionSpec),
                "accessories": ("accessories", AccessoriesSpec)
            }

            # Handle comprehensive analyzer - queue visualizations for all saved presets
            if analyzer_name == "comprehensive" and "results" in data:
                for result_type, result_data in data["results"].items():
                    if result_data and result_type in analyzer_category_map:
                        # Convert Pydantic model to dict if needed
                        if not isinstance(result_data, dict):
                            if hasattr(result_data, 'model_dump'):
                                result_dict = result_data.model_dump()
                            elif hasattr(result_data, 'dict'):
                                result_dict = result_data.dict()
                            else:
                                continue

                            # Add metadata if it exists on the object
                            if hasattr(result_data, '_metadata') and result_data._metadata:
                                if hasattr(result_data._metadata, 'model_dump'):
                                    result_dict['_metadata'] = result_data._metadata.model_dump()
                                elif hasattr(result_data._metadata, 'dict'):
                                    result_dict['_metadata'] = result_data._metadata.dict()
                        else:
                            result_dict = result_data

                        # Check if this result has a preset_id
                        if "_metadata" in result_dict and "preset_id" in result_dict["_metadata"]:
                            category, spec_class = analyzer_category_map[result_type]
                            preset_id = result_dict["_metadata"]["preset_id"]

                            def generate_visualization(cat=category, spec_cls=spec_class, res_data=result_dict, pid=preset_id, analyzer_type=result_type):
                                """Background task to generate preset visualization"""
                                try:
                                    preset_manager = PresetManager()
                                    preset_dir = preset_manager._get_preset_dir(cat)

                                    if analyzer_type == "outfit":
                                        # Use outfit-specific visualizer
                                        visualizer = OutfitVisualizer()
                                        spec = spec_cls(**res_data)
                                        visualizer.visualize(
                                            outfit=spec,
                                            output_dir=preset_dir,
                                            preset_id=pid
                                        )
                                    else:
                                        # Use generic visualizer for all other types
                                        visualizer = PresetVisualizer()
                                        spec = spec_cls(**res_data)
                                        visualizer.visualize(
                                            spec_type=cat,
                                            spec=spec,
                                            output_dir=preset_dir,
                                            preset_id=pid
                                        )

                                    print(f"✅ Generated preview for {pid} ({cat})")
                                except Exception as e:
                                    print(f"⚠️  Preview generation failed for {pid}: {e}")

                            background_tasks.add_task(generate_visualization)
                            print(f"🎨 Queued preview generation for {preset_id} ({category})")

            # Handle individual analyzer
            elif "_metadata" in data and "preset_id" in data["_metadata"]:
                preset_id = data["_metadata"]["preset_id"]

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
