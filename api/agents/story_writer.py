"""
Story Writer Agent

Expands story outline into full narrative text.
"""

import json
import aiofiles
from pathlib import Path
from typing import Dict, Any, List, Optional
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
                - prose_style_id: str (preset ID, e.g., 'humorous')
                - writer_config_id: str (optional, default: 'default')
                - perspective: str (default: 'third_person')
                - tense: str (default: 'past')

        Returns:
            Dict with 'written_story' key containing WrittenStory
        """
        # Validate input
        self.validate_input(input_data, ['outline', 'prose_style_id'])

        outline = input_data['outline']
        prose_style_id = input_data['prose_style_id']
        writer_config_id = input_data.get('writer_config_id', 'default')
        perspective = input_data.get('perspective', 'third_person')
        tense = input_data.get('tense', 'past')

        # Load configuration and presets
        config = await self._load_agent_config(writer_config_id)
        prose_preset = await self._load_preset('story_prose_styles', prose_style_id)

        # Build prompt using configuration
        prompt = await self._build_writing_prompt_from_config(
            config=config,
            outline=outline,
            prose_preset=prose_preset,
            perspective=perspective,
            tense=tense
        )

        # Get model from config (with fallback)
        model = config.get('model', 'gemini/gemini-2.0-flash-exp')

        # Call LLM
        try:
            response = await self.llm_router.acall(
                prompt=prompt,
                model=model,
                max_tokens=4000  # Longer for full story
            )

            # Parse response into structured format
            written_story = self._parse_story_response(
                response=response,
                outline=outline,
                prose_style=prose_style_id,
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

        # Build full story text with image placement markers
        # Insert image markers after each scene
        story_parts = []
        for i, scene_text in enumerate(scene_texts, 1):
            story_parts.append(scene_text)
            # Add image marker at the end of each scene
            story_parts.append(f"{{image_{i:02d}}}")

        full_story = "\n\n".join(story_parts)

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

    async def _load_agent_config(self, config_id: str) -> Dict[str, Any]:
        """Load agent configuration from file"""
        try:
            config_path = Path(f"/app/configs/agent_configs/story_writer/{config_id}.json")
            async with aiofiles.open(config_path, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"⚠️  Could not load writer config '{config_id}', using default: {e}")
            return {
                "prompt_template": {
                    "system_message": "You are a skilled story writer. Write engaging prose.",
                    "writing_approach": "Create clear, engaging narrative."
                }
            }

    async def _load_preset(self, category: str, preset_id: str) -> Dict[str, Any]:
        """Load preset from file"""
        try:
            preset_path = Path(f"/app/presets/{category}/{preset_id}.json")
            async with aiofiles.open(preset_path, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"⚠️  Could not load preset '{category}/{preset_id}': {e}")
            return {}

    async def _build_writing_prompt_from_config(
        self,
        config: Dict[str, Any],
        outline: Dict[str, Any],
        prose_preset: Dict[str, Any],
        perspective: str,
        tense: str
    ) -> str:
        """Build prompt dynamically from configuration and presets"""

        # Format outline
        outline_text = f"**Title**: {outline['title']}\n\n**Scenes**:\n"
        for scene in outline['outline']:
            outline_text += f"\n**Scene {scene['scene_number']}: {scene['title']}**\n"
            outline_text += f"- {scene['description']}\n"
            outline_text += f"- Action: {scene['action']}\n"
            outline_text += f"- Target length: ~{scene['estimated_words']} words\n"

        # Get configuration components
        prompt_template = config.get('prompt_template', {})
        system_message = prompt_template.get('system_message', '')
        writing_approach = prompt_template.get('writing_approach', '')
        writing_principles = prompt_template.get('writing_principles', [])
        writing_rules = prompt_template.get('writing_rules', [])
        scene_structure = prompt_template.get('scene_structure', {})
        techniques = prompt_template.get('techniques', {})
        avoid_list = prompt_template.get('avoid', [])

        # Get parameters from config
        params = config.get('parameters', {})
        word_count_range = params.get('word_count_range', [150, 300])

        # Build prompt
        prompt_parts = []

        # System message from config
        if system_message:
            prompt_parts.append(system_message)

        # Writing approach from config
        if writing_approach:
            prompt_parts.append(f"\n**Your Approach**: {writing_approach}")

        # Prose style from preset
        prose_name = prose_preset.get('suggested_name', 'Standard')
        prose_desc = prose_preset.get('description', '')
        prose_voice = prose_preset.get('voice', '')
        prose_techniques = prose_preset.get('techniques', [])
        prose_pacing = prose_preset.get('pacing', '')
        prose_avoid = prose_preset.get('avoid', [])

        prompt_parts.append(f"\n**Prose Style**: {prose_name}")
        if prose_desc:
            prompt_parts.append(f"- {prose_desc}")
        if prose_voice:
            prompt_parts.append(f"- Voice: {prose_voice}")
        if prose_pacing:
            prompt_parts.append(f"- Pacing: {prose_pacing}")

        # Prose techniques from preset
        if prose_techniques:
            prompt_parts.append(f"\n**Style Techniques**:")
            for tech in prose_techniques:
                prompt_parts.append(f"- {tech}")

        # Writing principles from config
        if writing_principles:
            prompt_parts.append(f"\n**Writing Principles**:")
            for principle in writing_principles:
                prompt_parts.append(f"- {principle}")

        # Writing rules from config (for configs like show_dont_tell)
        if writing_rules:
            prompt_parts.append(f"\n**Writing Rules** (CRITICAL):")
            for rule in writing_rules:
                prompt_parts.append(f"- {rule}")

        # Techniques from config
        if techniques:
            prompt_parts.append(f"\n**Techniques**:")
            for key, value in techniques.items():
                prompt_parts.append(f"- **{key.replace('_', ' ').title()}**: {value}")

        # Things to avoid
        all_avoid = []
        if prose_avoid:
            all_avoid.extend(prose_avoid)
        if avoid_list:
            all_avoid.extend(avoid_list)
        if all_avoid:
            prompt_parts.append(f"\n**Avoid**:")
            for item in all_avoid:
                prompt_parts.append(f"- {item}")

        # Scene structure from config
        if scene_structure:
            prompt_parts.append(f"\n**Scene Structure Guidance**:")
            for key, value in scene_structure.items():
                prompt_parts.append(f"- **{key.replace('_', ' ').title()}**: {value}")

        # Perspective and tense
        perspective_guidance = {
            'first_person': "Write from the protagonist's perspective using 'I'.",
            'third_person': "Write from an outside perspective using 'he/she/they'.",
            'second_person': "Write using 'you' to address the reader."
        }.get(perspective, "Use third person.")

        tense_guidance = {
            'past': "Use past tense throughout (walked, said, felt).",
            'present': "Use present tense for immediacy (walks, says, feels)."
        }.get(tense, "Use past tense.")

        prompt_parts.append(f"\n**Technical Requirements**:")
        prompt_parts.append(f"- Perspective: {perspective} - {perspective_guidance}")
        prompt_parts.append(f"- Tense: {tense} - {tense_guidance}")
        prompt_parts.append(f"- Scene length: {word_count_range[0]}-{word_count_range[1]} words each")

        # The outline
        prompt_parts.append(f"\n**Story Outline**:")
        prompt_parts.append(outline_text)

        # Instructions
        prompt_parts.append(f"\n**Instructions**:")
        prompt_parts.append(f"1. Write each scene to approximately the target word count")
        prompt_parts.append(f"2. Maintain consistent character voice throughout")
        prompt_parts.append(f"3. Create smooth transitions between scenes")
        prompt_parts.append(f"4. Stay true to the outline's plot points")
        prompt_parts.append(f"5. Use scene markers: '--- Scene X: [Title] ---'")

        prompt_parts.append(f"\nWrite the complete story now with all {len(outline['outline'])} scenes:")

        return "\n".join(prompt_parts)
