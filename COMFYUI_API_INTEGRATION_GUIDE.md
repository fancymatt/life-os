# ComfyUI API Integration Guide for Life-OS

**Research Date**: 2025-10-24
**Focus**: Production-ready headless ComfyUI integration for FastAPI backend with RTX 4090 GPU

---

## Table of Contents

1. [Overview](#overview)
2. [Viable Integration Approaches](#viable-integration-approaches)
3. [Recommended Solution](#recommended-solution)
4. [ComfyUI Native API Architecture](#comfyui-native-api-architecture)
5. [Workflow JSON Structure](#workflow-json-structure)
6. [Python Client Libraries](#python-client-libraries)
7. [Network Architecture](#network-architecture)
8. [Docker Deployment for RTX 4090](#docker-deployment-for-rtx-4090)
9. [Model Management](#model-management)
10. [Security Considerations](#security-considerations)
11. [Production Implementation Roadmap](#production-implementation-roadmap)

---

## Overview

ComfyUI is a powerful node-based Stable Diffusion workflow system that can be run as a headless API service. This guide outlines how to integrate ComfyUI with the Life-OS FastAPI backend, with ComfyUI running on a separate RTX 4090-equipped machine.

### Key Capabilities

- **Headless Operation**: ComfyUI runs as a Python HTTP server without GUI
- **REST + WebSocket API**: Submit workflows via REST, get real-time updates via WebSocket
- **JSON Workflow Format**: Workflows defined as JSON (programmatically generated)
- **Network Deployment**: Run on remote GPU machine, access over LAN/WAN
- **Model Management**: Auto-download models from HuggingFace/Civitai

---

## Viable Integration Approaches

### Approach 1: Native ComfyUI API (Recommended)

**Description**: Use ComfyUI's built-in HTTP server with native REST/WebSocket endpoints.

**Pros**:
- No additional dependencies or wrappers
- Direct access to all ComfyUI features
- Well-documented API (official docs + community examples)
- Active development and community support
- Zero abstraction overhead

**Cons**:
- Requires manual WebSocket connection handling
- Must manage workflow JSON format manually
- No built-in authentication (needs reverse proxy)

**Best For**: Production deployments where you want full control and minimal dependencies.

---

### Approach 2: Python Client Libraries

**Description**: Use community-built Python wrappers that simplify ComfyUI API interactions.

**Available Libraries**:

1. **comfyuiclient** (sugarkwork/Comfyui_api_client)
   - Both sync and async support
   - Automatic workflow format conversion
   - Simple connection management

2. **comfyui-python-api** (andreyryabtsev)
   - Event-based callbacks for progress tracking
   - Queue position monitoring
   - Good for chatbots/Discord bots

3. **comfy_api_simplified** (deimos-deimos)
   - Lightweight wrapper over REST API
   - Easy parameter editing
   - Simple queuing

**Pros**:
- Simplified API interactions
- Built-in progress tracking
- Less boilerplate code

**Cons**:
- Additional dependency maintenance
- Potential lag behind ComfyUI updates
- May not expose all native features

**Best For**: Rapid prototyping or when you need simplified abstractions.

---

### Approach 3: Managed Services (BentoML, RunComfy, Modal)

**Description**: Use third-party platforms that host/manage ComfyUI with API access.

**Pros**:
- Zero infrastructure management
- Auto-scaling
- Built-in monitoring and logging
- Production-ready out of the box

**Cons**:
- Vendor lock-in
- Recurring costs (pay-per-use)
- Cannot use your own RTX 4090
- Less control over environment

**Best For**: Cloud-first deployments without local GPU resources.

---

### Approach 4: Custom FastAPI Wrapper

**Description**: Build a thin FastAPI layer on top of ComfyUI (alexisrolland/ComfyUI-FastAPI).

**Pros**:
- RESTful API design
- Familiar FastAPI patterns
- Easy integration with existing Life-OS backend
- Can add custom authentication/validation

**Cons**:
- Additional codebase to maintain
- Another service to deploy
- Adds latency between FastAPI → ComfyUI

**Best For**: When you need custom API design or want to hide ComfyUI complexity from clients.

---

## Recommended Solution

**Use Approach 1 (Native ComfyUI API) + Approach 4 (Custom FastAPI Wrapper)**

### Architecture:

```
Life-OS Frontend
    ↓ HTTP
Life-OS FastAPI Backend (Mac/Server)
    ↓ HTTP/WebSocket
ComfyUI Native API (RTX 4090 PC)
    ↓ GPU Execution
Generated Images → Network Share/S3
```

### Rationale:

1. **Native API**: Full control, no vendor lock-in, active community support
2. **FastAPI Wrapper**: Provides:
   - Authentication/authorization (JWT tokens)
   - Request validation (Pydantic models)
   - Job queue integration (Redis)
   - Error handling and retries
   - Image retrieval and storage
   - Workflow template management

3. **RTX 4090**: Maximum local performance, no cloud costs

---

## ComfyUI Native API Architecture

### Core Endpoints

ComfyUI runs on **port 8188** by default and exposes these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ws?clientId={id}` | WebSocket | Real-time status updates and execution progress |
| `/prompt` | POST | Queue workflow for execution (returns prompt_id) |
| `/queue` | GET | View current queue status |
| `/history/{prompt_id}` | GET | Retrieve execution results and outputs |
| `/view?filename={}&subfolder={}&type={}` | GET | Download generated images |
| `/upload/image` | POST | Upload images for workflows (img2img, ControlNet, etc.) |
| `/system_stats` | GET | System information and GPU stats |
| `/object_info` | GET | Available nodes and their parameters |

### Workflow Execution Flow

```python
import uuid
import json
import websocket
import urllib.request

# 1. Generate unique client ID
client_id = str(uuid.uuid4())

# 2. Connect to WebSocket for progress updates
ws = websocket.WebSocket()
ws.connect(f"ws://{server_address}:8188/ws?clientId={client_id}")

# 3. Queue the workflow
def queue_prompt(prompt_json):
    payload = {
        "prompt": prompt_json,
        "client_id": client_id
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}:8188/prompt", data=data)
    response = urllib.request.urlopen(req).read()
    return json.loads(response)

result = queue_prompt(workflow_json)
prompt_id = result['prompt_id']

# 4. Listen for WebSocket messages
while True:
    msg = json.loads(ws.recv())
    if msg['type'] == 'executing':
        data = msg['data']
        if data['node'] is None and data['prompt_id'] == prompt_id:
            break  # Execution finished

# 5. Retrieve results
def get_history(prompt_id):
    url = f"http://{server_address}:8188/history/{prompt_id}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())

history = get_history(prompt_id)[prompt_id]

# 6. Download generated images
def get_image(filename, subfolder, folder_type):
    params = urllib.parse.urlencode({
        "filename": filename,
        "subfolder": subfolder,
        "type": folder_type
    })
    url = f"http://{server_address}:8188/view?{params}"
    with urllib.request.urlopen(url) as response:
        return response.read()

for node_id in history['outputs']:
    node_output = history['outputs'][node_id]
    if 'images' in node_output:
        for image in node_output['images']:
            image_data = get_image(
                image['filename'],
                image['subfolder'],
                image['type']
            )
            # Save or process image_data
```

---

## Workflow JSON Structure

### Two JSON Formats

ComfyUI uses two different JSON formats:

1. **Workflow JSON** (UI format)
   - Contains node positions, visual layout
   - Used by ComfyUI frontend
   - NOT used for API execution

2. **Workflow API JSON** (execution format)
   - Contains only execution logic
   - Node definitions, inputs, connections
   - THIS is what you send to `/prompt` endpoint

### Exporting API Format

In ComfyUI web UI:
1. Enable Dev Mode (Settings → Enable Dev mode Options)
2. Click "Save (API Format)" button
3. Save as `workflow_api.json`

### API JSON Structure

```json
{
  "3": {
    "inputs": {
      "seed": 156680208700286,
      "steps": 20,
      "cfg": 8.0,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0,
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "sd_xl_base_1.0.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "6": {
    "inputs": {
      "text": "A beautiful sunset over mountains",
      "clip": ["4", 1]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  }
  // ... more nodes
}
```

### Modifying Workflows Programmatically

```python
import json

# Load workflow template
with open('workflow_api.json', 'r') as f:
    workflow = json.load(f)

# Modify parameters
workflow["3"]["inputs"]["seed"] = random.randint(0, 2**32)
workflow["6"]["inputs"]["text"] = user_prompt
workflow["4"]["inputs"]["ckpt_name"] = selected_model

# Queue modified workflow
queue_prompt(workflow)
```

### Template System with Metadata

For auto-downloading models, add metadata to node properties:

```json
{
  "39": {
    "type": "VAELoader",
    "properties": {
      "Node name for S&R": "VAELoader",
      "models": [
        {
          "name": "sd_xl_vae.safetensors",
          "url": "https://huggingface.co/stabilityai/sdxl-vae/blob/main/sdxl_vae.safetensors",
          "hash": "2fc39d31359a4b0a64f55876d8ff7fa8d780956ae2cb13463b0223e15148976b",
          "hash_type": "SHA256",
          "directory": "vae"
        }
      ]
    },
    "widgets_values": ["sd_xl_vae.safetensors"]
  }
}
```

---

## Python Client Libraries

### Option 1: comfyuiclient (Recommended for simplicity)

**Installation**:
```bash
pip install comfyuiclient
```

**Usage**:
```python
from comfyuiclient import ComfyUIClient

client = ComfyUIClient("http://192.168.1.100:8188")

# Load workflow
workflow = client.load_workflow("workflow.json")

# Modify parameters
workflow.set_node_param("6", "text", "A futuristic cityscape")

# Execute
result = client.execute(workflow)

# Get images
images = client.get_images(result.prompt_id)
```

### Option 2: comfyui-python-api (Best for event-driven apps)

**Installation**:
```bash
pip install comfyui-python-api
```

**Usage**:
```python
from comfyui_python_api import ComfyUIAPI

api = ComfyUIAPI("http://192.168.1.100:8188")

def on_progress(node_name, progress):
    print(f"{node_name}: {progress}%")

def on_complete(prompt_id):
    images = api.get_images(prompt_id)
    print(f"Generated {len(images)} images")

api.queue_workflow(
    workflow_json,
    on_progress=on_progress,
    on_complete=on_complete
)
```

---

## Network Architecture

### Deployment Topology

```
┌─────────────────────────────────────────────────────────┐
│ Life-OS FastAPI Backend (Mac/Linux Server)             │
│ - Port 8000 (exposed to internet)                      │
│ - JWT authentication                                    │
│ - Job queue (Redis)                                     │
│ - Workflow template management                          │
│ - Image storage/retrieval                               │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ HTTP/WebSocket over LAN
                  │ (192.168.1.x or Tailscale VPN)
                  │
┌─────────────────▼───────────────────────────────────────┐
│ ComfyUI Server (RTX 4090 PC)                           │
│ - Port 8188 (internal LAN only)                        │
│ - Docker container or systemd service                   │
│ - Model storage (500GB+)                                │
│ - Generated images → NFS/SMB share                      │
└─────────────────────────────────────────────────────────┘
```

### Network Configuration

**Option A: Local LAN** (Simplest)
- ComfyUI PC: Static IP `192.168.1.100`
- Life-OS Backend connects directly over LAN
- No internet exposure for ComfyUI
- Lowest latency

**Option B: Tailscale VPN** (Recommended for remote access)
- Install Tailscale on both machines
- ComfyUI accessible at `100.x.x.x` (Tailscale IP)
- Secure encrypted tunnel
- Works from anywhere

**Option C: Cloudflare Tunnel** (For internet exposure)
- ComfyUI → Cloudflare Tunnel → Public URL
- Built-in authentication
- Protects home IP
- Adds latency

### Port Forwarding (Option A)

On RTX 4090 PC, start ComfyUI with:
```bash
python main.py --listen 0.0.0.0 --port 8188
```

Firewall rule (Ubuntu/Debian):
```bash
sudo ufw allow from 192.168.1.0/24 to any port 8188
```

### File Sharing for Generated Images

**Option 1: NFS Share** (Linux/Mac)
```bash
# On RTX 4090 PC (Ubuntu)
sudo apt install nfs-kernel-server
sudo mkdir -p /mnt/comfyui_output
sudo chown nobody:nogroup /mnt/comfyui_output
echo "/mnt/comfyui_output 192.168.1.0/24(rw,sync,no_subtree_check)" | sudo tee -a /etc/exports
sudo exportfs -a

# On Life-OS Backend (Mac)
sudo mount -t nfs 192.168.1.100:/mnt/comfyui_output /path/to/local/mount
```

**Option 2: SMB/Samba** (Windows-compatible)
```bash
# On RTX 4090 PC
sudo apt install samba
# Configure /etc/samba/smb.conf
```

**Option 3: HTTP Download** (Simplest)
- Use ComfyUI `/view` endpoint to download images
- No additional file sharing setup
- Life-OS backend fetches via HTTP

---

## Docker Deployment for RTX 4090

### Recommended Docker Image

**yanwk/comfyui-boot** (Most popular, production-ready)

**Features**:
- CUDA 12.8 support
- Automatic model downloads
- Volume mounts for persistence
- Easy port configuration

### Docker Compose Setup

Create `docker-compose.yml` on RTX 4090 PC:

```yaml
version: '3.8'

services:
  comfyui:
    image: yanwk/comfyui-boot:latest
    container_name: comfyui-server
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
      - CLI_ARGS=--listen 0.0.0.0 --port 8188
    ports:
      - "8188:8188"
    volumes:
      # Models (large, 200GB+)
      - ./models:/app/ComfyUI/models
      # Custom nodes
      - ./custom_nodes:/app/ComfyUI/custom_nodes
      # Workflows
      - ./workflows:/app/ComfyUI/user/default/workflows
      # Output images
      - ./output:/app/ComfyUI/output
      # Input images
      - ./input:/app/ComfyUI/input
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
```

### Startup Commands

```bash
# First time setup
docker-compose pull
docker-compose up -d

# Check logs
docker logs -f comfyui-server

# Restart
docker-compose restart

# Update
docker-compose pull
docker-compose up -d --force-recreate
```

### GPU Verification

Inside container:
```bash
docker exec comfyui-server nvidia-smi
```

Expected output:
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.x        Driver Version: 535.x        CUDA Version: 12.8    |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce RTX 4090  On   | 00000000:01:00.0  On |                  Off |
| 30%   45C    P8    25W / 450W |   1024MiB / 24564MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

### Storage Requirements

- **Models**: 100-500GB (depending on collection)
  - SDXL Base: ~6GB
  - ControlNet models: ~1-2GB each
  - LoRA models: ~100-500MB each
  - IP-Adapter: ~2GB
- **Custom Nodes**: 1-5GB
- **Output Images**: 10-100GB (grows over time)

### Systemd Service (Alternative to Docker)

If you prefer systemd over Docker:

```bash
# /etc/systemd/system/comfyui.service
[Unit]
Description=ComfyUI Stable Diffusion Server
After=network.target

[Service]
Type=simple
User=comfyui
WorkingDirectory=/opt/ComfyUI
ExecStart=/usr/bin/python3 main.py --listen 0.0.0.0 --port 8188
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable comfyui
sudo systemctl start comfyui
sudo journalctl -u comfyui -f  # View logs
```

---

## Model Management

### Directory Structure

ComfyUI expects models in specific directories:

```
ComfyUI/models/
├── checkpoints/          # Stable Diffusion models (.safetensors)
├── vae/                  # VAE models
├── loras/                # LoRA models
├── controlnet/           # ControlNet models
├── ipadapter/            # IP-Adapter models
├── clip/                 # CLIP models
├── clip_vision/          # CLIP Vision models (auto-downloaded)
├── upscale_models/       # Upscaling models
├── embeddings/           # Textual inversion embeddings
└── hypernetworks/        # Hypernetwork models
```

### Auto-Download via ComfyUI Manager

1. **Install ComfyUI Manager** (custom node):
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/ltdrdata/ComfyUI-Manager.git
   cd ComfyUI-Manager
   pip install -r requirements.txt
   ```

2. **Access Manager UI**:
   - Open ComfyUI web interface
   - Click "Manager" button
   - Search for models by name
   - Click "Install" to auto-download

### Manual Model Installation

Download from HuggingFace/Civitai and place in correct directory:

```bash
# Example: Download SDXL Base
cd ComfyUI/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

# Example: Download ControlNet
cd ComfyUI/models/controlnet
wget https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth
```

### Programmatic Model Loading

Use workflow metadata to auto-download:

```python
# In workflow JSON
{
  "4": {
    "inputs": {
      "ckpt_name": "sd_xl_base_1.0.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "properties": {
      "models": [
        {
          "name": "sd_xl_base_1.0.safetensors",
          "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
          "hash": "...",
          "hash_type": "SHA256",
          "directory": "checkpoints"
        }
      ]
    }
  }
}
```

Then implement a model downloader in Life-OS:

```python
import hashlib
import requests
from pathlib import Path

def download_model_if_needed(model_info, comfyui_models_dir):
    model_path = Path(comfyui_models_dir) / model_info['directory'] / model_info['name']

    if model_path.exists():
        # Verify hash
        with open(model_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        if file_hash == model_info['hash']:
            return  # Model already exists and valid

    # Download
    response = requests.get(model_info['url'], stream=True)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    with open(model_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
```

### Recommended Models for RTX 4090

**Text-to-Image**:
- SDXL Base 1.0 (~6GB)
- SDXL Refiner (~6GB)
- SD 1.5 (~2GB) - for ControlNet/LoRA compatibility

**ControlNet** (for pose/depth/edge guidance):
- control_v11p_sd15_openpose (~1.5GB)
- control_v11f1p_sd15_depth (~1.5GB)
- control_v11p_sd15_canny (~1.5GB)

**IP-Adapter** (for style/character consistency):
- ip-adapter_sd15_plus (~2GB)
- ip-adapter-plus-face_sd15 (~2GB)

**LoRA** (for specific styles):
- Download on-demand from Civitai
- Store in `loras/` directory

---

## Security Considerations

### Critical: ComfyUI Has No Built-in Auth

ComfyUI's native API **does not include authentication or authorization**. This is a major security risk for production deployments.

### Recommended Security Layers

#### 1. Reverse Proxy with Authentication (REQUIRED for internet exposure)

**Nginx with Basic Auth**:

```nginx
# /etc/nginx/sites-available/comfyui
server {
    listen 443 ssl http2;
    server_name comfyui.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Basic authentication
    auth_basic "ComfyUI Access";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://127.0.0.1:8188;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8188/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Create `.htpasswd`:
```bash
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd username
```

#### 2. Cloudflare Tunnel (Easiest for home setups)

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create comfyui-tunnel

# Configure
cat > ~/.cloudflared/config.yml <<EOF
tunnel: comfyui-tunnel
credentials-file: /home/user/.cloudflared/tunnel_id.json

ingress:
  - hostname: comfyui.yourdomain.com
    service: http://localhost:8188
  - service: http_status:404
EOF

# Run tunnel
cloudflared tunnel run comfyui-tunnel
```

Then add **Cloudflare Access** policy:
- Require email domain
- Or use one-time PIN
- Or integrate with Google/GitHub auth

#### 3. Tailscale VPN (Best for private access)

```bash
# On both machines (Life-OS backend + RTX 4090 PC)
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# ComfyUI now accessible at Tailscale IP (100.x.x.x)
# No internet exposure, encrypted tunnel
```

#### 4. Firewall Rules (Defense in depth)

```bash
# Ubuntu/Debian
sudo ufw default deny incoming
sudo ufw allow from 192.168.1.0/24 to any port 8188  # LAN only
sudo ufw enable

# Or with Tailscale
sudo ufw allow from 100.64.0.0/10 to any port 8188  # Tailscale IPs
```

### API Key Integration (Future)

ComfyUI now supports API keys via PR #8041. To enable:

```python
# In ComfyUI config
{
  "api_key_enabled": true,
  "api_keys": {
    "your-secret-key": {
      "name": "Life-OS Backend",
      "permissions": ["read", "write", "execute"]
    }
  }
}
```

Then pass key in requests:
```python
headers = {
    "Authorization": f"Bearer {api_key}"
}
requests.post(f"{comfyui_url}/prompt", json=payload, headers=headers)
```

### Vulnerability Considerations

Recent security research (Snyk Labs) found vulnerabilities in ComfyUI custom nodes. Recommendations:

1. **Only install trusted custom nodes**
2. **Review code before installing**
3. **Use Docker** to isolate ComfyUI from host system
4. **Run as non-root user**
5. **Keep ComfyUI updated**

---

## Production Implementation Roadmap

### Phase 1: Local Development Setup (1-2 days)

**Goal**: Get ComfyUI running locally and test basic API interactions.

**Tasks**:
1. ✅ Install ComfyUI on RTX 4090 PC
2. ✅ Download base models (SDXL Base, SD 1.5)
3. ✅ Test native API with Python script
4. ✅ Export workflow as API JSON
5. ✅ Test modifying workflow parameters programmatically

**Deliverable**: Working ComfyUI server accessible at `http://192.168.1.100:8188`

---

### Phase 2: Network Setup (1 day)

**Goal**: Secure network connectivity between Life-OS and ComfyUI.

**Tasks**:
1. ✅ Configure static IP for RTX 4090 PC
2. ✅ Set up Tailscale VPN (or LAN-only access)
3. ✅ Test connectivity from Life-OS backend
4. ✅ Set up NFS/SMB share for generated images
5. ✅ Test image retrieval

**Deliverable**: Life-OS backend can reach ComfyUI and download images.

---

### Phase 3: FastAPI Integration (2-3 days)

**Goal**: Create ComfyUI service in Life-OS backend.

**Tasks**:
1. ✅ Create `api/services/comfyui_service.py`
   - WebSocket connection management
   - Workflow queuing
   - Progress tracking
   - Image retrieval

2. ✅ Create `api/routes/comfyui.py`
   - POST `/api/comfyui/generate` - Queue workflow
   - GET `/api/comfyui/status/{prompt_id}` - Check status
   - GET `/api/comfyui/result/{prompt_id}` - Get images
   - GET `/api/comfyui/models` - List available models

3. ✅ Add to existing job queue system
   - ComfyUI jobs tracked in Redis
   - Real-time progress via SSE
   - Error handling and retries

**Deliverable**: RESTful API for ComfyUI in Life-OS.

---

### Phase 4: Workflow Templates (2-3 days)

**Goal**: Create reusable workflow templates for common tasks.

**Tasks**:
1. ✅ Create template library in `comfyui_workflows/`
   - `text_to_image_sdxl.json`
   - `img2img_sdxl.json`
   - `controlnet_pose.json`
   - `ipadapter_style_transfer.json`

2. ✅ Build template parameter system
   - Define "slots" for user inputs (prompt, model, seed, etc.)
   - Validation for parameter types
   - Default values

3. ✅ Create template UI in frontend
   - Template selector
   - Parameter form generation
   - Preview mode

**Deliverable**: Users can select templates and fill in parameters via UI.

---

### Phase 5: Model Management (2 days)

**Goal**: Auto-download and manage models.

**Tasks**:
1. ✅ Build model metadata database
   - Track installed models
   - HuggingFace/Civitai URLs
   - File hashes for verification

2. ✅ Create model downloader service
   - Check if model exists
   - Download if missing
   - Verify hash

3. ✅ Frontend model browser
   - Search models
   - Install/uninstall
   - View model details

**Deliverable**: Users can browse and install models from UI.

---

### Phase 6: Production Hardening (2-3 days)

**Goal**: Deploy ComfyUI securely for production use.

**Tasks**:
1. ✅ Docker deployment with docker-compose
2. ✅ Reverse proxy with SSL (Nginx or Cloudflare)
3. ✅ Authentication layer (API keys or JWT)
4. ✅ Monitoring and logging
   - Prometheus metrics
   - Grafana dashboard
   - Error alerting
5. ✅ Backup strategy for models and workflows
6. ✅ Rate limiting and queue management

**Deliverable**: Production-ready ComfyUI deployment.

---

### Phase 7: Advanced Features (Ongoing)

**Tasks**:
- Custom node development for Life-OS-specific features
- Multi-GPU support (if adding more GPUs)
- Batch generation workflows
- Fine-tuning pipeline (train LoRAs from user photos)
- Video generation (AnimateDiff integration)

---

## Code Examples

### Example 1: Simple Text-to-Image Integration

```python
# api/services/comfyui_service.py
import json
import uuid
import asyncio
import aiohttp
import websockets
from pathlib import Path
from api.logging_config import get_logger

logger = get_logger(__name__)

class ComfyUIService:
    def __init__(self, server_url: str = "http://192.168.1.100:8188"):
        self.server_url = server_url
        self.ws_url = server_url.replace("http", "ws")

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        model: str = "sd_xl_base_1.0.safetensors",
        steps: int = 20,
        cfg: float = 7.0,
        seed: int = None
    ) -> dict:
        """
        Generate image using ComfyUI SDXL workflow.

        Returns:
            dict with keys: prompt_id, images (list of bytes)
        """
        # Generate random seed if not provided
        if seed is None:
            seed = random.randint(0, 2**32 - 1)

        # Load workflow template
        workflow_path = Path(__file__).parent.parent.parent / "comfyui_workflows" / "text_to_image_sdxl.json"
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)

        # Modify workflow with user parameters
        workflow["3"]["inputs"]["seed"] = seed
        workflow["3"]["inputs"]["steps"] = steps
        workflow["3"]["inputs"]["cfg"] = cfg
        workflow["4"]["inputs"]["ckpt_name"] = model
        workflow["6"]["inputs"]["text"] = prompt
        workflow["7"]["inputs"]["text"] = negative_prompt

        # Queue workflow
        prompt_id = await self._queue_workflow(workflow)
        logger.info(f"Queued ComfyUI workflow: {prompt_id}")

        # Wait for completion
        await self._wait_for_completion(prompt_id)
        logger.info(f"ComfyUI workflow completed: {prompt_id}")

        # Retrieve images
        images = await self._get_images(prompt_id)
        logger.info(f"Retrieved {len(images)} images from ComfyUI")

        return {
            "prompt_id": prompt_id,
            "images": images,
            "metadata": {
                "prompt": prompt,
                "model": model,
                "seed": seed,
                "steps": steps,
                "cfg": cfg
            }
        }

    async def _queue_workflow(self, workflow: dict) -> str:
        """Queue workflow and return prompt_id."""
        client_id = str(uuid.uuid4())
        payload = {
            "prompt": workflow,
            "client_id": client_id
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.server_url}/prompt", json=payload) as resp:
                result = await resp.json()
                return result['prompt_id']

    async def _wait_for_completion(self, prompt_id: str):
        """Wait for workflow execution to complete via WebSocket."""
        client_id = str(uuid.uuid4())
        ws_url = f"{self.ws_url}/ws?clientId={client_id}"

        async with websockets.connect(ws_url) as websocket:
            while True:
                msg = await websocket.recv()
                data = json.loads(msg)

                if data['type'] == 'executing':
                    node = data['data']['node']
                    exec_prompt_id = data['data']['prompt_id']

                    if exec_prompt_id == prompt_id and node is None:
                        # Execution finished
                        break

                elif data['type'] == 'execution_error':
                    error = data['data']
                    raise Exception(f"ComfyUI execution error: {error}")

    async def _get_images(self, prompt_id: str) -> list:
        """Retrieve generated images for a prompt_id."""
        async with aiohttp.ClientSession() as session:
            # Get history
            async with session.get(f"{self.server_url}/history/{prompt_id}") as resp:
                history = await resp.json()

            # Extract image info
            outputs = history[prompt_id]['outputs']
            images = []

            for node_id, node_output in outputs.items():
                if 'images' in node_output:
                    for image in node_output['images']:
                        # Download image
                        params = {
                            'filename': image['filename'],
                            'subfolder': image['subfolder'],
                            'type': image['type']
                        }
                        async with session.get(f"{self.server_url}/view", params=params) as img_resp:
                            images.append(await img_resp.read())

            return images
```

### Example 2: API Route

```python
# api/routes/comfyui.py
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Optional
from api.services.comfyui_service import ComfyUIService
from api.dependencies.auth import get_current_active_user
from api.models.user import User

router = APIRouter(prefix="/api/comfyui", tags=["ComfyUI"])
comfyui_service = ComfyUIService()

class GenerateImageRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation")
    negative_prompt: str = Field("", description="Negative prompt")
    model: str = Field("sd_xl_base_1.0.safetensors", description="Model name")
    steps: int = Field(20, ge=1, le=100, description="Number of steps")
    cfg: float = Field(7.0, ge=1.0, le=30.0, description="CFG scale")
    seed: Optional[int] = Field(None, description="Random seed")

class GenerateImageResponse(BaseModel):
    status: str
    prompt_id: str
    message: str

@router.post("/generate", response_model=GenerateImageResponse)
async def generate_image(
    request: GenerateImageRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Queue an image generation workflow on ComfyUI.

    Returns immediately with prompt_id. Use /status endpoint to check progress.
    """
    try:
        # Queue in background
        result = await comfyui_service.generate_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            model=request.model,
            steps=request.steps,
            cfg=request.cfg,
            seed=request.seed
        )

        return GenerateImageResponse(
            status="completed",
            prompt_id=result['prompt_id'],
            message=f"Generated {len(result['images'])} images"
        )

    except Exception as e:
        logger.error(f"ComfyUI generation failed: {e}")
        return GenerateImageResponse(
            status="failed",
            prompt_id="",
            message=str(e)
        )
```

### Example 3: Frontend Integration

```javascript
// frontend/src/ComfyUIGenerator.jsx
import React, { useState } from 'react';
import axios from 'axios';

function ComfyUIGenerator() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState([]);

  const handleGenerate = async () => {
    setLoading(true);

    try {
      const response = await axios.post('/api/comfyui/generate', {
        prompt: prompt,
        negative_prompt: 'blurry, low quality',
        model: 'sd_xl_base_1.0.safetensors',
        steps: 25,
        cfg: 7.5
      });

      if (response.data.status === 'completed') {
        // Fetch images
        const imgResponse = await axios.get(
          `/api/comfyui/result/${response.data.prompt_id}`
        );
        setImages(imgResponse.data.images);
      }
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="comfyui-generator">
      <h2>ComfyUI Image Generator</h2>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your prompt..."
        rows={4}
      />

      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Image'}
      </button>

      <div className="image-gallery">
        {images.map((img, idx) => (
          <img
            key={idx}
            src={`data:image/png;base64,${img}`}
            alt={`Generated ${idx}`}
          />
        ))}
      </div>
    </div>
  );
}

export default ComfyUIGenerator;
```

---

## Summary

### Key Takeaways

1. **Native API is Best**: Use ComfyUI's built-in REST/WebSocket API for maximum control and stability.

2. **FastAPI Wrapper**: Build a thin FastAPI layer for authentication, validation, and job management.

3. **Network Deployment**: Run ComfyUI on RTX 4090 PC, connect over LAN or Tailscale VPN.

4. **Docker is Recommended**: Use `yanwk/comfyui-boot` Docker image for easy deployment and updates.

5. **Security is Critical**: ComfyUI has no built-in auth. Use reverse proxy, Cloudflare Tunnel, or Tailscale.

6. **Workflow Templates**: Create reusable JSON templates for common generation tasks.

7. **Model Management**: Auto-download models via metadata or ComfyUI Manager.

8. **Production Roadmap**: 7 phases, ~2-3 weeks for full integration.

### Next Steps

1. Install ComfyUI on RTX 4090 PC (Docker recommended)
2. Test native API with Python script
3. Set up network connectivity (Tailscale or LAN)
4. Implement `ComfyUIService` in Life-OS backend
5. Create workflow templates
6. Build frontend UI for ComfyUI generation

---

## References

### Official Documentation
- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI API Docs](https://docs.comfy.org)
- [Workflow JSON Spec](https://docs.comfy.org/specs/workflow_json)

### Python Clients
- [comfyuiclient](https://github.com/sugarkwork/Comfyui_api_client)
- [comfyui-python-api](https://github.com/andreyryabtsev/comfyui-python-api)
- [comfy_api_simplified](https://github.com/deimos-deimos/comfy_api_simplified)

### Docker Images
- [yanwk/comfyui-boot](https://hub.docker.com/r/yanwk/comfyui-boot)
- [ai-dock/comfyui](https://github.com/ai-dock/comfyui)

### Tutorials
- [How to Use ComfyUI API with Python](https://medium.com/@next.trail.tech/how-to-use-comfyui-api-with-python-a-complete-guide-f786da157d57)
- [Building a Production-Ready ComfyUI API](https://www.viewcomfy.com/blog/building-a-production-ready-comfyui-api)
- [ComfyUI FastAPI Boilerplate](https://github.com/alexisrolland/ComfyUI-FastAPI)

### Security
- [Hacking ComfyUI Through Custom Nodes (Snyk Labs)](https://labs.snyk.io/resources/hacking-comfyui-through-custom-nodes/)
- [ComfyUI Server Configuration](https://comfyui-wiki.com/en/interface/server-config)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-24
**Author**: Claude (Anthropic)
**Status**: Research Complete, Ready for Implementation
