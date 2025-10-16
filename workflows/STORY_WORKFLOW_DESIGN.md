# Story Generation Workflow - Design Document

**Created**: 2025-10-15
**Status**: 🚧 Prototype Phase
**Purpose**: Validate workflow orchestration architecture for Phase 2

---

## Overview

The Story Generation Workflow is a **multi-agent workflow prototype** that creates illustrated stories involving characters. This serves as a test case for the workflow orchestration system planned in Phase 2.

### Workflow Steps

```
1. Story Planner Agent
   ├─ Input: Character, theme, target length
   ├─ Process: Generate story outline with scenes
   └─ Output: Story outline (JSON)
         ↓
2. Story Writer Agent
   ├─ Input: Story outline, prose style
   ├─ Process: Write full story with scene descriptions
   └─ Output: Complete story with scene markers
         ↓
3. Image Illustrator (existing modular generator)
   ├─ Input: Scene descriptions, character details
   ├─ Process: Generate images for key scenes
   └─ Output: Illustrated story (text + images)
```

---

## Architecture

### Workflow Engine (Minimal Implementation)

For this prototype, we'll create a **simplified workflow engine** that:
- Executes steps sequentially
- Passes data between steps
- Handles errors gracefully
- Tracks progress

**File**: `api/core/simple_workflow.py`

```python
class WorkflowStep:
    step_id: str
    execute: Callable  # Function to run
    inputs: List[str]  # Input variable names
    outputs: List[str] # Output variable names

class SimpleWorkflow:
    steps: List[WorkflowStep]
    context: Dict[str, Any]  # Shared data between steps

    async def execute():
        for step in steps:
            result = await step.execute(context)
            context.update(result)
```

### Agent Interface (Minimal Implementation)

**File**: `api/core/simple_agent.py`

```python
class Agent(ABC):
    @abstractmethod
    async def execute(self, input_data: Dict) -> Dict:
        """Execute agent task"""
        pass

    def get_config(self) -> Dict:
        """Return agent configuration"""
        pass
```

---

## Component Design

### 1. Story Planner Agent

**File**: `api/agents/story_planner.py`

**Input Schema**:
```json
{
  "character": {
    "name": "string",
    "appearance": "string (optional)",
    "personality": "string (optional)"
  },
  "theme": "string (e.g., 'adventure', 'mystery', 'friendship')",
  "target_scenes": "int (default: 5)",
  "age_group": "string (e.g., 'children', 'young_adult', 'adult')"
}
```

**Output Schema**:
```json
{
  "title": "string",
  "outline": [
    {
      "scene_number": 1,
      "title": "string",
      "description": "string",
      "action": "string",
      "illustration_prompt": "string (for image generation)",
      "estimated_words": 150
    }
  ],
  "total_estimated_words": 750
}
```

**Implementation**:
- Uses LLM (Gemini/OpenAI) to generate structured outline
- Ensures logical story flow
- Creates illustration prompts for each scene
- Can be parameterized with theme, tone, complexity

---

### 2. Story Writer Agent

**File**: `api/agents/story_writer.py`

**Input Schema**:
```json
{
  "outline": "StoryOutline (from planner)",
  "prose_style": "string (e.g., 'descriptive', 'concise', 'poetic')",
  "perspective": "string (e.g., 'first_person', 'third_person')",
  "tense": "string (e.g., 'past', 'present')"
}
```

**Output Schema**:
```json
{
  "title": "string",
  "story": "string (full text)",
  "scenes": [
    {
      "scene_number": 1,
      "text": "string (scene text)",
      "illustration_prompt": "string"
    }
  ],
  "word_count": 823,
  "metadata": {
    "prose_style": "descriptive",
    "perspective": "third_person",
    "generated_at": "ISO datetime"
  }
}
```

**Implementation**:
- Expands each scene from outline
- Maintains character consistency
- Applies prose style
- Includes scene markers for illustration

---

### 3. Image Illustrator (Wrapper for Existing Tools)

**File**: `api/agents/story_illustrator.py`

**Input Schema**:
```json
{
  "story": "WrittenStory (from writer)",
  "character_appearance": "string (visual description)",
  "art_style": "string (e.g., 'watercolor', 'digital_art', 'sketch')",
  "max_illustrations": "int (default: 5)"
}
```

**Output Schema**:
```json
{
  "title": "string",
  "story": "string",
  "illustrations": [
    {
      "scene_number": 1,
      "image_url": "string",
      "prompt_used": "string",
      "generation_time": "float"
    }
  ],
  "total_generation_time": 45.2
}
```

**Implementation**:
- Uses existing `modular_image_generator`
- Generates consistent character across scenes
- Applies art style
- Can use subject image if provided

---

## Workflow Definition

**File**: `workflows/definitions/story_generation.json`

```json
{
  "workflow_id": "story_generation_v1",
  "name": "Story Generation with Illustrations",
  "description": "Create an illustrated story from character and theme",
  "version": "1.0.0",
  "steps": [
    {
      "step_id": "plan_story",
      "agent": "story_planner",
      "inputs": ["character", "theme", "target_scenes", "age_group"],
      "outputs": ["outline"]
    },
    {
      "step_id": "write_story",
      "agent": "story_writer",
      "inputs": ["outline", "prose_style", "perspective", "tense"],
      "outputs": ["written_story"]
    },
    {
      "step_id": "illustrate_story",
      "agent": "story_illustrator",
      "inputs": ["written_story", "character_appearance", "art_style", "max_illustrations"],
      "outputs": ["illustrated_story"]
    }
  ],
  "parameters": {
    "character": {
      "type": "object",
      "required": true
    },
    "theme": {
      "type": "string",
      "default": "adventure"
    },
    "prose_style": {
      "type": "string",
      "default": "descriptive",
      "options": ["descriptive", "concise", "poetic", "humorous"]
    },
    "art_style": {
      "type": "string",
      "default": "digital_art",
      "options": ["watercolor", "digital_art", "sketch", "cartoon", "realistic"]
    }
  }
}
```

---

## API Endpoints

### Execute Workflow

```http
POST /api/workflows/story-generation/execute
Content-Type: application/json

{
  "character": {
    "name": "Luna",
    "appearance": "young girl with curly brown hair and green eyes",
    "personality": "curious and brave"
  },
  "theme": "adventure",
  "target_scenes": 5,
  "prose_style": "descriptive",
  "art_style": "watercolor",
  "max_illustrations": 5
}

Response:
{
  "workflow_execution_id": "wf_abc123",
  "status": "running",
  "current_step": "plan_story",
  "progress": 0.1
}
```

### Get Workflow Status

```http
GET /api/workflows/executions/{execution_id}

Response:
{
  "execution_id": "wf_abc123",
  "status": "completed",
  "progress": 1.0,
  "steps_completed": 3,
  "steps_total": 3,
  "result": {
    "title": "Luna's Magical Forest Adventure",
    "story": "...",
    "illustrations": [...]
  },
  "execution_time": 67.3,
  "started_at": "2025-10-15T14:30:00Z",
  "completed_at": "2025-10-15T14:31:07Z"
}
```

---

## Example Usage

### Scenario 1: Children's Adventure Story

```python
# Request
{
  "character": {
    "name": "Milo",
    "appearance": "small orange cat with white paws",
    "personality": "playful but sometimes scared"
  },
  "theme": "friendship",
  "target_scenes": 4,
  "age_group": "children",
  "prose_style": "simple",
  "art_style": "cartoon"
}

# Output (abbreviated)
{
  "title": "Milo Makes a Friend",
  "story": "Milo was a little orange cat who lived in a cozy house...",
  "scenes": [
    {
      "scene_number": 1,
      "text": "Milo was sitting by the window...",
      "illustration": "/output/milo_scene1.png"
    }
  ]
}
```

### Scenario 2: Mystery Story for Young Adults

```python
# Request
{
  "character": {
    "name": "Detective Sarah Chen",
    "appearance": "young woman with short black hair, wearing a trench coat",
    "personality": "sharp, observant, determined"
  },
  "theme": "mystery",
  "target_scenes": 6,
  "age_group": "young_adult",
  "prose_style": "concise",
  "art_style": "noir"
}
```

---

## Testing Strategy

### Unit Tests
- Test each agent independently
- Mock LLM responses
- Verify output schemas

### Integration Tests
- Test workflow execution end-to-end
- Test error handling (what if writer fails?)
- Test parameter variations

### Manual Tests
- Generate stories with different themes
- Try different prose styles
- Evaluate illustration quality
- Test edge cases (very short/long stories)

---

## Success Criteria

### Functional
- ✅ Workflow executes all 3 steps successfully
- ✅ Story has coherent beginning, middle, end
- ✅ Illustrations match scene descriptions
- ✅ Character consistency across scenes
- ✅ Parameterization works (theme, style, etc.)

### Technical
- ✅ Identifies architectural needs for Phase 2
- ✅ Demonstrates workflow orchestration patterns
- ✅ Tests agent communication
- ✅ Validates error handling approach
- ✅ Measures performance (total execution time)

### Architectural Insights
- Document what works well
- Document pain points
- Identify missing capabilities
- Suggest improvements for Phase 2

---

## Implementation Plan

### Step 1: Core Workflow Engine (2-3 hours)
- [ ] Create `api/core/simple_workflow.py`
- [ ] Create `api/core/simple_agent.py`
- [ ] Add workflow execution tracking
- [ ] Add error handling

### Step 2: Story Planner Agent (2-3 hours)
- [ ] Create `api/agents/story_planner.py`
- [ ] Implement LLM integration for outline generation
- [ ] Add scene structure validation
- [ ] Create illustration prompt generation
- [ ] Test with various themes

### Step 3: Story Writer Agent (2-3 hours)
- [ ] Create `api/agents/story_writer.py`
- [ ] Implement scene expansion logic
- [ ] Add prose style variations
- [ ] Ensure character consistency
- [ ] Test with different outlines

### Step 4: Image Illustrator Integration (1-2 hours)
- [ ] Create `api/agents/story_illustrator.py`
- [ ] Wrap existing modular image generator
- [ ] Add batch illustration support
- [ ] Handle illustration failures gracefully

### Step 5: API Endpoints (1-2 hours)
- [ ] Create `api/routes/workflows.py`
- [ ] Add workflow execution endpoint
- [ ] Add status checking endpoint
- [ ] Add workflow definition endpoint

### Step 6: Testing & Refinement (2-3 hours)
- [ ] End-to-end workflow tests
- [ ] Generate sample stories
- [ ] Document learnings
- [ ] Commit to git

**Total Estimated Time**: 10-16 hours

---

## Learnings to Document

After building this prototype, document:

1. **What worked well**:
   - Which patterns were easy to implement?
   - What felt natural?
   - What would scale well?

2. **Pain points**:
   - What was clunky or awkward?
   - What required workarounds?
   - What would break at scale?

3. **Missing capabilities**:
   - What features are needed for Phase 2?
   - What abstractions are missing?
   - What would improve developer experience?

4. **Performance observations**:
   - Bottlenecks?
   - Opportunities for parallelization?
   - Resource usage?

---

## Future Enhancements (Post-Prototype)

### Phase 2 Workflow Engine
- Parallel step execution
- Conditional branching (if/else)
- Loops (generate N variations)
- Retry logic with exponential backoff
- Workflow templates
- Visual workflow builder (UI)

### Enhanced Agents
- Multi-modal agents (text + image input)
- Agent collaboration (agents asking each other for help)
- Agent learning (improve from user feedback)
- Agent specialization (agents for specific genres)

### Advanced Features
- Story variations (generate 3 different endings)
- Interactive stories (user chooses path)
- Story editing (regenerate specific scenes)
- Export formats (PDF, ePub, video)
- Voice narration (text-to-speech)

---

## Notes for Phase 2 Architecture

Based on this prototype, Phase 2 should include:

1. **Plugin System**: Story agents should be plugins
2. **Workflow DSL**: JSON definition is good, but needs validation
3. **Context Management**: Agents need shared context (character details, etc.)
4. **Error Recovery**: Workflows need retry/fallback strategies
5. **Progress Tracking**: Real-time progress updates essential
6. **Cost Tracking**: Track LLM costs per workflow
7. **Caching**: Cache outlines, avoid regenerating entire stories
8. **Streaming**: Stream story text as it's generated
9. **Collaborative Editing**: User edits outline → regenerate story
10. **Permissions**: Some workflows may need approval (e.g., publishing)

---

## Example Output

**Input**:
```json
{
  "character": {"name": "Zara", "appearance": "astronaut", "personality": "determined"},
  "theme": "space exploration",
  "target_scenes": 5,
  "prose_style": "cinematic"
}
```

**Output** (abbreviated):
```
Title: Zara's Cosmic Discovery

Scene 1: The Mission Briefing
[Illustration: Zara in mission control room]
Zara stood before the holographic star map, her reflection ghosting across
the swirling galaxies. Tomorrow, she would pilot the Exodus One further
than any human had ventured...

Scene 2: Launch
[Illustration: Rocket launching into space]
The countdown echoed through her helmet. Three. Two. One. The world
transformed into a blur of sound and fury as thousands of tons of thrust
pushed her toward the stars...

[... 3 more scenes ...]

Total generation time: 73.4 seconds
Word count: 1,247
Illustrations: 5
```

---

**This prototype will inform all future workflow and agent architecture decisions.**
