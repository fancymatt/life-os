# Local LLM Integration Guide

**Status**: ✅ Implemented
**Last Updated**: 2025-10-16

---

## Overview

Life-OS now supports running local LLMs via **Ollama**, enabling:
- **Zero API costs** - Run models locally for free
- **Privacy** - Data never leaves your machine
- **Offline operation** - Works without internet
- **Customization** - Use any model from Ollama registry

---

## Quick Start

### 1. Start Ollama Service

```bash
# Start Ollama container
docker-compose up -d ollama

# Check Ollama status
curl http://localhost:11434/api/tags
```

### 2. Pull a Model

Via API:
```bash
curl -X POST http://localhost:8000/local-models/pull \
  -H "Content-Type: application/json" \
  -d '{"model_name": "llama3.2:3b"}'
```

Via CLI (inside ollama container):
```bash
docker exec -it ai-studio-ollama ollama pull llama3.2:3b
```

### 3. Use in Tools

Configure any tool to use a local model:

```bash
curl -X PUT http://localhost:8000/tool-configs/tools/outfit_analyzer \
  -H "Content-Type: application/json" \
  -d '{"model": "ollama/llama3.2:3b"}'
```

---

## Model Recommendations

### Small Models (2-4GB) - Fast, Good for Testing
| Model | Size | Use Case |
|-------|------|----------|
| `llama3.2:3b` | ~2GB | General purpose, fast |
| `phi3:mini` | ~2.3GB | Microsoft's efficient model |
| `gemma2:2b` | ~1.6GB | Very fast, lightweight |

### Medium Models (4-8GB) - Balanced Performance
| Model | Size | Use Case |
|-------|------|----------|
| `llama2:7b` | ~4GB | Reliable, well-tested |
| `mistral:7b` | ~4GB | Fast inference, good quality |
| `qwen2.5:7b` | ~4.7GB | Strong reasoning & coding |
| `codellama:7b` | ~4GB | Code generation |

### Large Models (26-50GB) - Powerful but Slow
| Model | Size | Use Case |
|-------|------|----------|
| `mixtral:8x7b` | ~26GB | Mixture of experts, very powerful |
| `qwen2.5:32b` | ~19GB | Strong reasoning |
| `llama3.1:70b` | ~40GB | Near GPT-4 quality |

### XLarge Models (40GB+) - Requires Significant Resources
| Model | Size | Use Case |
|-------|------|----------|
| `qwen2.5:72b` | ~41GB | GPT-4 class performance |
| `llama3.1:405b` | ~231GB | Cutting-edge (multi-GPU) |

---

## API Endpoints

### Model Management

```bash
# Get Ollama status
GET /local-models/status

# List downloaded models
GET /local-models/

# Get model info
GET /local-models/{model_name}

# Pull a model (background task)
POST /local-models/pull
{
  "model_name": "llama3.2:3b",
  "insecure": false
}

# Delete a model
DELETE /local-models/{model_name}

# Test a model
POST /local-models/test/{model_name}?prompt=Tell%20me%20a%20joke
```

### Using Local Models in Tools

Local models are accessed via LiteLLM with the `ollama/` prefix:

```python
# In router.py or any tool
router = LLMRouter(model="ollama/llama3.2:3b")
response = router.call("Analyze this image...")
```

```bash
# Via API
curl -X POST http://localhost:8000/analyze/outfit_analyzer \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/app/subjects/image.jpg",
    "model": "ollama/mistral:7b"
  }'
```

---

## Configuration

### models.yaml

```yaml
# Add local model aliases
aliases:
  llama: "ollama/llama3.2:3b"
  mistral: "ollama/mistral:7b"
  qwen: "ollama/qwen2.5:7b"

# Use local model as default for a tool
defaults:
  outfit_analyzer: "ollama/mistral:7b"
```

### docker-compose.yml

```yaml
ollama:
  image: ollama/ollama:latest
  ports:
    - "11434:11434"
  volumes:
    - ollama_models:/root/.ollama
  deploy:
    resources:
      limits:
        cpus: '8.0'
        memory: 16G
```

**Adjust resource limits based on your system!**

---

## Performance Tips

### 1. Choose Right Model Size
- Small (2-4GB): Testing, simple tasks
- Medium (7B): Most production use cases
- Large (32-72B): Complex reasoning, when quality > speed

### 2. Monitor Resources
```bash
# Check Ollama logs
docker logs ai-studio-ollama --tail 50

# Monitor resource usage
docker stats ai-studio-ollama
```

### 3. Batch Requests
Local models benefit from batching:
```python
# Process multiple images in one session
router = LLMRouter(model="ollama/mistral:7b")
for image in images:
    result = router.call_structured(prompt, OutfitSpec, images=[image])
```

### 4. Temperature Settings
- Lower (0.1-0.3): Consistent, factual responses
- Medium (0.5-0.7): Balanced creativity
- Higher (0.8-1.0): More creative/varied

---

## Troubleshooting

### Ollama Not Starting
```bash
# Check container status
docker ps -a | grep ollama

# View logs
docker logs ai-studio-ollama

# Restart
docker-compose restart ollama
```

### Model Pull Fails
```bash
# Pull directly via CLI
docker exec -it ai-studio-ollama ollama pull llama3.2:3b

# Check disk space
df -h

# Check Ollama status
curl http://localhost:11434/api/tags
```

### Slow Inference
1. **Use smaller model**: Try 3B or 7B instead of 70B
2. **Check resources**: Ensure adequate CPU/RAM allocated
3. **Reduce max_tokens**: Limit response length
4. **Use GPU** (if available): Add GPU passthrough to docker-compose

### Out of Memory
1. **Reduce model size**: Use 3B or 7B model
2. **Increase Docker memory**: Update docker-compose.yml limits
3. **Close other applications**: Free up system RAM
4. **Use quantized models**: Append `:q4_0` or `:q8_0` to model name

---

## Examples

### Example 1: Image Analysis with Local Model

```python
from ai_tools.shared.router import LLMRouter
from pathlib import Path

router = LLMRouter(model="ollama/mistral:7b")

response = router.call_structured(
    prompt="Analyze this outfit and extract key elements.",
    response_model=OutfitSpec,
    images=[Path("/app/subjects/image.jpg")],
    temperature=0.3
)

print(response.clothing_items)
```

### Example 2: Bulk Processing with Local Model

```python
# Process 100 images for free!
router = LLMRouter(model="ollama/qwen2.5:7b")

results = []
for image_path in image_paths:
    result = router.call_structured(
        prompt="Extract visual style",
        response_model=VisualStyleSpec,
        images=[image_path]
    )
    results.append(result)

# Cost: $0 (vs ~$15 with Gemini at $0.15/1M tokens)
```

### Example 3: Fallback Strategy

```python
# Try local first, fallback to cloud
try:
    router = LLMRouter(model="ollama/llama3.2:3b")
    result = router.call(prompt)
except Exception as e:
    print(f"Local model failed: {e}, falling back to Gemini")
    router = LLMRouter(model="gemini/gemini-2.0-flash-exp")
    result = router.call(prompt)
```

---

## Cost Comparison

### Processing 1,000 images

| Provider | Model | Cost |
|----------|-------|------|
| **Local (Ollama)** | llama3.2:3b | **$0** ✅ |
| **Local (Ollama)** | mixtral:8x7b | **$0** ✅ |
| Gemini | gemini-2.0-flash | ~$15 |
| OpenAI | gpt-4o | ~$250 |
| Anthropic | claude-3-5-sonnet | ~$300 |

**Savings with Local LLMs: 100%!**

---

## Next Steps

1. **Start Small**: Begin with `llama3.2:3b` for testing
2. **Benchmark**: Compare quality vs cloud models
3. **Scale Up**: Try larger models (7B, 32B, 72B)
4. **Optimize**: Tune temperature, max_tokens for your use case
5. **Production**: Consider GPU deployment for faster inference

---

## Resources

- **Ollama Docs**: https://ollama.com/library
- **Model Library**: https://ollama.com/library (browse all models)
- **LiteLLM Ollama Docs**: https://docs.litellm.ai/docs/providers/ollama
- **FastAPI Docs**: /docs (after starting API)

---

**Questions?** Check `/docs` endpoint or review `api/routes/local_models.py`

