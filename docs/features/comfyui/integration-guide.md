# ComfyUI Integration Guide

**Last Updated**: 2025-10-24
**Status**: Ready for Implementation

---

## Quick Start

ComfyUI is a node-based Stable Diffusion workflow system that runs as a headless API service. This guide covers integration with Life-OS FastAPI backend using an RTX 4090-equipped machine.

### TL;DR - Recommended Approach

```
Life-OS FastAPI Backend
    ↓ HTTP/WebSocket
ComfyUI Native API (RTX 4090)
    ↓ GPU Execution
Generated Images
```

**Timeline**: 2-3 weeks for full integration

---

## Integration Approaches

### 1. Native ComfyUI API ⭐ RECOMMENDED

**Use built-in REST/WebSocket endpoints directly**

**Pros**:
- No dependencies, full control
- Active development
- Well-documented

**Cons**:
- Manual WebSocket handling
- No built-in authentication

### 2. Python Client Libraries

**Use wrapper like `comfyuiclient`**

**Pros**:
- Simplified API
- Less boilerplate

**Cons**:
- Extra dependency
- May lag behind updates

### 3. Hybrid (Native + FastAPI Wrapper) ⭐ BEST FOR LIFE-OS

**Combine native API with custom wrapper**

**Provides**:
- Full control
- Authentication (JWT)
- Job queue integration
- Workflow template management

---

## Core ComfyUI API

ComfyUI runs on **port 8188** by default.

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ws?clientId={id}` | WebSocket | Real-time progress updates |
| `/prompt` | POST | Queue workflow (returns prompt_id) |
| `/queue` | GET | View queue status |
| `/history/{prompt_id}` | GET | Retrieve results |
| `/view?filename={}` | GET | Download images |
| `/upload/image` | POST | Upload reference images |
| `/system_stats` | GET | GPU stats |

### Workflow Execution Flow

```python
import uuid, json, websocket, urllib.request

# 1. Connect to WebSocket
client_id = str(uuid.uuid4())
ws = websocket.WebSocket()
ws.connect(f"ws://{server}:8188/ws?clientId={client_id}")

# 2. Queue workflow
payload = {"prompt": workflow_json, "client_id": client_id}
response = urllib.request.urlopen(
    urllib.request.Request(
        f"http://{server}:8188/prompt",
        data=json.dumps(payload).encode('utf-8')
    )
).read()
prompt_id = json.loads(response)['prompt_id']

# 3. Listen for completion
while True:
    msg = json.loads(ws.recv())
    if msg['type'] == 'executing':
        if msg['data']['node'] is None and msg['data']['prompt_id'] == prompt_id:
            break  # Done

# 4. Retrieve images
history = json.loads(
    urllib.request.urlopen(f"http://{server}:8188/history/{prompt_id}").read()
)[prompt_id]
```

---

## Workflow JSON Structure

ComfyUI uses **API Format JSON** (not UI format).

### Exporting Workflow

1. Enable Dev Mode in ComfyUI settings
2. Click "Save (API Format)"
3. Save as `workflow_api.json`

### Example Structure

```json
{
  "3": {
    "inputs": {
      "seed": 123456,
      "steps": 20,
      "cfg": 7.0,
      "sampler_name": "euler",
      "model": ["4", 0],
      "positive": ["6", 0]
    },
    "class_type": "KSampler"
  },
  "4": {
    "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
    "class_type": "CheckpointLoaderSimple"
  },
  "6": {
    "inputs": {
      "text": "A beautiful sunset",
      "clip": ["4", 1]
    },
    "class_type": "CLIPTextEncode"
  }
}
```

### Modify Programmatically

```python
# Load template
with open('workflow_api.json', 'r') as f:
    workflow = json.load(f)

# Modify parameters
workflow["3"]["inputs"]["seed"] = random.randint(0, 2**32)
workflow["6"]["inputs"]["text"] = user_prompt
workflow["4"]["inputs"]["ckpt_name"] = selected_model
```

---

## Life-OS FastAPI Integration

### Service Layer

```python
# api/services/comfyui_service.py
import json, uuid, asyncio, aiohttp, websockets
from pathlib import Path

class ComfyUIService:
    def __init__(self, server_url: str = "http://192.168.1.100:8188"):
        self.server_url = server_url
        self.ws_url = server_url.replace("http", "ws")

    async def generate_image(
        self,
        prompt: str,
        model: str = "sd_xl_base_1.0.safetensors",
        steps: int = 20,
        seed: int = None
    ) -> dict:
        # Load workflow template
        workflow = self._load_template("text_to_image_sdxl")

        # Modify parameters
        workflow["3"]["inputs"]["seed"] = seed or random.randint(0, 2**32)
        workflow["6"]["inputs"]["text"] = prompt

        # Queue and wait
        prompt_id = await self._queue_workflow(workflow)
        await self._wait_for_completion(prompt_id)
        images = await self._get_images(prompt_id)

        return {"prompt_id": prompt_id, "images": images}
```

### API Route

```python
# api/routes/comfyui.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/comfyui")

class GenerateRequest(BaseModel):
    prompt: str
    model: str = "sd_xl_base_1.0.safetensors"
    steps: int = 20

@router.post("/generate")
async def generate_image(request: GenerateRequest):
    result = await comfyui_service.generate_image(
        prompt=request.prompt,
        model=request.model,
        steps=request.steps
    )
    return {"status": "completed", "images": result["images"]}
```

---

## Network Setup

### Option A: Local LAN (Simplest)
- ComfyUI PC: Static IP `192.168.1.100`
- Lowest latency
- No internet exposure

### Option B: Tailscale VPN ⭐ RECOMMENDED
```bash
# Install on both machines
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# ComfyUI now at 100.x.x.x (Tailscale IP)
# Encrypted, works from anywhere
```

### Option C: Cloudflare Tunnel
- Public access with authentication
- Adds latency

---

## Security (CRITICAL)

ComfyUI has **NO built-in authentication**. Choose a security layer:

### Tailscale VPN (Easiest)
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Encrypted tunnel, no internet exposure
```

### Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl;
    server_name comfyui.local;

    auth_basic "ComfyUI";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://127.0.0.1:8188;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Firewall Rules
```bash
# LAN only
sudo ufw allow from 192.168.1.0/24 to any port 8188

# Or Tailscale IPs
sudo ufw allow from 100.64.0.0/10 to any port 8188
```

---

## Model Management

### Required Models for SDXL

```
ComfyUI/models/
├── checkpoints/
│   └── sd_xl_base_1.0.safetensors (6GB)
├── vae/
│   └── sdxl_vae.safetensors (335MB)
└── clip_vision/ (auto-downloaded)
```

### Download Command

```bash
cd ComfyUI/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

### Auto-Download via Metadata

Add to workflow JSON:
```json
{
  "4": {
    "properties": {
      "models": [{
        "name": "sd_xl_base_1.0.safetensors",
        "url": "https://huggingface.co/...",
        "hash": "...",
        "directory": "checkpoints"
      }]
    }
  }
}
```

---

## Implementation Roadmap

### Phase 1: Local Setup (1-2 days)
- Install ComfyUI on RTX 4090 PC (Docker recommended)
- Download base models
- Test native API with Python
- Export workflow as JSON

### Phase 2: Network Setup (1 day)
- Configure Tailscale VPN or static IP
- Test connectivity from Life-OS
- Set up file sharing for images

### Phase 3: FastAPI Integration (2-3 days)
- Create `ComfyUIService`
- Add API routes
- Integrate with job queue

### Phase 4: Workflow Templates (2-3 days)
- Build template library
- Parameter system
- Frontend template selector

### Phase 5: Model Management (2 days)
- Model metadata database
- Auto-downloader
- Frontend model browser

### Phase 6: Production Hardening (2-3 days)
- Docker deployment
- SSL + authentication
- Monitoring + logging

### Phase 7: Advanced Features (Ongoing)
- Custom nodes
- Batch workflows
- Fine-tuning pipeline

**Total**: 2-3 weeks for full integration

---

## Performance Benchmarks (RTX 4090)

| Task | Model | Resolution | Time |
|------|-------|------------|------|
| Text-to-Image | SDXL Base | 1024x1024 | 3-5s (20 steps) |
| Text-to-Image | SD 1.5 | 512x512 | 1-2s (20 steps) |
| ControlNet | SDXL + ControlNet | 1024x1024 | 5-8s (20 steps) |
| Batch (4) | SDXL Base | 1024x1024 | 10-15s (20 steps) |

**Throughput**: ~10-20 images/minute

---

## Common Issues

### File Not Found
**Solution**: Use absolute paths, verify model files exist

### WebSocket Drops
**Solution**: Reconnection logic, heartbeat pings

### GPU Out of Memory
**Solution**: Reduce batch size, use smaller models, enable CPU offload

### Slow Generation
**Solution**: Use xFormers, enable fp16, reduce steps

### No Images Returned
**Solution**: Check SaveImage node exists, verify output directory permissions

---

## Resources

### Official
- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI Docs](https://docs.comfy.org)
- [Workflow JSON Spec](https://docs.comfy.org/specs/workflow_json)

### Python Clients
- [comfyuiclient](https://github.com/sugarkwork/Comfyui_api_client)
- [comfyui-python-api](https://github.com/andreyryabtsev/comfyui-python-api)

### Docker
- [yanwk/comfyui-boot](https://hub.docker.com/r/yanwk/comfyui-boot)
- [ai-dock/comfyui](https://github.com/ai-dock/comfyui)

### Tutorials
- [ComfyUI API Complete Guide](https://learncodecamp.net/comfyui-api-endpoints-complete-guide/)
- [Building Production ComfyUI API](https://www.viewcomfy.com/blog/building-a-production-ready-comfyui-api)

---

## Next Steps

1. Install ComfyUI on RTX 4090 PC (see `rtx-4090-setup.md`)
2. Test native API with Python script
3. Set up network access (Tailscale recommended)
4. Create `ComfyUIService` in Life-OS backend
5. Build first workflow template
6. Test end-to-end from frontend

---

**See also**: `rtx-4090-setup.md` for detailed hardware setup instructions
