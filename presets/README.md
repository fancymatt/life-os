# Presets

This directory contains **user-editable presets** - curated, reusable building blocks for AI tools.

## What are Presets?

Presets are promoted artifacts from analysis tools that you want to reuse and potentially refine manually. Unlike cache (which is ephemeral), presets are:

- **Permanent** - They don't expire
- **Editable** - You can modify them by hand
- **Named** - They have meaningful names you choose
- **Versioned** - They can be committed to git
- **Shareable** - They can be shared across projects/teams

## Directory Structure

```
presets/
├── outfits/           # Outfit analyses (OutfitSpec)
├── visual-styles/     # Photographic styles (VisualStyleSpec)
├── art-styles/        # Artistic styles (ArtStyleSpec)
├── hair-styles/       # Hair structure/cut (HairStyleSpec)
├── hair-colors/       # Hair coloring (HairColorSpec)
├── makeup/            # Makeup applications (MakeupSpec)
├── expressions/       # Facial expressions (ExpressionSpec)
├── accessories/       # Accessories (AccessoriesSpec)
└── video-prompts/     # Video prompts (VideoPromptSpec)
```

## Preset Format

Each preset is a JSON file with:
- `_metadata`: Provenance information (created_at, tool, model_used, notes)
- Fields specific to the preset type

Example: `outfits/fancy-suit.json`

```json
{
  "_metadata": {
    "created_at": "2025-10-14T14:30:22Z",
    "tool": "outfit-analyzer",
    "tool_version": "1.0.0",
    "source_image": "refs/suit.jpg",
    "source_hash": "a3f8b92c",
    "model_used": "gemini-2.0-flash",
    "notes": "Professional black suit, edited to emphasize slim fit"
  },
  "clothing_items": [
    {
      "item": "suit jacket",
      "fabric": "wool",
      "color": "charcoal black",
      "details": "notch lapel, two-button, slim fit, single vent"
    }
  ],
  "style_genre": "modern professional",
  "formality": "business formal",
  "aesthetic": "contemporary minimalist"
}
```

## Workflow

### 1. Analyze → Cache
```bash
# Analyze an image (auto-cached)
ai-tool analyze outfit refs/suit.jpg
```

### 2. Cache → Preset (Promote)
```bash
# If you like the result, promote it to a preset
ai-tool save-preset outfit refs/suit.jpg --name fancy-suit
```

### 3. Edit Preset
```bash
# Edit the preset manually
ai-tool edit-preset outfit fancy-suit
# Or open in your editor: presets/outfits/fancy-suit.json
```

### 4. Use Preset
```bash
# Use the preset in generation
ai-tool generate --outfit fancy-suit --subject jaimee.jpg
```

## Management Commands

```bash
# List all presets
ai-tool list-presets outfit

# Show preset details
ai-tool show-preset outfit fancy-suit

# Validate preset
ai-tool validate-preset outfit fancy-suit

# Delete preset
ai-tool delete-preset outfit fancy-suit
```

## Best Practices

1. **Meaningful Names**: Use descriptive names (e.g., `corporate-headshot` not `style1`)
2. **Add Notes**: Include context in the `notes` field
3. **Version Control**: Commit presets to git for history tracking
4. **Organize**: Use consistent naming conventions within each category
5. **Test**: Validate presets after manual edits

## Tips

- Start with generated presets, then refine them
- Keep a library of your best presets
- Share presets across projects by copying preset files
- Use presets as templates for variations
