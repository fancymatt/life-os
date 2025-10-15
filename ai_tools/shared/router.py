"""
AI Model Router using LiteLLM

Provides a unified interface for calling multiple LLM providers (Gemini, OpenAI, Claude, etc.)
with retry logic, rate limiting, and structured output parsing.
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel
import litellm
from litellm import completion, acompletion
import yaml

# Configure LiteLLM
litellm.set_verbose = False  # Set to True for debugging


class RouterConfig:
    """Configuration for the router"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent.parent / "configs" / "models.yaml"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            # Return default config
            return {
                "defaults": {
                    "timeout": 180,
                    "retries": 3,
                    "temperature": 0.7,
                },
                "routing": {
                    "timeout": 180,
                    "retries": 3,
                }
            }

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get_model_for_tool(self, tool_name: str) -> str:
        """Get the configured model for a specific tool"""
        defaults = self.config.get("defaults", {})
        model = defaults.get(tool_name, "gemini-2.0-flash")

        # Check for environment-specific overrides
        env = os.getenv("AI_STUDIO_ENV", "production")
        overrides = self.config.get("overrides", {}).get(env, {})

        return overrides.get(tool_name, model)

    def get_routing_config(self) -> Dict[str, Any]:
        """Get routing configuration"""
        return self.config.get("routing", {
            "timeout": 180,
            "retries": 3,
        })


class LLMRouter:
    """
    Router for calling LLMs through LiteLLM

    Supports:
    - Multiple providers (Gemini, OpenAI, Claude, etc.)
    - Structured output parsing (JSON)
    - Image inputs
    - Retry logic
    - Cost tracking
    """

    def __init__(self, model: Optional[str] = None, config: Optional[RouterConfig] = None):
        """
        Initialize the router

        Args:
            model: Default model to use (e.g., "gemini-2.0-flash", "gpt-4o", "claude-3-5-sonnet")
            config: RouterConfig instance (optional)
        """
        self.config = config or RouterConfig()
        self.model = model or "gemini-2.0-flash"
        self.routing_config = self.config.get_routing_config()

    def encode_image(self, image_path: Union[str, Path]) -> str:
        """
        Encode an image to base64 for API calls

        Args:
            image_path: Path to the image file

        Returns:
            Base64 encoded image string
        """
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def create_image_message(self, image_path: Union[str, Path], detail: str = "high") -> Dict[str, Any]:
        """
        Create an image message for LiteLLM

        Args:
            image_path: Path to the image
            detail: Image detail level ("low", "high", "auto")

        Returns:
            Message dict with image
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # For some models, we need to encode to base64
        # LiteLLM handles the provider-specific format
        base64_image = self.encode_image(image_path)

        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": detail
            }
        }

    def call(
        self,
        prompt: str,
        model: Optional[str] = None,
        images: Optional[List[Union[str, Path]]] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Call an LLM with text and optional images

        Args:
            prompt: User prompt text
            model: Model to use (overrides default)
            images: List of image paths to include
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            response_format: Response format spec (e.g., {"type": "json_object"})
            **kwargs: Additional arguments for LiteLLM

        Returns:
            Response text from the model
        """
        model = model or self.model

        # Build messages
        messages = []

        # System message
        if system:
            messages.append({
                "role": "system",
                "content": system
            })

        # User message (with optional images)
        if images:
            content = []

            # Add images first
            for image_path in images:
                content.append(self.create_image_message(image_path))

            # Add text prompt
            content.append({
                "type": "text",
                "text": prompt
            })

            messages.append({
                "role": "user",
                "content": content
            })
        else:
            messages.append({
                "role": "user",
                "content": prompt
            })

        # Call LiteLLM
        response = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            timeout=self.routing_config.get("timeout", 180),
            num_retries=self.routing_config.get("retries", 3),
            **kwargs
        )

        return response.choices[0].message.content

    def call_structured(
        self,
        prompt: str,
        response_model: type[BaseModel],
        model: Optional[str] = None,
        images: Optional[List[Union[str, Path]]] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> BaseModel:
        """
        Call an LLM and parse response into a Pydantic model

        Args:
            prompt: User prompt text
            response_model: Pydantic model class for response
            model: Model to use (overrides default)
            images: List of image paths to include
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional arguments for LiteLLM

        Returns:
            Parsed Pydantic model instance
        """
        # Instruct model to return JSON
        json_instruction = f"\n\nRespond with valid JSON matching this schema:\n{response_model.model_json_schema()}"
        full_prompt = prompt + json_instruction

        # Request JSON format
        response_format = {"type": "json_object"}

        # Call the model
        response_text = self.call(
            prompt=full_prompt,
            model=model,
            images=images,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            **kwargs
        )

        # Parse JSON response
        try:
            # Try to parse directly
            response_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_data = json.loads(response_text.strip())

        # Parse into Pydantic model
        return response_model.model_validate(response_data)

    async def acall(
        self,
        prompt: str,
        model: Optional[str] = None,
        images: Optional[List[Union[str, Path]]] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Async version of call()

        Args: Same as call()

        Returns:
            Response text from the model
        """
        model = model or self.model

        # Build messages (same as sync version)
        messages = []

        if system:
            messages.append({
                "role": "system",
                "content": system
            })

        if images:
            content = []
            for image_path in images:
                content.append(self.create_image_message(image_path))
            content.append({
                "type": "text",
                "text": prompt
            })
            messages.append({
                "role": "user",
                "content": content
            })
        else:
            messages.append({
                "role": "user",
                "content": prompt
            })

        # Call LiteLLM async
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            timeout=self.routing_config.get("timeout", 180),
            num_retries=self.routing_config.get("retries", 3),
            **kwargs
        )

        return response.choices[0].message.content

    def generate_image_with_gemini(
        self,
        prompt: str,
        image_path: Union[str, Path],
        model: str = "gemini-2.5-flash-image",
        temperature: float = 0.8,
        **kwargs
    ) -> bytes:
        """
        Generate an image using Gemini's native image generation

        Args:
            prompt: Text prompt for image generation
            image_path: Source image path (for subject preservation)
            model: Gemini model to use
            temperature: Generation temperature (0.0-1.0)
            **kwargs: Additional arguments

        Returns:
            Image bytes (PNG/JPEG format)
        """
        try:
            import requests

            # Encode the image
            base64_image = self.encode_image(image_path)

            # Determine mime type
            image_path = Path(image_path)
            ext = image_path.suffix.lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }.get(ext, 'image/jpeg')

            # Build the request for Gemini API
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")

            # Use Gemini's REST API for generation
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

            headers = {
                "Content-Type": "application/json"
            }

            payload = {
                "contents": [{
                    "parts": [
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": base64_image
                            }
                        },
                        {
                            "text": prompt
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "topK": 40,
                    "topP": 0.95
                }
            }

            # Make the request
            response = requests.post(url, headers=headers, json=payload, timeout=180)

            # Parse response before checking status
            result = response.json()

            # Check for Gemini API errors (content filtering, etc.)
            if response.status_code != 200:
                error_message = "Unknown error"

                # Extract error details from Gemini response
                if "error" in result:
                    error_info = result["error"]
                    if isinstance(error_info, dict):
                        error_message = error_info.get("message", str(error_info))
                    else:
                        error_message = str(error_info)

                raise Exception(f"Gemini API error: {error_message}")

            # Check for content filtering / safety blocks
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]

                # Check finish reason for blocks
                finish_reason = candidate.get("finishReason", "")
                if finish_reason in ["SAFETY", "BLOCKED_REASON", "CONTENT_FILTER"]:
                    # Get safety ratings for more context
                    safety_ratings = candidate.get("safetyRatings", [])
                    blocked_categories = [
                        rating["category"] for rating in safety_ratings
                        if rating.get("blocked", False)
                    ]

                    if blocked_categories:
                        categories_str = ", ".join(blocked_categories)
                        raise Exception(f"Content filtered by Gemini safety systems. Blocked categories: {categories_str}")
                    else:
                        raise Exception(f"Content filtered by Gemini safety systems (reason: {finish_reason})")

                # Extract image data
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "inlineData" in part:
                            # Decode base64 image
                            image_data = part["inlineData"]["data"]
                            return base64.b64decode(image_data)

            # If we get here, no image was found but no clear error either
            raise Exception(f"No image in Gemini response. API returned: {result.get('candidates', [{}])[0].get('finishReason', 'unknown reason')}")

        except Exception as e:
            raise Exception(f"Gemini image generation failed: {e}")

    async def agenerate_image_with_gemini(
        self,
        prompt: str,
        image_path: Union[str, Path],
        model: str = "gemini-2.5-flash-image",
        temperature: float = 0.8,
        **kwargs
    ) -> bytes:
        """
        Async version: Generate an image using Gemini's native image generation

        Args:
            prompt: Text prompt for image generation
            image_path: Source image path (for subject preservation)
            model: Gemini model to use
            temperature: Generation temperature (0.0-1.0)
            **kwargs: Additional arguments

        Returns:
            Image bytes (PNG/JPEG format)
        """
        try:
            import httpx

            # Encode the image
            base64_image = self.encode_image(image_path)

            # Determine mime type
            image_path = Path(image_path)
            ext = image_path.suffix.lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }.get(ext, 'image/jpeg')

            # Build the request for Gemini API
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")

            # Use Gemini's REST API for generation
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

            headers = {
                "Content-Type": "application/json"
            }

            payload = {
                "contents": [{
                    "parts": [
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": base64_image
                            }
                        },
                        {
                            "text": prompt
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "topK": 40,
                    "topP": 0.95
                }
            }

            # Make async request
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(url, headers=headers, json=payload)

            # Parse response
            result = response.json()

            # Check for Gemini API errors (content filtering, etc.)
            if response.status_code != 200:
                error_message = "Unknown error"

                # Extract error details from Gemini response
                if "error" in result:
                    error_info = result["error"]
                    if isinstance(error_info, dict):
                        error_message = error_info.get("message", str(error_info))
                    else:
                        error_message = str(error_info)

                raise Exception(f"Gemini API error: {error_message}")

            # Check for content filtering / safety blocks
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]

                # Check finish reason for blocks
                finish_reason = candidate.get("finishReason", "")
                if finish_reason in ["SAFETY", "BLOCKED_REASON", "CONTENT_FILTER"]:
                    # Get safety ratings for more context
                    safety_ratings = candidate.get("safetyRatings", [])
                    blocked_categories = [
                        rating["category"] for rating in safety_ratings
                        if rating.get("blocked", False)
                    ]

                    if blocked_categories:
                        categories_str = ", ".join(blocked_categories)
                        raise Exception(f"Content filtered by Gemini safety systems. Blocked categories: {categories_str}")
                    else:
                        raise Exception(f"Content filtered by Gemini safety systems (reason: {finish_reason})")

                # Extract image data
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "inlineData" in part:
                            # Decode base64 image
                            image_data = part["inlineData"]["data"]
                            return base64.b64decode(image_data)

            # If we get here, no image was found but no clear error either
            raise Exception(f"No image in Gemini response. API returned: {result.get('candidates', [{}])[0].get('finishReason', 'unknown reason')}")

        except Exception as e:
            raise Exception(f"Gemini image generation failed: {e}")

    def generate_image(
        self,
        prompt: str,
        image_path: Optional[Union[str, Path]] = None,
        model: str = "gemini-2.5-flash-image",
        provider: str = "gemini",
        size: str = "1024x1792",
        quality: str = "standard",
        temperature: float = 0.8,
        **kwargs
    ) -> bytes:
        """
        Generate an image using various providers

        Args:
            prompt: Text prompt for image generation
            image_path: Source image (required for Gemini, optional for DALL-E)
            model: Model to use
            provider: Provider ("gemini" or "dalle")
            size: Image size (DALL-E only)
            quality: Image quality (DALL-E only)
            temperature: Generation temperature (Gemini only)
            **kwargs: Additional arguments

        Returns:
            Image bytes (PNG/JPEG format)
        """
        if provider == "gemini" or model.startswith("gemini"):
            if not image_path:
                raise ValueError("image_path is required for Gemini image generation")
            return self.generate_image_with_gemini(prompt, image_path, model, temperature, **kwargs)
        elif provider == "dalle" or model.startswith("dall-e"):
            # DALL-E fallback
            try:
                from openai import OpenAI
                import requests

                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                response = client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=1
                )

                image_url = response.data[0].url
                image_response = requests.get(image_url, timeout=60)
                image_response.raise_for_status()

                return image_response.content

            except Exception as e:
                raise Exception(f"DALL-E generation failed: {e}")
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def agenerate_image(
        self,
        prompt: str,
        image_path: Optional[Union[str, Path]] = None,
        model: str = "gemini-2.5-flash-image",
        provider: str = "gemini",
        size: str = "1024x1792",
        quality: str = "standard",
        temperature: float = 0.8,
        **kwargs
    ) -> bytes:
        """
        Async version: Generate an image using various providers

        Args:
            prompt: Text prompt for image generation
            image_path: Source image (required for Gemini, optional for DALL-E)
            model: Model to use
            provider: Provider ("gemini" or "dalle")
            size: Image size (DALL-E only)
            quality: Image quality (DALL-E only)
            temperature: Generation temperature (Gemini only)
            **kwargs: Additional arguments

        Returns:
            Image bytes (PNG/JPEG format)
        """
        if provider == "gemini" or model.startswith("gemini"):
            if not image_path:
                raise ValueError("image_path is required for Gemini image generation")
            return await self.agenerate_image_with_gemini(prompt, image_path, model, temperature, **kwargs)
        elif provider == "dalle" or model.startswith("dall-e"):
            # DALL-E fallback (using sync OpenAI SDK in thread pool)
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            def _generate_dalle():
                try:
                    from openai import OpenAI
                    import requests

                    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                    response = client.images.generate(
                        model=model,
                        prompt=prompt,
                        size=size,
                        quality=quality,
                        n=1
                    )

                    image_url = response.data[0].url
                    image_response = requests.get(image_url, timeout=60)
                    image_response.raise_for_status()

                    return image_response.content

                except Exception as e:
                    raise Exception(f"DALL-E generation failed: {e}")

            # Run sync DALL-E code in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                return await loop.run_in_executor(pool, _generate_dalle)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def edit_image(
        self,
        image_path: Union[str, Path],
        prompt: str,
        mask_path: Optional[Union[str, Path]] = None,
        model: str = "dall-e-2",
        size: str = "1024x1024",
        n: int = 1,
        **kwargs
    ) -> bytes:
        """
        Edit an image using DALL-E image editing

        Args:
            image_path: Path to source image (PNG, <4MB, square)
            prompt: Text prompt describing the desired edit
            mask_path: Optional mask image path (transparent areas will be edited)
            model: Model to use (dall-e-2)
            size: Output size (256x256, 512x512, 1024x1024)
            n: Number of variations
            **kwargs: Additional arguments

        Returns:
            Edited image bytes (PNG format)
        """
        try:
            from openai import OpenAI
            import requests

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Read image file
            with open(image_path, 'rb') as f:
                image_file = f.read()

            # Read mask if provided
            mask_file = None
            if mask_path:
                with open(mask_path, 'rb') as f:
                    mask_file = f.read()

            # Edit image
            if mask_file:
                response = client.images.edit(
                    model=model,
                    image=image_file,
                    mask=mask_file,
                    prompt=prompt,
                    size=size,
                    n=n
                )
            else:
                response = client.images.edit(
                    model=model,
                    image=image_file,
                    prompt=prompt,
                    size=size,
                    n=n
                )

            # Get image URL
            image_url = response.data[0].url

            # Download image
            image_response = requests.get(image_url, timeout=60)
            image_response.raise_for_status()

            return image_response.content

        except Exception as e:
            raise Exception(f"Image editing failed: {e}")

    def get_cost_estimate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a model call

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        try:
            return litellm.completion_cost(
                model=model,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens
            )
        except Exception:
            # Return 0 if cost estimation fails
            return 0.0


# Convenience function for quick calls
def call_llm(
    prompt: str,
    model: str = "gemini-2.0-flash",
    images: Optional[List[Union[str, Path]]] = None,
    system: Optional[str] = None,
    **kwargs
) -> str:
    """
    Quick function to call an LLM

    Args:
        prompt: User prompt
        model: Model to use
        images: Optional image paths
        system: Optional system prompt
        **kwargs: Additional arguments

    Returns:
        Response text
    """
    router = LLMRouter(model=model)
    return router.call(prompt, images=images, system=system, **kwargs)


def call_llm_structured(
    prompt: str,
    response_model: type[BaseModel],
    model: str = "gemini-2.0-flash",
    images: Optional[List[Union[str, Path]]] = None,
    system: Optional[str] = None,
    **kwargs
) -> BaseModel:
    """
    Quick function to call an LLM with structured output

    Args:
        prompt: User prompt
        response_model: Pydantic model for response
        model: Model to use
        images: Optional image paths
        system: Optional system prompt
        **kwargs: Additional arguments

    Returns:
        Parsed Pydantic model
    """
    router = LLMRouter(model=model)
    return router.call_structured(
        prompt,
        response_model=response_model,
        images=images,
        system=system,
        **kwargs
    )
