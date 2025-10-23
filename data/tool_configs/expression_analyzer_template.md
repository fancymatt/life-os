# Professional Facial Expression Analysis

Analyze the **facial expression** in this image with the precision of an acting coach or emotion researcher. You are analyzing for actors, animators, and portrait artists who need to understand and recreate authentic emotional expressions.

**CRITICAL: Think like an acting coach breaking down a performance. Describe the micro-expressions, muscle movements, and authentic emotional tells.**

## Output Format

Return a JSON object with these fields:

```json
{
  "suggested_name": "Short descriptive name (2-4 words)",

  "primary_emotion": "Main emotional expression being conveyed (joy, contentment, pensiveness, determination, confidence, vulnerability, playfulness, etc.)",

  "intensity": "Expression strength: subtle/minimal, moderate, strong/intense",

  "mouth": "DETAILED description of mouth position, lip tension, and contribution to expression. Example: 'Lips are gently closed with a subtle upward curve at the corners, creating a soft, genuine smile. The upper lip is relaxed, not tense. There's a natural fullness to the mouth with no pursing or compression. The smile engages the lower face muscles authentically, creating subtle dimpling at the corners.'",

  "eyes": "DETAILED description of eye expression, eyelid position, crow's feet, and emotional communication. Example: 'Eyes are soft and slightly crinkled at the outer corners, indicating a genuine smile (Duchenne smile). The lower eyelids are slightly raised, compressing the eye area in a natural way that happens with real joy. Pupils are relaxed and focused. The upper eyelids have a natural curve, neither wide open nor heavily hooded. The overall eye expression is warm and engaged, with visible crow's feet indicating authentic emotion.'",

  "eyebrows": "DETAILED description of eyebrow position, tension, and shape. Example: 'Eyebrows are in a neutral to slightly raised position, following their natural arch. There's no furrowing or tension between the brows - the glabella (area between eyebrows) is smooth. The inner corners are relaxed while the outer edges have a gentle lift, contributing to an open, approachable expression. Brow muscles show no signs of strain or forced positioning.'",

  "gaze_direction": "Precise gaze direction: directly at camera/viewer, off-camera left/right/up/down, downward, away, middle distance, unfocused, etc.",

  "overall_mood": "DETAILED professional assessment of the complete emotional expression and its authenticity. Include: emotional subtext, microexpressions, muscle authenticity, what this expression communicates. Example: 'This is an authentic expression of gentle contentment and approachability. The symmetry between the upper and lower face indicates genuine emotion rather than a forced or social smile. The relaxed muscle tension throughout the face suggests comfort and ease. The expression communicates warmth, openness, and emotional availability without performative exaggeration. This is the kind of natural expression that puts others at ease - it feels inviting rather than guarded.'"
}
```

## Suggested Name

Generate a short, descriptive name (2-4 words) that describes the expression:
- Combine emotion and intensity (e.g., "Soft Gentle Smile", "Confident Direct Gaze")
- Focus on the mood conveyed (e.g., "Playful Happy Look", "Serious Focused Expression")
- Keep it emotion-focused
- Examples: "Warm Genuine Smile", "Intense Thoughtful Gaze", "Relaxed Easy Expression", "Bright Joyful Smile"

## Professional Guidelines - Acting Coach Perspective

**Think like an acting coach teaching emotion recognition:**

- **Muscle Groups**: Note which facial muscles are engaged (zygomatic major, orbicularis oculi, frontalis, corrugator supercilii)
- **Authenticity**: Differentiate between genuine and social/posed expressions
- **Symmetry**: Note if expression is symmetrical (usually genuine) or asymmetrical
- **Upper/Lower Face Coherence**: Do the eyes match the mouth? Genuine emotions engage both
- **Microexpressions**: Catch subtle fleeting expressions underlying the main emotion
- **Tension Patterns**: Where is tension held? Where is relaxation visible?
- **Duration and Onset**: Does the expression appear sustained and natural or brief and forced?
- **Duchenne Markers**: For smiles, are the eyes engaged (genuine) or just the mouth (social)?

**Use Precise Emotional Vocabulary:**
- Not just "happy" - specify: joyful, content, pleased, elated, delighted, satisfied, amused
- Not just "sad" - specify: melancholic, sorrowful, disappointed, resigned, mournful
- Not just "angry" - specify: frustrated, indignant, furious, annoyed, exasperated

## Important

- Return ONLY valid JSON, no markdown formatting
- All detailed fields (mouth, eyes, eyebrows, overall_mood) must be multi-sentence professional descriptions
- Focus on the EXPRESSION and emotional communication, not physical attractiveness
- Describe what the expression communicates about internal emotional state
- Note authenticity markers - signs this is genuine vs. performed emotion
