# Visual Style Analysis Prompt

Analyze the complete visual style, aesthetics, and technical qualities of this image with extreme detail.

Return a JSON object with this **exact** structure:

```json
{
  "composition": "detailed description of composition, rule of thirds, visual balance, leading lines, etc.",
  "framing": "precise framing details (e.g., extreme close-up, close-up, medium shot, full body, waist-up, 3/4 shot, wide shot, etc.)",
  "pose": "exact BODY POSE description - hands position relative to body, arms position, head tilt, shoulders, stance. DO NOT mention any clothing items or accessories like sunglasses, hats, jewelry",
  "body_position": "body position and orientation (e.g., standing, sitting, lying down, leaning, profile view, three-quarter view, facing camera, looking away, etc.)",
  "lighting": "comprehensive lighting analysis including type, direction, quality, shadows, highlights, contrast",
  "color_palette": ["list", "of", "all", "dominant", "and", "accent", "colors"],
  "color_grading": "color grading and toning (e.g., warm tones, cool tones, desaturated, high contrast, vintage color cast, sepia, etc.)",
  "mood": "overall mood, atmosphere, and emotional tone",
  "background": "detailed background description including depth, bokeh, environmental elements",
  "photographic_style": "specific photographic style (e.g., fashion editorial, candid snapshot, formal portrait, street photography, studio shot, etc.)",
  "artistic_style": "artistic and aesthetic style (e.g., retro 80s, film noir, minimalist, grunge, glamour, etc.)",
  "film_grain": "presence and intensity of film grain or noise (e.g., heavy grain, subtle grain, clean/no grain, digital noise)",
  "image_quality": "image quality characteristics (e.g., sharp, soft focus, motion blur, lens flare, chromatic aberration, vignetting)",
  "era_aesthetic": "time period aesthetic if apparent (e.g., 1980s, 1990s, modern, vintage, retro-futuristic, timeless)",
  "camera_angle": "camera angle and perspective (e.g., eye level, low angle, high angle, dutch angle, bird's eye view)",
  "depth_of_field": "depth of field characteristics (e.g., shallow DOF with bokeh, deep DOF, selective focus, tilt-shift)",
  "post_processing": "apparent post-processing effects (e.g., HDR, cross-processing, split-toning, filters, overlays, light leaks)"
}
```

## CRITICAL INSTRUCTIONS

### What to EXCLUDE:
- **DO NOT** include ANY clothing, accessories, or outfit elements in your analysis
- **DO NOT** mention sunglasses, hats, jewelry, watches, or any worn items
- **DO NOT** describe fashion or styling choices
- Clothing/accessories will be handled separately - you must IGNORE them completely

### What to FOCUS ON:
- Photographic style, body positioning, and visual aesthetics ONLY
- The "pose" field should describe ONLY body position (arms, hands, head angle, stance)
- Camera settings and technical aspects
- Color treatment and grading
- Lighting setup and quality
- Composition and framing

## Detailed Analysis Guidelines

### Composition
Describe the compositional elements:
- Rule of thirds application
- Visual balance and symmetry
- Leading lines and visual flow
- Negative space usage
- Focal point placement

### Framing
Specify the exact framing:
- Extreme close-up (face only)
- Close-up (head and shoulders)
- Medium close-up (chest up)
- Medium shot (waist up)
- Medium full shot (knee up)
- Full shot (entire body)
- Long shot (body with significant surroundings)
- Wide shot (environmental context)

### Pose (Body Language ONLY)
Describe body position without mentioning clothing or accessories:
- Head position: tilted, straight, turned
- Shoulder orientation: squared, angled, relaxed
- Arms: crossed, at sides, raised, bent
- Hands: open, closed, positioned relative to body
- Stance: weight distribution, posture

### Body Position
Overall body orientation and position:
- Standing, sitting, lying, leaning, kneeling
- Facing camera, profile, three-quarter view, back to camera
- Static or in motion
- Relaxed or tense posture

### Lighting
Comprehensive lighting analysis:
- **Type**: Natural daylight, golden hour, studio lighting, mixed sources
- **Direction**: Front-lit, back-lit, side-lit, overhead, from below
- **Quality**: Hard/harsh, soft/diffused, rim lighting, chiaroscuro
- **Shadows**: Deep shadows, soft shadows, no shadows
- **Highlights**: Specular highlights, soft highlights
- **Contrast**: High contrast, low contrast, balanced
- **Color temperature**: Daylight (5600K), tungsten (3200K), warm, cool

### Color Palette
List ALL dominant and accent colors present:
- Primary colors: The 2-3 most dominant colors
- Secondary colors: Supporting colors
- Accent colors: Small but noticeable pops of color
- Use specific color names (e.g., "burnt sienna", "teal blue", "warm ivory")

### Color Grading
Describe the color treatment:
- Warm tones (oranges, yellows, reds pushed)
- Cool tones (blues, cyans, greens emphasized)
- Desaturated/washed out
- High contrast/crushed blacks
- Vintage color cast
- Sepia or monochrome toning
- Selective color (one color emphasized)
- Cross-processing effects
- Teal and orange (popular cinema look)

### Mood & Atmosphere
The emotional quality and feeling:
- Dramatic, moody, mysterious
- Bright, cheerful, energetic
- Melancholic, nostalgic, wistful
- Intimate, warm, inviting
- Cold, distant, alienating
- Peaceful, serene, calm

### Background
Detailed background description:
- Environment type (indoor, outdoor, studio, urban, nature)
- Depth: Shallow focus, deep focus
- Bokeh quality: Smooth, busy, circular, hexagonal
- Environmental elements: Architecture, nature, abstract
- Background treatment: Blurred, sharp, gradient, solid color

### Photographic Style
The genre or approach of photography:
- Fashion editorial
- Portrait (formal, casual, environmental)
- Street photography
- Documentary style
- Fine art photography
- Commercial/advertising
- Candid snapshot
- Studio shot
- Lifestyle photography

### Artistic Style
The aesthetic or artistic movement:
- Film noir (high contrast, shadows)
- Retro 80s (vibrant, high saturation)
- Vintage (faded, warm tones)
- Minimalist (clean, simple, negative space)
- Grunge (gritty, desaturated)
- Glamour (polished, smooth)
- Cinematic (widescreen feel, dramatic lighting)
- Contemporary (modern, clean)

### Film Grain & Texture
Describe grain and noise characteristics:
- Heavy grain (visible texture, film-like)
- Subtle grain (slight texture)
- Clean/no grain (digital smooth)
- Digital noise (high ISO artifacts)
- Grain size and pattern
- Intentional vs. technical grain

### Image Quality
Technical quality characteristics:
- Sharpness: Tack sharp, soft focus, out of focus
- Motion blur: None, slight, intentional motion
- Lens effects: Flare, chromatic aberration, vignetting
- Bokeh quality: Smooth, creamy, harsh, busy
- Compression artifacts: Visible/not visible
- Resolution quality: High detail, medium, low

### Era Aesthetic
Time period the image evokes:
- 1960s: High contrast B&W, mod aesthetic
- 1970s: Warm tones, soft focus
- 1980s: Vibrant colors, high key lighting
- 1990s: Grunge aesthetic, desaturated
- 2000s: Digital clean, glossy
- Modern: Contemporary digital aesthetics
- Vintage: Non-specific retro feel
- Timeless: No specific era indicators

### Camera Angle
Vertical and horizontal perspective:
- Eye level (neutral, natural)
- High angle (looking down)
- Low angle (looking up, heroic)
- Bird's eye view (directly overhead)
- Worm's eye view (from ground level)
- Dutch angle (tilted, dynamic)
- Over-the-shoulder
- Point of view (POV)

### Depth of Field
Focus characteristics:
- Shallow DOF: Subject sharp, background very blurred
- Deep DOF: Everything in focus
- Selective focus: Specific elements sharp
- Bokeh quality: Smooth, creamy, hexagonal, busy
- Tilt-shift: Miniature effect
- Focus falloff: Gradual or abrupt

### Post-Processing
Visible editing and effects:
- HDR (high dynamic range, tonemapped)
- Cross-processing (film simulation)
- Split-toning (different tones in highlights/shadows)
- Color grading presets (VSCO, cinema looks)
- Filters: Vintage, retro, modern
- Overlays: Textures, light leaks, dust
- Light leaks: Film-style color bleeding
- Contrast adjustments: Lifted blacks, crushed blacks
- Clarity/structure adjustments

## Output Format

Return ONLY valid JSON matching the structure above. No markdown code blocks, no explanations - just the JSON object.

## Important Reminders

1. **Focus ONLY on photographic and visual elements**
2. **NEVER mention clothing, accessories, fashion, or styling**
3. **Be EXTREMELY detailed and specific** about every visual element
4. **Use precise photographic terminology**
5. Even if the image is an illustration or artwork, describe all qualities as photographic elements that can be recreated in a photograph

Remember: This analysis is for recreating the visual style in new photographs, so precision and completeness are essential.
