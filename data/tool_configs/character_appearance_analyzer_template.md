# Character Appearance Analysis Prompt

Analyze the person in this image with precision. Extract detailed physical appearance information for character description and illustration reference.

This analysis uses a **modular structure** so individual aspects (face, hair, body) can be selectively used or negated during image generation.

Return a JSON object with this **exact** structure:

```json
{
  "age": "apparent age or age group (e.g., 'young child', 'teenager', 'young adult', 'middle-aged', 'elderly')",
  "skin_tone": "skin tone (e.g., 'fair', 'light', 'medium', 'olive', 'tan', 'brown', 'dark')",
  "face_description": "at least 25 words, complete facial description including shape, eyes, distinctive features, gender presentation, and ethnic features",
  "hair_description": "complete hair description including color, style, length, and texture",
  "body_description": "body description including build, height appearance, and physique",
  "overall_description": "a complete, flowing paragraph combining all features in natural language"
}
```

## Field Descriptions

### age
- Apparent age or age group
- Examples: "young child" (0-12), "teenager" (13-19), "young adult" (20-35), "middle-aged" (36-60), "elderly" (60+)
- Describe what you see, not actual age

### skin_tone
- Describe skin tone precisely
- Examples: "fair", "light", "medium", "olive", "tan", "brown", "dark", "deep brown"
- Can include undertones if relevant: "fair with cool undertones", "medium with warm undertones"

### face_description
- **Comprehensive** facial description combining multiple aspects
- Include:
  - Face shape
  - Eye description (color, shape, notable features)
  - Gender presentation (feminine, masculine, androgynous)
  - Ethnic features if discernible (East Asian, African, European, South Asian, Middle Eastern, Hispanic/Latin American, Indigenous)
  - Distinctive features (freckles, dimples, scars, piercings, etc.)
- Examples:
  - "Oval face with feminine features, brown almond-shaped eyes, and East Asian characteristics. Light freckles across nose and cheeks."
  - "Square, masculine face with blue eyes and European features. Strong jawline and slight stubble."
  - "Round face with androgynous features, green eyes, and fair complexion. Small dimples when smiling."

### hair_description
- **Comprehensive** hair description
- Include: color, style, length, texture
- Examples:
  - "Long, straight black hair with bangs, glossy texture"
  - "Short, curly brown hair in a natural afro style"
  - "Shoulder-length wavy blonde hair with highlights"
  - "Bald" or "shaved head" if applicable

### body_description
- **Comprehensive** body and physique description
- Include: build, height appearance, overall physique
- Examples:
  - "Tall and athletic with broad shoulders"
  - "Petite and slender, average height"
  - "Average height with stocky, muscular build"
  - "Short with curvy, heavyset build"

### overall_description
- A complete, natural-language paragraph combining all features
- Should flow as a cohesive character description
- Example: "A young adult woman with an oval face, feminine features, and fair skin tone with East Asian characteristics. She has brown almond-shaped eyes and light freckles across her nose and cheeks. Her long, straight black hair has a glossy texture. She appears to be of average height with a slender build."

## Critical Rules

### DO Include:
- All visible physical characteristics
- Objective descriptions
- Complete information for all required fields
- Gender presentation as observed (not assumed)
- Ethnic features only if clearly apparent

### DO NOT Include:
- Clothing or accessories (outfit details belong in outfit analysis)
- Personality traits or emotional state
- Background or environmental details
- Subjective judgments or assumptions

### Important Notes:
- Be respectful and objective in all descriptions
- Focus on visible, physical characteristics only
- For ethnic features, only describe if clearly apparent; omit from face_description if uncertain
- Descriptions should enable accurate character illustration
- **Modularity**: Each field (face, hair, body) should be complete and usable independently for image generation

## Output Format

Return ONLY a single JSON object (NOT an array) matching the structure above.

**CRITICAL**: Return the object directly, not wrapped in an array:
- ✅ CORRECT: `{"suggested_name": "...", "age": "...", ...}`
- ❌ WRONG: `[{"suggested_name": "...", ...}]`

No markdown code blocks, no explanations, no array brackets - just the JSON object.

Remember: This description will be used for consistent character illustration in stories and artwork. Each field may be used independently or in combination during image generation.
