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
    AWAITING_INPUT = "awaiting_input"  # Paused, waiting for user decision
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

    # Awaiting input state (for human-in-the-loop workflows)
    awaiting_data: Optional[Dict[str, Any]] = None  # Data for user to review
    user_input: Optional[Dict[str, Any]] = None  # User's response when resuming

    # Metadata
    user_id: Optional[str] = None  # For future multi-user support
    metadata: Optional[Dict[str, Any]] = None  # Generic metadata (entity_type, entity_id, etc.)
    cancelable: bool = True

    class Config:
        use_enum_values = True


class BriefCardAction(BaseModel):
    """Action button for Brief card"""
    action_id: str  # e.g., "approve", "edit", "cancel"
    label: str  # e.g., "Approve", "Edit Changes", "Cancel"
    style: Optional[str] = "primary"  # "primary", "secondary", "danger"
    endpoint: Optional[str] = None  # API endpoint to call when clicked


class BriefCard(BaseModel):
    """
    Brief Card - Surface job results/decisions to user

    Foundation for Phase 8 Daily Brief. Cards appear when:
    - Jobs pause in AWAITING_INPUT state
    - Background tasks complete and need review
    - Agents propose actions (Phase 9)
    """
    card_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str  # Associated job

    # Card content
    title: str  # e.g., "Merge Preview Ready"
    description: str  # e.g., "Review and approve merged clothing item"
    category: str = "work"  # "work", "creative", "life", "maintenance"

    # Actions (buttons user can click)
    actions: List[BriefCardAction] = []

    # Data payload (for UI to display details)
    data: Optional[Dict[str, Any]] = None

    # Provenance (why this surfaced)
    provenance: Optional[str] = None  # Full reasoning for surfacing this card

    # Lifecycle
    created_at: datetime = Field(default_factory=datetime.now)
    responded_at: Optional[datetime] = None
    dismissed: bool = False
    snoozed_until: Optional[datetime] = None

    # Response
    response: Optional[Dict[str, Any]] = None  # User's response when acted upon

    class Config:
        use_enum_values = True
