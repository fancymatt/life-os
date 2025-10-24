"""Job Queue Models"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class JobStatus(str, Enum):
    """Job execution status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    """Type of job"""
    ANALYZE = "analyze"
    COMPREHENSIVE_ANALYZE = "comprehensive_analyze"
    GENERATE_IMAGE = "generate_image"
    GENERATE_THUMBNAIL = "generate_thumbnail"
    BATCH_ANALYZE = "batch_analyze"
    BATCH_GENERATE = "batch_generate"
    WORKFLOW = "workflow"


class Job(BaseModel):
    """Job representation"""
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: JobType
    status: JobStatus = JobStatus.QUEUED
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Progress tracking
    progress: float = 0.0  # 0.0 to 1.0
    progress_message: Optional[str] = None
    current_step: Optional[int] = None
    total_steps: Optional[int] = None

    # Task details
    title: str  # e.g., "Analyzing outfit in photo.jpg"
    description: Optional[str] = None

    # Parent/child relationships (for comprehensive analysis)
    parent_job_id: Optional[str] = None
    child_job_ids: List[str] = []

    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # Metadata
    user_id: Optional[str] = None  # For future multi-user support
    metadata: Optional[Dict[str, Any]] = None  # Generic metadata (entity_type, entity_id, etc.)
    cancelable: bool = True

    class Config:
        use_enum_values = True
