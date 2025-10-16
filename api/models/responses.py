"""API Response Models"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Literal, List, Dict
from datetime import datetime


class APIInfo(BaseModel):
    """API information"""
    name: str = "AI-Studio API"
    version: str = "1.0.0"
    description: str = "API for AI-powered image analysis and generation"
    tools_count: int
    presets_count: int
    docs_url: str = "/docs"
    categories: List[str]


class ToolInfo(BaseModel):
    """Information about a tool"""
    name: str
    category: Literal["analyzer", "generator"]
    description: str
    estimated_cost: float
    avg_time_seconds: Optional[float] = None


class PresetInfo(BaseModel):
    """Preset information"""
    preset_id: str
    display_name: Optional[str] = None
    category: str
    created_at: Optional[str] = None
    tool: Optional[str] = None
    notes: Optional[str] = None


class PresetListResponse(BaseModel):
    """List of presets in a category"""
    category: str
    count: int
    presets: List[PresetInfo]


class AnalyzeResponse(BaseModel):
    """Response from analysis"""
    status: Literal["completed", "failed"]
    result: Optional[Dict[str, Any]] = None
    preset_id: Optional[str] = None
    preset_display_name: Optional[str] = None
    cost: float
    cache_hit: bool
    processing_time: Optional[float] = None
    error: Optional[str] = None


class GenerateResponse(BaseModel):
    """Response from generation"""
    status: Literal["completed", "failed"]
    result: Optional[Dict[str, Any]] = None  # {image_url, generation_time, cost}
    error: Optional[str] = None


class JobResponse(BaseModel):
    """Response for async jobs"""
    job_id: str
    type: Literal["analyze", "generate", "batch"]
    status: Literal["queued", "processing", "completed", "failed"]
    progress: Optional[Dict[str, Any]] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    cost: Optional[float] = None


class BatchResponse(BaseModel):
    """Response from batch operation"""
    batch_id: str
    total: int
    completed: int
    failed: int
    skipped: int
    status: Literal["queued", "processing", "completed", "failed"]
    results: List[Dict[str, Any]]
    total_cost: float
    total_time: Optional[float] = None


class UploadResponse(BaseModel):
    """Response from file upload"""
    filename: str
    url: str
    size_bytes: int
    mime_type: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    uptime_seconds: float
    checks: Dict[str, bool] = {
        "api_keys": False,
        "presets_dir": False,
        "cache_dir": False,
        "output_dir": False
    }


class CharacterInfo(BaseModel):
    """Character information"""
    character_id: str
    name: str
    visual_description: Optional[str] = None
    personality: Optional[str] = None
    reference_image_url: Optional[str] = None
    tags: List[str] = []
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = {}


class CharacterListResponse(BaseModel):
    """List of characters"""
    count: int
    characters: List[CharacterInfo]


class CharacterFromSubjectResponse(BaseModel):
    """Response from creating character from subject"""
    character: CharacterInfo
    analysis: Optional[Dict[str, Any]] = None
    created_presets: List[Dict[str, str]] = []  # [{"type": "outfit", "preset_id": "...", "name": "..."}]
