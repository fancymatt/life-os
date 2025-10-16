"""
Story Writer Agent

Expands story outline into full narrative text.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field

from api.core.simple_agent import Agent, AgentConfig
from ai_tools.shared.router import LLMRouter


class WrittenScene(BaseModel):
    """A written scene"""
    scene_number: int
    text: str
    illustration_prompt: str


class WrittenStory(BaseModel):
    """Complete written story"""
    title: str
    story: str = Field(description="Full story text with all scenes")
    scenes: List[WrittenScene]
    word_count: int
    metadata: Dict[str, Any] = {}


class StoryWriterAgent(Agent):
    """
    Agent that writes full stories from outlines

    Takes outline and prose style, generates complete narrative.
    """

    def __init__(self):
        super().__init__()
        self.llm_router = LLMRouter()

    def get_default_config(self) -> AgentConfig:
        return AgentConfig(
            agent_id="story_writer",
            name="Story Writer",
            description="Expands story outlines into full narrative text",
            version="1.0.0",
            estimated_time_seconds=30.0,
            estimated_cost=0.05
        )

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write full story from outline

        Args:
            input_data: Must contain:
                - outline: StoryOutline dict from planner
                - prose_style: str (default: 'descriptive')
                - perspective: str (default: 'third_person')
                - tense: str (default: 'past')

        Returns:
            Dict with 'written_story' key containing WrittenStory
        """
        # Validate input
        self.validate_input(input_data, ['outline'])

        outline = input_data['outline']
        prose_style = input_data.get('prose_style', 'descriptive')
        perspective = input_data.get('perspective', 'third_person')
        tense = input_data.get('tense', 'past')

        # Build prompt
        prompt = self._build_writing_prompt(
            outline=outline,
            prose_style=prose_style,
            perspective=perspective,
            tense=tense
        )

        # Call LLM
        try:
            response = await self.llm_router.acall(
                prompt=prompt,
                model="gemini/gemini-2.0-flash-exp",
                max_tokens=4000  # Longer for full story
            )

            # Parse response into structured format
            written_story = self._parse_story_response(
                response=response,
                outline=outline,
                prose_style=prose_style,
                perspective=perspective,
                tense=tense
            )

            return {
                "written_story": written_story.dict()
            }

        except Exception as e:
            raise RuntimeError(f"Story writing failed: {e}")

    def _build_writing_prompt(
        self,
        outline: Dict[str, Any],
        prose_style: str,
        perspective: str,
        tense: str
    ) -> str:
        """Build prompt for story writing"""

        # Format outline
        outline_text = f"**Title**: {outline['title']}\n\n**Scenes**:\n"
        for scene in outline['outline']:
            outline_text += f"\n**Scene {scene['scene_number']}: {scene['title']}**\n"
            outline_text += f"- {scene['description']}\n"
            outline_text += f"- Action: {scene['action']}\n"
            outline_text += f"- Target length: ~{scene['estimated_words']} words\n"

        # Prose style guidance
        style_guidance = {
            'descriptive': "Use rich, vivid descriptions. Paint scenes with sensory details. Show, don't tell.",
            'concise': "Use clear, direct language. Focus on action and dialogue. Keep descriptions brief.",
            'poetic': "Use metaphors and lyrical language. Create rhythm in the prose. Emphasize emotion.",
            'humorous': "Include wit and light-heartedness. Use playful language. Make the reader smile.",
            'simple': "Use simple words and short sentences. Perfect for young readers. Clear and easy to follow."
        }.get(prose_style, "Use engaging, appropriate language.")

        # Perspective guidance
        perspective_guidance = {
            'first_person': "Write from the protagonist's perspective using 'I'. Show their internal thoughts.",
            'third_person': "Write from an outside perspective using 'he/she/they'. Balance internal and external views.",
            'second_person': "Write using 'you' to directly address the reader (rare, use carefully)."
        }.get(perspective, "Use third person perspective.")

        # Tense guidance
        tense_guidance = {
            'past': "Use past tense throughout (walked, said, felt).",
            'present': "Use present tense for immediacy (walks, says, feels).",
            'past_perfect': "Use past perfect for complex timelines (had walked, had said)."
        }.get(tense, "Use past tense.")

        prompt = f"""Write a complete story based on this outline.

{outline_text}

**Writing Style**:
- **Prose Style**: {prose_style} - {style_guidance}
- **Perspective**: {perspective} - {perspective_guidance}
- **Tense**: {tense} - {tense_guidance}

**Instructions**:
1. Expand each scene to approximately the target word count
2. Maintain consistent character voice and personality throughout
3. Create smooth transitions between scenes
4. Use vivid descriptions and engaging dialogue
5. Build emotional resonance
6. Ensure the story flows naturally from beginning to end

**Scene Markers**:
Use clear scene breaks like this:
```
--- Scene 1: [Title] ---
[Scene content]

--- Scene 2: [Title] ---
[Scene content]
```

**Important**:
- Stay true to the outline's plot points
- Maintain the character's personality
- Create a cohesive, engaging narrative
- Match the target word counts approximately

Write the complete story now with all {len(outline['outline'])} scenes:"""

        return prompt

    def _parse_story_response(
        self,
        response: str,
        outline: Dict[str, Any],
        prose_style: str,
        perspective: str,
        tense: str
    ) -> WrittenStory:
        """Parse LLM response into structured story"""

        # Split story into scenes using markers
        scenes = []
        scene_texts = []

        # Try to split by scene markers
        parts = response.split('--- Scene ')
        if len(parts) > 1:
            for i, part in enumerate(parts[1:], 1):  # Skip first empty part
                # Extract scene text (after the scene header line)
                lines = part.split('\n', 1)
                if len(lines) > 1:
                    scene_text = lines[1].strip()
                else:
                    scene_text = part.strip()

                # Get illustration prompt from outline
                outline_scene = next(
                    (s for s in outline['outline'] if s['scene_number'] == i),
                    None
                )
                illustration_prompt = outline_scene['illustration_prompt'] if outline_scene else ""

                scenes.append(WrittenScene(
                    scene_number=i,
                    text=scene_text,
                    illustration_prompt=illustration_prompt
                ))
                scene_texts.append(scene_text)
        else:
            # If no scene markers, treat as single narrative
            # Try to split by expected number of scenes
            target_scenes = len(outline['outline'])
            # For now, just create one scene
            scenes.append(WrittenScene(
                scene_number=1,
                text=response.strip(),
                illustration_prompt=outline['outline'][0]['illustration_prompt'] if outline['outline'] else ""
            ))
            scene_texts.append(response.strip())

        # Calculate word count
        word_count = len(response.split())

        # Build full story text
        full_story = "\n\n".join(scene_texts)

        return WrittenStory(
            title=outline['title'],
            story=full_story,
            scenes=scenes,
            word_count=word_count,
            metadata={
                "prose_style": prose_style,
                "perspective": perspective,
                "tense": tense
            }
        )
