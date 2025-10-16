"""
Workflow Routes

Endpoints for executing multi-step workflows.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from api.core.simple_workflow import SimpleWorkflow, WorkflowDefinition, WorkflowStep
from api.agents.story_planner import StoryPlannerAgent
from api.agents.story_writer import StoryWriterAgent
from api.agents.story_illustrator import StoryIllustratorAgent
from api.services.job_queue import get_job_queue_manager
from api.models.jobs import JobType

router = APIRouter()


class TransformationParams(BaseModel):
    """Transformation story parameters"""
    type: str  # 'creature' or 'alteration'
    target: str  # Creature name or alteration description


class StoryGenerationRequest(BaseModel):
    """Request to generate a story"""
    character: Dict[str, Any]
    character_id: Optional[str] = None  # Character ID for fetching reference image
    story_type: str = "normal"  # 'normal' or 'transformation'
    # Story parameter preset IDs
    theme_id: str = "adventure"  # Preset ID from story_themes
    audience_id: str = "adult"  # Preset ID from story_audiences
    prose_style_id: str = "humorous"  # Preset ID from story_prose_styles
    # Agent configuration IDs
    planner_config_id: str = "default"
    writer_config_id: str = "default"
    illustrator_config_id: str = "default"
    # Story settings
    target_scenes: int = 5
    art_style: str = "realistic"
    max_illustrations: int = 5
    transformation: Optional[TransformationParams] = None  # Only for transformation stories
    # Appearance overrides
    outfit_id: Optional[str] = None  # Override outfit with preset
    hair_style_id: Optional[str] = None  # Override hair style with preset
    hair_color_id: Optional[str] = None  # Override hair color with preset


@router.post("/story-generation/execute")
async def execute_story_generation(request: StoryGenerationRequest, background_tasks: BackgroundTasks):
    """
    Execute story generation workflow

    Generates an illustrated story with:
    1. Story Planner - Creates outline
    2. Story Writer - Writes full story
    3. Story Illustrator - Generates illustrations

    Returns job_id for tracking progress via /api/jobs/{job_id}
    """
    # Create job for tracking
    job_manager = get_job_queue_manager()
    character_name = request.character.get('name', 'Character')
    job_id = job_manager.create_job(
        job_type=JobType.WORKFLOW,
        title=f"Generate Story: {character_name}",
        description=f"{request.theme_id.capitalize()} story with {request.max_illustrations} illustrations",
        total_steps=3,  # Planning, Writing, Illustrating
        cancelable=False
    )

    # Define background task
    async def execute_workflow():
        """Execute the story generation workflow"""
        job_manager = get_job_queue_manager()

        try:
            job_manager.start_job(job_id)
            job_manager.update_progress(job_id, 0.0, "Starting story generation...")

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
                        inputs=["character", "story_type", "theme_id", "audience_id", "target_scenes", "transformation", "planner_config_id"],
                        outputs=["outline"]
                    ),
                    WorkflowStep(
                        step_id="write_story",
                        agent_id="story_writer",
                        description="Write full story from outline",
                        inputs=["outline", "prose_style_id", "writer_config_id"],
                        outputs=["written_story"]
                    ),
                    WorkflowStep(
                        step_id="illustrate_story",
                        agent_id="story_illustrator",
                        description="Generate illustrations for scenes",
                        inputs=["written_story", "character_id", "character_appearance", "art_style", "max_illustrations", "outfit_id", "hair_style_id", "hair_color_id", "illustrator_config_id"],
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

            # Create workflow executor with progress callback
            def progress_callback(step_num: int, step_name: str, message: str):
                progress = step_num / 3.0
                job_manager.update_progress(
                    job_id,
                    progress,
                    message=message,
                    current_step=step_num
                )

            workflow = SimpleWorkflow(workflow_def, agents, progress_callback=progress_callback)

            # Prepare input parameters
            input_params = {
                "character": request.character,
                "character_id": request.character_id,
                "story_type": request.story_type,
                # Story parameter preset IDs
                "theme_id": request.theme_id,
                "audience_id": request.audience_id,
                "prose_style_id": request.prose_style_id,
                # Agent configuration IDs
                "planner_config_id": request.planner_config_id,
                "writer_config_id": request.writer_config_id,
                "illustrator_config_id": request.illustrator_config_id,
                # Story settings
                "target_scenes": request.target_scenes,
                "art_style": request.art_style,
                "max_illustrations": request.max_illustrations,
                "character_appearance": request.character.get('appearance', ''),
                "transformation": request.transformation.dict() if request.transformation else None,
                # Appearance overrides
                "outfit_id": request.outfit_id,
                "hair_style_id": request.hair_style_id,
                "hair_color_id": request.hair_color_id
            }

            # Execute workflow
            execution = await workflow.execute(input_params)

            # Check execution status
            if execution.status == "completed":
                job_manager.complete_job(job_id, result=execution.result)
                print(f"✅ Story generation completed: {execution.result.get('title', 'Untitled')}")
            else:
                job_manager.fail_job(job_id, execution.error or "Workflow failed")
                print(f"❌ Story generation failed: {execution.error}")

        except Exception as e:
            job_manager.fail_job(job_id, f"Story generation failed: {str(e)}")
            print(f"❌ Story generation failed with unexpected error: {e}")

    # Start workflow in background
    background_tasks.add_task(execute_workflow)

    return {
        "message": "Story generation started",
        "status": "queued",
        "job_id": job_id,
        "character": character_name,
        "theme_id": request.theme_id
    }




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
