# ComfyUI Network Architecture for Life-OS

**Visual diagrams and deployment patterns for ComfyUI integration**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         End User                                │
│                    (Web Browser)                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Life-OS Frontend                             │
│                  (React + Vite + Nginx)                         │
│                  Port 80/443 (Public)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/WebSocket
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  Life-OS FastAPI Backend                        │
│                     (Mac/Linux Server)                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Services:                                                │  │
│  │ - ComfyUIService (workflow management)                   │  │
│  │ - JobQueueService (Redis-based queue)                    │  │
│  │ - AuthService (JWT authentication)                       │  │
│  │ - ImageStorageService (S3/local storage)                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Port 8000 (Public)                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/WebSocket
                             │ Tailscale VPN or LAN
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    ComfyUI API Server                           │
│                     (RTX 4090 PC)                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ComfyUI Native Server:                                   │  │
│  │ - REST API (/prompt, /queue, /history, /view)           │  │
│  │ - WebSocket API (/ws for progress updates)              │  │
│  │ - Model Storage (500GB+)                                 │  │
│  │ - Generated Images (output/)                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Port 8188 (Internal LAN or Tailscale only)                     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ GPU: RTX 4090 (24GB VRAM)                                │  │
│  │ - CUDA 12.x                                               │  │
│  │ - PyTorch with CUDA support                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Image Generation Request

```
1. User Submits Request
   ┌──────────────────┐
   │ Frontend (React) │
   └────────┬─────────┘
            │ POST /api/comfyui/generate
            │ { prompt: "...", steps: 20, ... }
            ▼
   ┌──────────────────────────────────────┐
   │ FastAPI Backend: /api/comfyui/generate│
   └────────┬─────────────────────────────┘
            │ 1. Validate request (Pydantic)
            │ 2. Load workflow template
            │ 3. Inject user parameters
            ▼
   ┌──────────────────────┐
   │ ComfyUIService       │
   └────────┬─────────────┘
            │ queue_workflow()
            ▼

2. Queue on ComfyUI Server
   ┌──────────────────────────────────────┐
   │ POST http://100.x.x.x:8188/prompt    │
   │ { "prompt": workflow_json, ... }     │
   └────────┬─────────────────────────────┘
            │ Returns: { "prompt_id": "abc123" }
            ▼
   ┌──────────────────────┐
   │ ComfyUI Queue        │
   │ - Position: 1        │
   │ - Status: Pending    │
   └────────┬─────────────┘
            │
            ▼

3. Monitor Progress (WebSocket)
   ┌──────────────────────────────────────┐
   │ WebSocket ws://100.x.x.x:8188/ws     │
   └────────┬─────────────────────────────┘
            │ Stream messages:
            │ { "type": "progress", "value": 0.2 }
            │ { "type": "executing", "node": "KSampler" }
            │ { "type": "executing", "node": null } ← Done!
            ▼
   ┌──────────────────────┐
   │ GPU Execution        │
   │ - Model loaded       │
   │ - Sampling (20 steps)│
   │ - Saving image       │
   └────────┬─────────────┘
            │ Writes to output/
            ▼

4. Retrieve Results
   ┌──────────────────────────────────────────┐
   │ GET http://100.x.x.x:8188/history/abc123 │
   └────────┬─────────────────────────────────┘
            │ Returns: { "outputs": { "9": { "images": [...] } } }
            ▼
   ┌──────────────────────────────────────────────────────┐
   │ GET http://100.x.x.x:8188/view?filename=...&type=... │
   └────────┬─────────────────────────────────────────────┘
            │ Returns: PNG binary data
            ▼
   ┌──────────────────────┐
   │ FastAPI Backend      │
   │ - Save to storage    │
   │ - Create thumbnail   │
   │ - Update database    │
   └────────┬─────────────┘
            │ Return image URL
            ▼
   ┌──────────────────┐
   │ Frontend         │
   │ - Display image  │
   └──────────────────┘
```

---

## Network Deployment Options

### Option A: Local LAN (Simplest)

```
┌─────────────────────────────────────────────────────────────┐
│                    Home Network (192.168.1.x)               │
│                                                             │
│  ┌───────────────────────┐        ┌────────────────────┐   │
│  │ Life-OS Backend       │        │ ComfyUI Server     │   │
│  │ 192.168.1.50          │──────▶ │ 192.168.1.100      │   │
│  │ Port 8000 (Public)    │        │ Port 8188 (LAN)    │   │
│  └───────────────────────┘        └────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                      │
                      │ Port Forwarding (optional)
                      ▼
              ┌───────────────┐
              │   Internet    │
              └───────────────┘
```

**Pros**:
- Lowest latency
- No additional software
- Simple firewall rules

**Cons**:
- Only works on local network
- No remote access when away from home
- Requires static IP or DHCP reservation

**Setup**:
```bash
# On ComfyUI PC
python main.py --listen 0.0.0.0 --port 8188

# On Life-OS Backend
export COMFYUI_URL="http://192.168.1.100:8188"
```

---

### Option B: Tailscale VPN (Recommended)

```
┌──────────────────────────────────────────────────────────────┐
│                   Tailscale Network                          │
│              (Encrypted Mesh VPN, 100.x.x.x)                 │
│                                                              │
│  ┌────────────────────────┐        ┌─────────────────────┐  │
│  │ Life-OS Backend        │        │ ComfyUI Server      │  │
│  │ 100.101.102.103        │──────▶ │ 100.104.105.106     │  │
│  │ Tailscale + Public IP  │        │ Tailscale only      │  │
│  └────────────────────────┘        └─────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
         │                                       │
         │ Internet                              │ Internet
         │ (from anywhere)                       │ (from anywhere)
         ▼                                       ▼
   ┌──────────┐                           ┌──────────┐
   │ Laptop   │                           │ Desktop  │
   │ Remote   │                           │ Home     │
   └──────────┘                           └──────────┘
```

**Pros**:
- Works from anywhere (coffee shop, office, etc.)
- End-to-end encryption (WireGuard)
- No port forwarding needed
- Simple setup (install + login)
- Free for personal use

**Cons**:
- Requires Tailscale account
- Slight latency overhead (~10-50ms)

**Setup**:
```bash
# On both machines
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Find Tailscale IPs
tailscale ip -4

# On Life-OS Backend
export COMFYUI_URL="http://100.104.105.106:8188"
```

---

### Option C: Cloudflare Tunnel (Public Access)

```
┌────────────────────────────────────────────────────────────┐
│                    Your Home Network                       │
│                                                            │
│  ┌──────────────────────┐                                 │
│  │ ComfyUI Server       │                                 │
│  │ localhost:8188       │                                 │
│  └──────────┬───────────┘                                 │
│             │                                              │
│  ┌──────────▼───────────┐                                 │
│  │ cloudflared daemon   │                                 │
│  │ (Cloudflare Tunnel)  │                                 │
│  └──────────┬───────────┘                                 │
└─────────────┼────────────────────────────────────────────┘
              │ Encrypted tunnel
              │
┌─────────────▼────────────────────────────────────────────┐
│            Cloudflare Network Edge                       │
│                                                          │
│  ┌────────────────────────────────────────┐             │
│  │ comfyui.yourdomain.com                 │             │
│  │ - SSL certificate (automatic)          │             │
│  │ - DDoS protection                      │             │
│  │ - Cloudflare Access (authentication)   │             │
│  └────────────────────────────────────────┘             │
└──────────────────────────────────────────────────────────┘
              │ HTTPS
              ▼
      ┌───────────────┐
      │ End Users     │
      │ (Public)      │
      └───────────────┘
```

**Pros**:
- Public URL with SSL
- Built-in authentication (Cloudflare Access)
- DDoS protection
- No port forwarding
- Hides your home IP

**Cons**:
- Slight latency overhead
- Requires Cloudflare account
- Exposes ComfyUI to internet (even with auth)

**Setup**:
```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create comfyui

# Configure
cat > ~/.cloudflared/config.yml <<EOF
tunnel: comfyui
credentials-file: /home/user/.cloudflared/tunnel_id.json

ingress:
  - hostname: comfyui.yourdomain.com
    service: http://localhost:8188
  - service: http_status:404
EOF

# Run as service
sudo cloudflared service install
sudo systemctl start cloudflared

# Add DNS record (via Cloudflare dashboard)
# comfyui.yourdomain.com → CNAME → tunnel_id.cfargotunnel.com

# Add Cloudflare Access policy
# Application: comfyui.yourdomain.com
# Policy: Email domain = @yourdomain.com
```

---

### Option D: Nginx Reverse Proxy (Advanced)

```
┌─────────────────────────────────────────────────────────────┐
│                    Public Server / VPS                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Nginx Reverse Proxy                                  │  │
│  │ - Port 443 (HTTPS)                                   │  │
│  │ - SSL (Let's Encrypt)                                │  │
│  │ - Basic Auth or JWT                                  │  │
│  └───────────────┬──────────────────────────────────────┘  │
│                  │                                          │
└──────────────────┼──────────────────────────────────────────┘
                   │ Proxy to backend
                   ▼
          ┌─────────────────┐
          │ ComfyUI Server  │
          │ (RTX 4090 PC)   │
          │ Port 8188       │
          └─────────────────┘
          (via VPN or SSH tunnel)
```

**Pros**:
- Full control over auth and SSL
- Can add rate limiting, caching
- Professional setup

**Cons**:
- Requires VPS or server
- More complex setup
- Need to manage SSL certificates

**Setup**:
```nginx
# /etc/nginx/sites-available/comfyui
server {
    listen 443 ssl http2;
    server_name comfyui.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Authentication
    auth_basic "ComfyUI Access";
    auth_basic_user_file /etc/nginx/.htpasswd;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=comfyui:10m rate=10r/s;
    limit_req zone=comfyui burst=20;

    location / {
        proxy_pass http://192.168.1.100:8188;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long-running generations
        proxy_connect_timeout 60s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }

    location /ws {
        proxy_pass http://192.168.1.100:8188/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Docker Deployment Architecture

### Single Container (Simple)

```
┌──────────────────────────────────────────────────────────┐
│               Docker Host (RTX 4090 PC)                  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Container: comfyui-server                          │ │
│  │ Image: yanwk/comfyui-boot:latest                   │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ ComfyUI Application                          │ │ │
│  │  │ Port 8188 → 8188 (host)                      │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ Volume Mounts:                               │ │ │
│  │  │ - ./models → /app/ComfyUI/models             │ │ │
│  │  │ - ./output → /app/ComfyUI/output             │ │ │
│  │  │ - ./workflows → /app/ComfyUI/user/...        │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ GPU Access: nvidia-docker runtime            │ │ │
│  │  │ CUDA 12.x                                    │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  comfyui:
    image: yanwk/comfyui-boot:latest
    runtime: nvidia
    container_name: comfyui-server
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

---

### Multi-Container with Reverse Proxy

```
┌────────────────────────────────────────────────────────────┐
│              Docker Compose Stack (RTX 4090 PC)            │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Container: nginx-proxy                               │ │
│  │ Image: nginx:alpine                                  │ │
│  │ Port 443:443 → Internet                              │ │
│  └───────────────────┬──────────────────────────────────┘ │
│                      │                                    │
│                      │ Internal network                   │
│                      ▼                                    │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Container: comfyui-server                            │ │
│  │ Image: yanwk/comfyui-boot:latest                     │ │
│  │ Port 8188 (internal only)                            │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Container: redis (optional, for queue management)    │ │
│  │ Image: redis:alpine                                  │ │
│  │ Port 6379 (internal only)                            │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

**docker-compose.yml**:
```yaml
version: '3.8'

networks:
  comfyui-net:
    driver: bridge

services:
  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - comfyui-net
    depends_on:
      - comfyui
    restart: unless-stopped

  comfyui:
    image: yanwk/comfyui-boot:latest
    runtime: nvidia
    container_name: comfyui-server
    expose:
      - "8188"
    volumes:
      - ./models:/app/ComfyUI/models
      - ./output:/app/ComfyUI/output
    environment:
      - CLI_ARGS=--listen 0.0.0.0 --port 8188
    networks:
      - comfyui-net
    restart: unless-stopped

  redis:
    image: redis:alpine
    container_name: comfyui-redis
    expose:
      - "6379"
    networks:
      - comfyui-net
    restart: unless-stopped
```

---

## File Storage Patterns

### Pattern 1: HTTP Download (Simplest)

```
ComfyUI Server
└── output/
    └── 2025-10-24/
        └── abc123_00001.png

                │
                │ Life-OS Backend fetches via HTTP
                │ GET /view?filename=abc123_00001.png&type=output
                ▼

Life-OS Backend
└── storage/
    └── generated/
        └── abc123_00001.png
```

**Pros**: No file sharing setup, works anywhere
**Cons**: Extra network transfer, requires HTTP request per image

---

### Pattern 2: NFS Share (Best for LAN)

```
ComfyUI Server (NFS Server)
└── /mnt/comfyui_output/ ─────┐
                               │ NFS export
                               │
                Life-OS Backend│(NFS Client)
                └── /mnt/comfyui_output/ (mounted)
                    └── abc123_00001.png ← Direct access
```

**Setup**:
```bash
# On ComfyUI PC (Ubuntu)
sudo apt install nfs-kernel-server
sudo mkdir -p /mnt/comfyui_output
sudo chown nobody:nogroup /mnt/comfyui_output
echo "/mnt/comfyui_output 192.168.1.0/24(rw,sync,no_subtree_check)" | sudo tee -a /etc/exports
sudo exportfs -a

# On Life-OS Backend (Mac)
sudo mount -t nfs 192.168.1.100:/mnt/comfyui_output /path/to/mount
```

**Pros**: Direct file access, zero copy overhead
**Cons**: Only works on LAN, requires NFS setup

---

### Pattern 3: S3/Object Storage (Best for production)

```
ComfyUI Server
└── output/
    └── abc123_00001.png
        │
        │ Upload after generation
        │ (boto3 or aws cli)
        ▼
    ┌─────────────┐
    │ S3 Bucket   │
    │ MinIO / R2  │
    └─────────────┘
        │
        │ Download when needed
        │
        ▼
Life-OS Backend
└── cache/
    └── abc123_00001.png (temporary)
```

**Pros**: Scalable, works anywhere, CDN integration
**Cons**: Requires S3-compatible storage, costs

---

## Summary: Recommended Architecture

### For Development (Home Setup)

```
Life-OS Backend (Mac)
    ↓ LAN (192.168.1.x)
ComfyUI Docker (RTX 4090 PC)
    ↓ HTTP /view
Images fetched on-demand
```

**Why**: Simple, fast iteration, no extra setup

---

### For Production (Remote Access)

```
Life-OS Backend (VPS/Server)
    ↓ Tailscale VPN (100.x.x.x)
ComfyUI Docker (RTX 4090 PC)
    ↓ NFS share
Shared storage for images
```

**Why**: Secure, remote access, efficient file sharing

---

### For High Availability

```
Life-OS Backend (Cloud)
    ↓ HTTPS
ComfyUI Docker (RTX 4090 PC)
    ↓ Cloudflare Tunnel
Public access with authentication
    ↓ S3
Object storage for images
```

**Why**: Works from anywhere, scalable, protected

---

## Next Steps

1. Choose deployment option based on use case
2. Set up network connectivity (Tailscale recommended)
3. Deploy ComfyUI with Docker
4. Test API connectivity from Life-OS backend
5. Implement file storage pattern
6. Build FastAPI integration layer

---

**See `COMFYUI_API_INTEGRATION_GUIDE.md` for implementation details.**
