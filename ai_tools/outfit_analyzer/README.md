# Outfit Analyzer

Analyzes outfit images to extract detailed, structured outfit information including clothing items, fabrics, colors, construction details, style genre, formality level, and overall aesthetic.

## Features

- **Automatic Caching**: 7-day TTL with file hash validation
- **Preset Promotion**: Save and reuse refined analyses
- **Structured Output**: Returns validated Pydantic models
- **Metadata Tracking**: Records source, hash, model, timestamp
- **CLI Interface**: Command-line usage for quick analysis

## Architecture

```
Image → Cache Check → API Call → Parse → Cache → Optional Preset
                ↓                           ↓
            Cache Hit                   Reusable Artifact
```

## Usage

### Programmatic API

```python
from ai_tools.outfit_analyzer.tool import OutfitAnalyzer
from pathlib import Path

analyzer = OutfitAnalyzer()

# Basic analysis (auto-cached)
outfit = analyzer.analyze("image.jpg")

# Skip cache
outfit = analyzer.analyze("image.jpg", skip_cache=True)

# Save as preset
outfit = analyzer.analyze(
    "image.jpg",
    save_as_preset="casual-friday",
    preset_notes="Friday office outfit"
)

# Load from preset
outfit = analyzer.analyze_from_preset("casual-friday")

# Access structured data
print(outfit.style_genre)      # "modern minimalist"
print(outfit.formality)        # "business-casual"
for item in outfit.clothing_items:
    print(f"{item.item}: {item.color} {item.fabric}")
```

### CLI Usage

```bash
# Basic analysis
python ai_tools/outfit_analyzer/tool.py image.jpg

# Analyze and save as preset
python ai_tools/outfit_analyzer/tool.py image.jpg \
    --save-as professional-suit \
    --notes "Interview outfit"

# Skip cache (force re-analysis)
python ai_tools/outfit_analyzer/tool.py image.jpg --no-cache

# List all outfit presets
python ai_tools/outfit_analyzer/tool.py --list

# Use specific model
python ai_tools/outfit_analyzer/tool.py image.jpg --model gpt-4o
```

### Complete Workflow Example

```bash
# Run the workflow demo
python examples/test_outfit_analyzer.py path/to/outfit.jpg
```

## Output Structure

```python
OutfitSpec(
    clothing_items=[
        ClothingItem(
            item="slim-fit blazer",
            fabric="wool worsted",
            color="charcoal gray",
            details="two-button closure, notch lapels, ..."
        ),
        # ... more items
    ],
    style_genre="modern professional",
    formality="business-formal",
    aesthetic="minimalist with Italian tailoring influences"
)
```

## Preset Workflow

1. **Analyze**: Run analysis on an image
2. **Cache**: Result automatically cached (7 days)
3. **Promote**: Save as preset for manual refinement
4. **Edit**: Manually adjust the JSON preset file
5. **Reuse**: Load edited preset in other workflows

### Preset Structure

Presets are saved to `presets/outfits/{name}.json`:

```json
{
  "data": {
    "clothing_items": [...],
    "style_genre": "...",
    "formality": "...",
    "aesthetic": "..."
  },
  "metadata": {
    "created_at": "2025-01-15T10:30:00",
    "tool": "outfit-analyzer",
    "tool_version": "1.0.0",
    "model_used": "gemini-2.0-flash",
    "source_image": "path/to/image.jpg",
    "source_hash": "sha256:...",
    "notes": "User notes here"
  }
}
```

## Cache Behavior

- **Location**: `cache/outfits/`
- **TTL**: 7 days (configurable)
- **Validation**: SHA256 hash of source image
- **Invalidation**: Automatic on file changes

```python
# Get cache statistics
stats = analyzer.get_cache_stats()
print(f"Cached: {stats.total_items} items ({stats.total_size_mb:.2f} MB)")
print(f"Hit rate: {stats.hits / (stats.hits + stats.misses):.1%}")
```

## Model Configuration

Default model is set in `configs/models.yaml`:

```yaml
defaults:
  outfit_analyzer: "gemini-2.0-flash"
```

Override per-call:

```python
analyzer = OutfitAnalyzer(model="gpt-4o")
```

## Analysis Details

The analyzer extracts:

### Clothing Items
- Item type with style descriptors (e.g., "cropped bomber jacket")
- Fabric composition and quality (e.g., "heavyweight denim")
- Precise color descriptions (e.g., "midnight navy")
- Construction details (seams, hardware, closures)
- Fit characteristics (slim, relaxed, oversized)
- Condition and styling

### Style Information
- **Style Genre**: Fashion category (e.g., "streetwear", "preppy")
- **Formality**: casual | smart-casual | business-casual | business-formal | formal
- **Aesthetic**: Design philosophy and cultural influences

### Exclusions
The analyzer does NOT include:
- Eyewear (glasses, sunglasses)
- Weapons or tactical gear
- Makeup or cosmetics
- Environmental/lighting descriptions
- Background elements

## Examples

### Example 1: Professional Outfit

```python
outfit = analyzer.analyze("business-suit.jpg")

# Output:
# Style: modern professional
# Formality: business-formal
# Items:
#   - navy wool suit jacket (notch lapels, two-button)
#   - white cotton dress shirt (point collar, French cuffs)
#   - gray wool trousers (flat front, tapered)
#   - black leather oxford shoes (cap toe, Goodyear welt)
```

### Example 2: Casual Streetwear

```python
outfit = analyzer.analyze("streetwear.jpg", save_as_preset="street-look")

# Output:
# Style: contemporary streetwear
# Formality: casual
# Items:
#   - oversized cotton hoodie (gray, kangaroo pocket)
#   - black denim jeans (distressed, tapered fit)
#   - white leather sneakers (chunky sole, minimal design)
```

## Integration

Use analyzed outfits in other tools:

```python
# Analyze outfit
outfit = analyzer.analyze("photo.jpg", save_as_preset="fav-outfit")

# Later: Load in image generation
from ai_tools.outfit_generator.tool import OutfitGenerator

generator = OutfitGenerator()
result = generator.generate(
    outfit_preset="fav-outfit",  # Uses analyzed outfit
    visual_style="film-noir",
    person_description="tall, athletic build"
)
```

## Testing

```bash
# Unit tests
pytest tests/unit/test_outfit_analyzer.py -v

# Integration test with real API
python examples/test_outfit_analyzer.py test-image.jpg
```

## Metadata

Each analysis includes metadata:

```python
print(outfit._metadata.tool)           # "outfit-analyzer"
print(outfit._metadata.tool_version)   # "1.0.0"
print(outfit._metadata.model_used)     # "gemini-2.0-flash"
print(outfit._metadata.source_image)   # "path/to/image.jpg"
print(outfit._metadata.source_hash)    # "sha256:..."
print(outfit._metadata.created_at)     # datetime
```

This metadata enables:
- Audit trails
- Cache invalidation
- Preset versioning
- Reproducibility
