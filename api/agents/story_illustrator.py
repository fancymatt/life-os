"""
Story Illustrator Agent

Generates illustrations for story scenes using Gemini Flash 2.5.
"""

import asyncio
import json
import aiofiles
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from pathlib import Path
import time

from api.core.simple_agent import Agent, AgentConfig
from ai_tools.shared.router import LLMRouter, RouterConfig
from api.services.character_service import CharacterService
from ai_tools.character_appearance_analyzer.tool import CharacterAppearanceAnalyzer


class IllustrationResult(BaseModel):
    """Result of a single illustration"""
    scene_number: int
    image_url: str
    prompt_used: str
    generation_time: float


class IllustratedStory(BaseModel):
    """Story with illustrations"""
    title: str
    story: str
    illustrations: List[IllustrationResult]
    total_generation_time: float


class StoryIllustratorAgent(Agent):
    """
    Agent that creates illustrations for story scenes

    Uses existing modular image generator to create consistent character illustrations.
    """

    def __init__(self):
        super().__init__()
        config = RouterConfig()
        # Use Gemini Flash 2.5 for image generation
        model = config.get_model_for_tool("modular_image_generator")  # gemini-2.0-flash-exp
        self.router = LLMRouter(model=model)
        self.character_service = CharacterService()
        self.appearance_analyzer = CharacterAppearanceAnalyzer()

    def get_default_config(self) -> AgentConfig:
        return AgentConfig(
            agent_id="story_illustrator",
            name="Story Illustrator",
            description="Generates illustrations for story scenes",
            version="1.0.0",
            estimated_time_seconds=45.0,  # Depends on number of scenes
            estimated_cost=0.20  # $0.04 per image * 5 scenes
        )

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate illustrations for story

        Args:
            input_data: Must contain:
                - written_story: WrittenStory dict from writer
                - character_id: str (optional, for reference image)
                - character_appearance: str (visual description)
                - art_style: str (default: 'digital_art')
                - max_illustrations: int (default: 5)
                - outfit_id: str (optional, preset ID to override outfit)
                - hair_style_id: str (optional, preset ID to override hair style)
                - hair_color_id: str (optional, preset ID to override hair color)
                - illustrator_config_id: str (optional, default: 'default')

        Returns:
            Dict with 'illustrated_story' key containing IllustratedStory
        """
        # Validate input
        self.validate_input(input_data, ['written_story'])

        written_story = input_data['written_story']
        character_id = input_data.get('character_id')
        character_appearance = input_data.get('character_appearance', '')
        art_style = input_data.get('art_style', 'digital_art')
        max_illustrations = input_data.get('max_illustrations', 5)
        outfit_id = input_data.get('outfit_id')
        hair_style_id = input_data.get('hair_style_id')
        hair_color_id = input_data.get('hair_color_id')
        illustrator_config_id = input_data.get('illustrator_config_id', 'default')

        # Load illustrator configuration
        illustrator_config = await self._load_illustrator_config(illustrator_config_id)

        # Get model from config (with fallback)
        model = illustrator_config.get('model', 'gemini-2.5-flash-image')
        # Update router model for this execution
        self.router.model = model

        # Get character reference image and physical description
        character_image_path = None
        analyzed_appearance = None

        if character_id:
            try:
                # Get character data
                character_data = self.character_service.get_character(character_id)

                if character_data:
                    # Check if we already have a physical description
                    if character_data.get('physical_description'):
                        analyzed_appearance = character_data['physical_description']
                        print(f"✅ Using stored physical description")

                    # Get reference image
                    image_path = self.character_service.get_reference_image_path(character_id)
                    if image_path and Path(image_path).exists():
                        character_image_path = Path(image_path)
                        print(f"✅ Using character reference image: {character_image_path}")

                        # If no physical description exists, analyze and save it
                        if not analyzed_appearance:
                            print(f"🔍 Analyzing character appearance...")
                            appearance_spec = await self.appearance_analyzer.aanalyze(character_image_path)
                            analyzed_appearance = appearance_spec.overall_description
                            print(f"📝 Extracted appearance: {analyzed_appearance}")

                            # Save the physical description to the character entity
                            print(f"💾 Saving physical description to character entity...")
                            self.character_service.update_character(
                                character_id,
                                physical_description=analyzed_appearance
                            )
                            print(f"✅ Physical description saved")
            except Exception as e:
                print(f"⚠️  Could not process character: {e}")
                import traceback
                traceback.print_exc()
                # Continue with manual description

        # Build appearance overrides from presets
        appearance_overrides = await self._build_appearance_overrides(
            outfit_id=outfit_id,
            hair_style_id=hair_style_id,
            hair_color_id=hair_color_id
        )

        title = written_story['title']
        story_text = written_story['story']
        scenes = written_story['scenes']

        # Limit illustrations to max
        scenes_to_illustrate = scenes[:max_illustrations]

        # Generate illustrations (sequentially to avoid overloading)
        illustrations = []
        total_time = 0.0

        for scene in scenes_to_illustrate:
            try:
                start_time = time.time()

                # Build illustration prompt (use analyzed appearance if available)
                appearance_to_use = analyzed_appearance or character_appearance
                full_prompt = await self._build_illustration_prompt_from_config(
                    config=illustrator_config,
                    scene_prompt=scene['illustration_prompt'],
                    character_appearance=appearance_to_use,
                    art_style=art_style,
                    appearance_overrides=appearance_overrides
                )

                # Generate image using Gemini with character reference
                result = await self._generate_illustration(full_prompt, character_image_path)

                generation_time = time.time() - start_time

                illustrations.append(IllustrationResult(
                    scene_number=scene['scene_number'],
                    image_url=result['image_url'],
                    prompt_used=full_prompt,
                    generation_time=generation_time
                ))

                total_time += generation_time

            except Exception as e:
                print(f"Failed to generate illustration for scene {scene['scene_number']}: {e}")
                # Continue with other scenes even if one fails

        # Replace image placeholders with actual image URLs
        final_story_text = story_text
        for illustration in illustrations:
            placeholder = f"{{image_{illustration.scene_number:02d}}}"
            # Use markdown image syntax with alt text
            image_markdown = f"![Scene {illustration.scene_number}]({illustration.image_url})"
            final_story_text = final_story_text.replace(placeholder, image_markdown)

        illustrated_story = IllustratedStory(
            title=title,
            story=final_story_text,
            illustrations=illustrations,
            total_generation_time=total_time
        )

        return {
            "illustrated_story": illustrated_story.dict()
        }

    def _build_illustration_prompt(
        self,
        scene_prompt: str,
        character_appearance: str,
        art_style: str,
        appearance_overrides: Optional[str] = None
    ) -> str:
        """
        Build complete illustration prompt (legacy method, prefer _build_illustration_prompt_from_config)
        """

        # Check if user wants realistic/no style (match various formats)
        is_realistic = art_style and (
            'realistic' in art_style.lower() or
            'no style' in art_style.lower() or
            art_style.lower() == 'none'
        )

        # Combine all elements
        full_prompt = f"{scene_prompt}"

        if character_appearance:
            full_prompt += f". The character is {character_appearance}."

        # Add appearance overrides (outfit, hair, etc.)
        if appearance_overrides:
            full_prompt += f" {appearance_overrides}"

        # Add art style or realistic mode
        if not is_realistic:
            # Art style descriptions
            style_descriptions = {
                'watercolor': "watercolor painting style, soft colors, artistic brush strokes",
                'digital_art': "digital art, vibrant colors, detailed illustration",
                'sketch': "pencil sketch style, black and white, hand-drawn lines",
                'cartoon': "cartoon style, bold colors, simplified shapes, fun and playful",
                'oil_painting': "oil painting style, rich colors, textured brush strokes",
                'anime': "anime style, large expressive eyes, dynamic poses"
            }

            style_desc = style_descriptions.get(art_style, art_style)
            full_prompt += f". {style_desc}. High quality, professional illustration."
        else:
            # Realistic mode - no style modifications
            full_prompt += ". Photorealistic image, natural lighting, realistic photography style, high quality."

        return full_prompt

    async def _generate_illustration(self, prompt: str, character_image_path: Optional[Path] = None) -> Dict[str, Any]:
        """Generate a single illustration using Gemini Flash 2.5"""
        import uuid

        try:
            # Generate image with Gemini (with or without reference image)
            if character_image_path:
                # Use character reference image for consistent character appearance
                image_bytes = await self.router.agenerate_image(
                    prompt=prompt,
                    image_path=character_image_path,
                    model=self.router.model,
                    provider="gemini",
                    temperature=0.8
                )
            else:
                # Text-to-image generation without reference
                # Note: Gemini requires an image, so we'll still use DALL-E as fallback
                from openai import AsyncOpenAI
                import os
                import httpx

                client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = await client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1
                )

                # Download the image
                image_url = response.data[0].url
                async with httpx.AsyncClient() as http_client:
                    img_response = await http_client.get(image_url)
                    img_response.raise_for_status()
                    image_bytes = img_response.content

            # Save to output directory
            output_dir = Path("/app/output/stories")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename
            filename = f"story_ill_{uuid.uuid4().hex[:12]}.png"
            output_path = output_dir / filename

            # Use aiofiles for async file writing
            async with aiofiles.open(output_path, 'wb') as f:
                await f.write(image_bytes)

            # Return URL path
            return {
                "image_url": f"/output/stories/{filename}",
                "prompt": prompt
            }

        except Exception as e:
            print(f"Image generation failed: {e}")
            import traceback
            traceback.print_exc()
            # Return placeholder
            return {
                "image_url": "/output/placeholder.png",
                "prompt": prompt
            }

    async def _build_appearance_overrides(
        self,
        outfit_id: Optional[str] = None,
        hair_style_id: Optional[str] = None,
        hair_color_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Load presets and build appearance override description

        Returns a string describing the outfit, hair style, and hair color overrides
        """
        overrides = []

        # Load outfit preset
        if outfit_id:
            try:
                outfit_path = Path(f"/app/presets/outfits/{outfit_id}.json")
                if outfit_path.exists():
                    async with aiofiles.open(outfit_path, 'r') as f:
                        content = await f.read()
                        outfit_data = json.loads(content)

                    # Build outfit description from clothing items
                    outfit_items = []
                    for item in outfit_data.get('clothing_items', []):
                        item_desc = f"{item['color']} {item['item']}"
                        if item.get('details'):
                            item_desc += f" ({item['details']})"
                        outfit_items.append(item_desc)

                    if outfit_items:
                        overrides.append(f"Wearing: {', '.join(outfit_items)}")
                        print(f"✅ Applied outfit override: {outfit_data.get('suggested_name', outfit_id)}")
            except Exception as e:
                print(f"⚠️  Could not load outfit preset {outfit_id}: {e}")

        # Load hair style preset
        if hair_style_id:
            try:
                hair_style_path = Path(f"/app/presets/hair_styles/{hair_style_id}.json")
                if hair_style_path.exists():
                    async with aiofiles.open(hair_style_path, 'r') as f:
                        content = await f.read()
                        hair_style_data = json.loads(content)

                    # Build hair style description
                    style_desc = []
                    if hair_style_data.get('length'):
                        style_desc.append(hair_style_data['length'])
                    if hair_style_data.get('texture'):
                        style_desc.append(hair_style_data['texture'])
                    if hair_style_data.get('overall_style'):
                        style_desc.append(hair_style_data['overall_style'])

                    if style_desc:
                        overrides.append(f"Hair style: {' '.join(style_desc)}")
                        print(f"✅ Applied hair style override: {hair_style_data.get('suggested_name', hair_style_id)}")
            except Exception as e:
                print(f"⚠️  Could not load hair style preset {hair_style_id}: {e}")

        # Load hair color preset
        if hair_color_id:
            try:
                hair_color_path = Path(f"/app/presets/hair_colors/{hair_color_id}.json")
                if hair_color_path.exists():
                    async with aiofiles.open(hair_color_path, 'r') as f:
                        content = await f.read()
                        hair_color_data = json.loads(content)

                    # Build hair color description
                    color_desc = []
                    if hair_color_data.get('base_color'):
                        color_desc.append(hair_color_data['base_color'])
                    if hair_color_data.get('technique'):
                        color_desc.append(hair_color_data['technique'])
                    if hair_color_data.get('highlights'):
                        color_desc.append(f"with {hair_color_data['highlights']} highlights")

                    if color_desc:
                        overrides.append(f"Hair color: {' '.join(color_desc)}")
                        print(f"✅ Applied hair color override: {hair_color_data.get('suggested_name', hair_color_id)}")
            except Exception as e:
                print(f"⚠️  Could not load hair color preset {hair_color_id}: {e}")

        # Combine all overrides
        if overrides:
            return ". " + ". ".join(overrides) + "."
        return None

    async def _load_illustrator_config(self, config_id: str) -> Dict[str, Any]:
        """Load illustrator configuration from file"""
        try:
            config_path = Path(f"/app/configs/agent_configs/story_illustrator/{config_id}.json")
            async with aiofiles.open(config_path, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"⚠️  Could not load illustrator config '{config_id}', using default: {e}")
            return {
                "prompt_template": {
                    "system_message": "Create clear, engaging illustrations that capture key story moments.",
                    "illustration_approach": "Focus on character, action, and atmosphere."
                }
            }

    async def _build_illustration_prompt_from_config(
        self,
        config: Dict[str, Any],
        scene_prompt: str,
        character_appearance: str,
        art_style: str,
        appearance_overrides: Optional[str] = None
    ) -> str:
        """Build illustration prompt from configuration"""

        # Get configuration components
        prompt_template = config.get('prompt_template', {})
        system_message = prompt_template.get('system_message', '')
        visual_principles = prompt_template.get('visual_principles', [])
        prompt_structure = prompt_template.get('prompt_structure', {})
        lighting_guidance = prompt_template.get('lighting_guidance', '')
        shot_types = prompt_template.get('shot_types', [])
        style_notes = prompt_template.get('style_notes', [])

        # Check if user wants realistic/no style
        # Match variations: "realistic", "Realistic (No Style)", "no style", etc.
        is_realistic = art_style and (
            'realistic' in art_style.lower() or
            'no style' in art_style.lower() or
            art_style.lower() == 'none'
        )

        # Build prompt parts
        prompt_parts = []

        # Core scene description
        prompt_parts.append(scene_prompt)

        # Character appearance
        if character_appearance:
            prompt_parts.append(f"The character is {character_appearance}.")

        # Appearance overrides (outfit, hair, etc.)
        if appearance_overrides:
            prompt_parts.append(appearance_overrides)

        # Apply cinematography/composition guidance from config (independent of art style)
        # This includes framing, lighting, camera angles - works with both realistic and styled rendering

        # System context from config (for complex configs like cinematic)
        if system_message and system_message != "Create clear, engaging illustrations that capture key story moments.":
            # Only include if it's not the generic default
            prompt_parts.append(f"Composition Context: {system_message}")

        # Visual principles from config (composition, framing, mood)
        if visual_principles and len(visual_principles) > 0:
            # Add first few principles as inline guidance
            key_principles = visual_principles[:3]  # Top 3 most important
            for principle in key_principles:
                prompt_parts.append(principle)

        # Lighting guidance for specific configs
        if lighting_guidance:
            prompt_parts.append(lighting_guidance)

        # Style notes for specific configs (like storybook, graphic novel)
        # Note: These are about composition/mood, not rendering style
        if style_notes and len(style_notes) > 0:
            # Add one or two key style notes
            key_notes = style_notes[:2]
            for note in key_notes:
                prompt_parts.append(note)

        # Art style handling (realistic vs styled rendering)
        if not is_realistic:
            # Apply specific art style
            style_descriptions = {
                'watercolor': "watercolor painting style, soft colors, artistic brush strokes",
                'digital_art': "digital art, vibrant colors, detailed illustration",
                'sketch': "pencil sketch style, black and white, hand-drawn lines",
                'cartoon': "cartoon style, bold colors, simplified shapes, fun and playful",
                'oil_painting': "oil painting style, rich colors, textured brush strokes",
                'anime': "anime style, large expressive eyes, dynamic poses"
            }
            style_desc = style_descriptions.get(art_style, art_style)
            prompt_parts.append(f"{style_desc}. High quality, professional illustration.")
        else:
            # Realistic mode - no stylization
            prompt_parts.append("Photorealistic image, natural lighting, realistic photography style, high quality.")

        return " ".join(prompt_parts)
