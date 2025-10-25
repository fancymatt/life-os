# Entity Merger - Creative Fusion

You are an expert at creatively fusing two {{entity_type}} entities into a single hybrid.

Your task is to analyze two {{entity_type}} entities and CREATE A CREATIVE HYBRID that combines elements from both into ONE unified item.

## CRITICAL: Creative Fusion Rules

**DO NOT** simply list both items together (e.g., "gold earrings and airpods")
**DO** create a genuine hybrid that morphs characteristics from both items into a single novel item

### Fusion Strategy

1. **Identify the core elements from each item**:
   - Item type (earrings, airpods, shirt, etc.)
   - Materials (gold, plastic, cotton, etc.)
   - Shape/form (round, rectangular, sleeveless, etc.)
   - Function (wearable, audio device, protective, etc.)
   - Color/finish (gold, matte black, red, etc.)

2. **Create a hybrid by combining elements creatively**:
   - Take the form/shape from one item and apply materials/colors from the other
   - Combine functional aspects (e.g., earrings that play audio)
   - Blend visual characteristics (e.g., airpod-shaped jewelry)
   - Merge materials (e.g., gold-plated electronics, fabric with embedded tech)

### Examples of Creative Fusion

- **"Gold earrings" + "AirPods"** → "Gold-plated wireless earbuds shaped like decorative earrings" or "Earrings shaped like miniature AirPods with gold finish"
- **"Red cotton shirt" + "Blue leather jacket"** → "Purple cotton-leather hybrid jacket-shirt with mixed fabric construction"
- **"Round sunglasses" + "VR headset"** → "Round-lensed augmented reality eyewear with retro aesthetic"
- **"Silver necklace" + "Smartwatch"** → "Silver chain necklace with integrated smart pendant display"

### Field Merging Rules

- **Item name**: Create a NEW name that describes the hybrid (not "X and Y")
- **Materials**: Combine or blend materials creatively (e.g., "gold-accented polymer", "cotton-leather blend")
- **Color**: Mix colors if appropriate (red + blue = purple), or use one as primary with the other as accent
- **Details**: Describe how the hybrid combines features from both items
- **Category**: Choose the most appropriate category for the hybrid, or blend categories if supported

## Source Entities

**SOURCE ENTITY** (ID will be kept):
```json
{{source_entity}}
```

**TARGET ENTITY** (will be archived):
```json
{{target_entity}}
```

## Your Task

Analyze the two entities above and CREATE A CREATIVE HYBRID that fuses them into ONE novel item.

**Think creatively**: How can you combine the materials, colors, shapes, and functions into a single unique hybrid?

**Your output should be**:
- A single item that genuinely combines both sources
- Not a description of two separate items
- Creative and imaginative in how it blends characteristics
- Coherent and physically/conceptually plausible

**CRITICAL**: Return ONLY valid JSON matching the {{entity_type}} schema. Do not include markdown code blocks or explanations.
