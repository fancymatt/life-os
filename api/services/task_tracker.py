"""
Task Tracker Service

Tracks background task progress for long-running operations
"""

from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class TaskStatus(str, Enum):
    """Task status values"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskInfo:
    """Information about a background task"""

    def __init__(self, task_id: str, task_type: str, total: int = 1):
        self.task_id = task_id
        self.task_type = task_type
        self.status = TaskStatus.PENDING
        self.current = 0
        self.total = total
        self.message = ""
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status.value,
            "current": self.current,
            "total": self.total,
            "progress": (self.current / self.total * 100) if self.total > 0 else 0,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    def update(self, current: Optional[int] = None, message: Optional[str] = None):
        """Update task progress"""
        if current is not None:
            self.current = current
        if message is not None:
            self.message = message
        self.updated_at = datetime.now()

    def set_in_progress(self, message: str = ""):
        """Mark task as in progress"""
        self.status = TaskStatus.IN_PROGRESS
        self.message = message
        self.updated_at = datetime.now()

    def set_completed(self, result: Any = None, message: str = "Completed"):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.current = self.total
        self.result = result
        self.message = message
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def set_failed(self, error: str):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.error = error
        self.message = f"Failed: {error}"
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()


class TaskTracker:
    """
    Simple in-memory task tracker

    For production, this should be replaced with Redis or a database
    """

    def __init__(self):
        self._tasks: Dict[str, TaskInfo] = {}

    def create_task(self, task_type: str, total: int = 1) -> TaskInfo:
        """Create a new task and return its info"""
        task_id = str(uuid.uuid4())
        task = TaskInfo(task_id, task_type, total)
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Get task info by ID"""
        return self._tasks.get(task_id)

    def update_task(self, task_id: str, current: Optional[int] = None, message: Optional[str] = None):
        """Update task progress"""
        task = self.get_task(task_id)
        if task:
            task.update(current, message)

    def complete_task(self, task_id: str, result: Any = None, message: str = "Completed"):
        """Mark task as completed"""
        task = self.get_task(task_id)
        if task:
            task.set_completed(result, message)

    def fail_task(self, task_id: str, error: str):
        """Mark task as failed"""
        task = self.get_task(task_id)
        if task:
            task.set_failed(error)

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove tasks older than max_age_hours"""
        now = datetime.now()
        to_remove = []

        for task_id, task in self._tasks.items():
            age = (now - task.created_at).total_seconds() / 3600
            if age > max_age_hours and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                to_remove.append(task_id)

        for task_id in to_remove:
            del self._tasks[task_id]

        return len(to_remove)


# Global instance
_tracker: Optional[TaskTracker] = None


def get_task_tracker() -> TaskTracker:
    """Get the global task tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = TaskTracker()
    return _tracker
