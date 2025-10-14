Here’s a concise `.md` summary that captures everything about the tool and system you’ve been describing:

---

# AI-Studio Architecture: Modular Prompt Tools & Workflow Orchestration

## Overview

**AI-Studio** is a modular framework for developing, evaluating, and orchestrating AI-driven “prompt tools.”
Each tool performs a single, typed transformation — such as converting a creative brief into an art direction spec — and can be chained with other tools into complex workflows.
This allows outputs from one domain (e.g., cinematography) to be reused seamlessly in others (e.g., video generation, storyboard creation).

---

## Philosophy

* **Small, Composable Tools** — each tool performs one job with clearly defined input/output schemas.
* **Shared Guidance** — all tools reference a central library of creative or stylistic guidance.
* **Typed Interfaces** — every tool input/output uses Pydantic (or JSON Schema) types for validation and reusability.
* **Versioned Workflows** — workflows are composed of interchangeable tools that evolve independently.
* **Model Agnostic** — tools can call any LLM (Claude, Gemini, GPT, etc.) through a routing layer.
* **Continuous Improvement** — prompts are tested and benchmarked with *promptfoo* to ensure upgrades don’t regress quality.

---

## Layers

### 1. Capabilities (Specs)

Data models define what each tool consumes and produces.

```python
class Brief(BaseModel):
    description: str
    references: list[str] = []

class ArtDirectionSpec(BaseModel):
    mood: str
    palette: list[str]
    style_refs: list[str]

class CinematographySpec(BaseModel):
    shots: list[str]
    camera: str
    movement: str
    color_grade: str

class VideoPromptSpec(BaseModel):
    prompt: str
    model_hint: Optional[str] = None
```

---

### 2. Tools

Each tool:

* Has a Markdown/Jinja prompt template.
* Calls an LLM through a router (`LiteLLM` or similar).
* Produces validated structured output.
* Includes local `promptfoo` tests.
* Pulls current creative guidance dynamically.

Examples:
`art_direction`, `cinematography`, `video_prompt`, `storyboard_prompt`, `thumbnail_prompt`.

---

### 3. Shared Components

* **Router** — abstraction for LLM calls (multi-provider).
* **Guidance Loader** — retrieves the latest visual/creative guidelines from markdown sources or RAG.
* **JSON Utilities** — ensure robust parsing of model output.
* **promptfoo Tests** — enforce JSON validity, semantic correctness, and stylistic fidelity.

---

### 4. Workflows

Workflows compose tools into directed graphs, connecting outputs to inputs.

#### Example A: Promo Video

`Brief → ArtDirection → Cinematography → VideoPrompt → VideoGenerator`

#### Example B: Storyboard Pack

`Brief → ArtDirection → Cinematography → StoryboardPrompt (+ ThumbnailPrompt)`

Both workflows reuse the same intermediate tools but diverge in their final outputs.

---

## Example Project Layout

```
ai-studio/
  ai_capabilities/      # schemas
  ai_guides/            # shared visual guidance
  ai_tools/             # atomic prompt tools
  ai_workflows/         # orchestration scripts or LangGraph graphs
  configs/              # model router + environment configs
  README.md
```

---

## Testing with promptfoo

`promptfoo` is an open-source evaluation framework for prompts and LLM workflows.
It lets you define test cases, run them across providers, and assert correctness using JSON validation, semantic similarity, or model-graded rubrics.

```yaml
prompts:
  - file://../template.md
providers:
  - anthropic:messages:claude-sonnet
  - google:gemini-pro
tests:
  - vars:
      brief: '{"description": "Moody neon sci-fi alley"}'
    assert:
      - type: is-json
        schema:
          required: [mood, palette, style_refs]
```

Run locally:

```bash
npx promptfoo eval -o report.html
```

---

## Evolution Path

1. Start with Python scripts for tools and direct chaining.
2. Introduce **LangGraph** for graph-based orchestration and state management.
3. Use **Temporal** for long-running durable execution (batch video generation, etc.).
4. Instrument with **LangSmith** or **Arize Phoenix** for traces and metrics.
5. Optionally compile better prompts automatically via **DSPy**.
6. Expose the library via **MCP (Model Context Protocol)** for cross-agent interoperability.

---

## Why It Matters

* **Scalable Creativity:** small, testable tools can be remixed endlessly.
* **Cross-Project Leverage:** improvements to visual guidance or one tool propagate everywhere.
* **Reliability:** type safety + automated evaluation ensures structured, consistent outputs.
* **Interoperability:** router abstraction and open standards allow Claude, Gemini, GPT, and others to coexist.
* **Observability:** integrated testing and tracing make performance measurable.

---

**In short:**
AI-Studio turns your scattered prompts into a coherent ecosystem — a living library of modular creative tools that can be recombined into any future workflow.
