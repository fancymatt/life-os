# Image Generation Control Layer

**Status**: Proposed Architecture
**Created**: 2025-10-25

## Problem Statement

Different image generation models require fundamentally different input formats:

| Model | Input Style | Example |
|-------|------------|---------|
| **Qwen** | Short action + 1-5 reference images | `"Put person from image 1 in environment from image 2 wearing outfit from image 3"` |
| **Gemini** | Long descriptive text + 1 reference image | `"Transform this athletic woman with long auburn hair to be wearing an elegant flowing red evening gown with intricate lace details, standing in a luxurious marble ballroom with crystal chandeliers..."` |
| **DALL-E** | Pure creative text, no reference | `"A cyberpunk street scene at night with neon signs, rain-slicked pavement, and towering skyscrapers"` |

**Current problem**: Our AI tools generate Gemini-style prompts, which work poorly with Qwen. Switching models requires rewriting tool code.

**Solution**: Create a **control layer** that translates high-level "intent" into model-specific formats.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          AI Tool                                 │
│  (Composer, Outfit Generator, Style Transfer, etc.)             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ ImageGenerationIntent
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Image Generation Control Layer                │
│                                                                  │
│  • Detects target model (Qwen/Gemini/DALL-E)                   │
│  • Loads visual references (environment, outfit, style)         │
│  • Composes multi-item references if needed                     │
│  • Transforms intent → model-specific format                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
         ┌─────────┐   ┌─────────┐   ┌─────────┐
         │  Qwen   │   │ Gemini  │   │ DALL-E  │
         │ Router  │   │ Router  │   │ Router  │
         └─────────┘   └─────────┘   └─────────┘
```

---

## Intent Schema

### Core Intent Structure

```python
from typing import Optional, List, Literal
from pydantic import BaseModel

class ImageReference(BaseModel):
    """Reference to an image with optional description"""
    image_path: Optional[str] = None       # Path to preview image
    entity_id: Optional[str] = None        # UUID of entity (auto-loads preview)
    description: str                        # Text description (fallback)

class ImageGenerationIntent(BaseModel):
    """High-level description of what we want to generate"""

    # Core action type
    action: Literal[
        "place_in_environment",   # Subject + environment
        "apply_outfit",           # Subject + clothing
        "change_style",           # Subject + art style
        "transform_appearance",   # Subject + appearance changes
        "combine_elements"        # Multiple subjects/elements
    ]

    # Main subject (required)
    subject: ImageReference

    # Context elements (optional, depends on action)
    environment: Optional[ImageReference] = None
    outfit: Optional[List[ImageReference]] = None  # Multiple clothing items
    style: Optional[ImageReference] = None
    pose: Optional[ImageReference] = None

    # Additional context
    mood: Optional[str] = None             # "dramatic", "cheerful", etc.
    lighting: Optional[str] = None         # "golden hour", "studio", etc.
    camera_angle: Optional[str] = None     # "portrait", "full body", etc.

    # Model preferences (optional)
    preferred_model: Optional[str] = None  # "qwen", "gemini", "dalle"
    fallback_allowed: bool = True
```

### Example Intents

#### Simple Outfit Change
```python
ImageGenerationIntent(
    action="apply_outfit",
    subject=ImageReference(
        image_path="/app/characters/vanessa.png",
        description="Vanessa, athletic build, confident expression"
    ),
    outfit=[
        ImageReference(
            entity_id="clothing-item-uuid-1",  # Red leather jacket
            description="red leather jacket with silver zippers"
        )
    ],
    mood="edgy",
    lighting="urban night"
)
```

#### Complex Scene Composition
```python
ImageGenerationIntent(
    action="place_in_environment",
    subject=ImageReference(
        image_path="/app/characters/kat.png",
        description="Kat, punk aesthetic, multicolored hair"
    ),
    environment=ImageReference(
        entity_id="visual-style-cyberpunk-alley",
        description="narrow cyberpunk alley with neon signs and rain"
    ),
    outfit=[
        ImageReference(entity_id="jacket-uuid"),
        ImageReference(entity_id="pants-uuid"),
        ImageReference(entity_id="boots-uuid")
    ],
    style=ImageReference(
        image_path="/app/presets/anime-style.png",
        description="anime, cell-shaded, vibrant colors"
    ),
    lighting="neon reflections",
    camera_angle="full body"
)
```

---

## Control Layer Implementation

### Class Structure

```python
class ImageGenerationControlLayer:
    """
    Translates high-level intent into model-specific formats
    """

    def __init__(self, router_config: RouterConfig):
        self.config = router_config
        self.reference_composer = ReferenceComposer()

    async def generate(
        self,
        intent: ImageGenerationIntent
    ) -> bytes:
        """
        Main entry point: Intent → Image bytes

        Flow:
        1. Determine optimal model based on intent
        2. Load visual references from entities
        3. Compose multi-item references if needed
        4. Transform intent → model-specific format
        5. Call appropriate router
        6. Return image bytes
        """

        # 1. Model selection
        model = self._select_model(intent)

        # 2. Load reference images
        references = await self._load_references(intent)

        # 3. Compose multi-item references (e.g., multiple clothing items)
        composed_refs = await self._compose_references(references, model)

        # 4. Transform to model-specific format
        if model.startswith("qwen"):
            params = self._build_qwen_params(intent, composed_refs)
        elif model.startswith("gemini"):
            params = self._build_gemini_params(intent, composed_refs)
        elif model.startswith("dall-e"):
            params = self._build_dalle_params(intent)

        # 5. Generate image
        router = LLMRouter(model=model, config=self.config)
        image_bytes = await router.agenerate_image(**params)

        return image_bytes
```

### Model Selection Logic

```python
def _select_model(self, intent: ImageGenerationIntent) -> str:
    """
    Choose optimal model based on intent characteristics
    """

    # User preference
    if intent.preferred_model:
        return intent.preferred_model

    # Count available visual references
    ref_count = sum([
        bool(intent.subject.image_path or intent.subject.entity_id),
        bool(intent.environment and (intent.environment.image_path or intent.environment.entity_id)),
        bool(intent.outfit),
        bool(intent.style and (intent.style.image_path or intent.style.entity_id)),
    ])

    # Decision tree
    if ref_count >= 2:
        # Multiple references → Qwen (multi-image)
        return "comfyui/qwen-edit"

    elif ref_count == 1 and intent.subject.image_path:
        # Single reference + detailed text → Gemini
        return "gemini/gemini-2.5-flash-image"

    else:
        # Pure text generation → DALL-E or Gemini
        return "dall-e-3"
```

### Reference Composition

```python
class ReferenceComposer:
    """
    Handles composition of multiple visual references
    """

    async def compose_outfit_references(
        self,
        outfit_items: List[ImageReference]
    ) -> str:
        """
        Combine multiple clothing items into a single reference image

        Strategy:
        1. Load preview images for each item
        2. Create horizontal composite (side-by-side)
        3. Save to temporary file
        4. Return path

        Example:
        [Jacket] [Pants] [Boots] → Combined reference
        """
        from PIL import Image
        import tempfile

        # Load all preview images
        images = []
        for item in outfit_items:
            if item.entity_id:
                preview_path = await self._get_entity_preview(item.entity_id)
            elif item.image_path:
                preview_path = item.image_path
            else:
                continue  # Skip items without images

            img = Image.open(preview_path)
            images.append(img)

        if not images:
            return None

        # Calculate composite dimensions
        max_height = max(img.height for img in images)
        total_width = sum(img.width for img in images)

        # Create composite
        composite = Image.new('RGB', (total_width, max_height), color='white')

        x_offset = 0
        for img in images:
            # Center vertically
            y_offset = (max_height - img.height) // 2
            composite.paste(img, (x_offset, y_offset))
            x_offset += img.width

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(
            suffix='.png',
            delete=False,
            dir='/app/cache'
        )
        composite.save(temp_file.name)

        return temp_file.name
```

### Qwen Transformation

```python
def _build_qwen_params(
    self,
    intent: ImageGenerationIntent,
    references: Dict[str, str]
) -> Dict:
    """
    Transform intent → Qwen format

    Qwen format:
    - Short actionable prompt
    - 1-5 reference images
    - Explicit image references in text
    """

    # Build image list
    images = {}
    prompt_parts = []

    # Image 1: Always the subject
    if references.get('subject'):
        images['image1'] = references['subject']
        subject_ref = "the person in image 1"
    else:
        subject_ref = intent.subject.description

    # Image 2: Outfit (composite if multiple items)
    if references.get('outfit_composite'):
        images['image2'] = references['outfit_composite']
        outfit_ref = "the outfit from image 2"
    elif intent.outfit:
        outfit_ref = ", ".join(item.description for item in intent.outfit)
    else:
        outfit_ref = None

    # Image 3: Environment
    if references.get('environment'):
        images['image3'] = references['environment']
        env_ref = "the environment from image 3"
    elif intent.environment:
        env_ref = intent.environment.description
    else:
        env_ref = None

    # Build concise prompt based on action
    if intent.action == "apply_outfit":
        prompt = f"Put {outfit_ref} on {subject_ref}"

    elif intent.action == "place_in_environment":
        if outfit_ref and env_ref:
            prompt = f"Place {subject_ref} in {env_ref} wearing {outfit_ref}"
        elif env_ref:
            prompt = f"Place {subject_ref} in {env_ref}"
        else:
            prompt = f"Show {subject_ref}"

    # Add mood/lighting if specified
    if intent.lighting:
        prompt += f" with {intent.lighting} lighting"

    return {
        "prompt": prompt,
        "image_path": images.get('image1'),  # Primary for router
        "model": "comfyui/qwen-edit",
        # Additional images passed via kwargs to ComfyUI service
        "image2": images.get('image2'),
        "image3": images.get('image3'),
    }
```

### Gemini Transformation

```python
def _build_gemini_params(
    self,
    intent: ImageGenerationIntent,
    references: Dict[str, str]
) -> Dict:
    """
    Transform intent → Gemini format

    Gemini format:
    - Long descriptive prompt
    - Single reference image
    - Detailed visual descriptions
    """

    prompt_parts = []

    # Subject description
    prompt_parts.append(
        f"Transform this person ({intent.subject.description})"
    )

    # Outfit details
    if intent.outfit:
        outfit_desc = " and ".join(item.description for item in intent.outfit)
        prompt_parts.append(f"wearing {outfit_desc}")

    # Environment details
    if intent.environment:
        prompt_parts.append(
            f"in a {intent.environment.description} setting"
        )

    # Style details
    if intent.style:
        prompt_parts.append(
            f"rendered in {intent.style.description} art style"
        )

    # Lighting and mood
    if intent.lighting:
        prompt_parts.append(f"with {intent.lighting} lighting")
    if intent.mood:
        prompt_parts.append(f"conveying a {intent.mood} mood")

    # Camera angle
    if intent.camera_angle:
        prompt_parts.append(f"shown in {intent.camera_angle} view")

    # Technical quality instructions
    prompt_parts.append(
        "Maintain photorealistic quality, preserve facial features, "
        "ensure proper proportions and anatomy, pay attention to "
        "fabric textures and material properties"
    )

    prompt = ". ".join(prompt_parts) + "."

    return {
        "prompt": prompt,
        "image_path": references.get('subject'),
        "model": "gemini/gemini-2.5-flash-image",
        "temperature": 0.8
    }
```

---

## Visual Reference Management

### Entity Preview Images

Each entity type should have preview images available:

```python
# Clothing items
clothing_item.preview_image → "/app/entity_previews/clothing_items/{uuid}_preview.png"

# Visual styles (environments)
visual_style.preview_image → "/app/entity_previews/visual_styles/{uuid}_preview.png"

# Art styles
art_style.preview_image → "/app/presets/art_styles/{name}_example.png"

# Characters
character.preview_image → "/app/entity_previews/characters/{uuid}_preview.png"
```

### Preview Generation

When creating entities, generate preview images:

1. **Clothing items**: Extract/crop from source images
2. **Visual styles**: Generate example scene with Qwen/Gemini
3. **Art styles**: Store reference examples
4. **Characters**: Use primary portrait

---

## Multiple Clothing Items Strategy

### Problem

Qwen can reference images, but can't internally merge multiple clothing items. If we have:
- Red leather jacket (image A)
- Black jeans (image B)
- Combat boots (image C)

How do we pass all three?

### Solution: Pre-Composition

**Approach 1: Horizontal Grid (Recommended)**

```python
# Create composite: [Jacket] [Pants] [Boots]
composite = create_horizontal_grid([jacket_img, pants_img, boots_img])
```

**Advantages**:
- Single image2 reference
- Clear visual separation
- Works within Qwen's 5-image limit

**Prompt**: `"Put the outfit from image 2 on the person in image 1"`

**Approach 2: Sequential Application (Fallback)**

```python
# Pass 1: Apply jacket
result1 = qwen_edit(subject, jacket, "put on the jacket from image 2")

# Pass 2: Apply pants to result1
result2 = qwen_edit(result1, pants, "add the pants from image 2")

# Pass 3: Apply boots to result2
result3 = qwen_edit(result2, boots, "add the boots from image 2")
```

**Advantages**:
- More control over each item
- Can adjust between passes

**Disadvantages**:
- 3x slower
- Potential quality degradation
- More expensive (if using cloud models)

**Approach 3: Gemini Fallback**

```python
if len(outfit_items) > 3:
    # Too many items for Qwen → use Gemini with detailed text
    model = "gemini/gemini-2.5-flash-image"
    prompt = f"wearing {detailed_outfit_description}"
```

### Recommendation

1. **1-3 items**: Use horizontal grid composition (Approach 1)
2. **4+ items**: Fall back to Gemini with text descriptions (Approach 3)
3. **Complex layering needs**: Use sequential application (Approach 2)

---

## Implementation Phases

### Phase 1: Core Control Layer (Week 1)
- [ ] Create `ImageGenerationControlLayer` class
- [ ] Implement `ImageGenerationIntent` schema
- [ ] Build model selection logic
- [ ] Add Qwen transformation
- [ ] Add Gemini transformation

### Phase 2: Reference Management (Week 2)
- [ ] Create `ReferenceComposer` class
- [ ] Implement outfit composite generation
- [ ] Add entity preview loading
- [ ] Build preview caching system

### Phase 3: Tool Integration (Week 3)
- [ ] Update Composer to use control layer
- [ ] Update Outfit Generator
- [ ] Update Style Transfer Generator
- [ ] Migrate other image tools

### Phase 4: Advanced Features (Week 4)
- [ ] Add sequential application support
- [ ] Implement quality scoring
- [ ] Add automatic model fallback
- [ ] Create preview generation pipeline

---

## Usage Examples

### From Composer Tool

**Before (Direct Gemini prompting):**
```python
# Composer builds long text prompt
prompt = f"""
Transform this {character.appearance} to be wearing {outfit.description}
in a {environment.description} setting with {style.art_style} art style...
[300 more words of description]
"""
image_bytes = await router.agenerate_image(prompt, image_path, model="gemini")
```

**After (Intent-based):**
```python
# Composer builds intent
intent = ImageGenerationIntent(
    action="place_in_environment",
    subject=ImageReference(
        image_path=character_image,
        description=character.appearance
    ),
    environment=ImageReference(
        entity_id=environment.id  # Auto-loads preview
    ),
    outfit=[
        ImageReference(entity_id=item.id)
        for item in selected_clothing
    ],
    style=ImageReference(entity_id=style.id)
)

# Control layer handles everything
control_layer = ImageGenerationControlLayer(config)
image_bytes = await control_layer.generate(intent)
```

### Benefits

1. **Tools don't need to know about models**: Just express intent
2. **Easy model switching**: Change one config, everything adapts
3. **Optimal format per model**: Qwen gets images, Gemini gets text
4. **Automatic fallback**: If Qwen fails, try Gemini
5. **Reference composition**: Multiple clothing items handled automatically

---

## Testing Strategy

### Unit Tests
- Model selection logic
- Intent transformation for each model
- Reference composition
- Preview loading

### Integration Tests
- End-to-end generation with different intents
- Multi-item outfit composition
- Fallback scenarios
- Model switching

### Visual Regression Tests
- Compare outputs for same intent across models
- Ensure quality maintained after refactoring

---

## Future Enhancements

1. **Learned model selection**: Track which model works best for which intent types
2. **Dynamic prompt optimization**: A/B test different prompt structures
3. **Reference quality scoring**: Validate previews before using
4. **Multi-pass refinement**: Generate → evaluate → refine loop
5. **Intent templates**: Common patterns (outfit change, style transfer, etc.)

---

## Migration Path

To avoid breaking existing functionality:

1. **Phase 1**: Build control layer alongside existing code
2. **Phase 2**: Update one tool (Composer) to use new system
3. **Phase 3**: Validate outputs match or exceed old system
4. **Phase 4**: Gradually migrate other tools
5. **Phase 5**: Deprecate old direct prompting approach

Estimated timeline: **4 weeks** for full migration.
