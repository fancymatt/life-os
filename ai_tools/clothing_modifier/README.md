# Clothing Modifier Tool

AI-powered tool for modifying clothing item descriptions using natural language instructions.

## Overview

The Clothing Modifier uses AI to intelligently update clothing item descriptions based on simple text instructions. It preserves fields that aren't mentioned in the modification and maintains consistency across all fields.

## Features

- **Natural Language Input**: "Make these shoulder-length", "Change to red", "Add lace trim"
- **Selective Modification**: Only updates fields mentioned in the instruction
- **Consistency**: Ensures all fields (item, color, fabric, details, visual_description) remain aligned
- **Template Override**: Customize prompting via `data/tool_configs/clothing_modifier_template.md`
- **Configurable Model**: Set model in `configs/models.yaml`

## Usage

### Python API

```python
from ai_tools.clothing_modifier.tool import ClothingModifier

# Initialize modifier
modifier = ClothingModifier()

# Original item
item = {
    "item": "Black leather jacket",
    "category": "outerwear",
    "color": "black",
    "fabric": "leather",
    "details": "Classic motorcycle style with silver zippers",
    "visual_description": "A sleek black leather jacket"
}

# Modify
modified = modifier.modify(
    item=item,
    instruction="Change the color to burgundy and add quilted shoulders"
)

# Result
print(modified)
# {
#     "item": "Burgundy quilted leather jacket",
#     "category": "outerwear",
#     "color": "burgundy",
#     "fabric": "leather",
#     "details": "Classic motorcycle style with silver zippers and quilted shoulders",
#     "visual_description": "A burgundy leather jacket with quilted shoulder panels"
# }
```

### REST API

```bash
# Modify existing item (in-place)
curl -X POST http://localhost:8000/api/clothing-items/{item_id}/modify \
  -H "Content-Type: application/json" \
  -d '{"instruction": "Make these shoulder-length"}'

# Create variant (copy with changes)
curl -X POST http://localhost:8000/api/clothing-items/{item_id}/create-variant \
  -H "Content-Type: application/json" \
  -d '{"instruction": "Change to red with lace trim"}'
```

## Modification Examples

### Length Changes
- "Make these ankle-length"
- "Shorten to knee-length"
- "Extend to floor-length"

### Color Changes
- "Change the color to navy blue"
- "Make this burgundy"
- "Add red accents"

### Style Changes
- "Add lace trim"
- "Make this more formal"
- "Add floral embroidery"
- "Change to distressed style"

### Fabric Changes
- "Change to silk"
- "Make this in velvet"
- "Use a lighter cotton fabric"

### Combined Changes
- "Make this a red velvet version with gold buttons"
- "Change to knee-length with lace hem"
- "Navy blue casual version"

## Configuration

### Model Selection

Edit `configs/models.yaml`:

```yaml
# Clothing modification
clothing_modifier: "gemini/gemini-2.0-flash-exp"  # Fast, good at following instructions
# or
clothing_modifier: "openai/gpt-4"  # More creative, better at style understanding
```

### Custom Prompting

Override the default template by creating:

```
data/tool_configs/clothing_modifier_template.md
```

The template uses these variables:
- `{original_item}` - Item name
- `{original_category}` - Category (e.g., "outerwear")
- `{original_color}` - Color description
- `{original_fabric}` - Fabric/material
- `{original_details}` - Detailed description
- `{visual_description}` - Visual appearance
- `{instruction}` - User's modification request

## Use Cases

### In-Place Modification
- Quick corrections ("Fix the color to burgundy")
- Minor adjustments ("Add pockets")
- Updates based on real item ("Actually it has gold buttons, not silver")
- Sets `manually_modified: true` flag

### Variant Creation
- Design exploration ("What would this look like in red?")
- Seasonal variations ("Summer version with lighter fabric")
- Style iterations ("More formal version")
- Maintains `source_entity_id` link to original

## Error Handling

If AI modification fails:
- Returns original item with error note in `details` field
- Logs error for debugging
- Does not create partial/invalid items

## Temperature Setting

Default: `0.7` (creative but controlled)

- **Lower (0.3)**: More conservative, sticks closer to original
- **Higher (0.9)**: More creative interpretations

## Response Schema

Uses `ClothingItemResponse` schema:

```python
{
    "item": str,              # Short name
    "category": str,          # Category (preserved unless changed)
    "color": str,             # Primary color(s)
    "fabric": str,            # Material composition
    "details": str,           # Style details
    "visual_description": str # Visual appearance
}
```

## Tips

1. **Be specific**: "Change to navy blue" is better than "make it blue"
2. **One change at a time**: For complex changes, create multiple variants
3. **Review results**: AI interpretations may vary, check before saving
4. **Use variants**: Preserve originals by creating variants instead of modifying

## Related Tools

- **Entity Merger**: Merge duplicate clothing items
- **Outfit Analyzer**: Analyze clothing in images
- **Style Transfer**: Apply style to clothing visualizations

## Troubleshooting

**Modification doesn't preserve fields**:
- Check that template emphasizes preserving unchanged fields
- Verify instruction is specific about what to change

**Results are too creative**:
- Lower temperature in model config
- Make instruction more specific

**Fields are inconsistent**:
- Update template to emphasize consistency checks
- Use more specific instructions

## Development

Run standalone test:

```bash
cd /app
python3 -m ai_tools.clothing_modifier.tool
```

Run unit tests:

```bash
pytest tests/unit/test_clothing_modifier.py -v
```
