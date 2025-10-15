# Art Style Analysis

Analyze the **artistic style** of this image as if it were a piece of art or had artistic treatment applied.

Focus on the aesthetic and creative aspects that make this image feel like art - not the subject matter or photographic technique, but the **artistic rendering and stylistic choices**.

## Output Format

Return a JSON object with these fields:

```json
{
  "suggested_name": "Short descriptive name (2-4 words)",

  "medium": "What artistic medium does this resemble? (oil painting, watercolor, digital art, charcoal, ink, acrylic, mixed media, etc.)",

  "technique": "What artistic techniques are evident? (impasto, glazing, dry brush, stippling, cross-hatching, digital painting, etc.)",

  "color_palette": ["List", "all", "dominant", "colors", "used", "in", "the", "artwork"],

  "brush_style": "If applicable, describe the brushwork characteristics (visible brush strokes, smooth blending, textured, gestural, precise, etc.). Return null if not applicable.",

  "texture": "Describe the surface texture quality (rough, smooth, layered, flat, dimensional, matte, glossy, etc.)",

  "composition_style": "What compositional approach is used? (classical, modern, dynamic, static, balanced, asymmetrical, minimalist, busy, etc.)",

  "artistic_movement": "What art historical movement or style does this evoke? (impressionism, realism, abstract expressionism, surrealism, pop art, contemporary digital art, etc.)",

  "mood": "What emotional quality or atmosphere does the art create? (serene, energetic, melancholic, joyful, dramatic, ethereal, etc.)",

  "level_of_detail": "How detailed vs. loose is the rendering? (highly detailed/realistic, moderately detailed, loose/impressionistic, abstract/minimal, etc.)"
}
```

## Suggested Name

Generate a short, descriptive name (2-4 words) that captures the artistic style:
- Combine medium and movement (e.g., "Impressionist Oil Painting", "Digital Pop Art")
- Or use technique and mood (e.g., "Loose Watercolor Sketch", "Detailed Pencil Drawing")
- Keep it art-focused
- Examples: "Abstract Acrylic Art", "Realistic Oil Portrait", "Vintage Comic Style", "Modern Digital Illustration"

## Guidelines

- **Medium**: Identify what this looks like it was created with
- **Technique**: Describe HOW the art appears to be made
- **Color Palette**: List all significant colors (5-10 colors typically)
- **Brush Style**: Only describe if visible brush work or similar marks are present
- **Texture**: Describe the surface quality you perceive
- **Composition Style**: How is the visual space organized?
- **Artistic Movement**: What art history period or style does this reference?
- **Mood**: The emotional or atmospheric quality of the piece
- **Level of Detail**: Detailed realism vs. loose abstraction

## Important

- Focus on artistic aesthetics, not photographic technique
- If the image is a photograph, describe what artistic style it evokes or resembles
- Be specific and descriptive
- Return ONLY valid JSON, no markdown formatting
- All string fields must contain meaningful descriptions (no empty strings)
- color_palette must be an array of color names
- brush_style can be null if not applicable
