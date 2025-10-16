"""
Story Tool Routes

Endpoints for running individual story generation tools.
These are the component tools that make up the story generation workflow.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from pydantic import BaseModel

from api.models.jobs import JobType
from api.models.auth import User
from api.services.job_queue import get_job_queue_manager
from api.dependencies.auth import get_current_active_user
from api.agents.story_planner import StoryPlannerAgent
from api.agents.story_writer import StoryWriterAgent
from api.agents.story_illustrator import StoryIllustratorAgent

router = APIRouter()


# Request Models
class StoryPlannerRequest(BaseModel):
    """Request for story planner"""
    character: Dict[str, Any]
    theme: str = "adventure"
    target_word_count: int = 500
    max_scenes: int = 5


class StoryWriterRequest(BaseModel):
    """Request for story writer"""
    outline: Dict[str, Any]  # StoryOutline from planner
    character: Dict[str, Any]
    theme: str = "adventure"


class StoryIllustratorRequest(BaseModel):
    """Request for story illustrator"""
    written_story: Dict[str, Any]  # WrittenStory from writer
    character_appearance: str = ""
    art_style: str = "digital_art"
    max_illustrations: int = 5


# Response Models
class ToolResponse(BaseModel):
    """Response for tool execution"""
    status: str
    result: Optional[Dict[str, Any]] = None
    job_id: Optional[str] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


@router.get("/")
async def list_story_tools():
    """List all available story tools"""
    return [
        {
            "name": "story-planner",
            "display_name": "Story Planner",
            "description": "Creates a structured story outline with scenes and illustration prompts",
            "input": "Character info, theme, target word count",
            "output": "Story outline with title, scenes, and illustration prompts",
            "estimated_cost": 0.01,
            "estimated_time_seconds": 10
        },
        {
            "name": "story-writer",
            "display_name": "Story Writer",
            "description": "Writes the full narrative from a story outline",
            "input": "Story outline from planner",
            "output": "Complete written story with formatted text",
            "estimated_cost": 0.02,
            "estimated_time_seconds": 15
        },
        {
            "name": "story-illustrator",
            "display_name": "Story Illustrator",
            "description": "Generates illustrations for story scenes using DALL-E",
            "input": "Written story with scenes and character appearance",
            "output": "Story with generated illustration images",
            "estimated_cost": 0.20,
            "estimated_time_seconds": 45
        }
    ]


# Story Planner
async def run_planner_job(job_id: str, request: StoryPlannerRequest):
    """Background task to run story planner"""
    job_manager = get_job_queue_manager()

    try:
        job_manager.start_job(job_id)
        job_manager.update_progress(job_id, 0.2, "Planning story structure...")

        # Execute planner
        agent = StoryPlannerAgent()
        result = await agent.execute({
            "character": request.character,
            "theme": request.theme,
            "target_word_count": request.target_word_count,
            "max_scenes": request.max_scenes
        })

        job_manager.update_progress(job_id, 0.9, "Finalizing outline...")
        job_manager.complete_job(job_id, result)

    except Exception as e:
        job_manager.fail_job(job_id, str(e))


@router.post("/story-planner")
async def plan_story(
    request: StoryPlannerRequest,
    background_tasks: BackgroundTasks,
    async_mode: bool = Query(False, description="Run in background and return job_id"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a structured story outline

    Takes character information and theme, returns a story outline with:
    - Title
    - Scenes with descriptions and illustration prompts
    - Overall narrative structure
    """

    # Async mode: Create job and return immediately
    if async_mode:
        character_name = request.character.get('name', 'Character')
        job_id = get_job_queue_manager().create_job(
            job_type=JobType.WORKFLOW,
            title=f"Plan Story: {character_name}",
            description=f"{request.theme.capitalize()} story planning"
        )

        background_tasks.add_task(run_planner_job, job_id, request)

        return ToolResponse(
            status="queued",
            job_id=job_id
        )

    # Synchronous mode: Run and return result
    import time
    start_time = time.time()

    try:
        agent = StoryPlannerAgent()
        result = await agent.execute({
            "character": request.character,
            "theme": request.theme,
            "target_word_count": request.target_word_count,
            "max_scenes": request.max_scenes
        })

        processing_time = time.time() - start_time

        return ToolResponse(
            status="completed",
            result=result,
            processing_time=processing_time
        )

    except Exception as e:
        return ToolResponse(
            status="failed",
            error=str(e)
        )


# Story Writer
async def run_writer_job(job_id: str, request: StoryWriterRequest):
    """Background task to run story writer"""
    job_manager = get_job_queue_manager()

    try:
        job_manager.start_job(job_id)
        job_manager.update_progress(job_id, 0.2, "Writing story narrative...")

        # Execute writer
        agent = StoryWriterAgent()
        result = await agent.execute({
            "outline": request.outline,
            "character": request.character,
            "theme": request.theme
        })

        job_manager.update_progress(job_id, 0.9, "Finalizing story...")
        job_manager.complete_job(job_id, result)

    except Exception as e:
        job_manager.fail_job(job_id, str(e))


@router.post("/story-writer")
async def write_story(
    request: StoryWriterRequest,
    background_tasks: BackgroundTasks,
    async_mode: bool = Query(False, description="Run in background and return job_id"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Write a complete story from an outline

    Takes a story outline (from the planner) and generates the full narrative text.
    """

    # Async mode: Create job and return immediately
    if async_mode:
        outline_title = request.outline.get('title', 'Story')
        job_id = get_job_queue_manager().create_job(
            job_type=JobType.WORKFLOW,
            title=f"Write Story: {outline_title}",
            description="Writing full narrative"
        )

        background_tasks.add_task(run_writer_job, job_id, request)

        return ToolResponse(
            status="queued",
            job_id=job_id
        )

    # Synchronous mode: Run and return result
    import time
    start_time = time.time()

    try:
        agent = StoryWriterAgent()
        result = await agent.execute({
            "outline": request.outline,
            "character": request.character,
            "theme": request.theme
        })

        processing_time = time.time() - start_time

        return ToolResponse(
            status="completed",
            result=result,
            processing_time=processing_time
        )

    except Exception as e:
        return ToolResponse(
            status="failed",
            error=str(e)
        )


# Story Illustrator
async def run_illustrator_job(job_id: str, request: StoryIllustratorRequest):
    """Background task to run story illustrator"""
    job_manager = get_job_queue_manager()

    try:
        job_manager.start_job(job_id)
        job_manager.update_progress(job_id, 0.1, "Starting illustration generation...")

        # Execute illustrator
        agent = StoryIllustratorAgent()
        result = await agent.execute({
            "written_story": request.written_story,
            "character_appearance": request.character_appearance,
            "art_style": request.art_style,
            "max_illustrations": request.max_illustrations
        })

        job_manager.update_progress(job_id, 0.95, "Finalizing illustrations...")
        job_manager.complete_job(job_id, result)

    except Exception as e:
        job_manager.fail_job(job_id, str(e))


@router.post("/story-illustrator")
async def illustrate_story(
    request: StoryIllustratorRequest,
    background_tasks: BackgroundTasks,
    async_mode: bool = Query(False, description="Run in background and return job_id"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Generate illustrations for a story

    Takes a written story and generates illustrations for each scene using DALL-E 3.
    """

    # Async mode: Create job and return immediately
    if async_mode:
        story_title = request.written_story.get('title', 'Story')
        job_id = get_job_queue_manager().create_job(
            job_type=JobType.WORKFLOW,
            title=f"Illustrate Story: {story_title}",
            description=f"Generating {request.max_illustrations} illustrations"
        )

        background_tasks.add_task(run_illustrator_job, job_id, request)

        return ToolResponse(
            status="queued",
            job_id=job_id
        )

    # Synchronous mode: Run and return result
    import time
    start_time = time.time()

    try:
        agent = StoryIllustratorAgent()
        result = await agent.execute({
            "written_story": request.written_story,
            "character_appearance": request.character_appearance,
            "art_style": request.art_style,
            "max_illustrations": request.max_illustrations
        })

        processing_time = time.time() - start_time

        return ToolResponse(
            status="completed",
            result=result,
            processing_time=processing_time
        )

    except Exception as e:
        return ToolResponse(
            status="failed",
            error=str(e)
        )
