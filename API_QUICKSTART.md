# API Quickstart Guide

Complete guide for running and using the AI-Studio API.

## Quick Start

### Option 1: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start API server
./run_api.sh

# Or manually:
python3 -m uvicorn api.main:app --reload --port 8000
```

### Option 2: Run with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Access Points

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Volume Configuration (Docker)

The Docker setup mounts these directories as volumes:

```yaml
volumes:
  - ./presets:/app/presets      # User presets (persistent)
  - ./output:/app/output        # Generated images (persistent)
  - ./cache:/app/cache          # Analysis cache (can be ephemeral)
  - ./uploads:/app/uploads      # Temporary uploads
```

All presets and generated images persist across container restarts.

## API Endpoints

### Discovery

```bash
# Get API info
curl http://localhost:8000/

# List all tools
curl http://localhost:8000/tools

# Get tool info
curl http://localhost:8000/tools/outfit

# List preset categories
curl http://localhost:8000/presets

# List presets in category
curl http://localhost:8000/presets/outfits
```

### Analyzers

```bash
# Analyze outfit (with URL)
curl -X POST http://localhost:8000/analyze/outfit \
  -H "Content-Type: application/json" \
  -d '{
    "image": {"image_url": "http://example.com/photo.jpg"},
    "save_as_preset": "my-outfit"
  }'

# Analyze with uploaded file
curl -X POST http://localhost:8000/analyze/upload \
  -F "file=@photo.jpg"

# Then use the returned URL
curl -X POST http://localhost:8000/analyze/outfit \
  -H "Content-Type: application/json" \
  -d '{
    "image": {"image_url": "http://localhost:8000/uploads/photo.jpg"}
  }'

# Run comprehensive analysis
curl -X POST http://localhost:8000/analyze/comprehensive \
  -H "Content-Type: application/json" \
  -d '{
    "image": {"image_url": "http://example.com/photo.jpg"},
    "save_as_preset": "complete-look"
  }'
```

Available analyzers:
- `outfit` - Clothing analysis
- `visual-style` - Photographic style
- `art-style` - Artistic style
- `hair-style` - Hair structure
- `hair-color` - Hair color
- `makeup` - Makeup analysis
- `expression` - Facial expression
- `accessories` - Accessories
- `comprehensive` - All of the above

### Generators

```bash
# Generate with presets
curl -X POST http://localhost:8000/generate/modular \
  -H "Content-Type: application/json" \
  -d '{
    "subject_image": {"image_url": "http://example.com/subject.jpg"},
    "outfit": "casual-outfit",
    "visual_style": "film-noir",
    "temperature": 0.8
  }'

# Style transfer
curl -X POST http://localhost:8000/generate/style-transfer \
  -H "Content-Type": application/json" \
  -d '{
    "subject_image": {"image_url": "http://example.com/subject.jpg"},
    "visual_style": "vintage-warm"
  }'
```

Available generators:
- `modular` - Combine any specs
- `outfit` - Outfit + style
- `style-transfer` - Visual style only
- `art-style` - Artistic rendering
- `combined` - Multi-spec transformation

### Preset Management

```bash
# List all presets in category
curl http://localhost:8000/presets/outfits

# Get specific preset
curl http://localhost:8000/presets/outfits/casual-outfit

# Create preset
curl -X POST http://localhost:8000/presets/outfits \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-outfit",
    "data": {
      "style_genre": "casual",
      "formality": "casual",
      "clothing_items": []
    },
    "notes": "Custom preset"
  }'

# Update preset
curl -X PUT http://localhost:8000/presets/outfits/my-outfit \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "style_genre": "smart casual",
      "formality": "semi-formal"
    }
  }'

# Delete preset
curl -X DELETE http://localhost:8000/presets/outfits/my-outfit

# Duplicate preset
curl -X POST "http://localhost:8000/presets/outfits/casual-outfit/duplicate?new_name=casual-outfit-v2"
```

## Python Client Example

```python
import httpx

# Create client
client = httpx.Client(base_url="http://localhost:8000")

# Analyze outfit
response = client.post("/analyze/outfit", json={
    "image": {"image_url": "http://example.com/photo.jpg"},
    "save_as_preset": "my-outfit"
})
result = response.json()

# Generate image
response = client.post("/generate/modular", json={
    "subject_image": {"image_url": "http://example.com/subject.jpg"},
    "outfit": "my-outfit",
    "visual_style": "film-noir"
})
generation = response.json()

# Download generated image
if generation["status"] == "completed":
    image_url = generation["result"]["image_url"]
    image_response = client.get(image_url)
    with open("generated.png", "wb") as f:
        f.write(image_response.content)
```

## JavaScript/TypeScript Example

```javascript
const API_BASE = 'http://localhost:8000';

// Analyze outfit
const analyzeResponse = await fetch(`${API_BASE}/analyze/outfit`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    image: { image_url: 'http://example.com/photo.jpg' },
    save_as_preset: 'my-outfit'
  })
});
const analysis = await analyzeResponse.json();

// Generate image
const generateResponse = await fetch(`${API_BASE}/generate/modular`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    subject_image: { image_url: 'http://example.com/subject.jpg' },
    outfit: 'my-outfit',
    visual_style: 'film-noir'
  })
});
const generation = await generateResponse.json();

// Display generated image
if (generation.status === 'completed') {
  const imgElement = document.createElement('img');
  imgElement.src = `${API_BASE}${generation.result.image_url}`;
  document.body.appendChild(imgElement);
}
```

## Response Examples

### Analysis Response

```json
{
  "status": "completed",
  "result": {
    "style_genre": "casual",
    "formality": "casual",
    "clothing_items": [
      {
        "item": "leather jacket",
        "fabric": "brown leather",
        "color": "chocolate brown",
        "details": "..."
      }
    ]
  },
  "preset_path": "presets/outfits/my-outfit.json",
  "cost": 0.001,
  "cache_hit": false,
  "processing_time": 3.2
}
```

### Generation Response

```json
{
  "status": "completed",
  "result": {
    "image_url": "/output/generated/subject_modular_20251014_163502.png",
    "generation_time": 9.5,
    "cost": 0.04
  }
}
```

## Environment Variables

Create `.env` file:

```bash
# Required
GEMINI_API_KEY=your_gemini_key_here

# Optional (for video tools)
OPENAI_API_KEY=your_openai_key_here

# API Configuration (optional)
API_TITLE="AI-Studio API"
API_VERSION="1.0.0"
HOST="0.0.0.0"
PORT=8000
CORS_ORIGINS=["*"]
```

## Docker Management

```bash
# Build image
docker-compose build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v

# Restart
docker-compose restart

# Shell into container
docker-compose exec api bash
```

## Troubleshooting

### Port Already in Use

```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000

# Or kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### API Keys Not Working

```bash
# Check environment variables in container
docker-compose exec api env | grep API_KEY

# Verify .env file is in project root
ls -la .env
```

### Volumes Not Persisting

```bash
# Check volume mounts
docker-compose config

# Verify directories exist
ls -la presets/ output/

# Check permissions
docker-compose exec api ls -la /app/presets
```

### Import Errors

```bash
# Rebuild with no cache
docker-compose build --no-cache

# Check Python path in container
docker-compose exec api python3 -c "import sys; print(sys.path)"
```

## Production Deployment

### Security

1. **Change CORS origins**:
```yaml
environment:
  - CORS_ORIGINS=["https://yourdomain.com"]
```

2. **Add authentication**: Implement JWT or API keys

3. **Use HTTPS**: Put behind nginx with SSL

4. **Rate limiting**: Add rate limiting middleware

5. **Secrets management**: Use Docker secrets or vault

### Scaling

```yaml
# docker-compose.yml
deploy:
  replicas: 3
  resources:
    limits:
      cpus: '4.0'
      memory: 8G
```

### Monitoring

```yaml
# Add health checks
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
```

## Next Steps

1. Test with CLI tools first
2. Try API endpoints with curl
3. Build web frontend
4. Add authentication
5. Deploy to production

For full documentation, see `API_ARCHITECTURE.md`.
