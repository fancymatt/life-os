# Outfit Analysis Prompt

Analyze the outfit in this image with extreme precision and detail. You are analyzing for fashion designers who need comprehensive information about every element.

Return a JSON object with this **exact** structure:

```json
{
  "suggested_name": "Short descriptive name (2-4 words)",
  "clothing_items": [
    {
      "item": "garment type",
      "fabric": "material and texture",
      "color": "precise color description",
      "details": "comprehensive construction, fit, and styling details"
    }
  ],
  "style_genre": "fashion genre and styling category",
  "formality": "formality level (casual/smart-casual/business-casual/business-formal/formal)",
  "aesthetic": "overall aesthetic influences and design philosophy"
}
```

## Suggested Name

Generate a short, descriptive name (2-4 words) that captures the key essence of this outfit:
- Focus on the most prominent or distinctive item (e.g., "Black Leather Jacket")
- Include key color if notable (e.g., "Red Floral Dress")
- Can reference the overall style (e.g., "Casual Denim Look", "Elegant Evening Wear")
- Keep it simple and memorable
- Examples: "Blue Denim Jacket", "Summer Floral Dress", "Black Suit Ensemble", "Cozy Sweater Look"

## Clothing Items Analysis

For EACH clothing item, provide:

### Item Field
- Exact garment type with all variations (e.g., "cropped bomber jacket", "midi wrap dress", "palazzo pants")
- Include specific style descriptors (fitted, oversized, tailored, relaxed, etc.)

### Fabric Field
- Fabric composition (e.g., "merino wool", "silk charmeuse", "heavyweight denim", "cotton poplin")
- Quality indicators (heavyweight, fine-gauge, brushed, woven, knit)
- Texture descriptions (smooth, textured, ribbed, cable-knit)
- **CRITICAL**: NEVER use "faux", "vegan", or "synthetic" - describe as genuine materials
  - Say "leather" not "faux leather"
  - Say "fur" not "faux fur"
  - Say "suede" not "faux suede"

### Color Field
- Use fashion color terminology (e.g., "midnight navy", "winter white", "camel beige", "oxblood red")
- For multi-color items, list all colors
- Specify contrast elements (e.g., "charcoal body with black collar and white cuffs")

### Details Field
Comprehensive description including:
- **Collar details**: Type and color (e.g., "white Peter Pan collar", "black notched lapel", "contrast white collar visible")
- **Cuffs and trim**: Colors if different from main garment (e.g., "white cuffs", "red piping")
- **Construction**: French seams, raw hem, topstitching, darted, pleated
- **Hardware**: Buttons, zippers, rivets with finish (gold-tone buttons, silver zipper, black rivets)
- **Closures**: Two-button, snap-front, zip-front, pullover
- **Pattern details**: Stripes, checks, prints with colors and scale
- **Pockets**: Types, placement, flap/welt/patch
- **Condition**: Pristine, distressed, vintage, worn-in
- **Styling**: Cuffed, tucked, belted, layered, unbuttoned
- **Fit**: Slim, relaxed, oversized, tailored, form-fitting
- **Special details**: Vents, pleats, darts, princess seams

## Style Genre

Fashion category ONLY - NO environmental or lighting descriptions:
- Genre: (e.g., "modern minimalist", "streetwear", "bohemian", "preppy", "avant-garde")
- Formality indicators
- Styling techniques visible
- Fashion influences or movements

## Formality

Choose the appropriate level:
- **casual**: Everyday relaxed wear
- **smart-casual**: Polished but comfortable
- **business-casual**: Office-appropriate but not formal
- **business-formal**: Traditional business attire
- **formal**: Evening wear, black-tie events

## Aesthetic

Overall aesthetic philosophy and design influences:
- Design movements (minimalist, maximalist, vintage, contemporary)
- Cultural influences (Japanese minimalism, French chic, Italian tailoring)
- Styling approach (effortless, polished, edgy, classic)
- Visual cohesion and proportion

## Critical Rules

### DO Include:
- All visible clothing items (tops, bottoms, outerwear, shoes)
- Accessories (watches, jewelry, belts, bags, scarves, hats - but NOT glasses or weapons)
- Detailed fabric, color, and construction information
- Styling choices and garment interaction

### DO NOT Include:
- Glasses or eyewear
- Weapons or weapon accessories (guns, knives, holsters, ammunition, tactical gear)
- Makeup, cosmetics, or facial features
- Tattoos, body art, or piercings (except earrings as accessories)
- Nail polish or nail art
- Environmental lighting (neon, street lights, atmospheric lighting)
- Background elements or settings
- Location or scene descriptions
- Atmospheric descriptions (moody, dark, noir, cyberpunk, etc.)

### Material Description Rules:
**ALWAYS** describe materials as genuine. Fashion designers need accurate material names:
- Leather (not faux leather, vegan leather, or synthetic leather)
- Fur (not faux fur or fake fur)
- Suede (not faux suede)
- Wool (not synthetic wool)
- This applies to ALL materials - use the genuine material name

## Output Format

Return ONLY valid JSON matching the structure above. No markdown code blocks, no explanations - just the JSON object.

Remember: Fashion designers need this level of detail for accurate recreation and styling decisions.
