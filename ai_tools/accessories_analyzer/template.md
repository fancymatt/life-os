# Accessories Analysis

Analyze all **accessories** visible in this image including jewelry, bags, belts, scarves, hats, watches, and other styling details.

## Output Format

Return a JSON object with these fields:

```json
{
  "jewelry": ["List of jewelry items: earrings, necklaces, bracelets, rings with descriptions"],

  "bags": "Bag or purse description if visible, otherwise null (leather crossbody bag, tote bag, clutch, etc.)",

  "belts": "Belt description if visible, otherwise null (brown leather belt, chain belt, etc.)",

  "scarves": "Scarf or wrap description if visible, otherwise null (silk scarf, knit scarf, etc.)",

  "hats": "Headwear description if visible, otherwise null (baseball cap, fedora, beanie, etc.)",

  "watches": "Watch description if visible, otherwise null (leather strap watch, smart watch, etc.)",

  "other": ["List of other accessories not covered above: sunglasses, hair accessories, pins, etc."],

  "overall_style": "Overall accessory styling approach (minimal/understated, statement pieces, layered, bold, classic, trendy, etc.)"
}
```

## Guidelines

- **Jewelry**: List each piece visible (e.g., "gold hoop earrings", "layered necklaces")
- **Bags**: Describe type, material, style if visible
- **Belts**: Note material, width, style if visible
- **Scarves**: Describe material, pattern, how it's worn if visible
- **Hats**: Type of headwear if visible
- **Watches**: Style and type if visible
- **Other**: Sunglasses, hair accessories, brooches, pins, etc.
- **Overall Style**: How would you describe the accessory approach?

## Important

- Return ONLY valid JSON, no markdown formatting
- jewelry and other are arrays (can be empty if none visible)
- bags, belts, scarves, hats, watches should be null if not visible
- overall_style must always have a description even if accessories are minimal
- If no accessories visible, note "minimal/no visible accessories" but still complete all fields appropriately
