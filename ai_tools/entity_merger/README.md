# Entity Merger Tool

Intelligently merges duplicate entities using AI analysis.

## Features

- **Template-based prompting** - Edit prompts in `template.md`
- **Custom template override** - Create `data/tool_configs/entity_merger_template.md` to customize
- **Configurable model** - Set in `configs/models.yaml`
- **Fallback logic** - Simple merge if AI fails
- **Preserves all data** - Combines information from both entities

## Usage

### From Code

```python
from ai_tools.entity_merger.tool import EntityMerger

merger = EntityMerger()
merged = merger.merge(
    entity_type="clothing_item",
    source_entity={"item": "Black Jeans", "color": "Black", ...},
    target_entity={"item": "Skinny Black Jeans", "color": "Black", "fabric": "Denim", ...}
)
# Returns: {"item": "Skinny Black Jeans", "color": "Black", "fabric": "Denim", ...}
```

### From CLI

```bash
# Merge two entities from JSON files
python ai_tools/entity_merger/tool.py character source.json target.json

# Use custom model
python ai_tools/entity_merger/tool.py clothing_item source.json target.json --model gemini/gemini-2.5-flash

# Save output to file
python ai_tools/entity_merger/tool.py character source.json target.json --output merged.json
```

## How It Works

1. **Load template** - Checks for custom override, falls back to base template
2. **Fill template** - Inserts entity type and entity data into template
3. **Call AI** - Uses configured model to generate merged entity
4. **Parse response** - Strips markdown code blocks, parses JSON
5. **Fallback** - If AI fails, uses simple merge logic

## Customizing the Template

Create `data/tool_configs/entity_merger_template.md`:

```markdown
# Entity Merger

You are merging {{entity_type}} entities.

Source: {{source_entity}}
Target: {{target_entity}}

Create a merged version that...
```

Available template variables:
- `{{entity_type}}` - Entity type (e.g., "clothing_item")
- `{{source_entity}}` - JSON of source entity (ID will be kept)
- `{{target_entity}}` - JSON of target entity (will be archived)

## Configuration

In `configs/models.yaml`:

```yaml
defaults:
  entity_merger: "gemini/gemini-2.0-flash-exp"

tool_settings:
  entity_merger:
    temperature: 0.3  # Lower for consistency
```

## Merge Strategy

The AI follows these rules:

1. **Preserve all unique information** from both entities
2. **Combine descriptions intelligently** - synthesize, don't concatenate
3. **Merge tags** - union of both sets
4. **Combine metadata** - preserve all metadata fields
5. **Choose most detailed** - prefer more complete fields
6. **Maintain consistency** - ensure merged data is coherent

## Examples

### Merging Clothing Items

**Source:**
```json
{
  "item": "Black Jeans",
  "color": "Black",
  "details": "Slim fit"
}
```

**Target:**
```json
{
  "item": "Skinny Black Jeans",
  "color": "Black",
  "fabric": "Stretch denim",
  "details": "High-rise, 5-pocket styling"
}
```

**Merged:**
```json
{
  "item": "Skinny Black Jeans",
  "color": "Black",
  "fabric": "Stretch denim",
  "details": "High-rise, slim fit, 5-pocket styling"
}
```

### Merging Characters

**Source:**
```json
{
  "name": "Jenny",
  "visual_description": "Blonde hair, blue eyes",
  "tags": ["protagonist", "kind"]
}
```

**Target:**
```json
{
  "name": "Jenny Martinez",
  "visual_description": "Long blonde hair, blue eyes, athletic build",
  "personality": "Kind and adventurous",
  "tags": ["protagonist", "adventurer"]
}
```

**Merged:**
```json
{
  "name": "Jenny Martinez",
  "visual_description": "Long blonde hair, blue eyes, athletic build",
  "personality": "Kind and adventurous",
  "tags": ["protagonist", "kind", "adventurer"]
}
```

## Fallback Merge Logic

If AI fails, the tool uses simple merge:

1. Start with source entity (copy all fields)
2. For each field in target:
   - If source doesn't have it or it's empty, use target's value
   - If both have lists, merge and deduplicate
   - If both have dicts, merge (target overwrites source keys)
3. Skip IDs and timestamps (never merge these)

This ensures the merge always succeeds, even if AI is unavailable.
