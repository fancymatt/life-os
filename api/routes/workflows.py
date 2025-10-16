"""
Workflow Routes

Endpoints for executing multi-step workflows.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from api.core.simple_workflow import SimpleWorkflow, WorkflowDefinition, WorkflowStep, WorkflowExecution
from api.agents.story_planner import StoryPlannerAgent
from api.agents.story_writer import StoryWriterAgent
from api.agents.story_illustrator import StoryIllustratorAgent

router = APIRouter()

# In-memory storage for workflow executions
workflow_executions: Dict[str, WorkflowExecution] = {}


class StoryGenerationRequest(BaseModel):
    """Request to generate a story"""
    character: Dict[str, Any]
    theme: str = "adventure"
    target_scenes: int = 5
    age_group: str = "children"
    prose_style: str = "descriptive"
    art_style: str = "digital_art"
    max_illustrations: int = 5


@router.post("/story-generation/execute")
async def execute_story_generation(request: StoryGenerationRequest):
    """
    Execute story generation workflow

    Generates an illustrated story with:
    1. Story Planner - Creates outline
    2. Story Writer - Writes full story
    3. Story Illustrator - Generates illustrations

    Returns execution_id for tracking progress.
    """
    try:
        # Create workflow definition
        workflow_def = WorkflowDefinition(
            workflow_id="story_generation_v1",
            name="Story Generation with Illustrations",
            description="Create an illustrated story from character and theme",
            version="1.0.0",
            steps=[
                WorkflowStep(
                    step_id="plan_story",
                    agent_id="story_planner",
                    description="Generate story outline",
                    inputs=["character", "theme", "target_scenes", "age_group"],
                    outputs=["outline"]
                ),
                WorkflowStep(
                    step_id="write_story",
                    agent_id="story_writer",
                    description="Write full story from outline",
                    inputs=["outline", "prose_style"],
                    outputs=["written_story"]
                ),
                WorkflowStep(
                    step_id="illustrate_story",
                    agent_id="story_illustrator",
                    description="Generate illustrations for scenes",
                    inputs=["written_story", "art_style", "max_illustrations"],
                    outputs=["illustrated_story"]
                )
            ]
        )

        # Create agents
        agents = {
            "story_planner": StoryPlannerAgent(),
            "story_writer": StoryWriterAgent(),
            "story_illustrator": StoryIllustratorAgent()
        }

        # Create workflow executor
        workflow = SimpleWorkflow(workflow_def, agents)

        # Prepare input parameters
        input_params = {
            "character": request.character,
            "theme": request.theme,
            "target_scenes": request.target_scenes,
            "age_group": request.age_group,
            "prose_style": request.prose_style,
            "art_style": request.art_style,
            "max_illustrations": request.max_illustrations,
            "character_appearance": request.character.get('appearance', '')
        }

        # Execute workflow
        execution = await workflow.execute(input_params)

        # Store execution for later retrieval
        workflow_executions[execution.execution_id] = execution

        # Return immediate response
        return {
            "execution_id": execution.execution_id,
            "status": execution.status,
            "message": "Workflow execution started" if execution.status == "running" else "Workflow completed",
            "current_step": execution.current_step,
            "progress": execution.progress,
            "result": execution.result if execution.status == "completed" else None,
            "error": execution.error if execution.status == "failed" else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    """
    Get workflow execution status and results

    Returns current status, progress, and results if completed.
    """
    execution = workflow_executions.get(execution_id)

    if not execution:
        raise HTTPException(status_code=404, detail=f"Execution not found: {execution_id}")

    return {
        "execution_id": execution.execution_id,
        "workflow_id": execution.workflow_id,
        "status": execution.status,
        "current_step": execution.current_step,
        "steps_completed": execution.steps_completed,
        "steps_total": execution.steps_total,
        "progress": execution.progress,
        "result": execution.result,
        "error": execution.error,
        "started_at": execution.started_at.isoformat(),
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "execution_time": execution.execution_time
    }


@router.get("/executions")
async def list_executions(limit: int = 10):
    """
    List recent workflow executions

    Returns most recent workflow executions.
    """
    executions = sorted(
        workflow_executions.values(),
        key=lambda x: x.started_at,
        reverse=True
    )[:limit]

    return [
        {
            "execution_id": e.execution_id,
            "workflow_id": e.workflow_id,
            "status": e.status,
            "progress": e.progress,
            "started_at": e.started_at.isoformat(),
            "execution_time": e.execution_time
        }
        for e in executions
    ]


@router.get("/story-generation/info")
async def get_story_generation_info():
    """
    Get information about the story generation workflow

    Returns workflow definition and parameter options.
    """
    return {
        "workflow_id": "story_generation_v1",
        "name": "Story Generation with Illustrations",
        "description": "Create an illustrated story from character and theme",
        "steps": [
            {
                "step": 1,
                "name": "Story Planning",
                "description": "Generates story outline with scenes",
                "estimated_time": "10-15 seconds"
            },
            {
                "step": 2,
                "name": "Story Writing",
                "description": "Writes full story from outline",
                "estimated_time": "20-30 seconds"
            },
            {
                "step": 3,
                "name": "Story Illustration",
                "description": "Generates images for key scenes",
                "estimated_time": "30-60 seconds"
            }
        ],
        "parameters": {
            "character": {
                "type": "object",
                "required": True,
                "description": "Character details (name, appearance, personality)",
                "example": {
                    "name": "Luna",
                    "appearance": "young girl with curly brown hair and green eyes",
                    "personality": "curious and brave"
                }
            },
            "theme": {
                "type": "string",
                "default": "adventure",
                "options": ["adventure", "mystery", "friendship", "fantasy", "sci-fi", "humor"],
                "description": "Story theme"
            },
            "target_scenes": {
                "type": "integer",
                "default": 5,
                "min": 3,
                "max": 10,
                "description": "Number of scenes in the story"
            },
            "age_group": {
                "type": "string",
                "default": "children",
                "options": ["children", "young_adult", "adult"],
                "description": "Target audience age group"
            },
            "prose_style": {
                "type": "string",
                "default": "descriptive",
                "options": ["descriptive", "concise", "poetic", "humorous", "simple"],
                "description": "Writing style"
            },
            "art_style": {
                "type": "string",
                "default": "digital_art",
                "options": ["watercolor", "digital_art", "sketch", "cartoon", "realistic", "anime"],
                "description": "Illustration style"
            },
            "max_illustrations": {
                "type": "integer",
                "default": 5,
                "min": 1,
                "max": 10,
                "description": "Maximum number of illustrations to generate"
            }
        },
        "estimated_cost": "$0.05-$0.30 depending on complexity",
        "estimated_time": "60-120 seconds total"
    }
