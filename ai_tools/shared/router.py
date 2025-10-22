"""
AI Model Router using LiteLLM

Provides a unified interface for calling multiple LLM providers (Gemini, OpenAI, Claude, etc.)
with retry logic, rate limiting, and structured output parsing.

CRITICAL - Gemini Model Naming Convention:
==========================================
✅ CORRECT model names (use these):
    - "gemini/gemini-2.5-flash-image"  # Image generation (NEW dedicated model)
    - "gemini/gemini-2.0-flash-exp"    # Text/analysis (multimodal)

❌ WRONG (these don't exist or won't work):
    - "gemini/gemini-2.5-flash-latest" # No image generation support
    - "gemini-2.5-flash-image"         # Missing "gemini/" prefix for LiteLLM routing

How Routing Works:
-----------------
1. LiteLLM expects: "gemini/model-name" (prefix for routing)
2. This router strips the "gemini/" prefix at lines 433, 615 before calling Gemini API
3. Gemini API receives: "model-name" (no prefix)

DO NOT change model names without verifying they exist in Gemini docs.
DO NOT remove the prefix stripping logic - it's required for proper routing.

Gemini Image Generation Requirements (see lines 403-772):
---------------------------------------------------------
- Model: gemini/gemini-2.5-flash-image (with prefix)
- Auth: Header-based (x-goog-api-key), NOT query parameter
- responseModalities: ["image"] REQUIRED in generationConfig
- API: POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
"""

import os
import json
import base64
import asyncio
import random
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel
import litellm
from litellm import completion, acompletion
import yaml

# Configure LiteLLM
litellm.set_verbose = True  # Set to True for debugging
litellm.drop_params = True  # Automatically drop unsupported parameters (e.g., temperature for GPT-5)


class RouterConfig:
    """Configuration for the router"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent.parent / "configs" / "models.yaml"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with overrides"""
        # Load base config
        if not self.config_path.exists():
            # Return default config
            base_config = {
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
        else:
            with open(self.config_path, 'r') as f:
                base_config = yaml.safe_load(f)

        # Load user overrides (writable location)
        overrides_path = Path(__file__).parent.parent.parent / "data" / "tool_configs" / "overrides.yaml"
        if overrides_path.exists():
            with open(overrides_path, 'r') as f:
                overrides = yaml.safe_load(f) or {}

                # Merge overrides into base config
                if 'defaults' in overrides:
                    base_config.setdefault('defaults', {}).update(overrides['defaults'])
                if 'tool_settings' in overrides:
                    base_config.setdefault('tool_settings', {}).update(overrides['tool_settings'])

        return base_config

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

    def encode_image(self, image_path: Union[str, Path], max_size_mb: float = 1.0) -> str:
        """
        Encode an image to base64 for API calls, with automatic resizing for large images

        Args:
            image_path: Path to the image file
            max_size_mb: Maximum file size in MB before resizing (default: 1.0)

        Returns:
            Base64 encoded image string
        """
        from PIL import Image
        import tempfile

        image_path = Path(image_path)

        # Check file size
        file_size_mb = image_path.stat().st_size / (1024 * 1024)

        if file_size_mb > max_size_mb:
            print(f"📏 Image is {file_size_mb:.2f}MB, resizing to reduce size...")

            # Open image with PIL
            img = Image.open(image_path)

            # Calculate new size (reduce by size ratio squared, since area scales quadratically)
            # Target: reduce file size by approximately the ratio needed
            size_ratio = max_size_mb / file_size_mb
            dimension_ratio = size_ratio ** 0.5  # Square root since area = width × height

            new_width = int(img.width * dimension_ratio)
            new_height = int(img.height * dimension_ratio)

            print(f"   Original: {img.width}x{img.height}")
            print(f"   Resized: {new_width}x{new_height}")

            # Resize image with high-quality resampling
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=image_path.suffix, delete=False) as tmp_file:
                temp_path = Path(tmp_file.name)

                # Preserve format and optimize
                if image_path.suffix.lower() in ['.jpg', '.jpeg']:
                    resized_img.save(temp_path, 'JPEG', quality=85, optimize=True)
                elif image_path.suffix.lower() == '.png':
                    resized_img.save(temp_path, 'PNG', optimize=True)
                else:
                    resized_img.save(temp_path, format=img.format, optimize=True)

            # Encode the resized image
            with open(temp_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')

            # Clean up temp file
            temp_path.unlink()

            # Check final size
            final_size_mb = len(base64.b64decode(encoded)) / (1024 * 1024)
            print(f"   Final size: {final_size_mb:.2f}MB")

            return encoded
        else:
            # Image is small enough, encode directly
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
        # Instruct model to return JSON (with clearer instructions)
        schema = response_model.model_json_schema()
        required_fields = schema.get('required', [])
        properties = schema.get('properties', {})

        # Build a simple field list
        field_descriptions = []
        for field in required_fields:
            if field.startswith('_'):
                continue
            field_info = properties.get(field, {})
            field_desc = field_info.get('description', '')
            field_descriptions.append(f'  "{field}": "{field_desc}"')

        field_list = ',\n'.join(field_descriptions)

        json_instruction = f"""

IMPORTANT: Respond with a JSON object containing actual data values (NOT the schema definition).

Required fields:
{{
{field_list}
}}

Example format:
{{
  "age": "young adult",
  "skin_tone": "fair",
  "face_description": "Oval face with...",
  "hair_description": "Long brown hair...",
  "body_description": "Athletic build..."
}}

Your response must be ONLY the JSON object with real data values - no schema, no explanations."""

        full_prompt = prompt + json_instruction

        # Request JSON format (but skip for Ollama - it doesn't support this parameter)
        model_name = model or self.model
        call_kwargs = {}
        if not model_name.startswith('ollama/'):
            call_kwargs['response_format'] = {"type": "json_object"}

        # Call the model
        response_text = self.call(
            prompt=full_prompt,
            model=model,
            images=images,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            **call_kwargs,
            **kwargs
        )

        # Parse JSON response with robust extraction
        try:
            # Try to parse directly
            response_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try multiple extraction strategies
            response_text = response_text.strip()

            # Strategy 1: Remove markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # Strategy 2: Extract JSON object from text (handles "Thinking..." prefix)
            # Find first { and last }
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx + 1]
                    response_data = json.loads(json_text)
                else:
                    # No JSON object found
                    raise json.JSONDecodeError(f"No JSON object found in response", response_text, 0)
            except json.JSONDecodeError:
                # Strategy 3: Try to find JSON array
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx + 1]
                    response_data = json.loads(json_text)
                else:
                    # Strategy 4: Parse markdown-style key-value format
                    # Example: **age:** young adult **skin_tone:** fair
                    import re

                    # Get expected fields from schema
                    schema = response_model.model_json_schema()
                    expected_fields = set(schema.get('properties', {}).keys())

                    # Try to extract field-value pairs
                    response_data = {}
                    for field in expected_fields:
                        if field.startswith('_'):
                            continue  # Skip private fields like _metadata

                        # Look for patterns like: **field:** value or field: value
                        patterns = [
                            rf'\*\*{field}\*\*:\s*([^\*]+?)(?=\s*\*\*|\s*$)',  # **field:** value
                            rf'{field}:\s*([^\n]+?)(?=\n|$)',  # field: value
                            rf'"{field}":\s*"([^"]+)"',  # "field": "value"
                        ]

                        for pattern in patterns:
                            match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
                            if match:
                                value = match.group(1).strip()
                                # Clean up common artifacts
                                value = value.replace('...', '').strip()
                                value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
                                if value and len(value) > 2:  # Only accept non-trivial values
                                    response_data[field] = value
                                    break

                    # Only accept if we got at least half the required fields
                    if len(response_data) < len(expected_fields) / 2:
                        # Give up and show what we got
                        raise ValueError(f"Could not extract valid JSON from response. Response text: {response_text[:500]}")

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

    async def acall_structured(
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
        Async version: Call an LLM and parse response into a Pydantic model

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
        # Instruct model to return JSON (with clearer instructions)
        schema = response_model.model_json_schema()
        required_fields = schema.get('required', [])
        properties = schema.get('properties', {})

        # Build a simple field list
        field_descriptions = []
        for field in required_fields:
            if field.startswith('_'):
                continue
            field_info = properties.get(field, {})
            field_desc = field_info.get('description', '')
            field_descriptions.append(f'  "{field}": "{field_desc}"')

        field_list = ',\n'.join(field_descriptions)

        json_instruction = f"""

IMPORTANT: Respond with a JSON object containing actual data values (NOT the schema definition).

Required fields:
{{
{field_list}
}}

Example format:
{{
  "age": "young adult",
  "skin_tone": "fair",
  "face_description": "Oval face with...",
  "hair_description": "Long brown hair...",
  "body_description": "Athletic build..."
}}

Your response must be ONLY the JSON object with real data values - no schema, no explanations."""

        full_prompt = prompt + json_instruction

        # Request JSON format (but skip for Ollama - it doesn't support this parameter)
        model_name = model or self.model
        call_kwargs = {}
        if not model_name.startswith('ollama/'):
            call_kwargs['response_format'] = {"type": "json_object"}

        # Call the model asynchronously
        response_text = await self.acall(
            prompt=full_prompt,
            model=model,
            images=images,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            **call_kwargs,
            **kwargs
        )

        # Debug: Log raw response
        print(f"\n🔍 RAW MODEL RESPONSE (first 1000 chars):\n{response_text[:1000]}\n")

        # Parse JSON response with robust extraction
        try:
            # Try to parse directly
            response_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try multiple extraction strategies
            response_text = response_text.strip()

            # Strategy 1: Remove markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # Strategy 2: Extract JSON object from text (handles "Thinking..." prefix)
            # Find first { and last }
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx + 1]
                    response_data = json.loads(json_text)
                else:
                    # No JSON object found
                    raise json.JSONDecodeError(f"No JSON object found in response", response_text, 0)
            except json.JSONDecodeError:
                # Strategy 3: Try to find JSON array
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx + 1]
                    response_data = json.loads(json_text)
                else:
                    # Strategy 4: Parse markdown-style key-value format
                    # Example: **age:** young adult **skin_tone:** fair
                    import re

                    # Get expected fields from schema
                    schema = response_model.model_json_schema()
                    expected_fields = set(schema.get('properties', {}).keys())

                    # Try to extract field-value pairs
                    response_data = {}
                    for field in expected_fields:
                        if field.startswith('_'):
                            continue  # Skip private fields like _metadata

                        # Look for patterns like: **field:** value or field: value
                        patterns = [
                            rf'\*\*{field}\*\*:\s*([^\*]+?)(?=\s*\*\*|\s*$)',  # **field:** value
                            rf'{field}:\s*([^\n]+?)(?=\n|$)',  # field: value
                            rf'"{field}":\s*"([^"]+)"',  # "field": "value"
                        ]

                        for pattern in patterns:
                            match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
                            if match:
                                value = match.group(1).strip()
                                # Clean up common artifacts
                                value = value.replace('...', '').strip()
                                value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
                                if value and len(value) > 2:  # Only accept non-trivial values
                                    response_data[field] = value
                                    break

                    # Only accept if we got at least half the required fields
                    if len(response_data) < len(expected_fields) / 2:
                        # Give up and show what we got
                        raise ValueError(f"Could not extract valid JSON from response. Response text: {response_text[:500]}")

        # Parse into Pydantic model
        return response_model.model_validate(response_data)

    def generate_image_with_gemini(
        self,
        prompt: str,
        image_path: Union[str, Path],
        model: str = "gemini-2.5-flash-image",
        temperature: float = 0.8,
        max_retries: int = 3,
        **kwargs
    ) -> bytes:
        """
        Generate an image using Gemini's native image generation

        Includes retry logic with exponential backoff for transient failures.

        Args:
            prompt: Text prompt for image generation
            image_path: Source image path (for subject preservation)
            model: Gemini model to use (e.g., "gemini-2.5-flash-image" or "gemini/gemini-2.5-flash-image")
            temperature: Generation temperature (0.0-1.0)
            max_retries: Maximum retry attempts for transient failures (default: 3)
            **kwargs: Additional arguments

        Returns:
            Image bytes (PNG/JPEG format)
        """
        import requests
        import time

        # Strip "gemini/" prefix if present (for LiteLLM compatibility)
        if model.startswith("gemini/"):
            model = model[7:]  # Remove "gemini/" prefix

        # Encode the image (do this once, outside retry loop)
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

        # Use Gemini's REST API for image generation
        # Per docs: https://ai.google.dev/gemini-api/docs/image-generation
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
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
                "topP": 0.95,
                "responseModalities": ["image"]
            }
        }

        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(max_retries):
            try:
                # Make the request
                response = requests.post(url, headers=headers, json=payload, timeout=180)

                # Parse response before checking status
                result = response.json()

                # Check for Gemini API errors (content filtering, etc.)
                if response.status_code >= 400:
                    error_message = "Unknown error"

                    # Extract error details from Gemini response
                    if "error" in result:
                        error_info = result["error"]
                        if isinstance(error_info, dict):
                            error_message = error_info.get("message", str(error_info))
                        else:
                            error_message = str(error_info)

                    # Check if this is a permanent error (4xx) or transient (5xx)
                    if 400 <= response.status_code < 500:
                        # Client error - permanent, don't retry
                        raise Exception(f"Gemini API error (permanent): {error_message}")
                    else:
                        # Server error (5xx) - transient, can retry
                        raise Exception(f"Gemini API error (transient): {error_message}")

                # Check for content filtering / safety blocks (PERMANENT - don't retry)
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

                        # Content filtering is PERMANENT - don't retry
                        if blocked_categories:
                            categories_str = ", ".join(blocked_categories)
                            raise ValueError(f"Content filtered by Gemini safety systems. Blocked categories: {categories_str}")
                        else:
                            raise ValueError(f"Content filtered by Gemini safety systems (reason: {finish_reason})")

                    # Extract image data
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "inlineData" in part:
                                # Decode base64 image
                                image_data = part["inlineData"]["data"]
                                return base64.b64decode(image_data)

                # If we get here, no image was found but no clear error either
                raise Exception(f"No image in Gemini response. API returned: {result.get('candidates', [{}])[0].get('finishReason', 'unknown reason')}")

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                # Transient network errors - retry
                last_error = e
                error_type = type(e).__name__

                if attempt < max_retries - 1:
                    # Calculate exponential backoff with jitter
                    backoff = (2 ** attempt) + (random.random() * 0.5)
                    print(f"⚠️ {error_type} on attempt {attempt + 1}/{max_retries}. Retrying in {backoff:.1f}s...")
                    time.sleep(backoff)
                    continue
                else:
                    # Max retries reached
                    raise Exception(f"Gemini image generation failed after {max_retries} attempts: {e}")

            except ValueError as e:
                # Permanent errors (content filtering, missing API key, etc.) - don't retry
                raise Exception(f"Gemini image generation failed (permanent error): {e}")

            except Exception as e:
                # Check if this is a transient error worth retrying
                error_msg = str(e).lower()
                is_transient = any(keyword in error_msg for keyword in [
                    'transient', 'timeout', 'network', 'connection', 'temporary', '5xx', '500', '502', '503', '504'
                ])

                if is_transient and attempt < max_retries - 1:
                    last_error = e
                    backoff = (2 ** attempt) + (random.random() * 0.5)
                    print(f"⚠️ Transient error on attempt {attempt + 1}/{max_retries}. Retrying in {backoff:.1f}s...")
                    time.sleep(backoff)
                    continue
                else:
                    # Permanent error or max retries reached
                    raise Exception(f"Gemini image generation failed: {e}")

        # Should never reach here, but just in case
        raise Exception(f"Gemini image generation failed after {max_retries} attempts: {last_error}")

    async def agenerate_image_with_gemini(
        self,
        prompt: str,
        image_path: Union[str, Path],
        model: str = "gemini-2.5-flash-image",
        temperature: float = 0.8,
        max_retries: int = 3,
        **kwargs
    ) -> bytes:
        """
        Async version: Generate an image using Gemini's native image generation

        Includes retry logic with exponential backoff for transient failures.

        Args:
            prompt: Text prompt for image generation
            image_path: Source image path (for subject preservation)
            model: Gemini model to use (e.g., "gemini-2.5-flash-image" or "gemini/gemini-2.5-flash-image")
            temperature: Generation temperature (0.0-1.0)
            max_retries: Maximum retry attempts for transient failures (default: 3)
            **kwargs: Additional arguments

        Returns:
            Image bytes (PNG/JPEG format)
        """
        import httpx

        # Strip "gemini/" prefix if present (for LiteLLM compatibility)
        if model.startswith("gemini/"):
            model = model[7:]  # Remove "gemini/" prefix

        # Encode the image (do this once, outside retry loop)
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

        # Use Gemini's REST API for image generation
        # Per docs: https://ai.google.dev/gemini-api/docs/image-generation
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
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
                "topP": 0.95,
                "responseModalities": ["image"]
            }
        }

        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(max_retries):
            try:
                # Make async request
                async with httpx.AsyncClient(timeout=180.0) as client:
                    response = await client.post(url, headers=headers, json=payload)

                # Debug logging
                print(f"🔍 Gemini API Response Status: {response.status_code}")
                print(f"🔍 Response Headers: {dict(response.headers)}")
                print(f"🔍 Response Body (first 500 chars): {response.text[:500]}")

                # Parse response
                result = response.json()

                # Check for Gemini API errors (content filtering, etc.)
                if response.status_code >= 400:
                    error_message = "Unknown error"

                    # Extract error details from Gemini response
                    if "error" in result:
                        error_info = result["error"]
                        if isinstance(error_info, dict):
                            error_message = error_info.get("message", str(error_info))
                        else:
                            error_message = str(error_info)

                    # Check if this is a permanent error (4xx) or transient (5xx)
                    if 400 <= response.status_code < 500:
                        # Client error - permanent, don't retry
                        raise Exception(f"Gemini API error (permanent): {error_message}")
                    else:
                        # Server error (5xx) - transient, can retry
                        raise Exception(f"Gemini API error (transient): {error_message}")

                # Check for content filtering / safety blocks (PERMANENT - don't retry)
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

                        # Content filtering is PERMANENT - don't retry
                        if blocked_categories:
                            categories_str = ", ".join(blocked_categories)
                            raise ValueError(f"Content filtered by Gemini safety systems. Blocked categories: {categories_str}")
                        else:
                            raise ValueError(f"Content filtered by Gemini safety systems (reason: {finish_reason})")

                    # Extract image data
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "inlineData" in part:
                                # Decode base64 image
                                image_data = part["inlineData"]["data"]
                                return base64.b64decode(image_data)

                # If we get here, no image was found but no clear error either
                raise Exception(f"No image in Gemini response. API returned: {result.get('candidates', [{}])[0].get('finishReason', 'unknown reason')}")

            except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
                # Transient network errors - retry
                last_error = e
                error_type = type(e).__name__

                if attempt < max_retries - 1:
                    # Calculate exponential backoff with jitter
                    backoff = (2 ** attempt) + (random.random() * 0.5)
                    print(f"⚠️ {error_type} on attempt {attempt + 1}/{max_retries}. Retrying in {backoff:.1f}s...")
                    await asyncio.sleep(backoff)
                    continue
                else:
                    # Max retries reached
                    raise Exception(f"Gemini image generation failed after {max_retries} attempts: {e}")

            except ValueError as e:
                # Permanent errors (content filtering, missing API key, etc.) - don't retry
                raise Exception(f"Gemini image generation failed (permanent error): {e}")

            except Exception as e:
                # Check if this is a transient error worth retrying
                error_msg = str(e).lower()
                is_transient = any(keyword in error_msg for keyword in [
                    'transient', 'timeout', 'network', 'connection', 'temporary', '5xx', '500', '502', '503', '504'
                ])

                if is_transient and attempt < max_retries - 1:
                    last_error = e
                    backoff = (2 ** attempt) + (random.random() * 0.5)
                    print(f"⚠️ Transient error on attempt {attempt + 1}/{max_retries}. Retrying in {backoff:.1f}s...")
                    await asyncio.sleep(backoff)
                    continue
                else:
                    # Permanent error or max retries reached
                    raise Exception(f"Gemini image generation failed: {e}")

        # Should never reach here, but just in case
        raise Exception(f"Gemini image generation failed after {max_retries} attempts: {last_error}")

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
