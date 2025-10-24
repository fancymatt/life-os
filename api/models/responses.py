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


class TagInfo(BaseModel):
    """Tag information"""
    tag_id: str
    name: str
    category: Optional[str] = None
    color: Optional[str] = None
    usage_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CharacterInfo(BaseModel):
    """Character information"""
    character_id: str
    name: str
    visual_description: Optional[str] = None
    physical_description: Optional[str] = None
    personality: Optional[str] = None
    reference_image_url: Optional[str] = None
    tags: List["TagInfo"] = []  # Now returns full tag objects instead of strings
    created_at: Optional[str] = None
    archived: bool = False
    archived_at: Optional[str] = None
    metadata: Dict[str, Any] = {}

    # Detailed appearance fields (from character_appearance_analyzer)
    age: Optional[str] = None
    skin_tone: Optional[str] = None
    face_description: Optional[str] = None
    hair_description: Optional[str] = None
    body_description: Optional[str] = None


class CharacterListResponse(BaseModel):
    """List of characters"""
    count: int
    characters: List[CharacterInfo]


class CharacterFromSubjectResponse(BaseModel):
    """Response from creating character from subject"""
    character: CharacterInfo
    analysis: Optional[Dict[str, Any]] = None
    created_presets: List[Dict[str, str]] = []  # [{"type": "outfit", "preset_id": "...", "name": "..."}]


# ============================================================================
# Board Game Models
# ============================================================================

class BoardGameInfo(BaseModel):
    """Board game information"""
    game_id: str
    name: str
    bgg_id: Optional[int] = None
    designer: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    player_count_min: Optional[int] = None
    player_count_max: Optional[int] = None
    playtime_min: Optional[int] = None
    playtime_max: Optional[int] = None
    complexity: Optional[float] = None
    tags: List["TagInfo"] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BoardGameListResponse(BaseModel):
    """List of board games"""
    count: int
    games: List[BoardGameInfo]


class DocumentInfo(BaseModel):
    """Document information"""
    document_id: str
    game_id: Optional[str] = None
    title: str
    source_type: Literal["pdf", "url", "text"]
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    page_count: Optional[int] = None
    file_size_bytes: Optional[int] = None
    processed: bool = False
    processed_at: Optional[str] = None
    markdown_path: Optional[str] = None
    vector_ids: List[str] = []
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = {}


class DocumentListResponse(BaseModel):
    """List of documents"""
    count: int
    documents: List[DocumentInfo]


class QAInfo(BaseModel):
    """Q&A information"""
    qa_id: str
    question: str
    answer: str
    context_type: Literal["document", "general", "image", "comparison"]
    game_id: Optional[str] = None
    document_ids: List[str] = []
    image_url: Optional[str] = None
    citations: List[Dict[str, Any]] = []  # [{"document_id": "...", "page": 5, "excerpt": "..."}]
    is_favorite: bool = False
    was_helpful: Optional[bool] = None
    user_notes: Optional[str] = None
    custom_tags: List[str] = []
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = {}


class QAListResponse(BaseModel):
    """List of Q&As"""
    count: int
    qas: List[QAInfo]


class BGGSearchResult(BaseModel):
    """BoardGameGeek search result"""
    bgg_id: int
    name: str
    year: Optional[int] = None
    type: str


class BGGSearchResponse(BaseModel):
    """Response from BGG search"""
    query: str
    count: int
    results: List[BGGSearchResult]


class DocumentProcessResponse(BaseModel):
    """Response from document processing"""
    status: Literal["completed", "failed"]
    document: Optional[DocumentInfo] = None
    markdown_path: Optional[str] = None
    chunk_count: Optional[int] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None


# ============================================================================
# Tag Models
# ============================================================================
# Note: TagInfo is defined earlier (line 112) before CharacterInfo to support forward reference


class TagListResponse(BaseModel):
    """List of tags"""
    count: int
    tags: List[TagInfo]


class EntityTagsResponse(BaseModel):
    """Tags for an entity"""
    entity_type: str
    entity_id: str
    tags: List[TagInfo]


class TagStatisticsResponse(BaseModel):
    """Tag usage statistics"""
    total_tags: int
    total_relationships: int
    top_tags: List[Dict[str, Any]]  # [{"tag_id": "...", "name": "...", "usage_count": 5}]
    tags_by_category: Dict[str, int]  # {"style": 10, "material": 5, ...}


class TagAutocompleteResponse(BaseModel):
    """Autocomplete suggestions for tags"""
    query: str
    suggestions: List[TagInfo]
