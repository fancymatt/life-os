# Qwen Image Edit Best Practices

**Model**: Qwen-Image-Edit-2509
**Last Updated**: 2025-10-25

## Overview

Qwen Image Edit is a multi-modal image editing model that excels at combining reference images with short, actionable text prompts. Unlike text-heavy models (like Gemini), Qwen works best with **visual references + concise instructions**.

---

## Optimal Configuration Settings

### With Lightning LoRA (Recommended - Fast)

```yaml
steps: 4                    # 4-step Lightning LoRA acceleration
cfg: 1.0                    # Low CFG for Lightning LoRA
sampler: euler
scheduler: simple           # or beta
denoise: 1.0
lora_strength: 1.0          # Full LoRA effect
seed: randomize             # For variations
```

**Execution time**: ~2-4 seconds on RTX 4090

### Without Lightning LoRA (Higher Quality)

```yaml
steps: 20                   # More steps for standard diffusion
cfg: 2.5                    # Higher CFG for better prompt adherence
sampler: euler
scheduler: simple
denoise: 1.0
seed: randomize
```

**Execution time**: ~10-15 seconds on RTX 4090

### VRAM Considerations

- **FP8 models**: Require 24GB+ VRAM
- **GGUF models**: Work on lower VRAM (Q3_K_S, Q4, Q5 variants)
- **Image scaling**: Always scale inputs to ~1 megapixel to avoid quality loss

---

## Prompting Philosophy

### Core Principle: Show, Don't Tell

Qwen Image Edit is **reference-driven**, not text-driven. The model works best when you:

1. **Provide visual references** for what you want
2. **Use short, actionable text** to describe the transformation
3. **Reference images explicitly** in your prompt

### Prompt Structure

```
[Action] [What] [How] [Where/Context]

✅ Good Examples:
- "Put the outfit from image 2 on the person in image 1"
- "Change the background to a beach sunset"
- "Make the lighting golden hour from the left"
- "Swap the shirt to the red jacket from image 2"

❌ Bad Examples (Too Text-Heavy):
- "The character should be wearing an elegant flowing red evening gown with intricate lace details and a sweetheart neckline, standing in a luxurious ballroom with marble floors and crystal chandeliers"
```

**Why this fails**: Qwen expects visual references, not detailed descriptions. Use image2 for the outfit, image3 for the environment.

---

## Multi-Image Workflows

### Supported Configurations

The `TextEncodeQwenImageEditPlus` node supports **up to 5 reference images**:

- `image1`: Primary subject (required)
- `image2`: Secondary reference (optional)
- `image3`: Tertiary reference (optional)
- `image4`: Additional reference (optional)
- `image5`: Additional reference (optional)

### Common Use Cases

#### 1. Outfit Transfer

```
image1: Person in current outfit
image2: Reference outfit (from another photo)

Prompt: "Put the outfit from image 2 on the person in image 1"
```

#### 2. Scene Composition

```
image1: Character/subject
image2: Background environment

Prompt: "Place the person from image 1 into the scene from image 2"
```

#### 3. Multi-Character Merging

```
image1: First character
image2: Second character

Prompt: "Show both people from image 1 and image 2 standing together"
```

#### 4. Style + Subject + Environment

```
image1: Primary subject
image2: Visual style reference
image3: Environment/background

Prompt: "Place the person from image 1 in the environment from image 3 with the art style from image 2"
```

### Image Referencing in Prompts

When using multiple images, explicitly reference them:

- ✅ "the person from image 1"
- ✅ "the outfit in image 2"
- ✅ "the background from image 3"
- ❌ "the person" (ambiguous if multiple people)

---

## Negative Prompts

Keep negative prompts focused on **quality issues**, not content:

```
Recommended: "blurry, distorted, artifacts, low quality, deformed"

Avoid: "no red clothing, no modern buildings" (doesn't work well)
```

Qwen responds better to positive instructions ("make X look like Y") than prohibitions ("don't include Z").

---

## Specific Task Guidelines

### Relighting

Be specific about:
- **Direction**: "from the left", "overhead", "behind"
- **Quality**: "soft", "harsh", "dramatic"
- **Time/mood**: "golden hour", "blue hour", "studio lighting"

Example: `"Add soft golden hour lighting from the left"`

### Background Replacement

Specify both:
- **Scene**: What the new background is
- **Mood/time**: Atmospheric context

Example: `"Change background to overcast city street at dusk"`

### Outfit/Costume Changes

For best results:
- Provide a reference image of the desired outfit
- Mention if pose/expression should change
- Specify any style considerations

Example: `"Swap to the outfit from image 2, adjusting pose to match"`

### Text Editing in Images

Qwen supports bilingual (English/Chinese) text editing:
- Preserves original font style and size
- Can add, delete, or modify text
- Works best with clear, readable text

Example: `"Change the sign text to 'Open 24/7' in white"`

---

## Troubleshooting

### Results Look Over-Processed

**Symptoms**: Too smooth, plastic-looking, or overly stylized

**Solutions**:
1. Lower CFG scale (try 0.8 instead of 1.0)
2. Disable Lightning LoRA
3. Reduce steps slightly (try 3 instead of 4)

### Edits Are Too Weak

**Symptoms**: Changes barely visible, prompt not followed

**Solutions**:
1. Increase CFG scale (try 1.5-2.0)
2. Increase steps (try 6-8 with Lightning, 25-30 without)
3. Make prompt more specific and actionable
4. Ensure reference images are clear and relevant

### File Not Found Errors

**Symptoms**: "Image not found" or node execution failures

**Solutions**:
1. Ensure ComfyUI is running latest version
2. Check that all model files are in correct directories:
   - `models/diffusion_models/` - UNET
   - `models/text_encoders/` - CLIP
   - `models/vae/` - VAE
   - `models/loras/` - Lightning LoRA
3. Verify image paths use proper format

### Output Images Different Size Than Input

**Symptoms**: Resolution changed unexpectedly

**Solutions**:
1. Use `ImageScaleToTotalPixels` node set to 1.0 megapixels
2. Check VAE encoding/decoding isn't introducing scaling
3. Verify LoadImage node isn't auto-resizing

---

## Model Architecture Notes

### Dual Control System

Qwen-Image-Edit uses two parallel control streams:

1. **Qwen2.5-VL (Vision-Language)**: Semantic understanding from text + images
2. **VAE Encoder**: Visual appearance preservation from input image

This dual approach allows:
- High-fidelity visual preservation (from VAE)
- Intelligent semantic edits (from VL model)
- Coherent blending of both streams

### Image Preprocessing

All reference images undergo:
- **VAE encoding**: Resized to 1024x1024
- **VL encoding**: Resized to 384x384
- **Scaling**: Recommended to ~1 megapixel total

Large images (>2MP) may cause:
- Quality degradation
- Slower processing
- Memory issues

---

## Comparison: Qwen vs Gemini vs DALL-E

| Feature | Qwen Image Edit | Gemini 2.5 Flash | DALL-E 3 |
|---------|----------------|------------------|----------|
| **Input** | 1-5 reference images + short prompt | 1 reference image + detailed prompt | Text only (no reference) |
| **Prompt Style** | Actionable, concise | Descriptive, detailed | Creative, descriptive |
| **Speed** | 2-4s (Lightning) | 8-15s | 15-30s |
| **Cost** | $0 (local) | $0.04/image | $0.04-0.08/image |
| **Best For** | Outfit transfer, scene composition | Subject-preserving transformations | Creative generation |
| **Weaknesses** | Needs good references | Limited multi-image support | Can't preserve subjects well |

---

## Workflow Integration Tips

### When to Use Qwen

✅ **Good candidates**:
- Outfit/costume changes with reference images
- Background replacement with environment photos
- Multi-character composition
- Style transfer with visual examples
- Pose adjustments with reference poses

❌ **Poor candidates**:
- Pure text-to-image generation (no reference)
- Highly creative/abstract concepts without visual refs
- Photorealistic face generation from text alone

### Fallback Strategy

If Qwen produces poor results:

1. **Switch to Gemini** if you have:
   - Strong text descriptions
   - Single subject preservation needed
   - No good visual references

2. **Pre-compose references** if you need:
   - Multiple clothing items → Merge in photo editor first
   - Complex multi-element scenes → Stage separately, then combine

3. **Use IP-Adapter (SDXL)** if you need:
   - Completely new composition
   - Character consistency across scenes
   - Higher creative flexibility

---

## Future Improvements

### Potential Enhancements

1. **Smart reference selection**: Auto-pick best images from entity library
2. **Prompt templating**: Pre-built patterns for common tasks
3. **Multi-pass composition**: Layer multiple edits sequentially
4. **Reference image pre-processing**: Auto-crop, scale, enhance inputs
5. **Quality scoring**: Detect when output doesn't match intent

### Research Areas

- Optimal CFG schedules for different edit types
- Reference image quality vs output quality correlation
- Multi-reference weighting strategies
- Semantic vs appearance control balance

---

## Additional Resources

- [ComfyUI Official Qwen Tutorial](https://docs.comfy.org/tutorials/image/qwen/qwen-image-edit)
- [Qwen-Image GitHub](https://github.com/QwenLM/Qwen-Image)
- [Hugging Face Model Card](https://huggingface.co/Qwen/Qwen-Image-Edit)
- [ComfyUI-QwenEditUtils](https://github.com/lrzjason/Comfyui-QwenEditUtils)
