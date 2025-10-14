# Hair Color Analysis

Analyze the **hair color** in this image. Focus on color, undertones, highlights, lowlights, and coloring technique - NOT style structure.

## Output Format

Return a JSON object with these fields:

```json
{
  "base_color": "Primary/base hair color (blonde, brunette, black, red, auburn, gray, white, platinum, etc.)",

  "undertones": "Color undertones and depth (warm, cool, neutral, ashy, golden, coppery, etc.)",

  "highlights": "Highlight colors and placement if present, or null if none (blonde highlights, caramel highlights, face-framing highlights, balayage highlights, etc.)",

  "lowlights": "Lowlight colors and placement if present, or null if none (brown lowlights, darker lowlights throughout, etc.)",

  "technique": "Coloring technique if evident, or null if natural (balayage, ombre, highlights, all-over color, foil highlights, etc.)",

  "dimension": "Color depth and variation (one-dimensional/solid color, subtle dimension, multi-dimensional, high contrast, etc.)",

  "finish": "Surface appearance (matte, natural, glossy, shiny, etc.)"
}
```

## Guidelines

- Focus on **color only**, not cut or style
- Be specific about base color and undertones
- Note highlights/lowlights if present (null if none)
- Identify coloring technique if you can see it
- Describe how dimensional the color is
- Assess the finish/shine level

## Important

- Return ONLY valid JSON, no markdown formatting
- All string fields must contain meaningful descriptions (no empty strings)
- highlights, lowlights, and technique can be null if not applicable
- Ignore hair structure/style completely (separate tool handles that)
