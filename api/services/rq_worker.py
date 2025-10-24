"""
Redis Queue (RQ) Worker Service

Provides distributed job queue for long-running background tasks.
Jobs are executed by separate worker processes for true parallelism.
"""

import os
from typing import Optional, Any, Callable
from redis import Redis
from rq import Queue
from rq.job import Job

from api.logging_config import get_logger

logger = get_logger(__name__)


class RQService:
    """
    Redis Queue service for distributed job execution

    Features:
    - Distributed workers (run multiple worker processes)
    - True parallelism (no GIL blocking)
    - Automatic retry on failure
    - Job result storage
    - Integrates with existing JobQueueManager for tracking
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize RQ service

        Args:
            redis_url: Redis connection URL (defaults to env var or localhost)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_conn = Redis.from_url(self.redis_url)

        # Normal queue for general jobs (matches docker-compose worker config)
        self.queue = Queue('normal', connection=self.redis_conn, default_timeout=600)  # 10 min timeout

        # High priority queue for user-initiated actions
        self.high_priority_queue = Queue('high', connection=self.redis_conn, default_timeout=300)

        # Low priority queue for batch operations
        self.low_priority_queue = Queue('low', connection=self.redis_conn, default_timeout=1800)

        logger.info(f"RQ service initialized with Redis: {self.redis_url}")

    def enqueue(
        self,
        func: Callable,
        *args,
        priority: str = 'normal',
        job_id: Optional[str] = None,
        **kwargs
    ) -> Job:
        """
        Enqueue a job for execution by RQ workers

        Args:
            func: Function to execute (must be importable by workers)
            *args: Positional arguments to pass to func
            priority: 'high', 'normal', or 'low' (determines which queue)
            job_id: Optional job ID (useful for tracking with JobQueueManager)
            **kwargs: Keyword arguments to pass to func

        Returns:
            RQ Job object
        """
        # Select queue based on priority
        if priority == 'high':
            queue = self.high_priority_queue
        elif priority == 'low':
            queue = self.low_priority_queue
        else:
            queue = self.queue

        # Enqueue job
        rq_job = queue.enqueue(
            func,
            *args,
            job_id=job_id,
            **kwargs
        )

        logger.info(
            f"Enqueued job {rq_job.id} in {priority} priority queue",
            extra={'extra_fields': {
                'rq_job_id': rq_job.id,
                'function': func.__name__,
                'priority': priority
            }}
        )

        return rq_job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get RQ job by ID"""
        return Job.fetch(job_id, connection=self.redis_conn)

    def get_queue_stats(self) -> dict:
        """Get statistics about queue sizes"""
        return {
            'normal': {
                'queued': len(self.queue),
                'started': self.queue.started_job_registry.count,
                'finished': self.queue.finished_job_registry.count,
                'failed': self.queue.failed_job_registry.count
            },
            'high': {
                'queued': len(self.high_priority_queue),
                'started': self.high_priority_queue.started_job_registry.count,
                'finished': self.high_priority_queue.finished_job_registry.count,
                'failed': self.high_priority_queue.failed_job_registry.count
            },
            'low': {
                'queued': len(self.low_priority_queue),
                'started': self.low_priority_queue.started_job_registry.count,
                'finished': self.low_priority_queue.finished_job_registry.count,
                'failed': self.low_priority_queue.failed_job_registry.count
            }
        }


# Global singleton instance
_rq_service: Optional[RQService] = None


def get_rq_service() -> RQService:
    """Get or initialize the global RQ service"""
    global _rq_service

    if _rq_service is None:
        _rq_service = RQService()

    return _rq_service
