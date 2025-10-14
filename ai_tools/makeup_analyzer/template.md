# Makeup Analysis

Analyze the **makeup** in this image including complexion, eyes, lips, and overall makeup style.

## Output Format

Return a JSON object with these fields:

```json
{
  "complexion": "Foundation, blush, highlighter, contour details (dewy foundation with subtle contour, matte base with rosy blush, etc.)",

  "eyes": "Eye shadow, liner, mascara, brows (neutral matte shadow, winged black liner, full lashes, groomed brows, etc.)",

  "lips": "Lip color, finish, and application (nude matte lipstick, glossy pink lip, red lip, natural tinted balm, etc.)",

  "overall_style": "Makeup style category (natural/no-makeup makeup, glam, editorial, smoky eye, fresh-faced, bold, etc.)",

  "intensity": "Overall makeup intensity level (natural/minimal, moderate, dramatic/full)",

  "color_palette": ["List", "dominant", "makeup", "colors", "like", "bronze", "pink", "nude", "etc."]
}
```

## Guidelines

- **Complexion**: Describe base, blush, highlight, contour if visible
- **Eyes**: Cover shadow, liner, mascara, brow grooming
- **Lips**: Note color, finish (matte/glossy/satin), intensity
- **Overall Style**: What makeup aesthetic is this?
- **Intensity**: How much makeup overall?
- **Color Palette**: List 3-7 dominant makeup colors

## Important

- Return ONLY valid JSON, no markdown formatting
- All string fields must contain meaningful descriptions (no empty strings)
- color_palette must be an array of color names
- If no makeup is visible, describe as "natural/no visible makeup" but still analyze any subtle elements
