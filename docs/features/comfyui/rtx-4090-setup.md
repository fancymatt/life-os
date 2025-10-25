# RTX 4090 PC ComfyUI Setup Guide

**Purpose**: Set up ComfyUI with Docker on RTX 4090 PC for Life-OS local image generation
**Target OS**: Windows 11 + WSL2 OR Ubuntu 24.04 (native Linux)
**Estimated Time**: 2-4 hours (mostly downloads)
**Prerequisites**: RTX 4090 installed, internet connection, ~100GB free storage

---

## Overview

This guide will set up your RTX 4090 PC as a headless ComfyUI server that Life-OS on your Mac Studio can call via API. The setup includes:

1. ✅ OS preparation (Windows WSL2 or Linux)
2. ✅ NVIDIA drivers and Container Toolkit
3. ✅ Docker installation
4. ✅ ComfyUI container deployment
5. ✅ Model downloads (~50-80GB depending on models chosen)
6. ✅ Custom nodes installation
7. ✅ Network configuration and testing
8. ✅ Workflow templates setup

**End State**: ComfyUI running at `http://YOUR_PC_IP:8188`, accessible from Mac Studio

## Model Options

This guide supports two primary workflows:

**Option A: IP-Adapter-FaceID (SDXL-based)**
- Face preservation and style transfer
- ~20-30GB models
- Established workflow, extensive community support

**Option B: Qwen-Image-Edit (RECOMMENDED - State of the Art)**
- Advanced image editing with semantic and appearance control
- Bilingual text editing (Chinese/English)
- Native ComfyUI support
- ~30-40GB models (FP8 quantized)
- Superior editing capabilities for tasks similar to Gemini 2.5 image editing


distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
---

## 🚨 MANUAL STEPS (YOU MUST DO THESE)

These steps **require manual intervention** and cannot be fully automated:

### Manual Step 1: Choose Your OS Path

**Option A: Windows 11 + WSL2** (Recommended if already on Windows)
- Easier if you already use Windows
- WSL2 provides Linux environment
- Docker Desktop available
- Slightly more overhead but user-friendly

**Option B: Ubuntu 24.04 Native** (Recommended for maximum performance)
- Direct GPU access (no Windows overhead)
- Better Docker performance
- More complex initial setup
- Ideal for dedicated server

**✋ ACTION REQUIRED**: Choose your path and follow the corresponding section below.

---

### Manual Step 2A: Windows 11 + WSL2 Setup

#### Prerequisites Check
1. **Windows Version**: Windows 11 (build 22000 or higher)
   - Check: `winver` in Run dialog (Win+R)
   - If older: Update Windows first

2. **BIOS Settings**: Virtualization enabled
   - Restart PC → Enter BIOS (usually Del, F2, or F12 during boot)
   - Look for: "Intel VT-x" or "AMD-V" or "SVM Mode"
   - Enable if disabled
   - Save and exit

3. **WSL2 Installation**
   - Open PowerShell **as Administrator**
   - Run:
     ```powershell
     wsl --install
     ```
   - This installs WSL2 + Ubuntu 22.04 by default
   - **Restart computer when prompted**

4. **After Restart**: Complete Ubuntu Setup
   - WSL will launch automatically
   - Create username (e.g., `yourname`)
   - Create password
   - **WRITE DOWN YOUR USERNAME** - you'll need it later

5. **Verify WSL2**
   - Open PowerShell (as Administrator)
   - Run:
     ```powershell
     wsl --list --verbose
     ```
   - Should show Ubuntu with VERSION 2
   - If VERSION 1: Convert with:
     ```powershell
     wsl --set-version Ubuntu 2
     ```

#### Install NVIDIA Drivers (Windows)
1. **Download NVIDIA Drivers**
   - Go to: https://www.nvidia.com/Download/index.aspx
   - Product: GeForce RTX 40 Series → RTX 4090
   - OS: Windows 11
   - Download latest **Game Ready Driver** or **Studio Driver**

2. **Install Driver**
   - Run installer
   - Choose "Express Installation"
   - Restart if prompted

3. **Verify GPU**
   - Open PowerShell
   - Run:
     ```powershell
     nvidia-smi
     ```
   - Should show RTX 4090 with 24GB VRAM

#### Install Docker Desktop for Windows
1. **Download Docker Desktop**
   - Go to: https://www.docker.com/products/docker-desktop/
   - Download Windows version
   - Run installer
   - **Enable WSL2 backend** (should be default)
   - Restart if prompted

2. **Launch Docker Desktop**
   - Start Docker Desktop
   - Wait for it to fully start (whale icon in system tray turns steady)
   - Open Settings (gear icon)
   - **Resources → WSL Integration**:
     - Enable "Ubuntu" (or your WSL distro)
     - Apply & Restart

3. **Verify Docker in WSL**
   - Open Ubuntu terminal (search "Ubuntu" in Start menu)
   - Run:
     ```bash
     docker --version
     ```
   - Should show Docker version 24.x or higher

#### Install NVIDIA Container Toolkit (WSL2)
1. **Open Ubuntu Terminal** (WSL2)
2. **Run these commands** (copy-paste each block):

   ```bash
   # Add NVIDIA GPG key
   curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
     sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

   # Add repository
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
     sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
     sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

   # Update and install
   sudo apt-get update
   sudo apt-get install -y nvidia-container-toolkit

   # Configure Docker runtime
   sudo nvidia-ctk runtime configure --runtime=docker
   ```

3. **Restart Docker Desktop**
   - Close Docker Desktop completely (right-click system tray icon → Quit)
   - Re-open Docker Desktop
   - Wait for it to start

4. **Verify GPU Access in Docker**
   ```bash
   # In Ubuntu terminal
   docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi
   ```
   - Should show RTX 4090 info
   - **If this fails**: See Troubleshooting section

✅ **CHECKPOINT**: If `nvidia-smi` works in Docker, you're ready to proceed to "Claude Code Automated Setup"

---

### Manual Step 2B: Ubuntu 24.04 Native Setup

#### Prerequisites Check
1. **Fresh Ubuntu Installation**
   - Download: https://ubuntu.com/download/desktop
   - Version: Ubuntu 24.04 LTS
   - Create bootable USB (use Rufus on Windows or Etcher on Mac)
   - Install Ubuntu (follow on-screen instructions)
   - **WRITE DOWN YOUR USERNAME** - you'll need it later

2. **Post-Installation Updates**
   - Open Terminal (Ctrl+Alt+T)
   - Run:
     ```bash
     sudo apt update && sudo apt upgrade -y
     ```
   - Restart if kernel updates installed

#### Install NVIDIA Drivers (Ubuntu)
1. **Remove Existing Drivers** (if any)
   ```bash
   sudo apt remove --purge nvidia-* -y
   sudo apt autoremove -y
   ```

2. **Add NVIDIA PPA**
   ```bash
   sudo add-apt-repository ppa:graphics-drivers/ppa -y
   sudo apt update
   ```

3. **Install Latest Driver**
   ```bash
   # Check recommended driver
   ubuntu-drivers devices

   # Install recommended (usually nvidia-driver-XXX)
   sudo ubuntu-drivers autoinstall

   # OR install specific version (e.g., 550)
   # sudo apt install nvidia-driver-550 -y
   ```

4. **Reboot**
   ```bash
   sudo reboot
   ```

5. **Verify GPU**
   ```bash
   nvidia-smi
   ```
   - Should show RTX 4090 with 24GB VRAM
   - Driver version should be 535+ (preferably 550+)

#### Install Docker (Ubuntu)
1. **Remove Old Versions** (if any)
   ```bash
   sudo apt remove docker docker-engine docker.io containerd runc -y
   ```

2. **Install Prerequisites**
   ```bash
   sudo apt install -y \
     ca-certificates \
     curl \
     gnupg \
     lsb-release
   ```

3. **Add Docker GPG Key**
   ```bash
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
     sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   ```

4. **Add Docker Repository**
   ```bash
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
     https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) stable" | \
     sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

5. **Install Docker**
   ```bash
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
   ```

6. **Add User to Docker Group**
   ```bash
   sudo usermod -aG docker $USER
   ```

7. **Log Out and Back In** (required for group changes)
   ```bash
   # Log out of your session, then log back in
   # OR run: newgrp docker
   ```

8. **Verify Docker**
   ```bash
   docker --version
   docker compose version
   ```

#### Install NVIDIA Container Toolkit (Ubuntu)
1. **Add NVIDIA GPG Key**
   ```bash
   curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
     sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
   ```

2. **Add Repository**
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
     sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
     sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
   ```

3. **Install Toolkit**
   ```bash
   sudo apt-get update
   sudo apt-get install -y nvidia-container-toolkit
   ```

4. **Configure Docker Runtime**
   ```bash
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```

5. **Verify GPU Access in Docker**
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi
   ```
   - Should show RTX 4090 info
   - **If this fails**: See Troubleshooting section

✅ **CHECKPOINT**: If `nvidia-smi` works in Docker, you're ready to proceed to "Claude Code Automated Setup"

---

### Manual Step 3: Network Configuration

**Goal**: Make ComfyUI accessible from your Mac Studio (192.168.x.x network)

#### Find Your PC's IP Address

**Windows + WSL2**:
1. Open PowerShell (Windows side, not WSL)
2. Run:
   ```powershell
   ipconfig
   ```
3. Look for "Ethernet adapter" or "Wireless LAN adapter"
4. Find "IPv4 Address": e.g., `192.168.1.100`
5. **WRITE DOWN THIS IP ADDRESS**

**Ubuntu Native**:
1. Open Terminal
2. Run:
   ```bash
   ip addr show
   ```
3. Look for interface (usually `eth0` or `enp*` for ethernet, `wlan0` for WiFi)
4. Find `inet` address: e.g., `192.168.1.100/24`
5. **WRITE DOWN THIS IP ADDRESS** (without the /24)

#### Set Static IP (Recommended)

**Why**: Prevents IP from changing, breaking Life-OS connection

**Windows**:
1. Control Panel → Network and Sharing Center → Change adapter settings
2. Right-click your network adapter → Properties
3. Select "Internet Protocol Version 4 (TCP/IPv4)" → Properties
4. Select "Use the following IP address"
5. Enter:
   - IP address: `192.168.1.100` (or your chosen static IP)
   - Subnet mask: `255.255.255.0`
   - Default gateway: `192.168.1.1` (usually your router)
   - DNS: `8.8.8.8` (Google DNS) or your router's IP
6. Click OK

**Ubuntu**:
1. Open Settings → Network
2. Click gear icon next to your connection
3. Go to "IPv4" tab
4. Change Method to "Manual"
5. Add Address:
   - Address: `192.168.1.100`
   - Netmask: `255.255.255.0`
   - Gateway: `192.168.1.1`
6. DNS: `8.8.8.8`
7. Apply

#### Firewall Configuration

**Windows Firewall**:
1. Search "Windows Defender Firewall" → Advanced settings
2. Click "Inbound Rules" → "New Rule"
3. Rule Type: Port → Next
4. Protocol: TCP, Port: 8188 → Next
5. Action: Allow the connection → Next
6. Profile: Check all (Domain, Private, Public) → Next
7. Name: "ComfyUI API" → Finish

**Ubuntu Firewall** (if ufw enabled):
```bash
sudo ufw allow 8188/tcp
sudo ufw reload
```

#### Test Network from Mac Studio

**On Mac Studio**, open Terminal and run:
```bash
ping 192.168.1.100
```
- Should get replies
- If "Request timeout": Check firewall, network connection, static IP

✅ **CHECKPOINT**: If ping succeeds, network is ready

---

## 🤖 CLAUDE CODE AUTOMATED SETUP

**From this point forward, Claude Code can execute the remaining steps automatically.**

**Instructions for Claude Code**:
1. SSH into the RTX 4090 PC (or run locally if already on that machine)
2. Create a working directory: `~/comfyui-setup`
3. Execute each phase sequentially
4. Verify each checkpoint before proceeding

---

## Phase 1: Directory Structure Setup

**Goal**: Create organized directory structure for ComfyUI

**Commands**:
```bash
# Create base directory
mkdir -p ~/comfyui
cd ~/comfyui

# Create subdirectories
mkdir -p run              # ComfyUI runtime (venv, source)
mkdir -p basedir          # User data
mkdir -p workflows        # Workflow templates (API format)
mkdir -p models           # Will create subdirs later
mkdir -p output           # Generated images
mkdir -p logs             # Container logs

# Verify structure
tree -L 1 ~/comfyui
```

**Expected Output**:
```
/home/username/comfyui
├── basedir
├── logs
├── models
├── output
├── run
└── workflows
```

✅ **CHECKPOINT**: All directories created

---

## Phase 2: Docker Compose Configuration

**Goal**: Create docker-compose.yml for ComfyUI container

**Commands**:
```bash
cd ~/comfyui

# Get current user UID/GID
USER_UID=$(id -u)
USER_GID=$(id -g)

echo "User UID: $USER_UID"
echo "User GID: $USER_GID"

# Create docker-compose.yml
cat > docker-compose.yml <<EOF
version: '3.8'

services:
  comfyui:
    image: mmartial/comfyui-nvidia-docker:ubuntu24_cuda12.6.3-latest
    container_name: comfyui-server
    runtime: nvidia

    ports:
      - "0.0.0.0:8188:8188"  # Expose to network

    volumes:
      - ./run:/comfy/mnt
      - ./basedir:/basedir
      - ./workflows:/workflows
      - ./output:/basedir/output
      - ./models:/basedir/models

    environment:
      - WANTED_UID=$USER_UID
      - WANTED_GID=$USER_GID
      - BASE_DIRECTORY=/basedir
      - SECURITY_LEVEL=normal
      - NVIDIA_VISIBLE_DEVICES=all
      - CUDA_VISIBLE_DEVICES=0

    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
        limits:
          memory: 32G

    restart: unless-stopped

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8188/system_stats"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
EOF

echo "docker-compose.yml created"
cat docker-compose.yml
```

✅ **CHECKPOINT**: docker-compose.yml exists and shows your UID/GID

---

## Phase 3: Initial ComfyUI Startup

**Goal**: Start ComfyUI for the first time (downloads ~5GB)

**Commands**:
```bash
cd ~/comfyui

# Pull the Docker image (may take 5-10 minutes)
docker compose pull

# Start ComfyUI in background
docker compose up -d

# Follow logs to see startup progress
docker compose logs -f
```

**What to Watch For**:
- "Starting ComfyUI..."
- "Loading models from /basedir/models"
- "Starting server on 0.0.0.0:8188"
- **May take 2-5 minutes for first startup**

**Wait for**: `"To see the GUI go to: http://0.0.0.0:8188"`

**Stop following logs**: Press `Ctrl+C` (container keeps running)

**Verify Container Running**:
```bash
docker ps

# Should show:
# CONTAINER ID   IMAGE                              STATUS         PORTS
# xxxxx          mmartial/comfyui-nvidia-docker     Up X seconds   0.0.0.0:8188->8188/tcp
```

✅ **CHECKPOINT**: Container running, port 8188 exposed

---

## Phase 4: Health Check & API Verification

**Goal**: Verify ComfyUI API is accessible

**Commands**:
```bash
# Wait a few seconds for ComfyUI to fully start
sleep 10

# Test local access
curl -s http://localhost:8188/system_stats | jq

# If jq not installed:
# curl -s http://localhost:8188/system_stats
```

**Expected Output** (should include):
```json
{
  "system": {
    "os": "Linux",
    "python_version": "3.11.x",
    "embedded_python": false
  },
  "devices": [
    {
      "name": "NVIDIA GeForce RTX 4090",
      "type": "cuda",
      "vram_total": 25757220864,
      "vram_free": 25757220864
    }
  ]
}
```

**If jq not installed** (optional but helpful):
```bash
# Ubuntu/WSL2
sudo apt install -y jq

# Then re-run:
curl -s http://localhost:8188/system_stats | jq
```

✅ **CHECKPOINT**: API returns system stats showing RTX 4090

---

## Phase 5: Model Directory Structure

**Goal**: Create organized directories for different model types

**Commands**:
```bash
cd ~/comfyui/models

# Create model subdirectories
mkdir -p checkpoints           # Base models (SDXL, Flux, etc.)
mkdir -p diffusion_models      # Qwen-Image-Edit and other modern diffusion models
mkdir -p text_encoders         # Text encoders (Qwen, CLIP, etc.)
mkdir -p ipadapter            # IP-Adapter models
mkdir -p loras                # LoRA fine-tunes
mkdir -p controlnet           # ControlNet models
mkdir -p model_patches        # Model patches for ControlNet variants
mkdir -p insightface/models   # Face recognition
mkdir -p clip_vision          # CLIP vision encoders
mkdir -p vae                  # VAE models
mkdir -p upscale_models       # Upscalers

# Create README for organization
cat > README.md <<'EOF'
# ComfyUI Models Directory

This directory contains all AI models for ComfyUI.

## Directory Structure

- **checkpoints/**: Base diffusion models (SDXL, Flux, SD1.5)
- **diffusion_models/**: Modern diffusion models (Qwen-Image-Edit, etc.)
- **text_encoders/**: Text encoders (Qwen 2.5 VL, CLIP, etc.)
- **ipadapter/**: IP-Adapter models for face/style preservation
- **loras/**: LoRA fine-tunes for specific styles or subjects
- **controlnet/**: ControlNet models for pose/structure control
- **model_patches/**: Model patches for ControlNet variants
- **insightface/**: Face detection and recognition models
- **clip_vision/**: CLIP vision encoders for image understanding
- **vae/**: VAE models for latent encoding/decoding
- **upscale_models/**: Image upscaling models (ESRGAN, etc.)

## Storage Requirements

### Option A: IP-Adapter-FaceID (SDXL)
- SDXL Base: ~7 GB
- IP-Adapter models: ~500 MB each
- ControlNet: ~1-2 GB each
- Total: ~20-30 GB

### Option B: Qwen-Image-Edit (Recommended)
- Qwen-Image-Edit (FP8): ~20 GB
- Text Encoder (FP8): ~7 GB
- VAE: ~300 MB
- LoRA/ControlNet (optional): ~1-5 GB
- Total: ~30-40 GB

### Both Options
- Total recommended: 80-100 GB

## Model Sources

### IP-Adapter-FaceID
- SDXL: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- IP-Adapter: https://huggingface.co/h94/IP-Adapter-FaceID
- ControlNet: https://huggingface.co/lllyasviel/ControlNet

### Qwen-Image-Edit
- Qwen-Image-Edit: https://huggingface.co/Qwen/Qwen-Image-Edit
- Model Repository: https://modelscope.cn/models/Qwen/Qwen-Image-Edit
EOF

# Verify structure
tree -L 1 ~/comfyui/models
```

✅ **CHECKPOINT**: Model directories created

---

## Phase 6: Essential Model Downloads

**Goal**: Download critical models for IP-Adapter-FaceID workflow

**⚠️ WARNING**: This will download ~20-30 GB. Ensure adequate disk space and internet.

### 6.1: SDXL Base Model (~7 GB)

```bash
cd ~/comfyui/models/checkpoints

# Download SDXL base
wget -c https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

# Verify download
ls -lh sd_xl_base_1.0.safetensors
# Should show ~6.9 GB
```

### 6.2: IP-Adapter-FaceID Models (~2 GB total)

```bash
cd ~/comfyui/models/ipadapter

# IP-Adapter FaceID PlusV2 (SDXL)
wget -c https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sdxl.bin

# IP-Adapter FaceID (SDXL)
wget -c https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sdxl.bin

# IP-Adapter base (for reference)
wget -c https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors

# Verify
ls -lh
```

### 6.3: CLIP Vision Encoder (~3.5 GB)

```bash
cd ~/comfyui/models/clip_vision

# Download CLIP ViT-H
wget -c https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors

# Rename for ComfyUI compatibility
mv model.safetensors CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors

# Verify
ls -lh
```

### 6.4: InsightFace Models (~350 MB)

```bash
cd ~/comfyui/models/insightface/models

# Clone antelopev2 model pack
git clone https://huggingface.co/DIAMONIK7777/antelopev2

# Move files to correct location
mv antelopev2/* .
rmdir antelopev2

# Verify
ls -lh
# Should show: 1k3d68.onnx, 2d106det.onnx, genderage.onnx, glintr100.onnx, scrfd_10g_bnkps.onnx
```

### 6.5: VAE (Optional but Recommended) (~300 MB)

```bash
cd ~/comfyui/models/vae

# SDXL VAE
wget -c https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors

# Verify
ls -lh
```

### 6.6: Model Download Summary

```bash
# Check total storage used
du -sh ~/comfyui/models/

# List all downloaded models
find ~/comfyui/models -type f -name "*.safetensors" -o -name "*.bin" -o -name "*.onnx" | sort
```

**Expected Total**: ~15-20 GB after essential models

✅ **CHECKPOINT**: All essential models downloaded

---

## Phase 6B: Qwen-Image-Edit Models (Alternative/Additional)

**Goal**: Download Qwen-Image-Edit for state-of-the-art image editing

**⚠️ NOTE**: This is an alternative to or addition to the IP-Adapter-FaceID models above. Qwen-Image-Edit provides superior image editing capabilities similar to Gemini 2.5 image editing.

**⚠️ WARNING**: This will download ~30-40 GB additional models.

### 6B.1: Qwen-Image-Edit Core Model (~20 GB)

```bash
cd ~/comfyui/models/diffusion_models

# Download Qwen-Image-Edit FP8 quantized model (recommended for RTX 4090)
# Using huggingface-cli for reliable downloads
pip install -U huggingface_hub

# Download the FP8 model file
huggingface-cli download Qwen/Qwen-Image-Edit \
  qwen_image_fp8_e4m3fn.safetensors \
  --local-dir . \
  --local-dir-use-symlinks False

# Verify download
ls -lh qwen_image_fp8_e4m3fn.safetensors
# Should show ~20.4 GB
```

**Alternative: GGUF version for even lower VRAM** (if needed):
```bash
# For systems with less VRAM, use GGUF quantized version
# Note: Requires ComfyUI-GGUF custom node (install in Phase 7)
huggingface-cli download city96/Qwen-Image-Edit-GGUF \
  qwen-image-edit-Q8_0.gguf \
  --local-dir . \
  --local-dir-use-symlinks False
```

### 6B.2: Qwen Text Encoder (~7 GB)

```bash
cd ~/comfyui/models/text_encoders

# Download Qwen 2.5 VL text encoder (FP8)
huggingface-cli download Qwen/Qwen-Image-Edit \
  qwen_2.5_vl_7b_fp8_scaled.safetensors \
  --local-dir . \
  --local-dir-use-symlinks False

# Verify
ls -lh qwen_2.5_vl_7b_fp8_scaled.safetensors
```

### 6B.3: Qwen VAE (~300 MB)

```bash
cd ~/comfyui/models/vae

# Download Qwen-Image VAE
huggingface-cli download Qwen/Qwen-Image-Edit \
  qwen_image_vae.safetensors \
  --local-dir . \
  --local-dir-use-symlinks False

# Verify
ls -lh qwen_image_vae.safetensors
```

### 6B.4: Qwen Lightning LoRA (Optional - for faster generation)

```bash
cd ~/comfyui/models/loras

# Download 8-step acceleration LoRA
huggingface-cli download Qwen/Qwen-Image-Edit \
  Qwen-Image-Lightning-8steps-V1.0.safetensors \
  --local-dir . \
  --local-dir-use-symlinks False

# Verify
ls -lh Qwen-Image-Lightning-8steps-V1.0.safetensors
```

### 6B.5: Qwen ControlNet (Optional - for advanced control)

```bash
cd ~/comfyui/models/controlnet

# Download ControlNet-Union for unified control
huggingface-cli download InstantX/Qwen-Image-InstantX-ControlNet-Union \
  Qwen-Image-InstantX-ControlNet-Union.safetensors \
  --local-dir . \
  --local-dir-use-symlinks False

# Verify
ls -lh Qwen-Image-InstantX-ControlNet-Union.safetensors
```

### 6B.6: Qwen Model Download Summary

```bash
# Check total storage used
du -sh ~/comfyui/models/diffusion_models/
du -sh ~/comfyui/models/text_encoders/
du -sh ~/comfyui/models/

# List all Qwen models
find ~/comfyui/models -type f -name "*qwen*" -o -name "*Qwen*" | sort
```

**Expected Total for Qwen-Image-Edit**: ~30-40 GB

**Performance Notes**:
- RTX 4090 uses ~86% VRAM during generation
- Standard generation: ~90-100 seconds
- With Lightning LoRA: ~50-60 seconds
- Supports 1024x1024 and higher resolutions

✅ **CHECKPOINT**: Qwen-Image-Edit models downloaded

---

## Phase 7: Custom Nodes Installation

**Goal**: Install ComfyUI plugins for IP-Adapter, Qwen-Image-Edit, ControlNet, etc.

**⚠️ NOTE**: Install the nodes relevant to your chosen workflow (IP-Adapter OR Qwen-Image-Edit OR both)

**Commands**:
```bash
# Enter the running container
docker exec -it comfyui-server bash

# Now inside container:

cd /basedir/custom_nodes

# === For IP-Adapter-FaceID Workflow ===

# 1. IP-Adapter Plus (REQUIRED for FaceID)
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
cd ComfyUI_IPAdapter_plus
pip install -r requirements.txt
cd ..

# 4. Impact Pack (for FaceDetailer and utilities)
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
cd ComfyUI-Impact-Pack
pip install -r requirements.txt
cd ..

# === For Qwen-Image-Edit Workflow (Native support, but optional nodes enhance functionality) ===

# 5. ComfyUI-GGUF (OPTIONAL - only if using GGUF quantized models)
git clone https://github.com/city96/ComfyUI-GGUF.git
cd ComfyUI-GGUF
pip install -r requirements.txt
cd ..

# === For Both Workflows ===

# 2. ComfyUI Essentials (useful utilities)
git clone https://github.com/cubiq/ComfyUI_essentials.git
cd ComfyUI_essentials
pip install -r requirements.txt
cd ..

# 3. ControlNet Preprocessors (for advanced control)
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
cd comfyui_controlnet_aux
pip install -r requirements.txt
cd ..

# List installed custom nodes
ls -la

# Exit container
exit
```

**Note on Qwen-Image-Edit**: Qwen-Image-Edit has **native ComfyUI support** as of 2025, meaning the core functionality works without custom nodes. However, optional nodes like ComfyUI-GGUF enable additional features (quantized models) and comfyui_controlnet_aux provides preprocessing capabilities.

**Restart ComfyUI** (to load new nodes):
```bash
cd ~/comfyui
docker compose restart

# Wait for restart
sleep 10

# Check logs
docker compose logs --tail 50
```

**Verify Custom Nodes Loaded**:
```bash
# Check object_info endpoint (lists all available nodes)
curl -s http://localhost:8188/object_info | jq 'keys | map(select(contains("IPAdapter") or contains("FaceID")))'

# Should return array including:
# ["IPAdapterFaceID", "IPAdapterModelLoader", "IPAdapterApply", ...]
```

✅ **CHECKPOINT**: Custom nodes installed and loaded

---

## Phase 8: Test Workflow Creation

**Goal**: Create and test a simple IP-Adapter-FaceID workflow

### 8.1: Create Test Subject Image

```bash
# Create test directory
mkdir -p ~/comfyui/basedir/input

# Download a test portrait image (or use your own)
cd ~/comfyui/basedir/input
wget -O test_portrait.jpg "https://thispersondoesnotexist.com/"

# Verify image downloaded
ls -lh test_portrait.jpg
```

### 8.2: Create Simple Workflow JSON

```bash
cd ~/comfyui/workflows

cat > test_basic_generation.json <<'EOF'
{
  "3": {
    "inputs": {
      "seed": 42,
      "steps": 20,
      "cfg": 7.0,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0,
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    },
    "class_type": "KSampler",
    "_meta": {"title": "KSampler"}
  },
  "4": {
    "inputs": {
      "ckpt_name": "sd_xl_base_1.0.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {"title": "Load Checkpoint"}
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {"title": "Empty Latent"}
  },
  "6": {
    "inputs": {
      "text": "portrait of a person as a high elf with pointed ears, elegant features, ethereal appearance, detailed fantasy art",
      "clip": ["4", 1]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {"title": "Positive Prompt"}
  },
  "7": {
    "inputs": {
      "text": "low quality, blurry, deformed, ugly, bad anatomy",
      "clip": ["4", 1]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {"title": "Negative Prompt"}
  },
  "8": {
    "inputs": {
      "samples": ["3", 0],
      "vae": ["4", 2]
    },
    "class_type": "VAEDecode",
    "_meta": {"title": "VAE Decode"}
  },
  "9": {
    "inputs": {
      "filename_prefix": "test_output",
      "images": ["8", 0]
    },
    "class_type": "SaveImage",
    "_meta": {"title": "Save Image"}
  }
}
EOF

echo "Test workflow created"
```

### 8.3: Test Generation via API

```bash
# Queue the test workflow
curl -X POST http://localhost:8188/prompt \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "prompt": {
    "3": {
      "inputs": {
        "seed": 42,
        "steps": 20,
        "cfg": 7.0,
        "sampler_name": "euler",
        "scheduler": "normal",
        "denoise": 1.0,
        "model": ["4", 0],
        "positive": ["6", 0],
        "negative": ["7", 0],
        "latent_image": ["5", 0]
      },
      "class_type": "KSampler"
    },
    "4": {
      "inputs": {
        "ckpt_name": "sd_xl_base_1.0.safetensors"
      },
      "class_type": "CheckpointLoaderSimple"
    },
    "5": {
      "inputs": {
        "width": 1024,
        "height": 1024,
        "batch_size": 1
      },
      "class_type": "EmptyLatentImage"
    },
    "6": {
      "inputs": {
        "text": "portrait of a person as a high elf, detailed fantasy art",
        "clip": ["4", 1]
      },
      "class_type": "CLIPTextEncode"
    },
    "7": {
      "inputs": {
        "text": "low quality, blurry, deformed",
        "clip": ["4", 1]
      },
      "class_type": "CLIPTextEncode"
    },
    "8": {
      "inputs": {
        "samples": ["3", 0],
        "vae": ["4", 2]
      },
      "class_type": "VAEDecode"
    },
    "9": {
      "inputs": {
        "filename_prefix": "test_output",
        "images": ["8", 0]
      },
      "class_type": "SaveImage"
    }
  },
  "client_id": "test-client-123"
}
EOF
```

**Expected Response**:
```json
{
  "prompt_id": "abc-123-def-456",
  "number": 1,
  "node_errors": {}
}
```

**Save the prompt_id** from response, then check status:
```bash
# Replace PROMPT_ID with actual value
PROMPT_ID="abc-123-def-456"

# Poll for completion (may take 15-30 seconds)
while true; do
  STATUS=$(curl -s http://localhost:8188/history/$PROMPT_ID | jq -r ".[\"$PROMPT_ID\"] | has(\"outputs\")")
  echo "Checking status... Complete: $STATUS"
  if [ "$STATUS" = "true" ]; then
    break
  fi
  sleep 2
done

echo "Generation complete!"

# Get output image info
curl -s http://localhost:8188/history/$PROMPT_ID | jq ".[\"$PROMPT_ID\"].outputs"
```

**Check Output**:
```bash
# List generated images
ls -lh ~/comfyui/output/

# Should see: test_output_00001_.png (or similar)
```

✅ **CHECKPOINT**: Test image generated successfully

---

## Phase 8B: Qwen-Image-Edit Workflow Testing

**Goal**: Create and test a Qwen-Image-Edit workflow for image editing

**⚠️ NOTE**: Only complete this phase if you installed Qwen-Image-Edit models in Phase 6B

### 8B.1: Access Qwen Workflow Templates

ComfyUI includes native workflow templates for Qwen-Image-Edit:

**Via ComfyUI Web UI** (easiest):
1. Open http://localhost:8188 in browser
2. Click template icon in sidebar
3. Navigate to: Browse Templates → Image → Qwen Image Edit
4. Select a template to load

**Via API** (for testing):

### 8B.2: Create Simple Qwen Edit Workflow

```bash
cd ~/comfyui/workflows

cat > qwen_image_edit_test.json <<'EOF'
{
  "1": {
    "inputs": {
      "model_name": "qwen_image_fp8_e4m3fn.safetensors"
    },
    "class_type": "DiffusionModelLoader",
    "_meta": {"title": "Load Qwen Model"}
  },
  "2": {
    "inputs": {
      "text_encoder_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors"
    },
    "class_type": "DualCLIPLoader",
    "_meta": {"title": "Load Text Encoder"}
  },
  "3": {
    "inputs": {
      "vae_name": "qwen_image_vae.safetensors"
    },
    "class_type": "VAELoader",
    "_meta": {"title": "Load VAE"}
  },
  "4": {
    "inputs": {
      "image": "test_portrait.jpg",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {"title": "Load Input Image"}
  },
  "5": {
    "inputs": {
      "text": "Transform this person into a cyberpunk character with neon hair and futuristic clothing",
      "clip": ["2", 0]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {"title": "Edit Prompt"}
  },
  "6": {
    "inputs": {
      "seed": 42,
      "steps": 50,
      "cfg": 4.0,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 0.85,
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
      "text": "blurry, low quality, distorted",
      "clip": ["2", 0]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {"title": "Negative Prompt"}
  },
  "8": {
    "inputs": {
      "pixels": ["4", 0],
      "vae": ["3", 0]
    },
    "class_type": "VAEEncode",
    "_meta": {"title": "Encode Image"}
  },
  "9": {
    "inputs": {
      "samples": ["6", 0],
      "vae": ["3", 0]
    },
    "class_type": "VAEDecode",
    "_meta": {"title": "Decode Result"}
  },
  "10": {
    "inputs": {
      "filename_prefix": "qwen_edit_test",
      "images": ["9", 0]
    },
    "class_type": "SaveImage",
    "_meta": {"title": "Save Edited Image"}
  }
}
EOF

echo "Qwen test workflow created"
```

### 8B.3: Prepare Test Image

```bash
# Ensure test image exists
cd ~/comfyui/basedir/input
ls -lh test_portrait.jpg

# If not present, download one:
wget -O test_portrait.jpg "https://thispersondoesnotexist.com/"
```

### 8B.4: Test Qwen via ComfyUI Web UI

1. Open http://localhost:8188 in browser on the RTX PC
2. Load the workflow template for Qwen-Image-Edit
3. Upload your test image
4. Enter an edit prompt like: "Make this person look like a fantasy elf with pointed ears and magical aura"
5. Click "Queue Prompt"
6. Monitor progress (will take ~90 seconds on RTX 4090)
7. View result in output folder

### 8B.5: Verify Qwen Performance

```bash
# Monitor GPU usage during generation
watch -n 1 nvidia-smi

# Check generation output
ls -lh ~/comfyui/output/qwen_edit_test*

# Review container logs for any errors
docker compose logs --tail 100 | grep -i qwen
```

**Expected Performance**:
- VRAM Usage: ~20-21 GB (~86% of RTX 4090)
- Generation Time: 90-100 seconds (50 steps)
- With Lightning LoRA: 50-60 seconds (8 steps)

**Qwen-Image-Edit Capabilities**:
- **Semantic Editing**: Change style, appearance, objects while maintaining identity
- **Text Editing**: Add/modify/remove text in multiple languages
- **Appearance Editing**: Precise modifications with unchanged regions preserved
- **High Resolution**: Supports 1024x1024 and higher

✅ **CHECKPOINT**: Qwen-Image-Edit workflow tested successfully

---

## Phase 9: Network Access Testing (From Mac Studio)

**Goal**: Verify Mac Studio can access ComfyUI API

**On Mac Studio, run**:
```bash
# Replace with your RTX PC's IP
RTX_PC_IP="192.168.1.100"

# Test system stats endpoint
curl -s http://$RTX_PC_IP:8188/system_stats | jq

# Should return JSON with RTX 4090 info
```

**If successful**, you should see:
```json
{
  "system": { ... },
  "devices": [
    {
      "name": "NVIDIA GeForce RTX 4090",
      "vram_total": 25757220864
    }
  ]
}
```

**If this fails**:
- Check firewall on RTX PC (port 8188)
- Verify Docker is exposing port: `docker ps` should show `0.0.0.0:8188->8188/tcp`
- Check network connectivity: `ping 192.168.1.100` from Mac

✅ **CHECKPOINT**: Mac Studio can access ComfyUI API

---

## Phase 10: Create Startup Script

**Goal**: Easy start/stop/restart of ComfyUI

```bash
cd ~/comfyui

cat > comfyui.sh <<'EOF'
#!/bin/bash

# ComfyUI Management Script

case "$1" in
  start)
    echo "Starting ComfyUI..."
    docker compose up -d
    echo "Waiting for startup..."
    sleep 10
    docker compose logs --tail 20
    echo ""
    echo "ComfyUI started. Access at: http://$(hostname -I | awk '{print $1}'):8188"
    ;;

  stop)
    echo "Stopping ComfyUI..."
    docker compose down
    echo "ComfyUI stopped."
    ;;

  restart)
    echo "Restarting ComfyUI..."
    docker compose restart
    echo "Waiting for restart..."
    sleep 10
    docker compose logs --tail 20
    ;;

  logs)
    docker compose logs -f
    ;;

  status)
    docker compose ps
    echo ""
    curl -s http://localhost:8188/system_stats | jq -r '.devices[] | "GPU: \(.name), VRAM: \(.vram_total / 1024 / 1024 / 1024 | floor)GB"'
    ;;

  update)
    echo "Pulling latest ComfyUI image..."
    docker compose pull
    echo "Restarting with new image..."
    docker compose up -d
    ;;

  *)
    echo "Usage: $0 {start|stop|restart|logs|status|update}"
    exit 1
    ;;
esac
EOF

chmod +x comfyui.sh

echo "Management script created. Usage:"
echo "  ./comfyui.sh start    - Start ComfyUI"
echo "  ./comfyui.sh stop     - Stop ComfyUI"
echo "  ./comfyui.sh restart  - Restart ComfyUI"
echo "  ./comfyui.sh logs     - View logs (Ctrl+C to exit)"
echo "  ./comfyui.sh status   - Show status"
echo "  ./comfyui.sh update   - Update to latest version"
```

✅ **CHECKPOINT**: Management script created

---

## Phase 11: Auto-Start on Boot (Optional)

**Goal**: ComfyUI starts automatically when PC boots

### Option A: Docker Auto-Restart (Already Configured)

The `docker-compose.yml` already includes `restart: unless-stopped`, which means Docker will auto-start the container on boot (if Docker itself starts on boot).

**Verify Docker starts on boot**:

**Ubuntu**:
```bash
sudo systemctl enable docker
sudo systemctl status docker
```

**Windows + WSL2**:
- Docker Desktop should be set to "Start Docker Desktop when you log in" (in Settings)

### Option B: Systemd Service (Ubuntu Only)

```bash
# Create systemd service
sudo tee /etc/systemd/system/comfyui.service > /dev/null <<EOF
[Unit]
Description=ComfyUI Docker Container
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/$USER/comfyui
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=$USER

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl enable comfyui.service

# Test service
sudo systemctl start comfyui.service
sudo systemctl status comfyui.service
```

✅ **CHECKPOINT**: Auto-start configured (if desired)

---

## Phase 12: Create Info File for Life-OS Integration

**Goal**: Document connection details for Life-OS

```bash
cd ~/comfyui

cat > CONNECTION_INFO.txt <<EOF
# ComfyUI Connection Information

## Network Details
- **IP Address**: $(hostname -I | awk '{print $1}')
- **Port**: 8188
- **Base URL**: http://$(hostname -I | awk '{print $1}'):8188

## API Endpoints
- Health Check: http://$(hostname -I | awk '{print $1}'):8188/system_stats
- Queue Prompt: http://$(hostname -I | awk '{print $1}'):8188/prompt
- Get History: http://$(hostname -I | awk '{print $1}'):8188/history/{prompt_id}
- Download Image: http://$(hostname -I | awk '{print $1}'):8188/view?filename={filename}&type=output

## Environment Variables for Life-OS .env
COMFYUI_ENABLED=true
COMFYUI_URL=http://$(hostname -I | awk '{print $1}'):8188
COMFYUI_TIMEOUT=300

## Test Connection
From Mac Studio, run:
curl http://$(hostname -I | awk '{print $1}'):8188/system_stats | jq

## Installed Models
$(find ~/comfyui/models -type f \( -name "*.safetensors" -o -name "*.bin" -o -name "*.onnx" \) -exec ls -lh {} \; | awk '{print $9, "-", $5}')

## Management Commands
Start:   ~/comfyui/comfyui.sh start
Stop:    ~/comfyui/comfyui.sh stop
Restart: ~/comfyui/comfyui.sh restart
Logs:    ~/comfyui/comfyui.sh logs
Status:  ~/comfyui/comfyui.sh status

## Directory Structure
- Models:    ~/comfyui/models/
- Workflows: ~/comfyui/workflows/
- Output:    ~/comfyui/output/
- Logs:      ~/comfyui/logs/

## Installed Custom Nodes
$(docker exec comfyui-server ls /basedir/custom_nodes)

## Setup Date
$(date)
EOF

cat CONNECTION_INFO.txt
```

**Copy this file to Mac Studio** (via network share, USB, email, etc.)

✅ **CHECKPOINT**: Setup complete!

---

## 🎉 Setup Complete!

Your RTX 4090 PC is now running ComfyUI and ready to integrate with Life-OS.

### Quick Verification Checklist

Run these commands to verify everything works:

```bash
# 1. Container running
docker ps | grep comfyui-server

# 2. API accessible locally
curl -s http://localhost:8188/system_stats | jq '.devices[0].name'
# Should output: "NVIDIA GeForce RTX 4090"

# 3. Models loaded
ls ~/comfyui/models/checkpoints/
ls ~/comfyui/models/ipadapter/
ls ~/comfyui/models/clip_vision/

# 4. Custom nodes installed
docker exec comfyui-server ls /basedir/custom_nodes | grep IPAdapter

# 5. Test generation works
~/comfyui/comfyui.sh status
```

### Next Steps

1. **Copy CONNECTION_INFO.txt to Mac Studio**
2. **Update Life-OS .env** with ComfyUI URL
3. **Test from Mac Studio**: `curl http://YOUR_PC_IP:8188/system_stats`
4. **Begin Life-OS integration** (ComfyUIService implementation)

---

## 📊 System Information

**Storage Used**:
```bash
du -sh ~/comfyui/
```

**GPU Status**:
```bash
nvidia-smi
```

**Docker Resources**:
```bash
docker stats comfyui-server --no-stream
```

---

## 🎨 Qwen-Image-Edit Usage Examples

### Example 1: Semantic Style Transfer
**Input Image**: Portrait photo
**Prompt**: "Transform into a watercolor painting style"
**Parameters**: 50 steps, CFG 4.0, denoise 0.75

### Example 2: Object Modification
**Input Image**: Room interior
**Prompt**: "Replace the sofa with a modern minimalist couch"
**Parameters**: 50 steps, CFG 4.0, denoise 0.85

### Example 3: Text Editing
**Input Image**: Store sign with text
**Prompt**: "Change the store name to 'Golden Dragon Restaurant' in Chinese and English"
**Parameters**: 50 steps, CFG 4.0, denoise 0.90

### Example 4: Appearance Enhancement
**Input Image**: Product photo
**Prompt**: "Make the product more vibrant and add professional studio lighting"
**Parameters**: 50 steps, CFG 4.0, denoise 0.60

### Example 5: Fantasy/Creative Edits
**Input Image**: Portrait
**Prompt**: "Transform into an elven warrior with pointed ears, ethereal glow, and fantasy armor"
**Parameters**: 50 steps, CFG 4.0, denoise 0.85

### Parameter Tuning Guide

**Denoise Strength**:
- 0.3-0.5: Subtle changes, preserve original heavily
- 0.6-0.8: Balanced editing, recommended for most tasks
- 0.9-1.0: Strong modifications, less preservation

**CFG Scale**:
- 2.0-3.0: Very subtle prompt adherence
- 4.0-5.0: Recommended balance (default)
- 6.0-8.0: Strong prompt adherence, may lose naturalness

**Steps**:
- 8 steps: Use with Lightning LoRA only
- 20-30 steps: Fast preview quality
- 50 steps: Standard quality (recommended)
- 100+ steps: Diminishing returns, longer generation

### API Call Example for Life-OS

```python
import httpx
import asyncio

async def edit_image_qwen(image_path: str, prompt: str):
    """
    Edit an image using Qwen-Image-Edit via ComfyUI API
    """
    workflow = {
        "1": {
            "inputs": {"model_name": "qwen_image_fp8_e4m3fn.safetensors"},
            "class_type": "DiffusionModelLoader"
        },
        "2": {
            "inputs": {"text_encoder_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors"},
            "class_type": "DualCLIPLoader"
        },
        "3": {
            "inputs": {"vae_name": "qwen_image_vae.safetensors"},
            "class_type": "VAELoader"
        },
        "4": {
            "inputs": {"image": image_path, "upload": "image"},
            "class_type": "LoadImage"
        },
        "5": {
            "inputs": {"text": prompt, "clip": ["2", 0]},
            "class_type": "CLIPTextEncode"
        },
        "6": {
            "inputs": {
                "seed": 42,
                "steps": 50,
                "cfg": 4.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 0.85,
                "model": ["1", 0],
                "positive": ["5", 0],
                "negative": ["7", 0],
                "latent_image": ["8", 0]
            },
            "class_type": "KSampler"
        },
        "7": {
            "inputs": {"text": "blurry, low quality", "clip": ["2", 0]},
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {"pixels": ["4", 0], "vae": ["3", 0]},
            "class_type": "VAEEncode"
        },
        "9": {
            "inputs": {"samples": ["6", 0], "vae": ["3", 0]},
            "class_type": "VAEDecode"
        },
        "10": {
            "inputs": {"filename_prefix": "qwen_result", "images": ["9", 0]},
            "class_type": "SaveImage"
        }
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        # Queue the prompt
        response = await client.post(
            "http://YOUR_PC_IP:8188/prompt",
            json={"prompt": workflow, "client_id": "life-os"}
        )
        prompt_id = response.json()["prompt_id"]

        # Poll for completion
        while True:
            history = await client.get(f"http://YOUR_PC_IP:8188/history/{prompt_id}")
            if prompt_id in history.json() and "outputs" in history.json()[prompt_id]:
                return history.json()[prompt_id]["outputs"]
            await asyncio.sleep(2)

# Usage
result = await edit_image_qwen("input.jpg", "Transform into cyberpunk style")
```

---

## 🔧 Troubleshooting

### Issue: "CUDA not available" or "No GPU detected"

**Check**:
```bash
# On host (outside Docker)
nvidia-smi

# Inside Docker
docker exec comfyui-server nvidia-smi
```

**Solutions**:
- Ensure NVIDIA drivers installed: `nvidia-smi` should work on host
- Verify Container Toolkit: `sudo nvidia-ctk --version`
- Check docker-compose.yml has `runtime: nvidia` and deploy section
- Restart Docker: `sudo systemctl restart docker`

---

### Issue: "Port 8188 already in use"

**Check**:
```bash
sudo lsof -i :8188
# OR
sudo netstat -tulpn | grep 8188
```

**Solutions**:
- Kill process using port
- Change port in docker-compose.yml: `"8189:8188"` (use 8189 externally)

---

### Issue: "Connection refused" from Mac Studio

**Check**:
1. **Firewall**: `sudo ufw status` (Ubuntu) or Windows Firewall
2. **Docker port binding**: `docker ps` → should show `0.0.0.0:8188`
3. **Network reachable**: `ping YOUR_PC_IP` from Mac

**Solutions**:
- Add firewall rule: `sudo ufw allow 8188/tcp`
- Ensure docker-compose has `"0.0.0.0:8188:8188"` not `"127.0.0.1:8188:8188"`
- Check static IP is correct

---

### Issue: Model download failed (wget errors)

**Solutions**:
- Resume download: `wget -c URL` (continues partial download)
- Use alternative: `curl -L -O URL`
- Manual download from browser, then upload to server
- Check disk space: `df -h`

---

### Issue: Out of VRAM during generation

**Check**:
```bash
docker exec comfyui-server nvidia-smi
```

**Solutions**:
- Use smaller batch size (1 instead of 4)
- Reduce image resolution (768x768 instead of 1024x1024)
- Unload models between jobs (automatic in ComfyUI)
- Check no other GPU processes running

---

### Issue: Custom nodes not loading

**Check**:
```bash
docker compose logs | grep -i "error"
docker exec comfyui-server ls /basedir/custom_nodes
```

**Solutions**:
- Reinstall dependencies:
  ```bash
  docker exec -it comfyui-server bash
  cd /basedir/custom_nodes/ComfyUI_IPAdapter_plus
  pip install -r requirements.txt
  exit
  docker compose restart
  ```
- Check logs for import errors
- Verify model files in correct locations

---

### Issue: Qwen-Image-Edit model not loading or "Model not found"

**Check**:
```bash
# Verify models are in correct directories
ls -lh ~/comfyui/models/diffusion_models/qwen*
ls -lh ~/comfyui/models/text_encoders/qwen*
ls -lh ~/comfyui/models/vae/qwen*

# Check ComfyUI logs for model loading errors
docker compose logs | grep -i qwen
```

**Solutions**:
- Ensure models are in the correct subdirectories (`diffusion_models`, `text_encoders`, `vae`)
- Verify model file names match exactly (case-sensitive)
- Check ComfyUI version supports Qwen (requires nightly build from 2025)
- Restart ComfyUI after adding models: `~/comfyui/comfyui.sh restart`

---

### Issue: Qwen generation runs out of VRAM

**Check**:
```bash
docker exec comfyui-server nvidia-smi
```

**Solutions**:
- Use FP8 quantized models (not BF16 full precision)
- Use GGUF quantized version with ComfyUI-GGUF node
- Close other GPU applications
- Reduce batch size to 1
- Lower resolution (try 768x768 instead of 1024x1024)
- Clear VRAM between generations (automatic in ComfyUI)

---

### Issue: Qwen generation is very slow

**Check**:
```bash
# Monitor GPU utilization
nvidia-smi -l 1

# Should show ~95-100% GPU utilization during generation
```

**Solutions**:
- Install Lightning LoRA for 8-step acceleration (6x faster)
- Ensure CUDA is being used: Check logs for "Using device: cuda"
- Reduce steps: 30-40 steps often sufficient for previews
- Use distilled model variant if available
- Check no other processes using GPU: `nvidia-smi`

---

### Issue: Qwen edits don't match the prompt

**Check**:
- Review denoise and CFG parameters
- Check prompt clarity and specificity

**Solutions**:
- **Increase CFG scale**: 5.0-6.0 for stronger prompt adherence
- **Adjust denoise**:
  - Too low (< 0.5): Changes too subtle
  - Too high (> 0.9): May deviate from original too much
  - Sweet spot: 0.7-0.85 for most edits
- **Improve prompt**: Be specific about desired changes
- **Use negative prompt**: Specify what to avoid
- **Increase steps**: Try 70-100 steps for complex edits

---

## 📚 Additional Resources

### General ComfyUI
- **ComfyUI Official**: https://github.com/comfyanonymous/ComfyUI
- **ComfyUI Documentation**: https://docs.comfy.org/
- **ComfyUI Workflows**: https://comfyworkflows.com/

### IP-Adapter Resources
- **IP-Adapter**: https://github.com/cubiq/ComfyUI_IPAdapter_plus
- **IP-Adapter Models**: https://huggingface.co/h94/IP-Adapter-FaceID

### Qwen-Image-Edit Resources
- **Qwen-Image-Edit Official**: https://huggingface.co/Qwen/Qwen-Image-Edit
- **Qwen Documentation**: https://qwen.readthedocs.io/
- **ComfyUI Qwen Guide**: https://docs.comfy.org/tutorials/image/qwen/qwen-image
- **Model Repository (ModelScope)**: https://modelscope.cn/models/Qwen/Qwen-Image-Edit
- **Qwen-Image-Edit Blog**: https://blog.comfy.org/p/qwen-image-edit-comfyui-support

### Model Hubs
- **Hugging Face**: https://huggingface.co/models
- **CivitAI**: https://civitai.com/

---

## 🔄 Maintenance Tasks

### Weekly
- Check for ComfyUI updates: `~/comfyui/comfyui.sh update`
- Monitor disk space: `df -h`
- Review logs for errors: `~/comfyui/comfyui.sh logs | grep -i error`

### Monthly
- Update NVIDIA drivers
- Update Docker: `sudo apt update && sudo apt upgrade docker-ce`
- Clean old generated images: `find ~/comfyui/output -mtime +30 -delete`
- Backup workflows: `tar -czf workflows_backup.tar.gz ~/comfyui/workflows/`

### As Needed
- Download new models (LoRAs, ControlNets)
- Install new custom nodes
- Update workflows

---

## 📊 Workflow Comparison: IP-Adapter vs Qwen-Image-Edit

### IP-Adapter-FaceID (SDXL-based)

**Best For**:
- Face preservation across style transfers
- Portrait generation with specific identity
- Combining facial features from reference images
- Established workflows with extensive community support

**Strengths**:
- Lower VRAM usage (~12-15 GB)
- Faster generation (~15-30 seconds)
- Mature ecosystem, many tutorials
- Smaller model downloads (~20-30 GB)

**Limitations**:
- Limited to SDXL capabilities
- Less flexible for general image editing
- Focused primarily on face/portrait tasks

### Qwen-Image-Edit (RECOMMENDED)

**Best For**:
- Advanced image editing similar to Gemini 2.5
- Semantic modifications (style, objects, appearance)
- Text editing in images (bilingual Chinese/English)
- Precise appearance editing with region preservation
- Professional editing workflows

**Strengths**:
- State-of-the-art editing capabilities (2025)
- Native ComfyUI support
- Handles both semantic AND appearance edits
- Superior text rendering and editing
- Multilingual support
- Apache 2.0 license (commercial use OK)

**Limitations**:
- Higher VRAM usage (~20-21 GB)
- Slower generation (~90 seconds standard, ~50s with Lightning)
- Larger model downloads (~30-40 GB)
- Newer model, smaller community

### Recommendation for Life-OS / Nanobanana-like Tasks

**Use Qwen-Image-Edit** if your goal is to replicate Gemini 2.5 image editing capabilities. It provides:
- More powerful editing capabilities
- Better semantic understanding
- Superior text handling
- More versatile for diverse editing tasks

**Use IP-Adapter-FaceID** if you specifically need:
- Fast face-based style transfer
- Lower resource requirements
- Established workflow compatibility

**Use Both** if you have the storage (recommended):
- Qwen for general editing tasks
- IP-Adapter for specialized face operations
- Total: ~60-70 GB models

---

## 📝 Notes for Life-OS Integration

**Add to Life-OS `.env`**:
```bash
COMFYUI_ENABLED=true
COMFYUI_URL=http://YOUR_PC_IP:8188
COMFYUI_TIMEOUT=300
COMFYUI_DEFAULT_WORKFLOW=qwen-image-edit  # or ip-adapter-faceid
```

**Test from Life-OS API container**:
```bash
docker exec ai-studio-api python3 -c "
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://YOUR_PC_IP:8188/system_stats')
        print(response.json())

asyncio.run(test())
"
```

---

**Setup Complete! ComfyUI is ready for Life-OS integration.**
