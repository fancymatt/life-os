# ComfyUI Integration Summary

**Quick Reference for Life-OS ComfyUI Integration**

---

## TL;DR - Recommended Approach

**Use ComfyUI Native API + Custom FastAPI Wrapper**

```
Life-OS FastAPI Backend (Mac)
    ↓ HTTP/WebSocket over Tailscale VPN
ComfyUI Native API (RTX 4090 PC)
    ↓ GPU Execution
Generated Images → HTTP Download or NFS Share
```

**Timeline**: 2-3 weeks for full integration (7 phases)

---

## 5 Viable Approaches (Ranked)

### 1. Native ComfyUI API ⭐ RECOMMENDED
- **How**: Use built-in REST/WebSocket endpoints directly
- **Pros**: No dependencies, full control, active development
- **Cons**: Manual WebSocket handling, no auth
- **Best For**: Production deployments

### 2. Python Client Libraries (comfyuiclient)
- **How**: Use `pip install comfyuiclient` wrapper
- **Pros**: Simplified API, less boilerplate
- **Cons**: Extra dependency, may lag behind updates
- **Best For**: Rapid prototyping

### 3. Custom FastAPI Wrapper (alexisrolland/ComfyUI-FastAPI)
- **How**: Build thin REST layer on top of ComfyUI
- **Pros**: RESTful design, auth/validation built-in
- **Cons**: Extra service to maintain
- **Best For**: When you need custom API design

### 4. Managed Services (RunComfy, Modal, BentoML)
- **How**: Use cloud-hosted ComfyUI with API
- **Pros**: Zero infrastructure, auto-scaling
- **Cons**: Vendor lock-in, can't use your RTX 4090
- **Best For**: Cloud-first without local GPU

### 5. Hybrid (Native API + FastAPI Wrapper) ⭐ BEST
- **How**: Combine #1 + #3 (native API + custom wrapper)
- **Pros**: Full control + authentication + job queue integration
- **Cons**: Most code to write
- **Best For**: Life-OS production deployment

---

## Quick Start (15 Minutes)

### Step 1: Install ComfyUI on RTX 4090 PC

```bash
# Clone repository
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install -r requirements.txt

# Download SDXL model
cd models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

# Start server (accessible on network)
cd ../..
python main.py --listen 0.0.0.0 --port 8188
```

### Step 2: Test Native API

```python
# test_comfyui.py
import requests
import json

SERVER = "http://192.168.1.100:8188"

# Load workflow (export from ComfyUI UI as "API Format")
with open('workflow_api.json', 'r') as f:
    workflow = json.load(f)

# Queue workflow
response = requests.post(f"{SERVER}/prompt", json={
    "prompt": workflow,
    "client_id": "test-client"
})

prompt_id = response.json()['prompt_id']
print(f"Queued: {prompt_id}")

# Check history after completion
history = requests.get(f"{SERVER}/history/{prompt_id}").json()
print(history)
```

### Step 3: Verify GPU Usage

```bash
# Inside ComfyUI terminal, watch GPU activity
watch -n 1 nvidia-smi
```

---

## Example Workflow JSON Structure

```json
{
  "3": {
    "inputs": {
      "seed": 123456,
      "steps": 20,
      "cfg": 7.0,
      "sampler_name": "euler",
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0]
    },
    "class_type": "KSampler"
  },
  "4": {
    "inputs": {
      "ckpt_name": "sd_xl_base_1.0.safetensors"
    },
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

**To modify programmatically**:
```python
workflow["3"]["inputs"]["seed"] = random.randint(0, 2**32)
workflow["6"]["inputs"]["text"] = user_prompt
```

---

## Production Deployment (Docker Compose)

```yaml
# docker-compose.yml on RTX 4090 PC
version: '3.8'
services:
  comfyui:
    image: yanwk/comfyui-boot:latest
    runtime: nvidia
    ports:
      - "8188:8188"
    volumes:
      - ./models:/app/ComfyUI/models
      - ./output:/app/ComfyUI/output
      - ./workflows:/app/ComfyUI/user/default/workflows
    environment:
      - CLI_ARGS=--listen 0.0.0.0 --port 8188
    restart: unless-stopped
```

**Start**:
```bash
docker-compose up -d
docker logs -f comfyui
```

---

## Security Setup (CRITICAL)

ComfyUI has **NO built-in authentication**. Choose one:

### Option A: Tailscale VPN (Easiest, Most Secure)
```bash
# Install on both machines
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# ComfyUI now at 100.x.x.x (Tailscale IP)
# Encrypted, no internet exposure
```

### Option B: Cloudflare Tunnel (Public Access)
```bash
cloudflared tunnel create comfyui
cloudflared tunnel run comfyui
# Add Cloudflare Access policy for auth
```

### Option C: Nginx Reverse Proxy (LAN + SSL)
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

---

## Life-OS FastAPI Integration

### Service Layer

```python
# api/services/comfyui_service.py
class ComfyUIService:
    def __init__(self, server_url: str):
        self.server_url = server_url

    async def generate_image(self, prompt: str, **kwargs) -> dict:
        # Load workflow template
        workflow = self._load_template("text_to_image_sdxl")

        # Modify parameters
        workflow["6"]["inputs"]["text"] = prompt
        workflow["3"]["inputs"]["seed"] = kwargs.get("seed", random.randint(0, 2**32))

        # Queue and wait
        prompt_id = await self._queue_workflow(workflow)
        await self._wait_for_completion(prompt_id)

        # Retrieve images
        images = await self._get_images(prompt_id)
        return {"prompt_id": prompt_id, "images": images}
```

### API Route

```python
# api/routes/comfyui.py
@router.post("/api/comfyui/generate")
async def generate_image(request: GenerateRequest):
    result = await comfyui_service.generate_image(
        prompt=request.prompt,
        seed=request.seed,
        steps=request.steps
    )
    return {"status": "completed", "images": result["images"]}
```

---

## Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ws?clientId={id}` | WebSocket | Real-time progress updates |
| `/prompt` | POST | Queue workflow (returns prompt_id) |
| `/history/{prompt_id}` | GET | Get results |
| `/view?filename={}&type={}` | GET | Download image |
| `/upload/image` | POST | Upload reference images |
| `/queue` | GET | View queue status |
| `/system_stats` | GET | GPU/memory stats |

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

### Auto-Download via Workflow Metadata

```json
{
  "4": {
    "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
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

## Workflow Template System

### Create Template

1. Build workflow in ComfyUI UI
2. Export as "Save (API Format)" → `workflow_api.json`
3. Identify parameters to expose (prompts, seeds, models)
4. Create flattened parameter mapping

### Example Template with Parameters

```python
# comfyui_workflows/templates/text_to_image_sdxl.py
TEMPLATE = {
    "workflow": { /* full workflow JSON */ },
    "parameters": {
        "prompt": {
            "node_id": "6",
            "input_name": "text",
            "type": "string",
            "default": "A beautiful landscape"
        },
        "seed": {
            "node_id": "3",
            "input_name": "seed",
            "type": "integer",
            "default": -1  # -1 = random
        },
        "steps": {
            "node_id": "3",
            "input_name": "steps",
            "type": "integer",
            "min": 1,
            "max": 100,
            "default": 20
        }
    }
}
```

### Apply Parameters

```python
def apply_parameters(workflow, params):
    for param_name, param_value in params.items():
        config = TEMPLATE["parameters"][param_name]
        node_id = config["node_id"]
        input_name = config["input_name"]
        workflow[node_id]["inputs"][input_name] = param_value
    return workflow
```

---

## Common Issues & Solutions

### Issue: File Not Found Errors
**Solution**: Use absolute paths in workflows, verify model files exist

### Issue: WebSocket Connection Drops
**Solution**: Implement reconnection logic, use heartbeat pings

### Issue: GPU Out of Memory
**Solution**: Reduce batch size, use smaller models, enable CPU offload

### Issue: Slow Generation
**Solution**: Use xFormers attention, enable fp16, reduce steps

### Issue: No Images Returned
**Solution**: Check workflow has SaveImage node, verify output directory permissions

---

## Performance Benchmarks (RTX 4090)

| Task | Model | Resolution | Time |
|------|-------|------------|------|
| Text-to-Image | SDXL Base | 1024x1024 | 3-5s (20 steps) |
| Text-to-Image | SD 1.5 | 512x512 | 1-2s (20 steps) |
| ControlNet | SDXL + ControlNet | 1024x1024 | 5-8s (20 steps) |
| IP-Adapter | SDXL + IP-Adapter | 1024x1024 | 6-10s (20 steps) |
| Batch (4 images) | SDXL Base | 1024x1024 | 10-15s (20 steps) |

**Expected throughput**: ~10-20 images/minute for SDXL

---

## Implementation Roadmap

### Phase 1: Local Setup (1-2 days)
- Install ComfyUI on RTX 4090 PC
- Test native API with Python
- Export workflow as JSON

### Phase 2: Network Setup (1 day)
- Configure Tailscale VPN or static IP
- Test connectivity from Life-OS backend
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

**Total Timeline**: 2-3 weeks for full integration

---

## Resources

### Official
- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI Docs](https://docs.comfy.org)
- [Workflow JSON Spec](https://docs.comfy.org/specs/workflow_json)

### Community
- [ComfyUI Wiki](https://comfyui-wiki.com)
- [ComfyUI Examples](https://comfyanonymous.github.io/ComfyUI_examples/)
- [r/comfyui Subreddit](https://reddit.com/r/comfyui)

### Docker
- [yanwk/comfyui-boot](https://hub.docker.com/r/yanwk/comfyui-boot)
- [ai-dock/comfyui](https://github.com/ai-dock/comfyui)

### Python Clients
- [comfyuiclient](https://github.com/sugarkwork/Comfyui_api_client)
- [comfyui-python-api](https://github.com/andreyryabtsev/comfyui-python-api)

### Tutorials
- [ComfyUI API Complete Guide](https://learncodecamp.net/comfyui-api-endpoints-complete-guide/)
- [Building Production ComfyUI API](https://www.viewcomfy.com/blog/building-a-production-ready-comfyui-api)

---

## Next Steps

1. **Install ComfyUI** on RTX 4090 PC (use Docker for easiest setup)
2. **Test native API** with simple Python script
3. **Set up network** access (Tailscale recommended)
4. **Create `ComfyUIService`** in Life-OS backend
5. **Build first workflow template** (text-to-image SDXL)
6. **Test end-to-end** from Life-OS frontend

---

**See `COMFYUI_API_INTEGRATION_GUIDE.md` for detailed documentation.**
