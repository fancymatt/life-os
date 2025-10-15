"""Job Queue Manager Service"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from api.models.jobs import Job, JobStatus, JobType


class JobQueueManager:
    """
    Manages background jobs with progress tracking and real-time updates

    Features:
    - In-memory job storage
    - Progress tracking
    - Parent/child job relationships
    - Real-time updates via SSE
    - Automatic cleanup of old jobs
    """

    def __init__(self):
        self.jobs: Dict[str, Job] = {}  # job_id -> Job
        self.active_jobs: Set[str] = set()
        self._subscribers: List[asyncio.Queue] = []  # SSE subscribers

    def create_job(
        self,
        job_type: JobType,
        title: str,
        description: Optional[str] = None,
        parent_job_id: Optional[str] = None,
        total_steps: Optional[int] = None,
        cancelable: bool = True
    ) -> str:
        """
        Create and queue a new job

        Args:
            job_type: Type of job
            title: Job title/description
            description: Optional detailed description
            parent_job_id: Optional parent job ID for hierarchical jobs
            total_steps: Total number of steps (for progress tracking)
            cancelable: Whether job can be cancelled

        Returns:
            job_id: Unique job identifier
        """
        job = Job(
            type=job_type,
            title=title,
            description=description,
            parent_job_id=parent_job_id,
            total_steps=total_steps,
            cancelable=cancelable
        )

        self.jobs[job.job_id] = job

        # Add to parent's child list if applicable
        if parent_job_id and parent_job_id in self.jobs:
            self.jobs[parent_job_id].child_job_ids.append(job.job_id)

        # Notify subscribers (safe for sync/async contexts)
        self._schedule_notification(job)

        return job.job_id

    def start_job(self, job_id: str):
        """Mark job as started"""
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")

        job = self.jobs[job_id]
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        self.active_jobs.add(job_id)

        # Notify subscribers (safe for sync/async contexts)
        self._schedule_notification(job)

    def update_progress(
        self,
        job_id: str,
        progress: float,
        message: Optional[str] = None,
        current_step: Optional[int] = None
    ):
        """
        Update job progress

        Args:
            job_id: Job identifier
            progress: Progress value (0.0 to 1.0)
            message: Optional progress message
            current_step: Current step number
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")

        job = self.jobs[job_id]
        job.progress = max(0.0, min(1.0, progress))  # Clamp to [0, 1]
        if message:
            job.progress_message = message
        if current_step is not None:
            job.current_step = current_step

        # Update parent job progress if applicable
        if job.parent_job_id:
            self._update_parent_progress(job.parent_job_id)

        # Notify subscribers (safe for sync/async contexts)
        self._schedule_notification(job)

    def complete_job(self, job_id: str, result: Optional[Dict] = None):
        """Mark job as completed with result"""
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")

        job = self.jobs[job_id]
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now()
        job.progress = 1.0
        job.result = result
        self.active_jobs.discard(job_id)

        # Update parent job progress
        if job.parent_job_id:
            self._update_parent_progress(job.parent_job_id)

        # Notify subscribers (safe for sync/async contexts)
        self._schedule_notification(job)

    def fail_job(self, job_id: str, error: str):
        """Mark job as failed"""
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")

        job = self.jobs[job_id]
        job.status = JobStatus.FAILED
        job.completed_at = datetime.now()
        job.error = error
        self.active_jobs.discard(job_id)

        # Update parent job if applicable
        if job.parent_job_id:
            self._update_parent_progress(job.parent_job_id)

        # Notify subscribers (safe for sync/async contexts)
        self._schedule_notification(job)

    def cancel_job(self, job_id: str):
        """Cancel a running job"""
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")

        job = self.jobs[job_id]

        if not job.cancelable:
            raise ValueError(f"Job cannot be cancelled: {job_id}")

        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now()
        self.active_jobs.discard(job_id)

        # Cancel child jobs
        for child_id in job.child_job_ids:
            if child_id in self.jobs and self.jobs[child_id].status in [JobStatus.QUEUED, JobStatus.RUNNING]:
                self.cancel_job(child_id)

        # Notify subscribers (safe for sync/async contexts)
        self._schedule_notification(job)

    def get_job(self, job_id: str) -> Job:
        """Get job by ID"""
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")
        return self.jobs[job_id]

    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        limit: Optional[int] = None
    ) -> List[Job]:
        """
        List all jobs, optionally filtered by status

        Args:
            status: Optional status filter
            limit: Maximum number of jobs to return

        Returns:
            List of jobs, sorted by created_at (newest first)
        """
        jobs = list(self.jobs.values())

        # Filter by status
        if status:
            jobs = [j for j in jobs if j.status == status]

        # Sort by created_at (newest first)
        jobs.sort(key=lambda j: j.created_at, reverse=True)

        # Apply limit
        if limit:
            jobs = jobs[:limit]

        return jobs

    def delete_job(self, job_id: str):
        """Remove a job from the queue"""
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")

        job = self.jobs[job_id]

        # Only allow deletion of completed/failed/cancelled jobs
        if job.status in [JobStatus.QUEUED, JobStatus.RUNNING]:
            raise ValueError(f"Cannot delete active job: {job_id}")

        # Remove from parent's child list
        if job.parent_job_id and job.parent_job_id in self.jobs:
            parent = self.jobs[job.parent_job_id]
            if job_id in parent.child_job_ids:
                parent.child_job_ids.remove(job_id)

        del self.jobs[job_id]

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """
        Remove old completed/failed jobs

        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        jobs_to_delete = []

        for job_id, job in self.jobs.items():
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                if job.completed_at and job.completed_at < cutoff:
                    jobs_to_delete.append(job_id)

        for job_id in jobs_to_delete:
            try:
                self.delete_job(job_id)
            except ValueError:
                pass  # Job may have been deleted already

    # SSE support

    async def subscribe(self) -> asyncio.Queue:
        """Subscribe to job updates (SSE)"""
        queue = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from job updates"""
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    def _schedule_notification(self, job: Job):
        """Schedule notification to subscribers (safe from sync/async contexts)"""
        try:
            # Try to get the running event loop
            loop = asyncio.get_running_loop()
            # We're in an async context, create task
            loop.create_task(self._notify_subscribers(job))
        except RuntimeError:
            # No running loop - we're in sync context
            # Subscribers will get updates when they poll or via next async operation
            pass

    async def _notify_subscribers(self, job: Job):
        """Notify all SSE subscribers of job update"""
        # Remove dead queues
        self._subscribers = [
            q for q in self._subscribers
            if not (hasattr(q, '_closed') and q._closed)
        ]

        # Notify all subscribers
        for queue in self._subscribers:
            try:
                await queue.put(job)
            except:
                pass  # Ignore errors for dead subscribers

    # Private helpers

    def _update_parent_progress(self, parent_job_id: str):
        """Update parent job progress based on child jobs"""
        if parent_job_id not in self.jobs:
            return

        parent = self.jobs[parent_job_id]
        if not parent.child_job_ids:
            return

        # Calculate overall progress from children
        total_progress = 0.0
        completed_count = 0
        failed_count = 0

        for child_id in parent.child_job_ids:
            if child_id in self.jobs:
                child = self.jobs[child_id]
                total_progress += child.progress

                if child.status == JobStatus.COMPLETED:
                    completed_count += 1
                elif child.status == JobStatus.FAILED:
                    failed_count += 1

        # Update parent progress
        parent.progress = total_progress / len(parent.child_job_ids)
        parent.current_step = completed_count + failed_count
        parent.total_steps = len(parent.child_job_ids)
        parent.progress_message = f"{completed_count}/{len(parent.child_job_ids)} analyses complete"

        # Mark parent as completed if all children are done
        all_done = all(
            self.jobs[cid].status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
            for cid in parent.child_job_ids
            if cid in self.jobs
        )

        if all_done and parent.status == JobStatus.RUNNING:
            if failed_count > 0 and completed_count == 0:
                # All failed
                parent.status = JobStatus.FAILED
                parent.error = f"{failed_count} analyses failed"
            else:
                # At least some succeeded
                parent.status = JobStatus.COMPLETED

            parent.completed_at = datetime.now()
            self.active_jobs.discard(parent_job_id)


# Global singleton instance
job_queue_manager = JobQueueManager()
