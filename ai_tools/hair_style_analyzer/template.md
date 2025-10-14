# Hair Style Analysis

Analyze the **hair style structure** in this image. Focus on cut, length, layers, texture, volume, and styling - NOT color.

## Output Format

Return a JSON object with these fields:

```json
{
  "cut": "What type of haircut/cut is this? (bob, layers, blunt, shag, pixie, lob, etc.)",

  "length": "Overall hair length (very short, short, medium, long, very long, etc.)",

  "layers": "Describe the layering structure (no layers/one length, subtle layers, heavy layers, choppy layers, etc.)",

  "texture": "Natural texture and how it's styled (straight, wavy, curly, coily, sleek, tousled, etc.)",

  "volume": "Volume and body (flat, moderate volume, voluminous, big/full, etc.)",

  "parting": "Part placement and style (center part, side part, no part, zigzag part, etc.)",

  "front_styling": "How the front is styled - bangs, framing, face-framing layers (blunt bangs, side-swept bangs, curtain bangs, no bangs, face-framing layers, etc.)",

  "overall_style": "Overall hairstyle category (sleek bob, beachy waves, messy bun, high ponytail, braided updo, etc.)"
}
```

## Guidelines

- Focus on **structure and styling**, not color
- Be specific about cut type and layering
- Describe texture as both natural and styled
- Note any distinctive features (bangs, part, volume)
- Overall style should be a descriptive category

## Important

- Return ONLY valid JSON, no markdown formatting
- All string fields must contain meaningful descriptions (no empty strings)
- Ignore hair color completely (separate tool handles that)
