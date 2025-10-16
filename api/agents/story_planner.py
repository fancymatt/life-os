"""
Story Planner Agent

Generates story outlines with scenes and illustration prompts.
"""

import json
import aiofiles
from pathlib import Path
from typing import Dict, Any, Optional
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
                - story_type: str ('normal' or 'transformation')
                - theme_id: str (preset ID, e.g., 'modern_magic')
                - audience_id: str (preset ID, e.g., 'adult')
                - target_scenes: int (default: 5)
                - transformation: Optional dict with 'type' and 'target' (for transformation stories)
                - planner_config_id: str (optional, default: 'default')

        Returns:
            Dict with 'outline' key containing StoryOutline
        """
        # Validate input
        self.validate_input(input_data, ['character', 'theme_id', 'audience_id'])

        character = input_data['character']
        story_type = input_data.get('story_type', 'normal')
        theme_id = input_data['theme_id']
        audience_id = input_data['audience_id']
        target_scenes = input_data.get('target_scenes', 5)
        transformation = input_data.get('transformation')
        planner_config_id = input_data.get('planner_config_id', 'default')

        # Load configuration and presets
        config = await self._load_agent_config(planner_config_id)
        theme_preset = await self._load_preset('story_themes', theme_id)
        audience_preset = await self._load_preset('story_audiences', audience_id)

        # Build prompt using configuration
        prompt = await self._build_planning_prompt_from_config(
            config=config,
            character=character,
            story_type=story_type,
            theme_preset=theme_preset,
            audience_preset=audience_preset,
            target_scenes=target_scenes,
            transformation=transformation
        )

        # Get model from config (with fallback)
        model = config.get('model', 'gemini/gemini-2.0-flash-exp')

        # Call LLM with structured output
        try:
            outline = await self.llm_router.acall_structured(
                prompt=prompt,
                response_model=StoryOutline,
                model=model
            )

            return {
                "outline": outline.dict()
            }

        except Exception as e:
            raise RuntimeError(f"Story planning failed: {e}")

    def _build_planning_prompt(
        self,
        character: Dict[str, Any],
        story_type: str,
        theme: str,
        target_scenes: int,
        age_group: str,
        transformation: Dict[str, Any] = None
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

        # Build story-type specific prompt
        if story_type == 'transformation' and transformation:
            return self._build_transformation_prompt(
                character=character,
                transformation=transformation,
                theme=theme,
                target_scenes=target_scenes,
                age_group=age_group,
                age_guidance=age_guidance,
                char_desc=char_desc
            )
        else:
            # Normal story prompt
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

    def _build_transformation_prompt(
        self,
        character: Dict[str, Any],
        transformation: Dict[str, Any],
        theme: str,
        target_scenes: int,
        age_group: str,
        age_guidance: str,
        char_desc: str
    ) -> str:
        """Build prompt specifically for transformation stories"""

        transformation_type = transformation['type']
        transformation_target = transformation['target']

        if transformation_type == 'creature':
            transformation_desc = f"transforms into a {transformation_target}"
            transformation_detail = f"The transformation should be gradual and detailed, showing {character['name']} slowly becoming a {transformation_target}. Each scene should show progressive physical changes."
        else:  # alteration
            transformation_desc = f"undergoes physical alterations: {transformation_target}"
            transformation_detail = f"The transformation should be gradual and detailed, showing {character['name']} slowly developing these alterations: {transformation_target}. Each scene should show progressive physical changes."

        # Add theme context
        theme_context = ""
        if theme == "modern_magic":
            theme_context = "Set in the modern world where magic exists alongside everyday life. The story should blend contemporary settings (cities, technology, modern jobs) with magical elements. The transformation happens due to magical causes."

        prompt = f"""Create a TRANSFORMATION story outline where the character {transformation_desc}.

{char_desc}

**Transformation Details**:
- **Type**: {transformation_type}
- **Target**: {transformation_target}
- {transformation_detail}

**Requirements**:
- **Target Audience**: {age_group.replace('_', ' ').title()}
- **Number of Scenes**: {target_scenes}
- **Theme**: {theme.replace('_', ' ').title()}
{f"- **Theme Context**: {theme_context}" if theme_context else ""}
- **Style**: {age_guidance}

For each scene, provide:
1. **Scene Title**: Concise title for the scene
2. **Description**: What happens in this scene, INCLUDING DETAILED TRANSFORMATION PROGRESS (3-4 sentences)
3. **Action**: The key action or conflict, AND what transformation changes occur
4. **Illustration Prompt**: Detailed visual description showing the CURRENT STATE of transformation (e.g., "Scene 1: Normal appearance", "Scene 3: Hands becoming paws, fur appearing on arms", "Scene 5: Fully transformed into {transformation_target}")
5. **Estimated Words**: Approximate length of this scene when written (150-300 words to accommodate transformation details)

**TRANSFORMATION STORY STRUCTURE** (CRITICAL):
- **Scene 1**: {character['name']} is completely normal, no transformation yet. Show their original appearance clearly.
- **Scene 2**: FIRST SIGNS of transformation begin (small changes like tingling, slight physical changes)
- **Scenes 3-{target_scenes-2}**: PROGRESSIVE TRANSFORMATION - each scene shows MORE transformation (25%, 50%, 75% transformed). Be SPECIFIC about what body parts are changing.
- **Scene {target_scenes-1}**: NEARLY COMPLETE transformation (90-95% transformed)
- **Scene {target_scenes}**: FULLY TRANSFORMED - {character['name']} is now completely {transformation_target if transformation_type == 'creature' else 'altered with ' + transformation_target}

**CRITICAL REQUIREMENTS FOR ILLUSTRATION PROMPTS**:
- Scene 1: Must show {character['name']} in their NORMAL, ORIGINAL appearance
- Each subsequent scene: Must EXPLICITLY describe the PROGRESSIVE transformation state
- Include specific body part changes in EACH illustration prompt (ears, hands/paws, face, tail, fur/scales, etc.)
- Final scene: Must show the COMPLETE transformation

**Example Transformation Progression** (for reference):
- Scene 1: "{character['name']}, looking normal..."
- Scene 2: "{character['name']} with slightly pointed ears and tingling fingers..."
- Scene 3: "{character['name']} with fully pointed ears, hands becoming paws, small tail emerging..."
- Scene 4: "{character['name']} mostly transformed, walking on all fours, fully-formed tail, face changing..."
- Scene 5: "{character['name']} completely as a {transformation_target}, with all animal features..."

Create a compelling transformation story outline with VIVID, SPECIFIC transformation details in every scene."""

        return prompt

    async def _load_agent_config(self, config_id: str) -> Dict[str, Any]:
        """Load agent configuration from file"""
        try:
            config_path = Path(f"/app/configs/agent_configs/story_planner/{config_id}.json")
            async with aiofiles.open(config_path, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"⚠️  Could not load planner config '{config_id}', using default: {e}")
            # Return minimal default if file not found
            return {
                "prompt_template": {
                    "system_message": "You are an expert story planner. Create engaging story outlines.",
                    "planning_approach": "Create a well-structured story with clear beginning, middle, and end."
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

    async def _build_planning_prompt_from_config(
        self,
        config: Dict[str, Any],
        character: Dict[str, Any],
        story_type: str,
        theme_preset: Dict[str, Any],
        audience_preset: Dict[str, Any],
        target_scenes: int,
        transformation: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt dynamically from configuration and presets"""

        # Format character description
        char_desc = f"**Character**: {character['name']}"
        if character.get('appearance'):
            char_desc += f"\n- Appearance: {character['appearance']}"
        if character.get('personality'):
            char_desc += f"\n- Personality: {character['personality']}"

        # Get configuration components
        prompt_template = config.get('prompt_template', {})
        system_message = prompt_template.get('system_message', '')
        planning_approach = prompt_template.get('planning_approach', '')
        scene_requirements = prompt_template.get('scene_requirements', [])
        structure_guidance = prompt_template.get('structure_guidance', {})

        # Build prompt
        prompt_parts = []

        # System message from config
        if system_message:
            prompt_parts.append(system_message)

        # Planning approach from config
        if planning_approach:
            prompt_parts.append(f"\n**Your Approach**: {planning_approach}")

        # Theme information from preset
        theme_name = theme_preset.get('suggested_name', 'Story')
        theme_desc = theme_preset.get('description', '')
        theme_guidance = theme_preset.get('setting_guidance', '')

        prompt_parts.append(f"\n**Story Theme**: {theme_name}")
        if theme_desc:
            prompt_parts.append(f"- Description: {theme_desc}")
        if theme_guidance:
            prompt_parts.append(f"- Setting Guidance: {theme_guidance}")

        # Audience information from preset
        audience_name = audience_preset.get('suggested_name', 'General')
        language_guidance = audience_preset.get('language_guidance', '')
        content_guidelines = audience_preset.get('content_guidelines', '')
        story_structure = audience_preset.get('story_structure', '')

        prompt_parts.append(f"\n**Target Audience**: {audience_name}")
        if language_guidance:
            prompt_parts.append(f"- Language: {language_guidance}")
        if content_guidelines:
            prompt_parts.append(f"- Content: {content_guidelines}")
        if story_structure:
            prompt_parts.append(f"- Structure: {story_structure}")

        # Character
        prompt_parts.append(f"\n{char_desc}")

        # Requirements
        prompt_parts.append(f"\n**Requirements**:")
        prompt_parts.append(f"- **Number of Scenes**: {target_scenes}")

        # Scene requirements from config
        if scene_requirements:
            prompt_parts.append(f"\n**Scene Planning Considerations**:")
            for req in scene_requirements:
                prompt_parts.append(f"- {req}")

        # Structure guidance from config
        if structure_guidance:
            prompt_parts.append(f"\n**Story Structure Guidance**:")
            for key, value in structure_guidance.items():
                prompt_parts.append(f"- **{key.replace('_', ' ').title()}**: {value}")

        # Transformation specific
        if story_type == 'transformation' and transformation:
            transformation_type = transformation['type']
            transformation_target = transformation['target']

            if transformation_type == 'creature':
                transformation_desc = f"transforms into a {transformation_target}"
            else:
                transformation_desc = f"undergoes physical alterations: {transformation_target}"

            prompt_parts.append(f"\n**TRANSFORMATION STORY**:")
            prompt_parts.append(f"- Character {transformation_desc}")
            prompt_parts.append(f"- Show PROGRESSIVE transformation across scenes")
            prompt_parts.append(f"- Scene 1: Normal appearance")
            prompt_parts.append(f"- Middle scenes: Gradual physical changes (25%, 50%, 75%)")
            prompt_parts.append(f"- Final scene: Fully transformed")
            prompt_parts.append(f"- Include SPECIFIC body part changes in each scene's illustration prompt")

        # Output format
        prompt_parts.append(f"\n**For Each Scene, Provide**:")
        prompt_parts.append(f"1. **Scene Title**: Concise title")
        prompt_parts.append(f"2. **Description**: What happens (2-4 sentences)")
        prompt_parts.append(f"3. **Action**: Key action or conflict")
        prompt_parts.append(f"4. **Illustration Prompt**: Detailed visual description for image generation")
        prompt_parts.append(f"5. **Estimated Words**: Scene length (150-300 words)")

        prompt_parts.append(f"\nCreate a compelling story outline now.")

        return "\n".join(prompt_parts)
