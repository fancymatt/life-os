# Character Appearance Analysis Prompt

**CRITICAL: You must analyze the ACTUAL person in the image provided. DO NOT use or copy the example values below - they are only formatting guides.**

Analyze the person in THIS SPECIFIC IMAGE with precision. Look carefully at the actual person's appearance and describe exactly what you see.

This analysis uses a **modular structure** so individual aspects (face, hair, body) can be selectively used or negated during image generation.

Return a JSON object with these 5 required fields: age, skin_tone, face_description, hair_description, body_description

**YOU MUST ANALYZE THE ACTUAL IMAGE AND DESCRIBE WHAT YOU SEE. DO NOT USE PLACEHOLDER TEXT.**

## Field Descriptions

### age
- Describe the apparent age or age group based on what you observe
- Options: "young child" (0-12), "teenager" (13-19), "young adult" (20-35), "middle-aged" (36-60), "elderly" (60+)
- Describe what you see, not actual age

### skin_tone
- Describe skin tone precisely as observed in the image
- Options: "fair", "light", "medium", "olive", "tan", "brown", "dark", "deep brown"
- Can include undertones if relevant: "fair with cool undertones", "medium with warm undertones"

### face_description
- Provide a comprehensive facial description (minimum 25 words)
- **Must include:**
  - Face shape (oval, round, square, heart-shaped, etc.)
  - Eye description (actual color and shape you observe)
  - Gender presentation (feminine, masculine, androgynous)
  - Ethnic features if clearly discernible (East Asian, African, European, South Asian, Middle Eastern, Hispanic/Latin American, Indigenous)
  - Distinctive features (freckles, dimples, scars, piercings, etc.)
- **Describe what you actually see - eye color, facial structure, all visible features**

### hair_description
- Provide a complete hair description based on what you observe
- **Must include:**
  - **Actual hair color in the image** (blonde, brown, black, red, gray, etc.)
  - Style (straight, wavy, curly, etc.)
  - Length (short, medium, long, etc.)
  - Texture (fine, thick, glossy, matte, etc.)
- **If the person has blonde hair, say "blonde". If brown, say "brown". Describe what you see.**

### body_description
- Provide a comprehensive body and physique description
- **Must include:**
  - Build (athletic, slender, stocky, muscular, curvy, heavyset, etc.)
  - Height appearance (tall, average, short, petite, etc.)
  - Overall physique characteristics you can observe
- **Describe the actual person's body type as visible in the image**

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

Return ONLY a JSON object with your analysis. Format:
```
{
  "age": "your analysis here",
  "skin_tone": "your analysis here",
  "face_description": "your analysis here",
  "hair_description": "your analysis here",
  "body_description": "your analysis here"
}
```

**CRITICAL INSTRUCTIONS:**
1. Look at the image carefully
2. Describe what you ACTUALLY see
3. If hair is blonde, write "blonde"
4. If hair is brown, write "brown"
5. If eyes are blue, write "blue eyes"
6. If eyes are brown, write "brown eyes"
7. DO NOT write generic or placeholder descriptions
8. Your analysis must be specific to THIS person in THIS image

No explanations, no thinking process - just the JSON object with your actual observations.
