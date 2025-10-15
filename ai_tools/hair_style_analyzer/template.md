# Professional Hair Style Analysis

Analyze the **hair style structure** in this image with the precision and detail of a professional hair stylist. Focus on cut, length, layers, texture, volume, and styling - NOT color.

**CRITICAL: You MUST write detailed, multi-sentence professional descriptions for cut, layers, texture, front_styling, and overall_style. Short summaries will be REJECTED.**

## Output Format

Return a JSON object with these fields:

```json
{
  "suggested_name": "Short descriptive name (2-4 words)",

  "cut": "DETAILED 3-5 sentence professional description of the haircut. Include: cut type/name, shape and silhouette, perimeter technique (blunt, textured, graduated), interior layering method, weight line placement, and overall structure. Example: 'This is a precision blunt bob with a strong geometric perimeter that falls just below the jawline. The cut features a classic one-length technique with minimal internal texturing, creating a solid, dense shape. The perimeter is razor-sharp and maintains a perfect horizontal line all around the head. The weight is concentrated at the ends, giving the style its characteristic bold, graphic silhouette. The interior has subtle point-cutting to remove bulk while maintaining the dense appearance.'",

  "length": "Overall hair length using professional descriptors (e.g., 'chin-length', 'shoulder-length', 'collarbone-length', 'mid-back length', 'waist-length', 'very short/cropped', 'pixie length')",

  "layers": "DETAILED 3-5 sentence professional description of the layering structure. Include: layer placement and distribution, graduation degree, weight concentration, how layers create movement and shape, connectivity between sections, and elevation technique used. Example: 'The hair features heavy, dramatic layering throughout with significant elevation and over-direction. Layers begin at the crown and graduate down with a high elevation technique, creating substantial internal movement and removing weight from the mid-lengths. The graduation is quite pronounced with shorter interior layers creating lift and volume at the crown while longer perimeter lengths maintain density at the ends. The layers are connected with point-cutting and slide-cutting techniques to create soft, feathered transitions rather than harsh lines. This layering structure allows for maximum movement, body, and dimension in the overall shape.'",

  "texture": "DETAILED 3-5 sentence description of both natural texture and styling. Include: natural curl/wave pattern (straight, wavy, curly, coily), current finish (sleek, tousled, defined), styling techniques visible (blow-dried, flat-ironed, curled, air-dried), texture of ends, and any smoothing or texturizing products evident. Example: 'The hair has a naturally straight to slightly wavy base texture that has been meticulously styled for a sleek, polished finish. Every strand appears smooth and perfectly aligned, achieved through precision blow-drying with a round brush followed by flat-iron work to seal the cuticle. The texture is glass-like and reflective with no visible frizz or flyaways, indicating the use of smoothing serums and heat protectant. The ends maintain the same sleek texture without any wispy or piece-y separation. The overall finish is sophisticated and glossy with a mirror-like shine.'",

  "volume": "Volume and body using professional descriptors (e.g., 'flat at roots with body through mid-lengths', 'lifted crown with rounded shape', 'full and voluminous throughout', 'compressed with minimal volume', 'big hair with maximum body')",

  "parting": "Part placement and style (e.g., 'deep side part on the left', 'precise center part', 'no visible part/undone', 'zigzag part', 'off-center part', 'swept back with no defined part')",

  "front_styling": "DETAILED 2-4 sentence description of how the front and face-framing area is styled. Include: bang type and length (if applicable), face-framing layer placement, how front pieces fall, styling direction, and framing effect. Example: 'The front features long, dramatic side-swept bangs that fall across the forehead at a diagonal, grazing the eyebrow on one side. Soft face-framing layers begin at the cheekbone and gradually blend into the longer lengths, creating a flattering frame around the face. The front pieces are styled with a slight bend away from the face, adding movement and softness to the perimeter.'",

  "overall_style": "DETAILED 2-4 sentence professional description of the complete hairstyle. Include: style category/name, key distinctive features, styling approach, and overall aesthetic. Example: 'This is a modern interpretation of classic anime-inspired twin pigtails styled with a fashion-forward, editorial approach. The style features two high-positioned ponytails with extreme length and volume, secured at the crown area with a slight outward angle. The ponytails are styled with deliberately exaggerated movement and lift, creating a playful yet sophisticated silhouette that references Japanese street fashion and cosplay culture.'"
}
```

## Suggested Name

Generate a short, descriptive name (2-4 words) that describes the hairstyle:
- Use structure and length (e.g., "Long Layered Waves", "Short Pixie Cut")
- Can include texture or styling (e.g., "Sleek Straight Bob", "Messy Beach Waves")
- Keep it hairstyling-focused
- Examples: "Blunt Bob Cut", "Long Layered Hair", "Curly Shoulder-Length", "Slicked Back Ponytail"

## CRITICAL REQUIREMENTS

**YOU MUST PROVIDE DETAILED, PROFESSIONAL DESCRIPTIONS:**

### UNACCEPTABLE (TOO SHORT):
```json
{
  "cut": "Long pigtails",
  "layers": "Heavy layers",
  "texture": "Straight and sleek",
  "front_styling": "No bangs",
  "overall_style": "Anime pigtails"
}
```
❌ **REJECTED** - These are brief labels, NOT professional hair stylist descriptions!

### ACCEPTABLE (PROPERLY DETAILED):
```json
{
  "cut": "This style maintains significant length throughout with a long-layered cut technique that preserves the overall length while removing interior weight. The perimeter is kept very long, extending well past the mid-back when worn down, with a slightly tapered end shape rather than a blunt line. The cut incorporates vertical layering to reduce bulk and allow for easier styling into high ponytails without excessive heaviness. The interior is textured with point-cutting to create movement while maintaining the density needed for the voluminous pigtail silhouette.",

  "layers": "The hair features substantial layering throughout with a heavy graduation that removes significant weight from the interior while preserving length at the perimeter. Layers are distributed from the crown down with high elevation techniques, creating lift and body at the roots while allowing longer lengths to flow and move. The graduation is quite pronounced with several inches of difference between the shortest crown layers and the longest perimeter lengths. This extensive layering structure enables the dramatic volume and movement seen in the styled pigtails, preventing the hair from appearing flat or heavy despite its considerable length.",

  "texture": "The hair displays a naturally straight base texture that has been meticulously styled to achieve a perfectly sleek, glass-like finish with high shine. The strands are completely smooth and aligned, showing evidence of thorough blow-drying with a paddle brush followed by flat-iron passes to seal the cuticle and eliminate any texture or wave. There is no frizz, flyaway hairs, or piece-y separation visible - every strand flows in the same direction creating a unified, polished appearance. The finish is distinctly glossy and reflective, indicating the use of shine serums and smoothing products applied during the styling process.",

  "front_styling": "The front is styled without bangs, maintaining a clean, swept-back approach that keeps the forehead completely clear. The hairline is pulled back smoothly into the high pigtails without any face-framing pieces or shorter layers left out around the face. The front sections are secured tightly to create a sleek, polished look at the hairline with no soft or wispy pieces.",

  "overall_style": "This is a high fashion interpretation of anime-style twin pigtails, featuring two dramatically positioned ponytails secured at the upper crown area with significant height and outward projection. The style references Japanese animation and cosplay culture while being executed with salon-quality precision and polish. The pigtails are positioned symmetrically with substantial volume and length, creating an exaggerated, playful silhouette that makes a bold style statement."
}
```
✓ **ACCEPTED** - Detailed, professional descriptions that a hair stylist would use!

## Professional Guidelines

- **Think like a professional hair stylist** analyzing a client's hair for replication
- **Use industry terminology**: graduation, elevation, perimeter, weight line, internal layering, point-cutting, slide-cutting
- **Be specific about techniques**: How was it cut? How was it styled? What products/tools were likely used?
- **Describe structure and shape**: How does the cut create the overall silhouette?
- **Explain the "how" and "why"**: Why does this cut look this way? How do the layers create movement?
- **Focus on structure and styling**, completely ignore color

## Important

- Return ONLY valid JSON, no markdown formatting
- All detailed fields (cut, layers, texture, front_styling, overall_style) must be multi-sentence professional descriptions
- Short fields (length, volume, parting) can be concise professional descriptors
- Ignore hair color completely (separate tool handles that)
