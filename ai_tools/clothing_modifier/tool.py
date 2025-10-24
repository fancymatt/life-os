"""
Clothing Modifier Tool

Modifies clothing item descriptions based on natural language instructions.
Supports both in-place modification and variant creation.

Examples:
- "Make these shoulder-length"
- "Change the color to red"
- "Add floral embroidery"
- "Make this more casual"
"""

from typing import Dict, Any, Optional
import os
from ai_tools.shared.router import LLMRouter, RouterConfig
from api.logging_config import get_logger

logger = get_logger(__name__)


class ClothingModifier:
    """
    Modifies clothing item descriptions using AI.

    Features:
    - Template-based prompting
    - Custom template override support (data/tool_configs/clothing_modifier_template.md)
    - Configurable model (models.yaml)
    - Preserves fields not mentioned in modification
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Initialize the clothing modifier.

        Args:
            model: LLM model to use (defaults to models.yaml config)
            temperature: Temperature for generation (0.7 = creative but controlled)
        """
        if model is None:
            config = RouterConfig()
            model = config.get_model_for_tool("clothing_modifier")

        self.router = LLMRouter(model=model)
        self.temperature = temperature
        self._load_template()

    def _load_template(self):
        """Load the prompt template (with override support)"""
        # Check for custom override template
        override_path = "/app/data/tool_configs/clothing_modifier_template.md"
        base_path = os.path.join(os.path.dirname(__file__), "template.md")

        if os.path.exists(override_path):
            template_path = override_path
            logger.info(f"Using custom template: {override_path}")
        else:
            template_path = base_path
            logger.info(f"Using base template: {base_path}")

        with open(template_path, 'r') as f:
            self.template = f.read()

    def modify(
        self,
        item: Dict[str, Any],
        instruction: str
    ) -> Dict[str, Any]:
        """
        Modify a clothing item based on natural language instruction.

        Args:
            item: Original clothing item data (must include: item, category, color, fabric, details)
            instruction: Natural language modification request
                Examples:
                - "Make these shoulder-length"
                - "Change to red"
                - "Add lace trim"

        Returns:
            Modified clothing item data with updated fields

        Raises:
            ValueError: If instruction is empty or item is missing required fields
        """
        if not instruction or not instruction.strip():
            raise ValueError("Modification instruction cannot be empty")

        required_fields = ['item', 'category', 'color', 'fabric', 'details']
        missing = [f for f in required_fields if f not in item]
        if missing:
            raise ValueError(f"Item missing required fields: {missing}")

        # Build prompt from template
        prompt = self.template.format(
            original_item=item['item'],
            original_category=item['category'],
            original_color=item.get('color', 'not specified'),
            original_fabric=item.get('fabric', 'not specified'),
            original_details=item.get('details', 'not specified'),
            visual_description=item.get('visual_description', 'not specified'),
            instruction=instruction
        )

        logger.info(f"Modifying clothing item with instruction: {instruction}")

        # Define simple schema for structured output
        from pydantic import BaseModel, Field

        class ClothingItemModification(BaseModel):
            """Modified clothing item fields"""
            item: str = Field(description="Short name of the item")
            category: str = Field(description="Category (e.g., tops, bottoms, outerwear)")
            color: str = Field(description="Color description")
            fabric: str = Field(description="Fabric/material")
            details: str = Field(description="Construction and styling details")
            visual_description: str = Field(description="Visual appearance description", default="")

        try:
            # Get AI modification using structured output
            result = self.router.call_structured(
                prompt=prompt,
                response_model=ClothingItemModification,
                temperature=self.temperature
            )

            # Extract the clothing item data
            if hasattr(result, 'model_dump'):
                modified_data = result.model_dump()
            elif isinstance(result, dict):
                modified_data = result
            else:
                raise ValueError(f"Unexpected result type: {type(result)}")

            logger.info(f"Successfully modified clothing item")
            return modified_data

        except Exception as e:
            logger.error(f"AI modification failed: {e}")
            # Fallback: return original with error note
            fallback = item.copy()
            fallback['details'] = f"{item.get('details', '')} [Modification failed: {str(e)}]"
            return fallback


def modify_clothing(
    item: Dict[str, Any],
    instruction: str,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function for one-off clothing modifications.

    Args:
        item: Original clothing item data
        instruction: Modification instruction
        model: Optional model override

    Returns:
        Modified clothing item data
    """
    modifier = ClothingModifier(model=model)
    return modifier.modify(item, instruction)


if __name__ == "__main__":
    # Example usage
    sample_item = {
        "item": "Black leather jacket",
        "category": "outerwear",
        "color": "black",
        "fabric": "leather",
        "details": "Classic motorcycle style with silver zippers",
        "visual_description": "A sleek black leather jacket with asymmetric zipper closure"
    }

    instruction = "Change the color to burgundy and add quilted shoulders"

    modifier = ClothingModifier()
    result = modifier.modify(sample_item, instruction)

    logger.info("Original:", sample_item)
    logger.info("\nInstruction:", instruction)
    logger.info("\nModified:", result)
