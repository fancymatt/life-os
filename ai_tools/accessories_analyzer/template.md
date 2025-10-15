# Professional Accessories Analysis

Analyze all **accessories** in this image with the precision of a professional fashion stylist. You are analyzing for stylists, designers, and fashion professionals who need to understand complete accessory coordination.

**CRITICAL: Think like a professional fashion stylist noting every accessory detail for client recreation or editorial styling.**

## Output Format

```json
{
  "jewelry": ["Detailed list of each jewelry piece with material, style, and finish. Example: 'delicate gold chain necklace with small pendant', 'silver hoop earrings (medium, 2-inch diameter)', 'stacked thin gold rings on index and middle fingers'"],

  "bags": "Detailed bag description with type, material, hardware, and size, or null if not visible. Example: 'Black leather structured crossbody bag with gold chain strap and quilted pattern, approximately 8x6 inches'",

  "belts": "Detailed belt description with material, width, buckle style, and how it's worn, or null. Example: 'Brown leather belt, 1.5 inches wide, with antique gold rectangular buckle, worn at natural waist'",

  "scarves": "Detailed scarf description with material, pattern, size, and styling, or null. Example: 'Silk square scarf in paisley print (navy and gold), approximately 24x24 inches, tied loosely around neck in European knot'",

  "hats": "Detailed headwear description with style, material, and fit, or null. Example: 'Wide-brim felt fedora in camel color with black band, worn straight with slight tilt'",

  "watches": "Detailed watch description with case, strap, and style, or null. Example: 'Rose gold case watch with brown leather strap, classic round face, worn on left wrist'",

  "other": ["List other accessories not covered above: sunglasses, hair clips, brooches, pins, etc. with details"],

  "overall_style": "DETAILED professional assessment of accessory styling approach, coordination, and fashion sense. Example: 'Layered, eclectic accessory approach mixing metals (gold and silver) with bohemian sensibility. The styling shows confidence in breaking traditional jewelry rules while maintaining visual balance. Multiple delicate pieces create interest without overwhelming. The overall effect is curated but effortless, suggesting someone who understands proportion and knows how to make statement pieces work together.'"
}
```

## Professional Guidelines - Fashion Stylist Perspective

- **Be Specific About Materials**: leather type (patent, pebbled, smooth), metal finish (brushed gold, polished silver, rose gold)
- **Note Proportions**: jewelry thickness/delicacy, bag size, belt width, scarf dimensions
- **Describe Styling Choices**: how items are worn, layering techniques, intentional mismatching
- **Hardware Details**: clasp types, buckles, chains, zippers, studs, embellishments
- **Coordination Analysis**: Do accessories work together? What's the styling philosophy?
- **Fashion Context**: Is this minimalist, maximalist, trendy, classic, eclectic?

## Important

- jewelry and other are arrays - list each piece separately with full details
- bags, belts, scarves, hats, watches should be null if not visible
- overall_style must be a detailed professional assessment, not just "minimal" or "bold"
- Return ONLY valid JSON
