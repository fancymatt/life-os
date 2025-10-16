# Character Appearance Analysis Prompt

Analyze the person in this image with precision. Extract detailed physical appearance information for character description and illustration reference.

Return a JSON object with this **exact** structure:

```json
{
  "suggested_name": "Short descriptive name (2-4 words, e.g., 'Young Adult Woman', 'Middle-Aged Man')",
  "age_appearance": "apparent age or age group (e.g., 'young child', 'teenager', 'young adult', 'middle-aged', 'elderly')",
  "gender_presentation": "gender presentation (e.g., 'feminine', 'masculine', 'androgynous')",
  "ethnicity": "apparent ethnicity or ethnic features (or null if not discernible)",
  "skin_tone": "skin tone (e.g., 'fair', 'light', 'medium', 'olive', 'tan', 'brown', 'dark')",
  "face_shape": "face shape (e.g., 'round', 'oval', 'heart-shaped', 'square', 'long')",
  "hair_description": "complete hair description including color, style, length, and texture",
  "eye_description": "eye color and notable features",
  "build": "body build or physique (e.g., 'slender', 'athletic', 'average', 'stocky', 'petite', 'tall')",
  "height_appearance": "apparent height (e.g., 'short', 'average height', 'tall')",
  "distinctive_features": "any distinctive features like freckles, dimples, scars, tattoos, etc. (or null if none)",
  "overall_description": "a complete, flowing paragraph combining all features in natural language"
}
```

## Field Descriptions

### suggested_name
- A short, descriptive identifier (2-4 words)
- Examples: "Young Adult Woman", "Middle-Aged Man", "Teenage Girl", "Elderly Gentleman"
- Should capture age group and gender presentation

### age_appearance
- Apparent age or age group
- Examples: "young child" (0-12), "teenager" (13-19), "young adult" (20-35), "middle-aged" (36-60), "elderly" (60+)
- Describe what you see, not actual age

### gender_presentation
- How the person presents in terms of gender
- Options: "feminine", "masculine", "androgynous"
- Based on visible presentation, not assumptions

### ethnicity
- Apparent ethnicity or ethnic features if discernible
- Examples: "East Asian", "African", "European", "South Asian", "Middle Eastern", "Hispanic/Latin American", "Indigenous"
- Use null if not clearly discernible
- Be respectful and objective

### skin_tone
- Describe skin tone precisely
- Examples: "fair", "light", "medium", "olive", "tan", "brown", "dark", "deep brown"
- Can include undertones if relevant: "fair with cool undertones", "medium with warm undertones"

### face_shape
- Basic face shape
- Common types: "oval", "round", "heart-shaped", "square", "long", "diamond"

### hair_description
- **Comprehensive** hair description
- Include: color, style, length, texture
- Examples:
  - "Long, straight black hair with bangs, glossy texture"
  - "Short, curly brown hair in a natural afro style"
  - "Shoulder-length wavy blonde hair with highlights"
  - "Bald" or "shaved head" if applicable

### eye_description
- Eye color and notable features
- Examples:
  - "Brown almond-shaped eyes"
  - "Blue eyes with prominent eyelashes"
  - "Green eyes"
  - "Dark brown eyes"

### build
- Body build or physique
- Examples: "slender", "athletic", "average", "stocky", "muscular", "petite", "curvy", "heavyset"
- Be objective and respectful

### height_appearance
- Apparent height relative to average
- Options: "short", "average height", "tall", "very tall"

### distinctive_features
- Any notable distinguishing features
- Examples:
  - "Freckles across nose and cheeks"
  - "Dimples when smiling"
  - "Small scar above left eyebrow"
  - "Multiple ear piercings"
  - "Visible tattoos on arms"
- Use null if no distinctive features are visible

### overall_description
- A complete, natural-language paragraph combining all features
- Should flow as a cohesive character description
- Example: "A young adult woman with an oval face and fair skin tone. She has long, straight black hair and brown almond-shaped eyes. She appears to be of average height with a slender build. Her face is unmarked by distinctive features, presenting a clean, youthful appearance."

## Critical Rules

### DO Include:
- All visible physical characteristics
- Objective descriptions
- Complete information for all required fields

### DO NOT Include:
- Clothing or accessories (outfit details belong in outfit analysis)
- Personality traits or emotional state
- Background or environmental details
- Subjective judgments or assumptions

### Important Notes:
- Be respectful and objective in all descriptions
- Focus on visible, physical characteristics only
- For ethnicity, only describe if clearly apparent; use null if uncertain
- Descriptions should enable accurate character illustration

## Output Format

Return ONLY a single JSON object (NOT an array) matching the structure above.

**CRITICAL**: Return the object directly, not wrapped in an array:
- ✅ CORRECT: `{"suggested_name": "...", "age_appearance": "...", ...}`
- ❌ WRONG: `[{"suggested_name": "...", ...}]`

No markdown code blocks, no explanations, no array brackets - just the JSON object.

Remember: This description will be used for consistent character illustration in stories and artwork.
