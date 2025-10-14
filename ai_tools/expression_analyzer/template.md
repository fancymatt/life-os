# Facial Expression Analysis

Analyze the **facial expression** in this image including emotion, intensity, and specific facial features.

## Output Format

Return a JSON object with these fields:

```json
{
  "primary_emotion": "Main emotional expression (happy, sad, neutral, contemplative, confident, serious, playful, etc.)",

  "intensity": "How strong is the expression? (subtle/minimal, moderate, strong/intense)",

  "mouth": "Mouth position and shape (closed smile, open smile, neutral, slight upturn, pursed, relaxed, etc.)",

  "eyes": "Eye expression and appearance (smiling eyes/crinkled, soft, intense gaze, relaxed, wide, etc.)",

  "eyebrows": "Eyebrow position and shape (relaxed, slightly raised, furrowed, arched, neutral, etc.)",

  "gaze_direction": "Where is the subject looking? (directly at camera, off-camera left/right/up/down, downward, away, etc.)",

  "overall_mood": "Overall emotional impression and atmosphere (warm and approachable, mysterious and aloof, confident and assured, pensive, etc.)"
}
```

## Guidelines

- **Primary Emotion**: What is the main emotion being expressed?
- **Intensity**: How strongly is it expressed?
- **Mouth**: Describe the mouth's contribution to the expression
- **Eyes**: Eyes are crucial - describe their appearance and what they convey
- **Eyebrows**: Note eyebrow position (raised, neutral, furrowed, etc.)
- **Gaze Direction**: Where are they looking?
- **Overall Mood**: Sum up the complete emotional impression

## Important

- Return ONLY valid JSON, no markdown formatting
- All string fields must contain meaningful descriptions (no empty strings)
- Be specific but concise
- Focus on expression, not physical features or attractiveness
