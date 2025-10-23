# AI-Studio

Modular AI toolkit for image analysis, generation, and video creation. Extract structured data from images, save as reusable presets, and generate new images with any combination of styles, outfits, hair, makeup, and more.

## Features

- **9 Image Analyzers** - Extract outfit, style, hair, makeup, expression, accessories
- **6 Image Generators** - Generate images with modular spec composition
- **2 Video Tools** - Enhance prompts and generate videos with Sora
- **Intelligent Caching** - 7-day TTL with automatic invalidation
- **Preset System** - User-editable JSON specifications
- **Batch Workflows** - N × M × K generation with progress tracking
- **Cost Efficient** - ~$0.001 analysis, $0.04 generation

## Quick Start

```bash
# Setup
cp .env.example .env
# Add your GEMINI_API_KEY and optionally OPENAI_API_KEY

# Analyze an image (all aspects)
python ai_tools/comprehensive_analyzer/tool.py photo.jpg --save-all --prefix my-look

# Generate new image combining presets
python ai_tools/modular_image_generator/tool.py subject.jpg \
  --outfit casual-outfit \
  --visual-style film-noir \
  --hair-style beach-waves

# Batch generate (3 subjects × 2 outfits × 2 styles = 12 images)
python workflows/batch_outfit_generator.py \
  --subjects photos/*.jpg \
  --outfits casual,formal \
  --styles vintage,modern
```

## Installation

```bash
# Clone repository
git clone <repo-url>
cd life-os

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add GEMINI_API_KEY (required)
# Add OPENAI_API_KEY (optional, for video tools)
```

## Architecture

### Two-Tier Storage

**Cache (Ephemeral)**
- 7-day TTL with automatic expiration
- SHA256 file hashing for instant retrieval
- Prevents duplicate API calls
- Located in `cache/`

**Presets (Permanent)**
- User-editable JSON specifications
- Version tracked with metadata
- Mix-and-match for generation
- Located in `presets/`

### Workflow

```
1. Analyze Image → Structured JSON (cached)
2. Promote to Preset → Edit if needed
3. Generate with Presets → New image
```

### Provider Ecosystem

- **Analysis**: Gemini 2.0 Flash (~$0.001 per call)
- **Image Generation**: Gemini 2.5 Flash ($0.04 per image)
- **Video Enhancement**: GPT-4o/GPT-5
- **Video Generation**: Sora 2 / Sora 2 Pro

## Image Analyzers

### Individual Analyzers

All analyzers support:
- `--save-as <name>` - Save as preset
- `--no-cache` - Skip cache lookup
- `--list` - List existing presets
- `--model <model>` - Override default model

#### outfit_analyzer

Extract clothing items with fabric, color, and construction details.

```bash
python ai_tools/outfit_analyzer/tool.py image.jpg --save-as casual-look
```

Output: style_genre, formality, aesthetic, clothing_items[]

#### visual_style_analyzer

Extract 17 photographic aspects: composition, lighting, mood, color grading, etc.

```bash
python ai_tools/visual_style_analyzer/tool.py image.jpg --save-as film-noir
```

Output: composition, framing, lighting, color_palette, mood, photographic_style, etc.

#### art_style_analyzer

Analyze artistic style: medium, technique, art movement, mood.

```bash
python ai_tools/art_style_analyzer/tool.py image.jpg --save-as impressionist
```

Output: medium, technique, artistic_movement, color_palette, texture, mood

#### hair_style_analyzer

Analyze hair structure (not color): cut, length, layers, texture, volume.

```bash
python ai_tools/hair_style_analyzer/tool.py image.jpg --save-as beach-waves
```

Output: cut, length, layers, texture, volume, parting, overall_style

#### hair_color_analyzer

Analyze hair color (not structure): base color, undertones, highlights.

```bash
python ai_tools/hair_color_analyzer/tool.py image.jpg --save-as ash-blonde
```

Output: base_color, undertones, highlights, lowlights, technique, dimension

#### makeup_analyzer

Analyze makeup application: complexion, eyes, lips, intensity.

```bash
python ai_tools/makeup_analyzer/tool.py image.jpg --save-as natural-glam
```

Output: complexion, eyes, lips, overall_style, intensity, color_palette

#### expression_analyzer

Analyze facial expression: emotion, intensity, features, gaze.

```bash
python ai_tools/expression_analyzer/tool.py image.jpg --save-as confident-smile
```

Output: primary_emotion, intensity, mouth, eyes, eyebrows, gaze_direction

#### accessories_analyzer

Analyze accessories: jewelry, bags, belts, hats.

```bash
python ai_tools/accessories_analyzer/tool.py image.jpg --save-as minimal-jewelry
```

Output: jewelry[], bags, belts, hats, watches, overall_style

### comprehensive_analyzer

Run all 8 analyzers at once.

```bash
# Analyze everything
python ai_tools/comprehensive_analyzer/tool.py image.jpg

# Save all analyses as presets
python ai_tools/comprehensive_analyzer/tool.py image.jpg --save-all --prefix my-look
```

Creates 8 presets:
- my-look-outfit
- my-look-style
- my-look-art
- my-look-hairstyle
- my-look-haircolor
- my-look-makeup
- my-look-expression
- my-look-accessories

## Image Generators

### modular_image_generator

Main generator supporting any combination of specs.

```bash
# Outfit only
python ai_tools/modular_image_generator/tool.py subject.jpg \
  --outfit casual-outfit

# Outfit + Visual Style
python ai_tools/modular_image_generator/tool.py subject.jpg \
  --outfit formal-suit \
  --visual-style film-noir

# Full transformation
python ai_tools/modular_image_generator/tool.py subject.jpg \
  --outfit summer-dress \
  --visual-style vintage-style \
  --hair-style long-wavy \
  --hair-color blonde-highlights \
  --makeup natural-glam \
  --expression confident-smile \
  --accessories minimal-jewelry

# Custom output
python ai_tools/modular_image_generator/tool.py subject.jpg \
  --outfit casual \
  --output output/custom/
```

Options:
- `--outfit <preset>` - Outfit preset name
- `--visual-style <preset>` - Visual style preset name
- `--art-style <preset>` - Art style preset name
- `--hair-style <preset>` - Hair style preset name
- `--hair-color <preset>` - Hair color preset name
- `--makeup <preset>` - Makeup preset name
- `--expression <preset>` - Expression preset name
- `--accessories <preset>` - Accessories preset name
- `--output <dir>` - Output directory
- `--temperature <float>` - Generation temperature (default: 0.8)

### outfit_generator

Original outfit-focused generator.

```bash
python ai_tools/outfit_generator/tool.py subject.jpg \
  --outfit casual-outfit \
  --style film-noir
```

### style_transfer_generator

Transfer visual style only (preserves subject).

```bash
python ai_tools/style_transfer_generator/tool.py subject.jpg \
  --style vintage-warm \
  --strength 0.8
```

### art_style_generator

Generate with artistic style rendering.

```bash
python ai_tools/art_style_generator/tool.py subject.jpg \
  --art-style impressionist
```

### combined_transformation

Multi-spec transformation (alias for modular_image_generator).

```bash
python ai_tools/combined_transformation/tool.py subject.jpg \
  --outfit formal-suit \
  --visual-style modern-clean \
  --expression professional
```

## Video Tools

### video_prompt_enhancer

Enhance video prompts with GPT-4o/GPT-5.

```bash
python ai_tools/video_prompt_enhancer/tool.py "person walking on beach"
```

Output: Enhanced prompt with camera movements, lighting, atmosphere, timing.

### sora_video_generator

Generate videos with Sora API.

```bash
# 9:16 portrait video (4 seconds)
python ai_tools/sora_video_generator/tool.py "person walking on beach" \
  --size 720x1280 \
  --duration 4

# 16:9 landscape video (8 seconds)
python ai_tools/sora_video_generator/tool.py "city at sunset" \
  --size 1792x1024 \
  --duration 8 \
  --model sora-2

# Skip prompt enhancement
python ai_tools/sora_video_generator/tool.py "detailed prompt here" \
  --skip-enhancement
```

Sizes:
- `720x1280` - 9:16 portrait (mobile)
- `1792x1024` - 16:9 landscape (desktop)
- `1024x1792` - 9:16 tall portrait

Models:
- `sora-2` - $0.125/second
- `sora-2-pro` - $0.50/second (default)

## Workflows

### batch_outfit_generator

Generate all combinations of N subjects × M outfits × K styles.

```bash
# Basic batch
python workflows/batch_outfit_generator.py \
  --subjects subject.jpg \
  --outfits casual,formal \
  --styles vintage,modern

# Multiple subjects with glob
python workflows/batch_outfit_generator.py \
  --subjects photos/*.jpg \
  --outfits casual,formal,street \
  --styles film-noir,vintage

# Without styles (default background)
python workflows/batch_outfit_generator.py \
  --subjects subject.jpg \
  --outfits outfit1,outfit2,outfit3

# Custom output
python workflows/batch_outfit_generator.py \
  --subjects person*.jpg \
  --outfits casual \
  --styles modern \
  --output output/custom/
```

Options:
- `--subjects` - Image paths (supports glob patterns)
- `--outfits` - Comma-separated outfit preset names
- `--styles` - Comma-separated style preset names (optional)
- `--output` - Output directory (default: output/batch)
- `--temperature` - Generation temperature (default: 0.8)
- `--no-skip` - Regenerate even if output exists
- `--cost` - Cost per image for estimation (default: 0.04)

Output structure:
```
output/batch/
├── subject1/
│   ├── casual/
│   │   ├── vintage.png
│   │   └── modern.png
│   └── formal/
│       ├── vintage.png
│       └── modern.png
└── _batch_report.json
```

Features:
- Progress tracking with current/total
- Cost estimation before starting
- Preset validation
- Skip existing files
- Error handling with detailed logging
- JSON summary report

### end_to_end_workflow

Complete analysis and generation pipeline.

```bash
# Analyze only
python examples/end_to_end_workflow.py image.jpg

# Analyze and generate
python examples/end_to_end_workflow.py image.jpg --generate
```

## Presets

Presets are user-editable JSON files in `presets/` organized by category:

```
presets/
├── outfits/
├── visual_styles/
├── art_styles/
├── hair_styles/
├── hair_colors/
├── makeup/
├── expressions/
└── accessories/
```

### Creating Presets

1. Analyze an image:
```bash
python ai_tools/outfit_analyzer/tool.py image.jpg --save-as my-outfit
```

2. Edit the preset:
```bash
nano presets/outfits/my-outfit.json
```

3. Use in generation:
```bash
python ai_tools/modular_image_generator/tool.py subject.jpg --outfit my-outfit
```

### Preset Format

```json
{
  "clothing_items": [
    {
      "item": "leather jacket",
      "fabric": "distressed brown leather",
      "color": "chocolate brown",
      "details": "asymmetric zip, quilted shoulders"
    }
  ],
  "style_genre": "edgy casual",
  "formality": "casual",
  "aesthetic": "urban streetwear"
}
```

### Listing Presets

```bash
# List all outfits
python ai_tools/outfit_analyzer/tool.py --list

# List all visual styles
python ai_tools/visual_style_analyzer/tool.py --list

# List all presets in a category
ls presets/outfits/
```

## Cost Analysis

### Per-Image Workflow

| Operation | Provider | Cost |
|-----------|----------|------|
| Outfit analysis | Gemini 2.0 | ~$0.001 |
| Visual style analysis | Gemini 2.0 | ~$0.001 |
| Image generation | Gemini 2.5 | $0.04 |
| **Total** | | **~$0.042** |

### Comprehensive Analysis

| Operation | Cost |
|-----------|------|
| 8 analyzers | 8 × ~$0.001 = ~$0.008 |
| Image generation | $0.04 |
| **Total** | **~$0.048** |

### Batch Generation

3 subjects × 2 outfits × 2 styles = 12 images

| Operation | Cost |
|-----------|------|
| Analysis (cached) | ~$0.016 |
| Generation | 12 × $0.04 = $0.48 |
| **Total** | **~$0.496** |

### With Caching

| Iteration | Cost | Savings |
|-----------|------|---------|
| First | ~$0.042 | - |
| Subsequent (cached) | $0.04 | ~$0.002 |
| 100 iterations | $4.00 | ~$0.20 |

### Video Generation

| Model | Cost/Second | 4s Video | 12s Video |
|-------|-------------|----------|-----------|
| Sora 2 | $0.125 | $0.50 | $1.50 |
| Sora 2 Pro | $0.50 | $2.00 | $6.00 |

## Examples

### Example 1: Style Transfer

Extract style from one image, apply to another subject.

```bash
# 1. Analyze style from reference image
python ai_tools/visual_style_analyzer/tool.py reference.jpg --save-as film-noir

# 2. Apply to new subject
python ai_tools/modular_image_generator/tool.py subject.jpg --visual-style film-noir
```

### Example 2: Mix and Match

Combine outfit from one image with style from another.

```bash
# 1. Extract outfit from image A
python ai_tools/outfit_analyzer/tool.py imageA.jpg --save-as outfit-A

# 2. Extract style from image B
python ai_tools/visual_style_analyzer/tool.py imageB.jpg --save-as style-B

# 3. Combine on subject C
python ai_tools/modular_image_generator/tool.py subjectC.jpg \
  --outfit outfit-A \
  --visual-style style-B
```

### Example 3: Complete Transformation

Change everything about a subject.

```bash
# 1. Analyze target look
python ai_tools/comprehensive_analyzer/tool.py target.jpg --save-all --prefix target

# 2. Apply to new subject
python ai_tools/modular_image_generator/tool.py subject.jpg \
  --outfit target-outfit \
  --visual-style target-style \
  --hair-style target-hairstyle \
  --hair-color target-haircolor \
  --makeup target-makeup \
  --expression target-expression
```

### Example 4: Batch Variations

Generate multiple variations for A/B testing.

```bash
# Create presets for different styles
python ai_tools/visual_style_analyzer/tool.py vintage.jpg --save-as vintage
python ai_tools/visual_style_analyzer/tool.py modern.jpg --save-as modern
python ai_tools/visual_style_analyzer/tool.py dark.jpg --save-as dark

# Generate all combinations
python workflows/batch_outfit_generator.py \
  --subjects product.jpg \
  --outfits casual-outfit \
  --styles vintage,modern,dark
```

### Example 5: Video Generation

Create video with enhanced prompt.

```bash
# 1. Enhance prompt
python ai_tools/video_prompt_enhancer/tool.py "person walking on beach"
# Output: "Wide shot of a person walking along a sun-drenched beach at golden hour..."

# 2. Generate video
python ai_tools/sora_video_generator/tool.py \
  "Wide shot of a person walking along a sun-drenched beach at golden hour..." \
  --size 720x1280 \
  --duration 4
```

## Configuration

### Model Configuration

Edit `configs/models.yaml` to change default models:

```yaml
defaults:
  # Image Analysis Tools
  outfit_analyzer: "gemini/gemini-2.0-flash-exp"
  visual_style_analyzer: "gemini/gemini-2.0-flash-exp"

  # Image Generation Tools
  outfit_generator: "gemini-2.5-flash-preview"
  modular_image_generator: "gemini-2.5-flash-preview"

  # Video Tools
  video_prompt_enhancer: "gpt-4o"
  sora_video_generator: "sora-2-pro"
```

### Cache Settings

Cache is managed automatically with 7-day TTL. To clear cache:

```bash
rm -rf cache/
```

To disable cache for a single run:

```bash
python ai_tools/outfit_analyzer/tool.py image.jpg --no-cache
```

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional (for video tools)
OPENAI_API_KEY=your_openai_api_key
```

## Tool Reference

### All Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| outfit_analyzer | Extract outfit details | Image | OutfitSpec |
| visual_style_analyzer | Extract photographic style | Image | VisualStyleSpec |
| art_style_analyzer | Extract artistic style | Image | ArtStyleSpec |
| hair_style_analyzer | Extract hair structure | Image | HairStyleSpec |
| hair_color_analyzer | Extract hair color | Image | HairColorSpec |
| makeup_analyzer | Extract makeup details | Image | MakeupSpec |
| expression_analyzer | Extract facial expression | Image | ExpressionSpec |
| accessories_analyzer | Extract accessories | Image | AccessoriesSpec |
| comprehensive_analyzer | Run all analyzers | Image | ComprehensiveSpec |
| modular_image_generator | Generate with any specs | Subject + Specs | Image |
| outfit_generator | Generate with outfit | Subject + Outfit | Image |
| style_transfer_generator | Transfer style only | Subject + Style | Image |
| art_style_generator | Generate with art style | Subject + Art | Image |
| combined_transformation | Multi-spec generation | Subject + Specs | Image |
| video_prompt_enhancer | Enhance video prompt | Prompt | Enhanced Prompt |
| sora_video_generator | Generate video | Prompt | Video |

### Spec Types

All specs are defined in `ai_capabilities/specs.py`:

- **OutfitSpec** - clothing_items[], style_genre, formality, aesthetic
- **VisualStyleSpec** - 17 fields (composition, lighting, mood, etc.)
- **ArtStyleSpec** - medium, technique, artistic_movement, mood
- **HairStyleSpec** - cut, length, layers, texture, volume
- **HairColorSpec** - base_color, undertones, highlights, lowlights
- **MakeupSpec** - complexion, eyes, lips, intensity
- **ExpressionSpec** - primary_emotion, intensity, features
- **AccessoriesSpec** - jewelry[], bags, belts, hats
- **ComprehensiveSpec** - Combines all 8 specs above

## Troubleshooting

### Cache Issues

If seeing stale results:
```bash
# Clear specific category
rm -rf cache/outfits/

# Clear all cache
rm -rf cache/

# Force re-analysis
python ai_tools/outfit_analyzer/tool.py image.jpg --no-cache
```

### Missing API Key

```bash
# Check environment
echo $GEMINI_API_KEY

# Reload environment
source .env
```

### Import Errors

```bash
# Ensure in project root
cd /path/to/life-os

# Check Python path
python -c "import sys; print(sys.path)"
```

### Generation Failures

Check that:
1. Subject image exists and is valid
2. All preset names are correct (use `--list`)
3. API keys are set
4. Network connection is available

## Performance

### Caching Impact

| Operation | First Run | Cached |
|-----------|-----------|--------|
| Analysis | ~3-5s | ~0.1s |
| Cost | ~$0.001 | $0.00 |

### Batch Performance

| Images | Time (estimate) | Cost |
|--------|-----------------|------|
| 10 | ~5 minutes | $0.40 |
| 50 | ~25 minutes | $2.00 |
| 100 | ~50 minutes | $4.00 |

### Optimization Tips

1. **Use caching** - Don't skip cache unless necessary
2. **Batch operations** - Use batch workflow for multiple images
3. **Preset reuse** - Create preset library for common styles
4. **Temperature tuning** - Lower temperature (0.6-0.7) for consistency

## Development

### CI/CD Workflow

This project uses a **staging → production** deployment strategy with automated testing.

#### Branch Strategy

```
staging (development)  →  main (production)
    ↓                         ↓
Auto-deploy to          Manual approval
staging environment     for production
```

**Branches**:
- `staging` - Development branch, auto-deploys on push
- `main` - Production branch, requires PR approval

**Workflow Rules**:
1. ✅ **Always develop on `staging`** - Never commit directly to `main`
2. ✅ **All tests must pass** - 100% pass rate required
3. ✅ **PRs required for production** - `staging` → `main` via pull request
4. ✅ **Manual approval required** - Production deploys need explicit approval

#### Daily Development Workflow

```bash
# 1. Start on staging branch
git checkout staging

# 2. Make your changes
# ... edit files ...

# 3. Run tests locally
docker-compose exec api pytest tests/unit/ -v

# 4. Commit and push to staging
git add .
git commit -m "feat: Add new feature

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin staging

# 5. Staging auto-deploys (GitHub Actions runs tests)
# Check: https://github.com/your-repo/actions
```

**After push to `staging`**:
- ✅ GitHub Actions runs full test suite
- ✅ Backend CI checks: pytest, coverage, linting
- ✅ Frontend CI checks: vitest, eslint, build
- ✅ If all pass: Auto-deploy to staging environment (when configured)

#### Deploying to Production

```bash
# 1. Ensure staging is stable and tested
git checkout staging
git pull origin staging

# 2. Create pull request: staging → main
gh pr create --base main --head staging \
  --title "Deploy: Your Feature Name" \
  --body "## Summary

  Description of changes...

  ## Test Results
  - ✅ All unit tests passing (85/85)
  - ✅ Manual testing complete

  ## Deployment Checklist
  - [x] Tests passing
  - [x] No breaking changes
  - [x] Staging verified"

# Or create PR via web UI:
# https://github.com/your-repo/compare/main...staging

# 3. Wait for CI/CD checks to pass
# 4. Get approval (if required by branch protection)
# 5. Merge PR to main
# 6. Production deployment workflow runs (manual approval required)
```

**After merge to `main`**:
- ✅ Full test suite runs again (including slow tests)
- ⏸️ Manual approval required for production deployment
- 🚀 Deployment instructions shown in workflow
- ✅ Smoke tests run after deployment

#### Post-Deployment

```bash
# 1. Pull production changes
git checkout main
git pull origin main

# 2. Rebuild containers with production code
docker-compose up -d --build

# 3. Verify tests still pass
docker-compose exec api pytest tests/unit/ -v

# 4. Sync staging with main
git checkout staging
git merge main --ff-only
git push origin staging
```

#### GitHub Actions Workflows

**Backend CI** (`.github/workflows/backend-ci.yml`):
- Runs on: Push to `main`, PRs to `main`
- Tests: `pytest tests/unit/` (fast tests only)
- Coverage: Generates coverage report
- Linting: `ruff`, `black`, `isort`
- Triggers on: `api/**`, `ai_tools/**`, `tests/**` changes

**Frontend CI** (`.github/workflows/frontend-ci.yml`):
- Runs on: Push to `main`, PRs to `main`
- Tests: `npm test -- --run`
- Linting: `npm run lint`
- Build: `npm run build`
- Triggers on: `frontend/**` changes

**Deploy Staging** (`.github/workflows/deploy-staging.yml`):
- Runs on: Push to `staging` branch
- Tests: Full test suite
- Deployment: Auto-deploy to staging (SSH config needed)
- Notifications: Optional Slack notifications

**Deploy Production** (`.github/workflows/deploy-production.yml`):
- Runs on: Push to `main` branch
- Tests: Full test suite (including slow tests)
- Deployment: Manual approval required
- Safety: Creates backup before deployment
- Smoke tests: Runs critical path tests after deploy

#### Testing Requirements

**Before committing**:
```bash
# Run all unit tests
docker-compose exec api pytest tests/unit/ -v

# Must see: "85 passed" (100% pass rate)
```

**Test organization**:
```
tests/
├── unit/              # Fast, isolated tests (run in CI)
│   ├── test_cache.py
│   ├── test_preset.py
│   ├── test_router.py
│   └── test_specs.py
├── integration/       # API integration tests
├── smoke/            # Critical path tests
└── manual/           # Manual tests (not run in CI)
```

**Test markers**:
```bash
# Run only unit tests
pytest tests/unit/ -v -m unit

# Run only integration tests
pytest tests/integration/ -v -m integration

# Run smoke tests (critical paths)
pytest tests/smoke/ -v -m smoke

# Skip slow tests
pytest tests/ -v -m "not slow"
```

#### Environment Setup

**Local Development**:
```bash
# Copy environment template
cp .env.example .env

# Required variables
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key  # Optional
REQUIRE_AUTH=false       # Disable auth for local dev
```

**Staging Environment** (`.env.staging`):
```bash
ENVIRONMENT=staging
REQUIRE_AUTH=true
JWT_SECRET_KEY=staging_secret
DATABASE_URL=postgresql://...staging_db
BASE_URL=https://staging.yourdomain.com
```

**Production Environment** (`.env.production`):
```bash
ENVIRONMENT=production
REQUIRE_AUTH=true
JWT_SECRET_KEY=production_secret  # Use secure random key
DATABASE_URL=postgresql://...production_db
BASE_URL=https://yourdomain.com
```

#### Quick Reference

**Common Commands**:
```bash
# Check which branch you're on
git branch --show-current

# Run tests
docker-compose exec api pytest tests/unit/ -v

# Rebuild containers after code changes
docker-compose up -d --build

# View CI/CD workflow status
gh run list
gh run view <run-id>

# Create PR via CLI
gh pr create --base main --head staging --web

# Check deployment logs
docker logs ai-studio-api --tail 100
```

**Git Commit Format**:
```
<type>: <short description>

<optional detailed description>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `perf`, `chore`

**Branch Protection Rules** (configure on GitHub):
- ✅ Require pull request reviews (main branch)
- ✅ Require status checks to pass
- ✅ Require conversation resolution
- ✅ Do not allow force pushes

#### Troubleshooting CI/CD

**Tests failing in CI but passing locally**:
```bash
# Ensure you're on the right branch
git checkout staging
git pull origin staging

# Run tests in fresh container
docker-compose down
docker-compose up -d --build
docker-compose exec api pytest tests/unit/ -v
```

**Deployment blocked**:
- Check GitHub Actions tab for error details
- Ensure all required checks pass
- Verify branch protection rules allow merge
- Check if manual approval is needed

**Sync issues between staging and main**:
```bash
# If staging is behind main
git checkout staging
git merge main --ff-only
git push origin staging

# If main is ahead and you need to reconcile
git checkout staging
git pull origin main
# Resolve conflicts if any
git push origin staging
```

### Adding New Analyzers

1. Create directory:
```bash
mkdir -p ai_tools/my_analyzer
```

2. Create tool.py following existing pattern
3. Create template.md with prompt
4. Create __init__.py with exports
5. Add spec to `ai_capabilities/specs.py`
6. Update `configs/models.yaml`
7. **Add tests** in `tests/unit/test_my_analyzer.py`
8. **Update documentation** in this README

### Adding New Generators

Generators can extend `ModularImageGenerator`:

```python
from ai_tools.modular_image_generator.tool import ModularImageGenerator

class MyGenerator(ModularImageGenerator):
    def my_method(self, subject, specs):
        return self.generate(subject_image=subject, **specs)
```

## License

[Your License]

## Support

For issues or questions:
- GitHub Issues: [repo-url]/issues
- Documentation: This README

## Credits

Built with:
- Gemini 2.0 Flash (analysis)
- Gemini 2.5 Flash (image generation)
- GPT-4o/GPT-5 (prompt enhancement)
- Sora (video generation)
- LiteLLM (provider abstraction)
- Pydantic (structured outputs)
