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

        # FP8/Safetensors model names (Workflow 1: image_qwen_image_edit_2509.json)
        self.qwen_unet_fp8 = "qwen_image_edit_2509_fp8_e4m3fn.safetensors"  # FP8 UNET
        self.qwen_clip_fp8 = "qwen_2.5_vl_7b_fp8_scaled.safetensors"  # Qwen CLIP (FP8)
        self.qwen_vae = "qwen_image_vae.safetensors"  # Shared VAE for both workflows
        self.qwen_lightning_lora_fp8 = "Qwen-Image-Edit-Lightning-4steps-V1.0.safetensors"  # 4-step Lightning LoRA (no 2509 suffix)

        # GGUF model names (Workflow 2: QWEN-IMAGE-EDIT-PLUS_ULTRA.json)
        self.qwen_unet_gguf = "Qwen-Image-Edit-2509-Q8_0.gguf"  # GGUF UNET (Q8 quantization)
        self.qwen_clip_gguf = "Qwen2.5-VL-7B-Instruct-UD-Q4_K_S.gguf"  # GGUF CLIP (Q4 quantization)

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
            logger.error(f"Failed to upload image to ComfyUI: {e}", exc_info=True)
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

        # DEBUG: Log the actual model filenames being sent
        logger.info(f"🔍 DEBUG - Workflow model files being sent to ComfyUI:")
        for node_id, node in workflow.items():
            if "inputs" in node:
                if "unet_name" in node["inputs"]:
                    logger.info(f"  Node {node_id} UNET: {node['inputs']['unet_name']}")
                if "clip_name" in node["inputs"]:
                    logger.info(f"  Node {node_id} CLIP: {node['inputs']['clip_name']}")
                if "vae_name" in node["inputs"]:
                    logger.info(f"  Node {node_id} VAE: {node['inputs']['vae_name']}")

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

            # Check for errors FIRST (before checking outputs)
            if "error" in history or history.get("status", {}).get("status_str") == "error":
                # Extract error details from status messages
                error_msg = history.get("error", "Unknown error")
                status_messages = history.get("status", {}).get("messages", [])

                # Look for execution_error message
                for msg in status_messages:
                    if msg[0] == "execution_error":
                        error_details = msg[1]
                        node_id = error_details.get("node_id")
                        node_type = error_details.get("node_type")
                        exception_msg = error_details.get("exception_message", "")
                        error_msg = f"Node {node_id} ({node_type}) failed: {exception_msg.strip()}"
                        break

                logger.error(f"ComfyUI execution failed: {error_msg}")
                logger.error(f"Full error history: {history}")
                raise RuntimeError(f"ComfyUI execution failed: {error_msg}")

            # Check if complete
            if "outputs" in history:
                logger.info(f"ComfyUI prompt {prompt_id} completed")
                logger.info(f"Full history for {prompt_id}: {history}")
                return history["outputs"]

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

    def build_sdxl_ipadapter_workflow(
        self,
        reference_image: str,
        prompt: str,
        negative_prompt: str = "blurry, low quality, distorted",
        width: int = 1024,
        height: int = 1024,
        seed: int = 0,
        steps: int = 20,
        cfg: float = 7.0,
        ipadapter_weight: float = 1.0,
        checkpoint_name: str = "sd_xl_base_1.0.safetensors",
        ipadapter_model: str = "ip-adapter_sdxl_vit-h.safetensors",
        output_prefix: str = "sdxl_ipadapter"
    ) -> Dict[str, Any]:
        """
        Build SDXL + IP-Adapter workflow for character-guided generation

        Args:
            reference_image: Reference image filename (uploaded to ComfyUI)
            prompt: Generation prompt
            negative_prompt: Negative prompt
            width: Image width
            height: Image height
            seed: Random seed
            steps: Sampling steps
            cfg: CFG scale
            ipadapter_weight: IP-Adapter strength (0.0-1.0)
            checkpoint_name: SDXL checkpoint
            ipadapter_model: IP-Adapter model filename
            output_prefix: Output filename prefix

        Returns:
            ComfyUI workflow dict
        """
        return {
            "1": {
                "inputs": {"ckpt_name": checkpoint_name},
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Load Checkpoint"}
            },
            "2": {
                "inputs": {"image": reference_image},
                "class_type": "LoadImage",
                "_meta": {"title": "Load Reference Image"}
            },
            "3": {
                "inputs": {"ipadapter_file": ipadapter_model},
                "class_type": "IPAdapterModelLoader",
                "_meta": {"title": "Load IP-Adapter Model"}
            },
            "4": {
                "inputs": {"clip_name": "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"},
                "class_type": "CLIPVisionLoader",
                "_meta": {"title": "Load CLIP Vision"}
            },
            "5": {
                "inputs": {
                    "weight": ipadapter_weight,
                    "weight_type": "linear",
                    "combine_embeds": "concat",
                    "start_at": 0.0,
                    "end_at": 1.0,
                    "embeds_scaling": "V only",
                    "image": ["2", 0],
                    "model": ["1", 0],
                    "ipadapter": ["3", 0],
                    "clip_vision": ["4", 0]
                },
                "class_type": "IPAdapterAdvanced",
                "_meta": {"title": "Apply IP-Adapter"}
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Positive Prompt"}
            },
            "7": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Negative Prompt"}
            },
            "8": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Empty Latent"}
            },
            "9": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["5", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["8", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "Sampler"}
            },
            "10": {
                "inputs": {
                    "samples": ["9", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"}
            },
            "11": {
                "inputs": {
                    "filename_prefix": output_prefix,
                    "images": ["10", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            }
        }

    def build_sdxl_text2img_workflow(
        self,
        prompt: str,
        negative_prompt: str = "blurry, low quality, distorted",
        width: int = 1024,
        height: int = 1024,
        seed: int = 0,
        steps: int = 20,
        cfg: float = 7.0,
        checkpoint_name: str = "sd_xl_base_1.0.safetensors",
        output_prefix: str = "sdxl_gen"
    ) -> Dict[str, Any]:
        """
        Build a simple SDXL text-to-image workflow (using standard checkpoint)

        Args:
            prompt: Generation prompt
            negative_prompt: Negative prompt
            width: Image width (default 1024)
            height: Image height (default 1024)
            seed: Random seed
            steps: Number of sampling steps
            cfg: CFG scale
            checkpoint_name: SDXL checkpoint filename
            output_prefix: Output filename prefix

        Returns:
            ComfyUI workflow dict
        """
        return {
            "1": {
                "inputs": {"ckpt_name": checkpoint_name},
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Load Checkpoint"}
            },
            "2": {
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Positive Prompt"}
            },
            "3": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Negative Prompt"}
            },
            "4": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Empty Latent"}
            },
            "5": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "Sampler"}
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"}
            },
            "7": {
                "inputs": {
                    "filename_prefix": output_prefix,
                    "images": ["6", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            }
        }

    def build_qwen_edit_workflow(
        self,
        input_image: str,
        prompt: str,
        negative_prompt: str = "",
        seed: int = 0,
        steps: int = 4,
        cfg: float = 1.0,
        denoise: float = 1.0,
        output_prefix: str = "qwen_edit"
    ) -> Dict[str, Any]:
        """
        Build a Qwen-Image-Edit workflow (FP8/Safetensors + Lightning LoRA)

        Uses Workflow 1: image_qwen_image_edit_2509.json
        - FP8 models with standard ComfyUI loaders
        - 4-step Lightning LoRA for fast generation
        - Separate VAE loader (qwen_image_vae.safetensors)

        Args:
            input_image: Input image filename (must be uploaded first)
            prompt: Edit prompt
            negative_prompt: Negative prompt (usually empty for Qwen)
            seed: Random seed
            steps: Number of sampling steps (4 with Lightning LoRA, 20 without)
            cfg: CFG scale (1.0 with Lightning LoRA, 2.5 without)
            denoise: Denoise strength (1.0 = full denoise)
            output_prefix: Output filename prefix

        Returns:
            ComfyUI workflow dict
        """
        return {
            "1": {
                "inputs": {
                    "unet_name": self.qwen_unet_fp8,
                    "weight_dtype": "default"
                },
                "class_type": "UNETLoader",
                "_meta": {"title": "Load Qwen UNET (FP8)"}
            },
            "2": {
                "inputs": {
                    "clip_name": self.qwen_clip_fp8,
                    "type": "qwen_image"
                },
                "class_type": "CLIPLoader",
                "_meta": {"title": "Load Qwen CLIP (FP8)"}
            },
            "3": {
                "inputs": {"vae_name": self.qwen_vae},
                "class_type": "VAELoader",
                "_meta": {"title": "Load Qwen VAE"}
            },
            "4": {
                "inputs": {"image": input_image},
                "class_type": "LoadImage",
                "_meta": {"title": "Load Input Image"}
            },
            "5": {
                "inputs": {
                    "model": ["1", 0],
                    "lora_name": self.qwen_lightning_lora_fp8,
                    "strength_model": 1.0
                },
                "class_type": "LoraLoaderModelOnly",
                "_meta": {"title": "Load Lightning LoRA (4-step)"}
            },
            "6": {
                "inputs": {
                    "model": ["5", 0],
                    "shift": 3.0
                },
                "class_type": "ModelSamplingAuraFlow",
                "_meta": {"title": "Model Sampling AuraFlow"}
            },
            "7": {
                "inputs": {
                    "model": ["6", 0],
                    "strength": 1.0
                },
                "class_type": "CFGNorm",
                "_meta": {"title": "CFG Normalization"}
            },
            "8": {
                "inputs": {
                    "pixels": ["14", 0],  # Use scaled image
                    "vae": ["3", 0]
                },
                "class_type": "VAEEncode",
                "_meta": {"title": "Encode Input Image"}
            },
            "9": {
                "inputs": {
                    "clip": ["2", 0],
                    "vae": ["3", 0],
                    "image1": ["14", 0],  # Use scaled image
                    "prompt": prompt
                },
                "class_type": "TextEncodeQwenImageEditPlus",
                "_meta": {"title": "Encode Positive Prompt"}
            },
            "10": {
                "inputs": {
                    "clip": ["2", 0],
                    "vae": ["3", 0],
                    "image1": ["14", 0],  # Use scaled image
                    "prompt": negative_prompt
                },
                "class_type": "TextEncodeQwenImageEditPlus",
                "_meta": {"title": "Encode Negative Prompt"}
            },
            "14": {
                "inputs": {
                    "image": ["4", 0],  # Raw loaded image
                    "upscale_method": "lanczos",
                    "megapixels": 1.0
                },
                "class_type": "ImageScaleToTotalPixels",
                "_meta": {"title": "Scale Image to 1MP"}
            },
            "11": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": denoise,
                    "model": ["7", 0],
                    "positive": ["9", 0],
                    "negative": ["10", 0],
                    "latent_image": ["8", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "Sampler"}
            },
            "12": {
                "inputs": {
                    "samples": ["11", 0],
                    "vae": ["3", 0]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"}
            },
            "13": {
                "inputs": {
                    "filename_prefix": output_prefix,
                    "images": ["12", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            }
        }

    def build_qwen_edit_workflow_gguf(
        self,
        input_image: str,
        prompt: str,
        negative_prompt: str = "",
        seed: int = 0,
        steps: int = 4,
        cfg: float = 1.0,
        denoise: float = 1.0,
        output_prefix: str = "qwen_edit_gguf"
    ) -> Dict[str, Any]:
        """
        Build a Qwen-Image-Edit workflow (GGUF quantized version)

        Uses Workflow 2: QWEN-IMAGE-EDIT-PLUS_ULTRA.json
        - GGUF quantized models (Q8 UNET, Q4 CLIP)
        - Uses ComfyUI-GGUF plugin loaders
        - Smaller model sizes, slightly lower quality than FP8
        - Separate VAE loader (qwen_image_vae.safetensors)

        Args:
            input_image: Input image filename (must be uploaded first)
            prompt: Edit prompt
            negative_prompt: Negative prompt (usually empty for Qwen)
            seed: Random seed
            steps: Number of sampling steps
            cfg: CFG scale
            denoise: Denoise strength (1.0 = full denoise)
            output_prefix: Output filename prefix

        Returns:
            ComfyUI workflow dict
        """
        return {
            "1": {
                "inputs": {"unet_name": self.qwen_unet_gguf},
                "class_type": "UnetLoaderGGUF",
                "_meta": {"title": "Load Qwen UNET (GGUF Q8)"}
            },
            "2": {
                "inputs": {
                    "clip_name": self.qwen_clip_gguf,
                    "type": "qwen_image"
                },
                "class_type": "CLIPLoaderGGUF",
                "_meta": {"title": "Load Qwen CLIP (GGUF Q4)"}
            },
            "3": {
                "inputs": {"vae_name": self.qwen_vae},
                "class_type": "VAELoader",
                "_meta": {"title": "Load Qwen VAE"}
            },
            "4": {
                "inputs": {"image": input_image},
                "class_type": "LoadImage",
                "_meta": {"title": "Load Input Image"}
            },
            "5": {
                "inputs": {
                    "model": ["1", 0],
                    "shift": 3.0
                },
                "class_type": "ModelSamplingAuraFlow",
                "_meta": {"title": "Model Sampling AuraFlow"}
            },
            "6": {
                "inputs": {
                    "model": ["5", 0],
                    "strength": 1.0
                },
                "class_type": "CFGNorm",
                "_meta": {"title": "CFG Normalization"}
            },
            "7": {
                "inputs": {
                    "pixels": ["13", 0],  # Use scaled image
                    "vae": ["3", 0]
                },
                "class_type": "VAEEncode",
                "_meta": {"title": "Encode Input Image"}
            },
            "8": {
                "inputs": {
                    "clip": ["2", 0],
                    "vae": ["3", 0],
                    "image1": ["13", 0],  # Use scaled image
                    "prompt": prompt
                },
                "class_type": "TextEncodeQwenImageEditPlus",
                "_meta": {"title": "Encode Positive Prompt"}
            },
            "9": {
                "inputs": {
                    "clip": ["2", 0],
                    "vae": ["3", 0],
                    "image1": ["13", 0],  # Use scaled image
                    "prompt": negative_prompt
                },
                "class_type": "TextEncodeQwenImageEditPlus",
                "_meta": {"title": "Encode Negative Prompt"}
            },
            "13": {
                "inputs": {
                    "image": ["4", 0],  # Raw loaded image
                    "upscale_method": "lanczos",
                    "megapixels": 1.0
                },
                "class_type": "ImageScaleToTotalPixels",
                "_meta": {"title": "Scale Image to 1MP"}
            },
            "10": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": denoise,
                    "model": ["6", 0],
                    "positive": ["8", 0],
                    "negative": ["9", 0],
                    "latent_image": ["7", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "Sampler"}
            },
            "11": {
                "inputs": {
                    "samples": ["10", 0],
                    "vae": ["3", 0]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"}
            },
            "12": {
                "inputs": {
                    "filename_prefix": output_prefix,
                    "images": ["11", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            }
        }

    async def generate_image_sdxl(
        self,
        prompt: str,
        output_dir: Path,
        negative_prompt: str = "blurry, low quality, distorted",
        width: int = 1024,
        height: int = 1024,
        seed: int = 0,
        steps: int = 20,
        cfg: float = 7.0,
        checkpoint_name: str = "sd_xl_base_1.0.safetensors"
    ) -> Dict[str, Any]:
        """
        Generate an image from text using SDXL

        Args:
            prompt: Generation prompt
            output_dir: Output directory
            negative_prompt: Negative prompt
            width: Image width
            height: Image height
            seed: Random seed
            steps: Sampling steps
            cfg: CFG scale
            checkpoint_name: SDXL checkpoint to use

        Returns:
            Result dict with output_path and metadata
        """
        if not self.enabled:
            raise RuntimeError("ComfyUI is not enabled")

        try:
            # 1. Build workflow
            workflow = self.build_sdxl_text2img_workflow(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                seed=seed,
                steps=steps,
                cfg=cfg,
                checkpoint_name=checkpoint_name,
                output_prefix=f"lifeos_sdxl_{uuid.uuid4().hex[:8]}"
            )

            # 2. Queue prompt
            prompt_id = await self.queue_prompt(workflow)
            logger.info(f"Queued SDXL text-to-image workflow: {prompt_id}")

            # 3. Wait for completion
            outputs = await self.wait_for_completion(prompt_id)

            # 4. Download result
            # Extract output filename from outputs (node 7 is SaveImage)
            logger.info(f"Raw ComfyUI outputs: {outputs}")
            save_node_outputs = outputs.get("7", {})
            logger.info(f"Node 7 outputs: {save_node_outputs}")
            images = save_node_outputs.get("images", [])

            if not images:
                logger.error(f"No images in output. Full outputs structure: {outputs}")
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
            output_path = output_dir / f"sdxl_gen_{uuid.uuid4().hex[:8]}.png"
            output_path.write_bytes(image_bytes)

            logger.info(f"SDXL generation completed: {output_path}")

            return {
                "status": "success",
                "output_path": str(output_path),
                "prompt": prompt,
                "params": {
                    "width": width,
                    "height": height,
                    "steps": steps,
                    "cfg": cfg,
                    "seed": seed,
                    "checkpoint": checkpoint_name
                },
                "comfyui_prompt_id": prompt_id
            }

        except Exception as e:
            logger.error(f"SDXL generation failed: {e}")
            raise

    async def generate_with_ipadapter(
        self,
        reference_image_path: Path,
        prompt: str,
        output_dir: Path,
        negative_prompt: str = "blurry, low quality, distorted",
        width: int = 1024,
        height: int = 1024,
        seed: int = 0,
        steps: int = 20,
        cfg: float = 7.0,
        ipadapter_weight: float = 1.0,
        checkpoint_name: str = "sd_xl_base_1.0.safetensors"
    ) -> Dict[str, Any]:
        """
        Generate image using SDXL + IP-Adapter with reference character image

        Args:
            reference_image_path: Path to reference character image
            prompt: Generation prompt
            output_dir: Output directory
            negative_prompt: Negative prompt
            width: Image width
            height: Image height
            seed: Random seed
            steps: Sampling steps
            cfg: CFG scale
            ipadapter_weight: IP-Adapter strength
            checkpoint_name: SDXL checkpoint

        Returns:
            Result dict with output_path and metadata
        """
        if not self.enabled:
            raise RuntimeError("ComfyUI is not enabled")

        try:
            # 1. Upload reference image
            logger.info(f"Uploading reference image to ComfyUI: {reference_image_path}")
            upload_result = await self.upload_image(reference_image_path)
            reference_filename = upload_result["filename"]

            # 2. Build workflow
            workflow = self.build_sdxl_ipadapter_workflow(
                reference_image=reference_filename,
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                seed=seed,
                steps=steps,
                cfg=cfg,
                ipadapter_weight=ipadapter_weight,
                checkpoint_name=checkpoint_name,
                output_prefix=f"lifeos_ipadapter_{uuid.uuid4().hex[:8]}"
            )

            # 3. Queue prompt
            prompt_id = await self.queue_prompt(workflow)
            logger.info(f"Queued SDXL + IP-Adapter workflow: {prompt_id}")

            # 4. Wait for completion
            outputs = await self.wait_for_completion(prompt_id)

            # 5. Download result (node 11 is SaveImage)
            logger.info(f"Raw ComfyUI outputs: {outputs}")
            save_node_outputs = outputs.get("11", {})
            logger.info(f"Node 11 outputs: {save_node_outputs}")
            images = save_node_outputs.get("images", [])

            if not images:
                logger.error(f"No images in output. Full outputs structure: {outputs}")
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
            output_path = output_dir / f"ipadapter_{uuid.uuid4().hex[:8]}.png"
            output_path.write_bytes(image_bytes)

            logger.info(f"IP-Adapter generation completed: {output_path}")

            return {
                "status": "success",
                "output_path": str(output_path),
                "prompt": prompt,
                "params": {
                    "width": width,
                    "height": height,
                    "steps": steps,
                    "cfg": cfg,
                    "seed": seed,
                    "ipadapter_weight": ipadapter_weight,
                    "checkpoint": checkpoint_name
                },
                "comfyui_prompt_id": prompt_id
            }

        except Exception as e:
            logger.error(f"IP-Adapter generation failed: {e}")
            raise

    async def edit_image_qwen(
        self,
        input_image_path: Path,
        prompt: str,
        output_dir: Path,
        negative_prompt: str = "",
        seed: int = 0,
        steps: int = 4,
        cfg: float = 1.0,
        denoise: float = 1.0
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
            logger.info(f"Raw ComfyUI outputs (Qwen): {outputs}")
            save_node_outputs = outputs.get("13", {})  # Node 13 is SaveImage
            logger.info(f"Node 13 outputs: {save_node_outputs}")
            images = save_node_outputs.get("images", [])

            if not images:
                logger.error(f"No images in output (Qwen). Full outputs structure: {outputs}")
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

    async def edit_image_qwen_gguf(
        self,
        input_image_path: Path,
        prompt: str,
        output_dir: Path,
        negative_prompt: str = "",
        seed: int = 0,
        steps: int = 4,
        cfg: float = 1.0,
        denoise: float = 1.0
    ) -> Dict[str, Any]:
        """
        Edit an image using Qwen-Image-Edit (GGUF quantized models)

        Uses GGUF workflow with ComfyUI-GGUF plugin for smaller model sizes

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
            logger.info(f"Uploading image to ComfyUI (GGUF workflow): {input_image_path}")
            upload_result = await self.upload_image(input_image_path)
            input_filename = upload_result["filename"]

            # 2. Build GGUF workflow
            workflow = self.build_qwen_edit_workflow_gguf(
                input_image=input_filename,
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                steps=steps,
                cfg=cfg,
                denoise=denoise,
                output_prefix=f"lifeos_qwen_gguf_{uuid.uuid4().hex[:8]}"
            )

            # 3. Queue prompt
            prompt_id = await self.queue_prompt(workflow)
            logger.info(f"Queued Qwen-Image-Edit GGUF workflow: {prompt_id}")

            # 4. Wait for completion
            outputs = await self.wait_for_completion(prompt_id)

            # 5. Download result
            # Extract output filename from outputs (Node 12 is SaveImage in GGUF workflow)
            logger.info(f"Raw ComfyUI outputs (Qwen GGUF): {outputs}")
            save_node_outputs = outputs.get("12", {})  # Node 12 is SaveImage
            logger.info(f"Node 12 outputs: {save_node_outputs}")
            images = save_node_outputs.get("images", [])

            if not images:
                logger.error(f"No images in output (Qwen GGUF). Full outputs structure: {outputs}")
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
            output_path = output_dir / f"qwen_edit_gguf_{uuid.uuid4().hex[:8]}.png"
            output_path.write_bytes(image_bytes)

            logger.info(f"Qwen edit (GGUF) completed: {output_path}")

            return {
                "status": "success",
                "output_path": str(output_path),
                "prompt": prompt,
                "workflow": "gguf",
                "params": {
                    "steps": steps,
                    "cfg": cfg,
                    "denoise": denoise,
                    "seed": seed,
                    "models": {
                        "unet": self.qwen_unet_gguf,
                        "clip": self.qwen_clip_gguf,
                        "vae": self.qwen_vae
                    }
                },
                "comfyui_prompt_id": prompt_id
            }

        except Exception as e:
            logger.error(f"Qwen image edit (GGUF) failed: {e}")
            raise


# Singleton instance
_comfyui_service = None

def get_comfyui_service() -> ComfyUIService:
    """Get ComfyUI service singleton"""
    global _comfyui_service
    if _comfyui_service is None:
        _comfyui_service = ComfyUIService()
    return _comfyui_service
