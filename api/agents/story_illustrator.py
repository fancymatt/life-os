"""
Story Illustrator Agent

Generates illustrations for story scenes using the modular image generator.
"""

import asyncio
from typing import Dict, Any, List
from pydantic import BaseModel
from pathlib import Path
import time

from api.core.simple_agent import Agent, AgentConfig
from ai_tools.modular_image_generator.tool import ModularImageGenerator


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
        self.generator = ModularImageGenerator()

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
                - character_appearance: str (visual description)
                - art_style: str (default: 'digital_art')
                - max_illustrations: int (default: 5)

        Returns:
            Dict with 'illustrated_story' key containing IllustratedStory
        """
        # Validate input
        self.validate_input(input_data, ['written_story'])

        written_story = input_data['written_story']
        character_appearance = input_data.get('character_appearance', '')
        art_style = input_data.get('art_style', 'digital_art')
        max_illustrations = input_data.get('max_illustrations', 5)

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

                # Build illustration prompt
                full_prompt = self._build_illustration_prompt(
                    scene_prompt=scene['illustration_prompt'],
                    character_appearance=character_appearance,
                    art_style=art_style
                )

                # Generate image using modular generator
                result = await self._generate_illustration(full_prompt)

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

        illustrated_story = IllustratedStory(
            title=title,
            story=story_text,
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
        art_style: str
    ) -> str:
        """Build complete illustration prompt"""

        # Art style descriptions
        style_descriptions = {
            'watercolor': "watercolor painting style, soft colors, artistic brush strokes",
            'digital_art': "digital art, vibrant colors, detailed illustration",
            'sketch': "pencil sketch style, black and white, hand-drawn lines",
            'cartoon': "cartoon style, bold colors, simplified shapes, fun and playful",
            'realistic': "photorealistic style, detailed and lifelike",
            'oil_painting': "oil painting style, rich colors, textured brush strokes",
            'anime': "anime style, large expressive eyes, dynamic poses"
        }

        style_desc = style_descriptions.get(art_style, art_style)

        # Combine all elements
        full_prompt = f"{scene_prompt}"

        if character_appearance:
            full_prompt += f". The character is {character_appearance}."

        full_prompt += f". {style_desc}. High quality, professional illustration."

        return full_prompt

    async def _generate_illustration(self, prompt: str) -> Dict[str, Any]:
        """Generate a single illustration"""
        import os
        import base64
        from pathlib import Path
        from openai import AsyncOpenAI

        try:
            # Use DALL-E for text-to-image generation
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = await client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            # Download the generated image
            import httpx
            image_url = response.data[0].url

            async with httpx.AsyncClient() as http_client:
                img_response = await http_client.get(image_url)
                img_response.raise_for_status()
                image_data = img_response.content

            # Save to output directory
            output_dir = Path("/app/output/stories")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename
            import uuid
            filename = f"story_ill_{uuid.uuid4().hex[:12]}.png"
            output_path = output_dir / filename

            with open(output_path, 'wb') as f:
                f.write(image_data)

            # Return URL path
            return {
                "image_url": f"/output/stories/{filename}",
                "prompt": prompt
            }

        except Exception as e:
            print(f"Image generation failed: {e}")
            # Return placeholder
            return {
                "image_url": "/output/placeholder.png",
                "prompt": prompt
            }
