# Professional Makeup Analysis

Analyze the **makeup** in this image with the precision and expertise of a professional makeup artist. You are analyzing for makeup artists who need to recreate this exact look.

**CRITICAL: Think like a professional makeup artist breaking down a look for recreation. Be specific about products, application techniques, and placement.**

## Output Format

Return a JSON object with these fields:

```json
{
  "complexion": "DETAILED description of base, blush, bronzer, highlighter, and contour. Include: foundation finish (dewy/matte/natural), coverage level, blush placement and color, highlighter placement and intensity, contour technique if visible, overall skin finish. Example: 'Medium coverage dewy foundation with a natural, skin-like finish. Warm peachy blush applied to the apples of the cheeks and blended up toward the temples. Champagne highlighter on cheekbones, bridge of nose, and cupid's bow creating a subtle glow. No visible contouring - emphasis on fresh, luminous skin.'",

  "eyes": "DETAILED description of eyeshadow, eyeliner, mascara, and brows. Include: eyeshadow colors and placement (lid/crease/outer corner), blending technique, eyeliner style and placement, mascara application, brow shape and fill. Example: 'Soft brown matte shadow in the crease for definition, champagne shimmer on the lid, deeper brown in outer V. Thin black liner tight-lined along upper lash line, no wing. Full, dark lashes with volumizing mascara on top and bottom. Brows are naturally full, groomed and filled with soft brown powder in hair-like strokes, following natural arch.'",

  "lips": "DETAILED description of lip color, finish, application technique, and lip liner if visible. Example: 'Nude-pink lipstick with satin finish. Lips are well-defined with slightly overlining at the cupid's bow. Natural lip liner in matching tone used to define and prevent bleeding. Color is buildable and slightly deeper at the center, creating subtle dimension.'",

  "overall_style": "Professional description of the makeup style category and approach. Include: makeup aesthetic (natural/glam/editorial/etc.), who it would suit, occasion appropriateness, key techniques used. Example: 'Soft glam makeup with emphasis on luminous skin and defined but natural eyes. This is a polished everyday look suitable for photos, events, or professional settings. The technique showcases skin prep, strategic highlighting, and neutral tones that enhance rather than mask features. Classic and flattering approach that works across various skin tones.'",

  "intensity": "Makeup intensity level: natural/minimal, moderate/medium, dramatic/full",

  "color_palette": ["List", "ALL", "visible", "makeup", "colors", "like", "soft brown", "champagne", "nude pink", "warm peach", "black", "taupe"]
}
```

## CRITICAL REQUIREMENTS

**YOU MUST PROVIDE DETAILED, PROFESSIONAL MAKEUP ARTIST DESCRIPTIONS:**

### UNACCEPTABLE (TOO VAGUE):
```json
{
  "complexion": "Dewy foundation with blush",
  "eyes": "Brown eyeshadow with mascara",
  "lips": "Pink lipstick",
  "overall_style": "Natural makeup"
}
```
❌ **REJECTED** - These are surface-level observations, NOT professional makeup artist breakdowns!

### ACCEPTABLE (PROPERLY DETAILED):
```json
{
  "complexion": "Light to medium coverage foundation with a dewy, luminous finish that allows skin texture to show through naturally. The base has a slight sheen without looking oily. Soft coral-pink blush is applied to the apples of the cheeks with a fluffy brush and blended upward in a lifting motion toward the hairline. Liquid or cream highlighter in champagne-gold is placed on the high points: tops of cheekbones, down the bridge of the nose, inner corners of eyes, and cupid's bow, creating a natural-looking glow. No visible contour - the focus is on radiance and dimension through highlighting and strategic blush placement rather than sculpting.",

  "eyes": "Transition shade of soft taupe in the crease to create subtle depth, blended well into the brow bone. Mid-tone warm brown on the lid from lash line to crease, giving the eyes dimension without being dramatic. Deeper chocolate brown concentrated in the outer V and blended into the crease for definition. All shadows are matte and seamlessly blended with no harsh lines. Thin line of dark brown pencil liner smudged along the upper lash line for soft definition rather than a graphic line. Two coats of black volumizing and lengthening mascara on upper lashes, one light coat on lower lashes. Brows are naturally full and well-groomed, filled in with ash brown powder using light, hair-like strokes to maintain a natural appearance while adding structure.",

  "lips": "Nude-rose lipstick in a satin finish that's neither fully matte nor glossy - has a soft, comfortable sheen. The color is a 'my lips but better' shade that's slightly deeper and more pigmented than the natural lip color. Application appears even and smooth with good lip prep visible (no flaking or dryness). Subtle overlining at the cupid's bow to enhance the lip shape. Natural lip liner in a matching rosy-nude tone used to define the edges and prevent feathering, blended into the lipstick for a seamless finish.",

  "overall_style": "Professional everyday glam makeup emphasizing enhanced natural beauty rather than dramatic transformation. This is a refined approach suitable for professional headshots, daytime events, or anyone seeking polished yet approachable makeup. The technique demonstrates strong fundamentals: proper skin prep for a luminous base, strategic use of warm neutrals to add dimension without heaviness, and careful attention to blending and proportion. The color story is cohesive with warm undertones throughout (warm browns, peachy blush, nude-rose lips) creating harmony. This makeup works beautifully on camera and in person, flattering a wide range of skin tones and ages."
}
```
✓ **ACCEPTED** - Detailed professional analysis that a makeup artist could use to recreate the look!

## Professional Guidelines

- **Think like a professional makeup artist** creating a tutorial or breakdown
- **Use industry terminology**: transition shade, cut crease, baking, strobing, tight-lining, stippling, buffing
- **Be specific about placement**: apples of cheeks, outer V, waterline, lash line, high points, cupid's bow
- **Describe techniques**: how was it applied? Blended? Layered?
- **Note finish and texture**: matte, dewy, satin, shimmer, frost, metallic, natural
- **Explain product types when evident**: powder, cream, liquid, pencil, gel
- **Describe color accurately**: Use precise color names (taupe, not brown; champagne, not beige)

## Important

- Return ONLY valid JSON, no markdown formatting
- All detailed fields (complexion, eyes, lips, overall_style) must be multi-sentence professional descriptions
- color_palette must list ALL visible makeup colors (typically 5-10 colors)
- Intensity can be concise (natural/moderate/dramatic)
- Focus on makeup application and techniques, not the person's natural features
