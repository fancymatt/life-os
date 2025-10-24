"""
Entity Merger Tool

Uses AI to intelligently merge duplicate entities across all entity types.
Combines information from both entities while preserving unique details.

Supports template override in data/tool_configs/entity_merger_template.md
"""

from pathlib import Path
from typing import Dict, Any, Optional
import sys
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.shared.router import LLMRouter, RouterConfig
from api.config import settings
from api.logging_config import get_logger

logger = get_logger(__name__)


class EntityMerger:
    """
    Uses AI to intelligently merge duplicate entities

    Features:
    - Template-based prompting
    - Custom template override support
    - Configurable model
    - Fallback to simple merge on AI failure
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.3
    ):
        """
        Initialize the entity merger

        Args:
            model: Model to use (default from config)
            temperature: Model temperature (default: 0.3 for consistency)
        """
        # Get model from config if not specified
        if model is None:
            config = RouterConfig()
            model = config.get_model_for_tool("entity_merger")

        self.router = LLMRouter(model=model)
        self.temperature = temperature

    def _load_template(self) -> str:
        """
        Load template with override support.

        Checks for custom template first, then falls back to base template.
        """
        # Check for custom template override
        custom_template_path = settings.base_dir / "data" / "tool_configs" / "entity_merger_template.md"
        if custom_template_path.exists():
            logger.info(f"Using custom entity merger template ({custom_template_path.stat().st_size} bytes)")
            return custom_template_path.read_text()

        # Fall back to base template
        base_template_path = Path(__file__).parent / "template.md"
        logger.info(f"Using base entity merger template ({base_template_path.stat().st_size} bytes)")
        return base_template_path.read_text()

    def merge(
        self,
        entity_type: str,
        source_entity: Dict[str, Any],
        target_entity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge two entities using AI analysis

        Args:
            entity_type: Type of entity (character, clothing_item, etc.)
            source_entity: Entity to keep (this ID will remain)
            target_entity: Entity to merge in (this will be archived)

        Returns:
            Merged entity data with combined information

        Raises:
            Exception: If merge fails
        """
        logger.info(f"🔄 Merging {entity_type} entities...")
        logger.info(f"   Model: {self.router.model}")
        logger.info(f"   Temperature: {self.temperature}")
        logger.info(f"   Source: {len(source_entity)} fields")
        logger.info(f"   Target: {len(target_entity)} fields")

        # Load template
        template = self._load_template()

        # Fill template with entity data
        prompt = template.replace("{{entity_type}}", entity_type)
        prompt = prompt.replace("{{source_entity}}", json.dumps(source_entity, indent=2))
        prompt = prompt.replace("{{target_entity}}", json.dumps(target_entity, indent=2))

        try:
            # Call AI to merge entities
            response = self.router.call(
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=2000
            )

            # Parse AI response (strip markdown code blocks if present)
            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove trailing ```
            response_text = response_text.strip()

            merged_data = json.loads(response_text)

            logger.info(f"✅ AI generated merged {entity_type} with {len(merged_data)} fields")

            return merged_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI merge response: {e}")
            logger.error(f"Response text: {response_text[:200]}...")
            # Fallback to simple merge
            logger.warning("Falling back to simple merge logic")
            return self._simple_merge(source_entity, target_entity)
        except Exception as e:
            logger.error(f"Error in AI merge: {e}")
            raise

    def _simple_merge(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback simple merge if AI fails.
        Takes the non-empty value from either entity, preferring source.
        """
        logger.info("🔧 Using simple merge strategy (fallback)")
        merged = source.copy()

        for key, value in target.items():
            # Skip IDs and timestamps
            if key.endswith('_id') or key.endswith('_at'):
                continue

            # If source doesn't have this field or it's empty, use target's
            if key not in merged or not merged[key]:
                merged[key] = value
            # Special handling for lists (merge)
            elif isinstance(value, list) and isinstance(merged[key], list):
                # Merge lists, remove duplicates
                merged[key] = list(set(merged[key] + value))
            # Special handling for dicts (merge)
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key].update(value)

        return merged


def main():
    """CLI interface for entity merger"""
    import argparse
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Merge two entities using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge two characters from JSON files
  python tool.py character source.json target.json

  # Use custom model
  python tool.py character source.json target.json --model gemini/gemini-2.5-flash
        """
    )

    parser.add_argument(
        'entity_type',
        help='Entity type (character, clothing_item, etc.)'
    )

    parser.add_argument(
        'source_file',
        help='Path to source entity JSON file (ID will be kept)'
    )

    parser.add_argument(
        'target_file',
        help='Path to target entity JSON file (will be archived)'
    )

    parser.add_argument(
        '--model',
        help='Model to use (default from config)'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        default=0.3,
        help='Model temperature (default: 0.3)'
    )

    parser.add_argument(
        '--output',
        help='Output file path for merged entity'
    )

    args = parser.parse_args()

    # Load entity files
    try:
        with open(args.source_file) as f:
            source_entity = json.load(f)

        with open(args.target_file) as f:
            target_entity = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load entity files: {e}")
        sys.exit(1)

    # Merge entities
    merger = EntityMerger(model=args.model, temperature=args.temperature)

    try:
        merged = merger.merge(args.entity_type, source_entity, target_entity)

        # Print results
        logger.info("\n" + "="*70)
        logger.info(f"Merged {args.entity_type.title()}")
        logger.info("="*70)
        logger.info(json.dumps(merged, indent=2))
        logger.info("="*70)

        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(merged, f, indent=2)
            logger.info(f"\n💾 Saved merged entity to {args.output}")

    except Exception as e:
        logger.error(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
