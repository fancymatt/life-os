# Design Patterns & Best Practices

**Last Updated**: 2025-10-17
**Status**: Reference Guide

---

## Overview

This document captures the design patterns and best practices established in Life-OS, using the **Character + Appearance Analyzer** system as the gold standard example. These patterns should be replicated when building new entities, tools, and workflows.

---

## Table of Contents

1. [The Gold Standard: Character + Appearance Analyzer](#the-gold-standard-character--appearance-analyzer)
2. [Core Design Principles](#core-design-principles)
3. [Entity Design Pattern](#entity-design-pattern)
4. [AI Tool Design Pattern](#ai-tool-design-pattern)
5. [Tool-Entity Integration Pattern](#tool-entity-integration-pattern)
6. [Workflow Integration Pattern](#workflow-integration-pattern)
7. [UI/UX Patterns](#uiux-patterns)
8. [Data Flow Architecture](#data-flow-architecture)
9. [Replication Checklist](#replication-checklist)

---

## The Gold Standard: Character + Appearance Analyzer

### Why This Works Well

The Character entity and Appearance Analyzer demonstrate excellent patterns because:

1. **Modular Data Model**: Character appearance is broken into discrete, editable fields
2. **Standalone Tool**: The analyzer can be used independently or triggered from the UI
3. **Configurable**: Prompts and models can be edited without code changes
4. **Integrated**: The tool is seamlessly embedded in the character entity UI
5. **Workflow-Ready**: Character data and analysis flow into larger workflows (story generation)
6. **Great UX**: Toast notifications, loading states, real-time updates

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      CHARACTER SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌───────────────────────────┐       │
│  │   Entity:    │      │   AI Tool:                │       │
│  │  Character   │─────▶│  appearance_analyzer      │       │
│  │              │      │                           │       │
│  │ • Fields     │      │ • Prompt Template         │       │
│  │ • CRUD       │      │ • Model Config            │       │
│  │ • UI Config  │      │ • Structured Output       │       │
│  └──────────────┘      └───────────────────────────┘       │
│         │                         │                         │
│         └─────────┬───────────────┘                         │
│                   ▼                                         │
│         ┌──────────────────┐                                │
│         │   Workflow:      │                                │
│         │ Story Generation │                                │
│         │                  │                                │
│         │ Uses character   │                                │
│         │ appearance data  │                                │
│         └──────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Design Principles

### 1. Modularity Over Monoliths

**❌ Don't**: Single large text field for complex data
```python
character = {
    "appearance": "A tall woman with brown hair and green eyes..."  # Too vague
}
```

**✅ Do**: Break down into discrete, semantic fields
```python
character = {
    "age": "mid-30s",
    "skin_tone": "fair",
    "face_description": "oval face, green eyes, high cheekbones",
    "hair_description": "shoulder-length brown hair, wavy",
    "body_description": "tall, athletic build"
}
```

**Benefits**:
- Individual fields can be edited independently
- AI tools can target specific aspects
- Data can be composed flexibly for different contexts
- Easier validation and quality control

### 2. Separation of Concerns

**Data Layer** (entities) ↔ **Processing Layer** (tools) ↔ **Orchestration Layer** (workflows)

Each layer should be:
- **Independent**: Can function without the others
- **Composable**: Can be combined in different ways
- **Testable**: Can be tested in isolation

### 3. Configuration Over Code

**❌ Don't**: Hardcode prompts and models in Python
```python
class Analyzer:
    def analyze(self):
        prompt = "Analyze this image and..."  # Hardcoded
        model = "gemini-2.0-flash-exp"        # Hardcoded
```

**✅ Do**: Store configuration in editable files/database
```python
# Prompt in: ai_tools/character_appearance_analyzer/template.md
# Model in: configs/models.yaml or data/tool_configs/overrides.yaml
```

**Benefits**:
- Non-developers can tune prompts
- A/B testing different prompts/models
- No deployment needed for prompt changes
- User-specific customization possible

### 4. User Agency & Transparency

Give users control and visibility:
- **Re-analyze buttons**: Let users manually trigger AI processing
- **Editable results**: AI suggestions, not mandates
- **Toast notifications**: Show what's happening, when it's done
- **Progress indicators**: Loading states, spinners, step counters

---

## Entity Design Pattern

### Data Model Structure

**File**: `api/services/character_service.py`

```python
# Character data structure
{
    "character_id": "uuid",
    "name": "string",

    # Core fields
    "personality": "string",

    # Modular appearance fields (from AI analysis)
    "age": "string",
    "skin_tone": "string",
    "face_description": "string",
    "hair_description": "string",
    "body_description": "string",

    # Metadata
    "reference_image_path": "path",
    "created_at": "timestamp",
    "metadata": {}
}
```

### API Endpoints

**File**: `api/routes/characters.py`

Standard CRUD operations:
```python
GET    /api/characters/              # List all
GET    /api/characters/{id}          # Get one
POST   /api/characters/              # Create
PUT    /api/characters/{id}          # Update
DELETE /api/characters/{id}          # Delete
GET    /api/characters/{id}/image    # Get reference image
```

Special operations:
```python
POST   /api/characters/from-subject  # Create from subject image
POST   /api/characters/{id}/re-analyze-appearance  # Re-run analyzer
```

### Frontend Entity Configuration

**File**: `frontend/src/components/entities/configs/charactersConfig.jsx`

```javascript
export const charactersConfig = {
  entityType: 'character',
  title: 'Characters',
  icon: '👤',

  // Enable features
  enableSearch: true,
  enableSort: true,
  enableEdit: true,

  // Data fetching
  fetchEntities: async () => { /* ... */ },

  // UI renderers
  renderCard: (character) => { /* Grid card */ },
  renderPreview: (character) => { /* Detail sidebar preview */ },
  renderEdit: (character, editedData, handlers) => { /* Edit form */ },

  // CRUD operations
  saveEntity: async (character, updates) => { /* ... */ },
  deleteEntity: async (character) => { /* ... */ }
}
```

**Key Pattern**: The config object is data-driven and declarative. The EntityBrowser component handles the UI logic.

---

## AI Tool Design Pattern

### Directory Structure

```
ai_tools/character_appearance_analyzer/
├── tool.py              # Tool implementation
├── template.md          # Prompt template (editable)
└── README.md            # Tool documentation
```

### Tool Implementation

**File**: `ai_tools/character_appearance_analyzer/tool.py`

```python
from ai_capabilities.specs import CharacterAppearanceSpec
from ai_tools.shared.router import LLMRouter

class CharacterAppearanceAnalyzer:
    """
    Analyzes character appearance from images.

    Returns structured data with discrete appearance fields.
    """

    def __init__(self, model: Optional[str] = None):
        self.router = LLMRouter()
        self.model = model  # Allow model override

    async def aanalyze(self, image_path: Path) -> CharacterAppearanceSpec:
        """
        Analyze character appearance.

        Returns:
            CharacterAppearanceSpec with all appearance fields
        """
        # Load template (supports custom overrides)
        template = self._load_template()

        # Call LLM with structured output
        result = await self.router.generate_structured(
            model=self.model or self._get_default_model(),
            prompt=template,
            image=image_path,
            response_model=CharacterAppearanceSpec
        )

        return result

    def _load_template(self) -> str:
        """Load template with override support"""
        # Check for custom template first
        custom_path = settings.base_dir / "data" / "tool_configs" / f"{self.name}_template.md"
        if custom_path.exists():
            return custom_path.read_text()

        # Fall back to base template
        base_path = Path(__file__).parent / "template.md"
        return base_path.read_text()
```

### Structured Output Spec

**File**: `ai_capabilities/specs.py`

```python
from pydantic import BaseModel, Field

class CharacterAppearanceSpec(BaseModel):
    """Structured character appearance specification"""

    overall_description: str = Field(
        description="Complete physical description"
    )
    age: str = Field(
        description="Age or age range (e.g., 'mid-30s', 'elderly')"
    )
    skin_tone: str = Field(
        description="Skin color/tone"
    )
    face_description: str = Field(
        description="Face shape, eyes, features, gender presentation, ethnicity"
    )
    hair_description: str = Field(
        description="Hair color, style, length, texture"
    )
    body_description: str = Field(
        description="Build, height, physique"
    )
```

**Key Pattern**: Pydantic models ensure type safety and provide automatic validation. The LLM is instructed to return JSON matching this schema.

### Prompt Template

**File**: `ai_tools/character_appearance_analyzer/template.md`

```markdown
# Character Appearance Analysis

Analyze the provided image and extract detailed character appearance information.

## Instructions

1. Provide an overall physical description
2. Break down appearance into discrete components:
   - Age/age range
   - Skin tone
   - Face description (shape, eyes, features, gender presentation, ethnicity)
   - Hair description (color, style, length, texture)
   - Body description (build, height, physique)

## Guidelines

- Be specific and detailed
- Use objective, descriptive language
- Avoid subjective judgments
- Include all visible details

Return your analysis in the following JSON structure:
[Schema provided by Pydantic model]
```

**Key Pattern**: Templates are markdown for readability, stored separately from code, and support user customization.

---

## Tool-Entity Integration Pattern

### Re-Analyze Button Component

**File**: `frontend/src/components/entities/ReAnalyzeButton.jsx`

```javascript
function ReAnalyzeButton({ character, onUpdate, variant = 'default' }) {
  const [analyzing, setAnalyzing] = useState(false)
  const [toast, setToast] = useState(null)

  const handleReAnalyze = async () => {
    // Validate
    if (!character.referenceImageUrl) {
      setToast({ message: 'No reference image', type: 'error', duration: 3000 })
      return
    }

    // Start analysis
    setAnalyzing(true)
    setToast({ message: 'Analyzing appearance...', type: 'loading' })

    try {
      // Call API
      const response = await api.post(
        `/characters/${character.characterId}/re-analyze-appearance`
      )

      // Update entity data
      if (onUpdate) {
        onUpdate(response.data)
      }

      // Success notification
      setToast({
        message: 'Appearance re-analyzed! Remember to save.',
        type: 'success',
        duration: 4000
      })
    } catch (err) {
      // Error notification
      setToast({
        message: err.response?.data?.detail || 'Analysis failed',
        type: 'error',
        duration: 5000
      })
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <>
      <button onClick={handleReAnalyze} disabled={analyzing}>
        {analyzing ? '🔄 Analyzing...' : '🔍 Re-Analyze Appearance'}
      </button>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
    </>
  )
}
```

**Key Patterns**:
1. **Component isolation**: Reusable button component, not inline logic
2. **State management**: Local state for loading and notifications
3. **Error handling**: Graceful error display with user-friendly messages
4. **Loading states**: Disabled button + spinner during processing
5. **Callbacks**: `onUpdate` prop allows parent to react to changes
6. **Toast notifications**: Non-blocking, auto-dismissing feedback

### Backend Re-Analyze Endpoint

**File**: `api/routes/characters.py`

```python
@router.post("/{character_id}/re-analyze-appearance", response_model=CharacterInfo)
async def re_analyze_character_appearance(
    character_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Re-analyze appearance for a specific character.

    Forces re-analysis of reference image, updating all appearance fields.
    Returns updated character info immediately.
    """
    service = CharacterService()

    # Get character
    character_data = service.get_character(character_id)
    if not character_data:
        raise HTTPException(status_code=404, detail=f"Character not found")

    # Check for reference image
    if not character_data.get('reference_image_path'):
        raise HTTPException(status_code=400, detail=f"No reference image")

    try:
        # Run analyzer
        analyzer = CharacterAppearanceAnalyzer()
        appearance_spec = await analyzer.aanalyze(
            Path(character_data['reference_image_path'])
        )

        # Update character with all appearance fields
        character_data = service.update_character(
            character_id,
            physical_description=appearance_spec.overall_description,
            age=appearance_spec.age,
            skin_tone=appearance_spec.skin_tone,
            face_description=appearance_spec.face_description,
            hair_description=appearance_spec.hair_description,
            body_description=appearance_spec.body_description
        )

        print(f"✅ Appearance re-analyzed for {character_data['name']}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    return CharacterInfo(**character_data)
```

**Key Patterns**:
1. **Validation first**: Check character exists and has image
2. **Tool instantiation**: Create analyzer instance on-demand
3. **Service layer**: Use CharacterService for data operations
4. **Structured updates**: Update all discrete fields from analysis
5. **Error handling**: Proper HTTP status codes and error messages
6. **Logging**: Console output for debugging

---

## Workflow Integration Pattern

### Using Entity Data in Workflows

**File**: `api/routes/workflows.py`

```python
# Story generation workflow uses character appearance
async def execute_story_generation(request: StoryGenerationRequest):
    # Build character appearance from discrete fields
    appearance_parts = []
    if request.character.get('age'):
        appearance_parts.append(request.character['age'])
    if request.character.get('skin_tone'):
        appearance_parts.append(f"{request.character['skin_tone']} skin")
    if request.character.get('face_description'):
        appearance_parts.append(request.character['face_description'])
    if request.character.get('hair_description'):
        appearance_parts.append(request.character['hair_description'])
    if request.character.get('body_description'):
        appearance_parts.append(request.character['body_description'])

    character_appearance = ', '.join(appearance_parts)

    # Use in workflow
    input_params = {
        "character": request.character,
        "character_appearance": character_appearance,
        # ... other params
    }

    execution = await workflow.execute(input_params)
```

**Key Patterns**:
1. **Flexible composition**: Build appearance string from available fields
2. **Fallback support**: Handle missing fields gracefully
3. **Field prioritization**: Can choose which fields to include
4. **Context-aware**: Different workflows can compose data differently

---

## UI/UX Patterns

### Toast Notification System

**Files**:
- `frontend/src/components/Toast.jsx`
- `frontend/src/components/Toast.css`

**Usage Pattern**:
```javascript
// Loading state
setToast({ message: 'Processing...', type: 'loading' })

// Success state
setToast({ message: 'Success!', type: 'success', duration: 3000 })

// Error state
setToast({ message: 'Error occurred', type: 'error', duration: 5000 })

// Info state
setToast({ message: 'Info message', type: 'info', duration: 3000 })
```

**Design Principles**:
- **Non-blocking**: Appears at bottom of screen, doesn't interrupt
- **Auto-dismissing**: Success/error toasts disappear automatically
- **Persistent loading**: Loading toasts stay until operation completes
- **Color-coded**: Green (success), red (error), blue (info/loading)
- **Animated**: Smooth slide-in/out transitions
- **Mobile-friendly**: Repositions above navigation on mobile

**When to Use**:
- ✅ Background operations (API calls, analysis)
- ✅ Success/error feedback
- ✅ Non-critical information
- ❌ Critical errors requiring user action (use modal)
- ❌ Confirmations (use dialog/modal)

### Loading States

**Pattern**: Always show loading indicators for async operations

```javascript
// Button with loading state
<button disabled={loading}>
  {loading ? '🔄 Processing...' : '✓ Submit'}
</button>

// Spinner overlay
{loading && (
  <div className="loading-overlay">
    <div className="spinner"></div>
    <p>Processing...</p>
  </div>
)}
```

### Form Field Organization

**Pattern**: Group related fields with visual hierarchy

```javascript
{/* Section header */}
<h3 style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
  Appearance Details
</h3>

{/* Individual fields */}
<div style={{ marginBottom: '1.5rem' }}>
  <label>Age</label>
  <input value={age} onChange={handleChange} />
</div>
```

---

## Data Flow Architecture

### Read Path (Entity → Tool → Display)

```
1. User views character
   └─▶ GET /api/characters/{id}
       └─▶ CharacterService.get_character()
           └─▶ Read JSON file
               └─▶ Return character data
                   └─▶ Frontend renders fields
```

### Write Path (Tool → Entity → Storage)

```
1. User clicks "Re-Analyze"
   └─▶ POST /api/characters/{id}/re-analyze-appearance
       └─▶ CharacterAppearanceAnalyzer.aanalyze()
           └─▶ LLMRouter.generate_structured()
               └─▶ Returns CharacterAppearanceSpec
                   └─▶ CharacterService.update_character()
                       └─▶ Write JSON file
                           └─▶ Return updated data
                               └─▶ Frontend updates form
```

### Workflow Path (Entity → Workflow → Multiple Tools)

```
1. User creates story
   └─▶ POST /api/workflows/story-generation/execute
       └─▶ Load character data
           └─▶ Build appearance string from fields
               └─▶ StoryPlannerAgent (uses appearance)
                   └─▶ StoryWriterAgent
                       └─▶ StoryIllustratorAgent (uses appearance + character_id)
                           └─▶ Complete workflow
                               └─▶ Return story with illustrations
```

---

## Replication Checklist

When building a new entity + tool system, use this checklist:

### Entity Design
- [ ] Define modular data model (discrete fields, not monoliths)
- [ ] Create Pydantic response models
- [ ] Implement CRUD endpoints (GET, POST, PUT, DELETE)
- [ ] Add special endpoints for tool integration
- [ ] Create frontend entity configuration
- [ ] Implement renderCard, renderPreview, renderEdit
- [ ] Add search and sort capabilities
- [ ] Write entity service layer

### AI Tool Design
- [ ] Create tool directory structure
- [ ] Implement tool class with async methods
- [ ] Define Pydantic spec for structured output
- [ ] Create editable prompt template (template.md)
- [ ] Support custom template overrides
- [ ] Add model configuration
- [ ] Use LLMRouter for LLM calls
- [ ] Add proper error handling and logging
- [ ] Write tool documentation (README.md)

### Tool-Entity Integration
- [ ] Create trigger button component (e.g., ReAnalyzeButton)
- [ ] Add loading states and disabled states
- [ ] Implement toast notifications
- [ ] Add backend endpoint to trigger tool
- [ ] Update entity data with tool results
- [ ] Handle errors gracefully with user feedback
- [ ] Add confirmation dialogs for destructive actions (optional)
- [ ] Test integration end-to-end

### Workflow Integration
- [ ] Design workflow that uses entity data
- [ ] Build data composition logic (fields → strings/objects)
- [ ] Add fallback handling for missing fields
- [ ] Create workflow endpoints
- [ ] Implement background task execution
- [ ] Add job queue integration
- [ ] Test workflow with entity data

### UI/UX Polish
- [ ] Replace alerts with toast notifications
- [ ] Add loading indicators for all async operations
- [ ] Implement optimistic UI updates where appropriate
- [ ] Add proper error states with retry options
- [ ] Ensure mobile responsiveness
- [ ] Add keyboard shortcuts (optional)
- [ ] Test accessibility

### Configuration & Customization
- [ ] Add tool to tool configuration UI
- [ ] Support prompt editing via UI
- [ ] Support model selection via UI
- [ ] Add temperature/parameter controls
- [ ] Implement test functionality in config UI
- [ ] Document configuration options

### Testing & Documentation
- [ ] Test CRUD operations
- [ ] Test tool independently
- [ ] Test tool-entity integration
- [ ] Test workflow integration
- [ ] Write API documentation
- [ ] Update CLAUDE.md with new patterns
- [ ] Add examples to documentation

---

## Anti-Patterns to Avoid

### ❌ Don't: Hardcode AI Prompts
```python
# BAD
def analyze(self):
    prompt = "Analyze this character and tell me about their appearance..."
```

### ❌ Don't: Use Monolithic Fields
```python
# BAD
character = {
    "description": "A tall woman with brown hair..."  # Too vague, hard to use
}
```

### ❌ Don't: Block UI with Alerts
```javascript
// BAD
alert('Processing...')  // Blocks UI
const result = await process()
alert('Done!')  // Blocks UI
```

### ❌ Don't: Mix Concerns
```python
# BAD - Route doing everything
@router.post("/analyze")
async def analyze():
    # Loading data
    # Running AI
    # Saving results
    # All in one function!
```

### ❌ Don't: Ignore Loading States
```javascript
// BAD - No feedback during processing
const handleSubmit = async () => {
  await api.post('/process')  // User has no idea what's happening
}
```

### ❌ Don't: Skip Error Handling
```python
# BAD
result = await analyzer.analyze()  # What if this fails?
return result
```

---

## Future Patterns to Consider

As the system evolves, consider these patterns:

### 1. Tool Chaining
- One tool's output becomes another's input
- Example: Analyzer → Enhancer → Generator

### 2. Batch Operations
- Process multiple entities at once
- Progress tracking for batch jobs

### 3. Versioning
- Track changes to entity data over time
- Ability to rollback to previous versions

### 4. Collaboration
- Multi-user editing with conflict resolution
- Real-time updates via WebSockets

### 5. Caching
- Cache expensive AI operations
- Invalidation strategies

### 6. A/B Testing
- Test different prompts/models
- Collect metrics on performance

---

## Examples to Study

### Working Examples in Codebase

1. **Character + Appearance Analyzer** ⭐ Gold Standard
   - Entity: `api/routes/characters.py`
   - Tool: `ai_tools/character_appearance_analyzer/`
   - Integration: `frontend/src/components/entities/ReAnalyzeButton.jsx`
   - Workflow: `api/routes/workflows.py` (story generation)

2. **Story Generation Workflow**
   - Multi-agent workflow
   - Uses character data
   - Job queue integration

3. **Tool Configuration UI**
   - Edit prompts and models
   - Test tools with uploaded images
   - Model selection with restrictions

---

## Questions to Ask When Building

Before starting a new entity/tool, answer these:

1. **What discrete fields does this entity need?**
   - Don't use one big text field
   - Think about how each field will be used independently

2. **What AI tool will process this data?**
   - What's the input? (image, text, entity data)
   - What's the output? (Pydantic model)
   - Is the prompt editable by users?

3. **How will users interact with the tool?**
   - Button to trigger? Where in the UI?
   - What happens while processing?
   - What feedback do users get?

4. **How will this integrate with workflows?**
   - What data does the workflow need?
   - How is data composed/transformed?
   - Can it work with partial data?

5. **What can go wrong?**
   - Missing data?
   - API failures?
   - Invalid inputs?
   - How do we handle each case?

---

## Summary

The Character + Appearance Analyzer system demonstrates:

✅ **Modular data models** - Discrete, composable fields
✅ **Standalone tools** - Reusable, configurable AI components
✅ **Seamless integration** - Tools embedded in entity UI
✅ **Workflow-ready** - Data flows into larger processes
✅ **Great UX** - Toast notifications, loading states, real-time feedback
✅ **User control** - Editable prompts, manual triggers, configurable models
✅ **Clear separation** - Entities, tools, and workflows are independent layers

**Golden Rule**: When building new features, ask "How would this work if it followed the Character + Appearance Analyzer pattern?"

---

**Next Steps**: Use this document as a reference when planning new entities and tools. Update it as we discover new patterns and best practices.
