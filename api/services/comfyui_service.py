"""ComfyUI Service

Integrates with ComfyUI server for local image generation and editing.
Supports Qwen-Image-Edit GGUF workflow for state-of-the-art editing.
"""

import os
import asyncio
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
import httpx
from api.logging_config import get_logger

logger = get_logger(__name__)


class ComfyUIService:
    """Service for ComfyUI integration"""

    def __init__(self):
        """Initialize ComfyUI service"""
        self.enabled = os.getenv("COMFYUI_ENABLED", "false").lower() == "true"
        self.base_url = os.getenv("COMFYUI_URL", "http://localhost:8188")
        self.timeout = int(os.getenv("COMFYUI_TIMEOUT", "300"))
        self.default_workflow = os.getenv("COMFYUI_DEFAULT_WORKFLOW", "qwen-image-edit")

        # GGUF model names (detected from ComfyUI)
        self.qwen_unet = "Qwen-Image-Edit-2509-Q5_K_S.gguf"
        self.qwen_clip = "Qwen2.5-VL-7B-Instruct-UD-Q5_K_S.gguf"
        self.qwen_vae = "sdxl_vae.safetensors"  # Will upgrade to qwen_image_vae.safetensors when available

        logger.info(f"ComfyUI service initialized: enabled={self.enabled}, url={self.base_url}")

    async def health_check(self) -> Dict[str, Any]:
        """Check ComfyUI server health"""
        if not self.enabled:
            return {"status": "disabled", "available": False}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/system_stats")
                response.raise_for_status()
                stats = response.json()

                return {
                    "status": "healthy",
                    "available": True,
                    "gpu": stats.get("devices", [{}])[0].get("name", "Unknown"),
                    "vram_total_gb": stats.get("devices", [{}])[0].get("vram_total", 0) / (1024**3),
                    "vram_free_gb": stats.get("devices", [{}])[0].get("vram_free", 0) / (1024**3),
                    "comfyui_version": stats.get("system", {}).get("comfyui_version", "Unknown")
                }
        except Exception as e:
            logger.error(f"ComfyUI health check failed: {e}")
            return {"status": "error", "available": False, "error": str(e)}

    async def upload_image(self, image_path: Path, subfolder: str = "") -> Dict[str, str]:
        """
        Upload an image to ComfyUI

        Args:
            image_path: Path to image file
            subfolder: ComfyUI subfolder (default: input)

        Returns:
            Dict with uploaded filename and subfolder
        """
        if not self.enabled:
            raise RuntimeError("ComfyUI is not enabled")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                with open(image_path, "rb") as f:
                    files = {
                        "image": (image_path.name, f, "image/png"),
                        "subfolder": (None, subfolder)
                    }
                    response = await client.post(
                        f"{self.base_url}/upload/image",
                        files=files
                    )
                    response.raise_for_status()
                    result = response.json()

                    logger.info(f"Uploaded image to ComfyUI: {result}")
                    return {
                        "filename": result.get("name", image_path.name),
                        "subfolder": result.get("subfolder", subfolder)
                    }
        except Exception as e:
            logger.error(f"Failed to upload image to ComfyUI: {e}")
            raise

    async def queue_prompt(self, workflow: Dict[str, Any], client_id: Optional[str] = None) -> str:
        """
        Queue a workflow for execution

        Args:
            workflow: ComfyUI workflow dict
            client_id: Optional client identifier

        Returns:
            Prompt ID for tracking
        """
        if not self.enabled:
            raise RuntimeError("ComfyUI is not enabled")

        if client_id is None:
            client_id = f"lifeos-{uuid.uuid4()}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/prompt",
                    json={"prompt": workflow, "client_id": client_id}
                )

                # Log response details for debugging
                if response.status_code != 200:
                    error_body = response.text
                    logger.error(f"ComfyUI rejected workflow (HTTP {response.status_code}): {error_body}")

                response.raise_for_status()
                result = response.json()

                prompt_id = result.get("prompt_id")
                logger.info(f"Queued ComfyUI prompt: {prompt_id}")

                return prompt_id
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to queue ComfyUI prompt: HTTP {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to queue ComfyUI prompt: {e}")
            raise

    async def get_history(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution history for a prompt

        Args:
            prompt_id: Prompt ID to check

        Returns:
            History dict or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/history/{prompt_id}")
                response.raise_for_status()
                history = response.json()

                return history.get(prompt_id)
        except Exception as e:
            logger.warning(f"Failed to get ComfyUI history for {prompt_id}: {e}")
            return None

    async def wait_for_completion(
        self,
        prompt_id: str,
        poll_interval: float = 2.0,
        max_wait: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Wait for a prompt to complete

        Args:
            prompt_id: Prompt ID to wait for
            poll_interval: Seconds between polls
            max_wait: Maximum seconds to wait (None = use self.timeout)

        Returns:
            Completion result with outputs

        Raises:
            TimeoutError: If execution times out
            RuntimeError: If execution fails
        """
        if max_wait is None:
            max_wait = self.timeout

        start_time = asyncio.get_event_loop().time()

        while True:
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > max_wait:
                raise TimeoutError(f"ComfyUI execution timed out after {max_wait}s")

            # Check history
            history = await self.get_history(prompt_id)

            if history is None:
                # Not in history yet, keep waiting
                await asyncio.sleep(poll_interval)
                continue

            # Check if complete
            if "outputs" in history:
                logger.info(f"ComfyUI prompt {prompt_id} completed")
                return history["outputs"]

            # Check for errors
            if "error" in history or history.get("status", {}).get("status_str") == "error":
                error_msg = history.get("error", "Unknown error")
                logger.error(f"ComfyUI execution failed: {error_msg}")
                raise RuntimeError(f"ComfyUI execution failed: {error_msg}")

            # Still running, wait and retry
            await asyncio.sleep(poll_interval)

    async def download_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """
        Download an image from ComfyUI

        Args:
            filename: Image filename
            subfolder: Subfolder path
            folder_type: Folder type (output, input, temp)

        Returns:
            Image bytes
        """
        try:
            params = {
                "filename": filename,
                "type": folder_type
            }
            if subfolder:
                params["subfolder"] = subfolder

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/view",
                    params=params
                )
                response.raise_for_status()

                logger.info(f"Downloaded image from ComfyUI: {filename}")
                return response.content
        except Exception as e:
            logger.error(f"Failed to download image from ComfyUI: {e}")
            raise

    def build_qwen_edit_workflow(
        self,
        input_image: str,
        prompt: str,
        negative_prompt: str = "blurry, low quality, distorted",
        seed: int = 0,
        steps: int = 50,
        cfg: float = 4.0,
        denoise: float = 0.85,
        output_prefix: str = "qwen_edit"
    ) -> Dict[str, Any]:
        """
        Build a Qwen-Image-Edit workflow (GGUF version)

        Args:
            input_image: Input image filename (must be uploaded first)
            prompt: Edit prompt
            negative_prompt: Negative prompt
            seed: Random seed (-1 for random)
            steps: Number of sampling steps
            cfg: CFG scale
            denoise: Denoise strength (0.0-1.0)
            output_prefix: Output filename prefix

        Returns:
            ComfyUI workflow dict
        """
        return {
            "1": {
                "inputs": {"unet_name": self.qwen_unet},
                "class_type": "UnetLoaderGGUF",
                "_meta": {"title": "Load Qwen Unet (GGUF)"}
            },
            "2": {
                "inputs": {
                    "clip_name1": self.qwen_clip,
                    "clip_name2": self.qwen_clip,
                    "type": "sdxl"
                },
                "class_type": "DualCLIPLoaderGGUF",
                "_meta": {"title": "Load Qwen Text Encoder (GGUF)"}
            },
            "3": {
                "inputs": {"vae_name": self.qwen_vae},
                "class_type": "VAELoader",
                "_meta": {"title": "Load VAE"}
            },
            "4": {
                "inputs": {
                    "image": input_image
                },
                "class_type": "LoadImage",
                "_meta": {"title": "Load Input Image"}
            },
            "5": {
                "inputs": {
                    "clip": ["2", 0],
                    "prompt": prompt,
                    "vae": ["3", 0],
                    "image": ["4", 0]
                },
                "class_type": "TextEncodeQwenImageEdit",
                "_meta": {"title": "Encode Positive Prompt (Qwen)"}
            },
            "6": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": denoise,
                    "model": ["1", 0],
                    "positive": ["5", 0],
                    "negative": ["7", 0],
                    "latent_image": ["8", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "Qwen Sampler"}
            },
            "7": {
                "inputs": {
                    "clip": ["2", 0],
                    "prompt": negative_prompt
                },
                "class_type": "TextEncodeQwenImageEdit",
                "_meta": {"title": "Encode Negative Prompt (Qwen)"}
            },
            "8": {
                "inputs": {
                    "pixels": ["4", 0],
                    "vae": ["3", 0]
                },
                "class_type": "VAEEncode",
                "_meta": {"title": "Encode Input Image"}
            },
            "9": {
                "inputs": {
                    "samples": ["6", 0],
                    "vae": ["3", 0]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "Decode Output"}
            },
            "10": {
                "inputs": {
                    "filename_prefix": output_prefix,
                    "images": ["9", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Edited Image"}
            }
        }

    async def edit_image_qwen(
        self,
        input_image_path: Path,
        prompt: str,
        output_dir: Path,
        negative_prompt: str = "blurry, low quality, distorted",
        seed: int = 0,
        steps: int = 50,
        cfg: float = 4.0,
        denoise: float = 0.85
    ) -> Dict[str, Any]:
        """
        Edit an image using Qwen-Image-Edit

        Args:
            input_image_path: Path to input image
            prompt: Edit instruction
            output_dir: Output directory
            negative_prompt: Negative prompt
            seed: Random seed
            steps: Sampling steps
            cfg: CFG scale
            denoise: Denoise strength

        Returns:
            Result dict with output_path and metadata
        """
        if not self.enabled:
            raise RuntimeError("ComfyUI is not enabled")

        try:
            # 1. Upload image
            logger.info(f"Uploading image to ComfyUI: {input_image_path}")
            upload_result = await self.upload_image(input_image_path)
            input_filename = upload_result["filename"]

            # 2. Build workflow
            workflow = self.build_qwen_edit_workflow(
                input_image=input_filename,
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                steps=steps,
                cfg=cfg,
                denoise=denoise,
                output_prefix=f"lifeos_qwen_{uuid.uuid4().hex[:8]}"
            )

            # 3. Queue prompt
            prompt_id = await self.queue_prompt(workflow)
            logger.info(f"Queued Qwen-Image-Edit workflow: {prompt_id}")

            # 4. Wait for completion
            outputs = await self.wait_for_completion(prompt_id)

            # 5. Download result
            # Extract output filename from outputs
            save_node_outputs = outputs.get("10", {})  # Node 10 is SaveImage
            images = save_node_outputs.get("images", [])

            if not images:
                raise RuntimeError("No output images generated")

            output_image = images[0]
            output_filename = output_image["filename"]
            output_subfolder = output_image.get("subfolder", "")

            # Download image
            logger.info(f"Downloading result: {output_filename}")
            image_bytes = await self.download_image(
                filename=output_filename,
                subfolder=output_subfolder,
                folder_type="output"
            )

            # Save to output directory
            output_path = output_dir / f"qwen_edit_{uuid.uuid4().hex[:8]}.png"
            output_path.write_bytes(image_bytes)

            logger.info(f"Qwen edit completed: {output_path}")

            return {
                "status": "success",
                "output_path": str(output_path),
                "prompt": prompt,
                "params": {
                    "steps": steps,
                    "cfg": cfg,
                    "denoise": denoise,
                    "seed": seed
                },
                "comfyui_prompt_id": prompt_id
            }

        except Exception as e:
            logger.error(f"Qwen image edit failed: {e}")
            raise


# Singleton instance
_comfyui_service = None

def get_comfyui_service() -> ComfyUIService:
    """Get ComfyUI service singleton"""
    global _comfyui_service
    if _comfyui_service is None:
        _comfyui_service = ComfyUIService()
    return _comfyui_service
