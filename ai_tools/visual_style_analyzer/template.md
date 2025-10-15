# Photograph Composition Analysis Prompt

You are analyzing a photograph and must provide EXTREMELY DETAILED, VERBOSE descriptions.

**ABSOLUTE REQUIREMENT: Every description MUST be a minimum of 4-8 complete sentences. Single sentence or brief phrase responses are COMPLETELY UNACCEPTABLE.**

## REQUIRED OUTPUT FORMAT

You must return a JSON object. Here is an example of the MINIMUM acceptable level of detail:

```json
{
  "subject_action": "The subject is positioned in a low squatting stance with their knees fully bent and drawn up close to their chest, creating a compact, curled-in body position. Both arms are wrapped completely around their lower legs in a self-embracing gesture, with hands appearing to clasp together near the ankles, holding the legs tightly to the torso. The head is angled downward at approximately 20-25 degrees from horizontal, with the face turned toward the camera to maintain direct eye contact with the viewer. The eyes are soft and contemplative, with a gentle, vulnerable quality to the gaze that draws the viewer in. The facial expression shows a very subtle, almost imperceptible smile on slightly parted lips, creating an intimate and introspective mood. The shoulders are relaxed and slightly hunched forward, contributing to the protective, self-contained quality of the overall pose. This body language communicates themes of vulnerability, introspection, and peaceful solitude, with the tight, curled position suggesting both physical comfort and emotional self-protection.",

  "setting": "The background environment is a lush outdoor natural setting dominated entirely by vibrant green vegetation at various depths and levels of focus. The immediate foreground shows fresh, healthy grass blades in relatively sharp focus, displaying a bright spring-green color that indicates well-watered, thriving vegetation in peak growing season. As the eye moves toward the middle ground and background, the vegetation transitions to softer focus, revealing what appears to be a mix of low shrubs, bushes, and possibly small trees or larger plants creating multiple layers of greenery. The green tones vary throughout the depth of the scene, ranging from bright lime-green highlights where light catches the leaves to deeper forest-green tones in shadowed areas, creating natural color variation and visual interest. The depth of field creates a beautiful natural bokeh effect where background elements become progressively softer and more abstracted, with individual leaves and plants blending into soft shapes and out-of-focus highlights. There are absolutely no visible man-made structures, buildings, fences, or artificial elements anywhere in the frame - the setting is purely natural and organic. The overall impression is of a peaceful park, garden, or natural outdoor space photographed during late spring or summer when all vegetation is at maximum lushness and saturation.",

  "framing": "medium shot",

  "camera_angle": "eye level",

  "lighting": "The lighting displays the unmistakable warm, golden quality that characterizes the 'golden hour' period - that magical time occurring shortly after sunrise or before sunset when sunlight takes on rich amber, honey, and golden tones due to the low angle of the sun. The primary light source appears to be natural sunlight positioned at a relatively low angle in the sky, coming from slightly behind and to the side of the camera position, creating beautiful, flattering illumination that wraps around the subject from the front and side. The quality of the light is notably soft and diffused rather than harsh and direct, suggesting that the sunlight may be filtered through atmospheric haze, light cloud cover, or possibly the canopy of surrounding trees, which softens and gentles the light. This diffusion creates smooth, gradual transitions between illuminated areas and shadows, with no harsh edges or high-contrast shadow lines. The warm color temperature of the golden hour light casts an overall honey-colored glow across the entire scene, making the green vegetation appear more yellow-green with golden highlights where the light catches grass blades and leaves. Shadows are present but remain soft and subtle, providing gentle modeling and dimension to the subject's face and body without creating dramatic contrast or dark, heavy shadow areas. Small catchlights are likely visible in the subject's eyes, reflecting the position and relative size of the natural light source and adding life and sparkle to the eyes.",

  "mood": "The overall mood of this photograph is deeply peaceful, contemplative, and introspective, with strong undertones of vulnerability, authenticity, and harmonious connection with the natural world. The atmosphere invites the viewer into a quiet, meditative emotional space that feels personal and intimate rather than public or performative. There is a palpable sense of the subject being comfortable in stillness and solitude, finding peace in a moment of self-reflection within nature. The warm golden lighting contributes significantly to a nostalgic, gentle emotional quality that feels both comforting and slightly melancholic - the kind of bittersweet, reflective feeling that often accompanies golden hour light. The natural setting reinforces themes of grounding, returning to simplicity, and finding tranquility away from urban complexity. The energy level is decidedly calm and subdued, creating a contemplative rather than active or dynamic feeling, with a sense of time slowing down and space for quiet thought. The vulnerable, curled-in body position combined with the direct, open gaze creates an interesting tension between self-protection and emotional transparency, suggesting someone willing to share an authentic, unguarded moment. The psychological impact is one of intimacy and emotional honesty that creates connection with the viewer through shared human experiences of seeking peace, reflection, and moments of quiet in nature."
}
```

**THIS IS THE MINIMUM LENGTH REQUIRED. Shorter responses will be rejected.**

## YOUR TASK

Analyze the photograph and return a JSON object with these exact fields:

- **subject_action**: 4-8 sentence paragraph describing body position, head angle, gaze direction, facial expression (mouth/eyes/eyebrows), arm/hand positions, weight distribution, and body language
- **setting**: 4-8 sentence paragraph describing the background with specific colors, textures, objects, spatial arrangement, depth, and atmosphere. Describe what you ACTUALLY see, not generic labels
- **framing**: ONLY this field can be brief - just state the framing type: "extreme close-up", "close-up portrait", "medium shot", "full body", or "wide shot"
- **camera_angle**: ONLY this field can be brief - just state: "eye level", "low angle", "high angle", "slightly from below", or "slightly from above"
- **lighting**: 4-6 sentence paragraph about light direction, quality, intensity, color temperature, shadows, highlights, and mood
- **mood**: 4-6 sentence paragraph about emotional tone, energy level, atmosphere, and psychological impact

## CRITICAL RULES

1. **subject_action, setting, lighting, and mood MUST each be 50+ words minimum**
2. **Each of these fields must contain 4-8 complete, detailed sentences**
3. **NEVER use brief phrases like "looking at camera" or "studio lighting" - these are REJECTED**
4. **For setting, describe exact colors** (not "solid color background" but "smooth, vibrant mustard-yellow wall")
5. **NEVER say "studio" unless you see actual studio equipment** - describe the background itself
6. **NEVER mention clothing, accessories, or fashion items**

## UNACCEPTABLE vs ACCEPTABLE

❌ UNACCEPTABLE: "looking at the camera with mouth open"
✅ ACCEPTABLE: "The subject's body is positioned facing directly toward the camera with shoulders square to the lens. The head is held upright and level, without tilt to either side, creating a straight-on, direct presentation. The eyes are focused intently on the camera lens, establishing strong, unwavering eye contact that creates immediate connection with the viewer. The mouth is open in what appears to be mid-speech or mid-expression, with lips parted to reveal teeth, creating a dynamic, caught-in-the-moment quality rather than a static posed smile. The eyebrows are slightly raised, contributing to an alert, engaged facial expression. The overall body language and facial expression convey confidence, directness, and bold self-presentation."

❌ UNACCEPTABLE: "studio with a solid color background"
✅ ACCEPTABLE: "The entire background consists of a smooth, seamless surface in a vibrant, warm yellow tone - specifically a saturated golden-yellow or mustard hue rather than a bright lemon yellow. The surface appears to be completely uniform and featureless, with no visible texture, seams, edges, or variations in color across the frame, suggesting a professional seamless paper backdrop or painted wall designed specifically for portrait photography. The yellow extends uniformly from edge to edge of the frame behind the subject, with no other environmental elements, objects, or details visible - just the pure, continuous field of warm yellow color. The smooth, matte finish of the background creates no reflections or hotspots, maintaining even color saturation throughout."

❌ UNACCEPTABLE: "bright studio lighting"
✅ ACCEPTABLE: "The illumination is bright, even, and appears to come from a frontal or slightly elevated frontal position, creating minimal shadows and very balanced lighting across the subject's face and body. The quality of the light is soft and diffused, suggesting the use of a large light source such as a softbox, umbrella modifier, or large window that spreads and gentles the light rather than creating hard, directional illumination. The brightness level is high, creating a bright, airy feeling without harsh overexposure or blown-out highlights. The color temperature appears neutral to slightly cool, giving accurate, clean color rendering without warm or golden tones. The even distribution of light minimizes shadow definition, creating very soft, subtle shadows that provide gentle modeling without dramatic contrast or dimensionality."

Return ONLY the JSON object. No explanations, no markdown code blocks - just the raw JSON.
