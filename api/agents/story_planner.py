"""
Story Planner Agent

Generates story outlines with scenes and illustration prompts.
"""

import json
from typing import Dict, Any
from pydantic import BaseModel, Field

from api.core.simple_agent import Agent, AgentConfig
from ai_tools.shared.router import LLMRouter


class CharacterInput(BaseModel):
    """Character description"""
    name: str
    appearance: str = ""
    personality: str = ""


class StoryScene(BaseModel):
    """A single scene in the story"""
    scene_number: int
    title: str
    description: str = Field(description="What happens in this scene")
    action: str = Field(description="Key action or conflict")
    illustration_prompt: str = Field(description="Prompt for image generation")
    estimated_words: int = 150


class StoryOutline(BaseModel):
    """Complete story outline"""
    title: str
    outline: list[StoryScene]
    total_estimated_words: int


class StoryPlannerAgent(Agent):
    """
    Agent that creates story outlines

    Takes character and theme, generates structured outline with scenes.
    """

    def __init__(self):
        super().__init__()
        self.llm_router = LLMRouter()

    def get_default_config(self) -> AgentConfig:
        return AgentConfig(
            agent_id="story_planner",
            name="Story Planner",
            description="Creates story outlines with scenes and illustration prompts",
            version="1.0.0",
            estimated_time_seconds=15.0,
            estimated_cost=0.02
        )

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate story outline

        Args:
            input_data: Must contain:
                - character: Dict with name, appearance, personality
                - theme: str (e.g., 'adventure', 'mystery')
                - target_scenes: int (default: 5)
                - age_group: str (default: 'children')

        Returns:
            Dict with 'outline' key containing StoryOutline
        """
        # Validate input
        self.validate_input(input_data, ['character', 'theme'])

        character = input_data['character']
        theme = input_data['theme']
        target_scenes = input_data.get('target_scenes', 5)
        age_group = input_data.get('age_group', 'children')

        # Build prompt
        prompt = self._build_planning_prompt(
            character=character,
            theme=theme,
            target_scenes=target_scenes,
            age_group=age_group
        )

        # Call LLM with structured output
        try:
            outline = await self.llm_router.call_structured(
                prompt=prompt,
                response_model=StoryOutline,
                model="gemini-2.0-flash-exp"
            )

            return {
                "outline": outline.dict()
            }

        except Exception as e:
            raise RuntimeError(f"Story planning failed: {e}")

    def _build_planning_prompt(
        self,
        character: Dict[str, Any],
        theme: str,
        target_scenes: int,
        age_group: str
    ) -> str:
        """Build prompt for story planning"""

        # Format character description
        char_desc = f"**Character**: {character['name']}"
        if character.get('appearance'):
            char_desc += f"\n- Appearance: {character['appearance']}"
        if character.get('personality'):
            char_desc += f"\n- Personality: {character['personality']}"

        # Age-appropriate guidance
        age_guidance = {
            'children': "Simple language, clear moral lesson, happy ending. Focus on discovery and friendship.",
            'young_adult': "More complex themes, character growth, can include challenges. Age-appropriate conflicts.",
            'adult': "Nuanced themes, realistic conflicts, sophisticated language."
        }.get(age_group, "Age-appropriate language and themes.")

        prompt = f"""Create a story outline for a {theme} story.

{char_desc}

**Requirements**:
- **Target Audience**: {age_group.replace('_', ' ').title()}
- **Number of Scenes**: {target_scenes}
- **Theme**: {theme}
- **Style**: {age_guidance}

For each scene, provide:
1. **Scene Title**: Concise title for the scene
2. **Description**: What happens in this scene (2-3 sentences)
3. **Action**: The key action or conflict in this scene
4. **Illustration Prompt**: Detailed visual description for image generation (focus on {character['name']}'s appearance and the scene setting)
5. **Estimated Words**: Approximate length of this scene when written (100-300 words)

**Story Structure**:
- **Beginning** (Scene 1): Introduce {character['name']} and their world
- **Rising Action** (Scenes 2-{target_scenes-2}): Build conflict and adventure
- **Climax** (Scene {target_scenes-1}): Peak of action/challenge
- **Resolution** (Scene {target_scenes}): Satisfying conclusion

**Important**:
- Ensure scenes flow logically
- Maintain character consistency throughout
- Create vivid illustration prompts that capture key moments
- Each illustration prompt should mention {character['name']} and describe their appearance: {character.get('appearance', 'as described')}

Create a compelling {theme} story outline now."""

        return prompt
