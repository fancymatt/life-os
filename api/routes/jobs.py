"""Job Management Routes"""

import asyncio
import json
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional, List

from api.models.jobs import Job, JobStatus
from api.services.job_queue import get_job_queue_manager

router = APIRouter()


@router.get("", response_model=List[Job])
async def list_jobs(
    status: Optional[JobStatus] = Query(None, description="Filter by status"),
    limit: Optional[int] = Query(50, description="Maximum number of jobs to return")
):
    """
    List all jobs

    Query params:
    - status: Filter by job status (queued, running, completed, failed, cancelled)
    - limit: Maximum number of jobs to return (default: 50)
    """
    jobs = get_job_queue_manager().list_jobs(status=status, limit=limit)
    return jobs


@router.get("/stream", include_in_schema=False)
async def stream_jobs():
    """
    Server-Sent Events endpoint for real-time job updates

    Streams job status changes to connected clients.
    """
    async def event_generator():
        # Subscribe to job updates
        queue = await get_job_queue_manager().subscribe()

        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected'})}\n\n".encode('utf-8')

            # Stream job updates
            while True:
                try:
                    # Wait for job update with timeout
                    job = await asyncio.wait_for(queue.get(), timeout=30.0)

                    # Send job update (mode='json' handles datetime serialization)
                    job_data = job.model_dump(mode='json')
                    yield f"data: {json.dumps(job_data)}\n\n".encode('utf-8')

                except asyncio.TimeoutError:
                    # Send keepalive ping every 30 seconds
                    yield f": keepalive\n\n".encode('utf-8')

        except asyncio.CancelledError:
            # Client disconnected
            pass
        finally:
            # Unsubscribe
            get_job_queue_manager().unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get specific job details"""
    try:
        job = get_job_queue_manager().get_job(job_id)
        return job
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{job_id}/cancel", response_model=Job)
async def cancel_job(job_id: str):
    """Cancel a running job"""
    try:
        get_job_queue_manager().cancel_job(job_id)
        job = get_job_queue_manager().get_job(job_id)
        return job
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Remove a completed/failed job from history"""
    try:
        get_job_queue_manager().delete_job(job_id)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
