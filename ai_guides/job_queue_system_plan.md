# Holistic Job Queue Management System - Design Plan

## Overview
Create a centralized job queue system that tracks all long-running operations, allowing users to close modals and continue working while tasks execute in the background. A floating UI element shows all ongoing tasks and their progress.

## Current State
- All operations are blocking (user must wait for completion)
- Background tasks exist but aren't tracked or visible to users
- No way to see progress of thumbnail generation
- Can't start multiple operations simultaneously
- User gets stuck in modals until operations complete

## Goals
1. **Non-blocking operations**: Users can start tasks and immediately continue working
2. **Progress visibility**: See real-time progress of all operations
3. **Concurrent operations**: Run multiple analyses/generations simultaneously
4. **Task management**: View, cancel, or retry failed operations
5. **Better UX**: Floating task manager that doesn't interfere with workflow

---

## Architecture

### 1. Backend: Job Queue Manager

#### Job Data Model
```python
class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(str, Enum):
    ANALYZE = "analyze"
    COMPREHENSIVE_ANALYZE = "comprehensive_analyze"
    GENERATE_IMAGE = "generate_image"
    GENERATE_THUMBNAIL = "generate_thumbnail"
    BATCH_ANALYZE = "batch_analyze"
    BATCH_GENERATE = "batch_generate"

class Job(BaseModel):
    job_id: str  # UUID
    type: JobType
    status: JobStatus
    created_at: datetime
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
    cancelable: bool = True
```

#### Job Queue Manager Service
```python
class JobQueueManager:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}  # In-memory for now
        self.active_jobs: Set[str] = set()

    def create_job(self, job_type: JobType, title: str, **kwargs) -> str:
        """Create and queue a new job"""

    def start_job(self, job_id: str):
        """Mark job as started"""

    def update_progress(self, job_id: str, progress: float, message: str):
        """Update job progress"""

    def complete_job(self, job_id: str, result: Dict[str, Any]):
        """Mark job as completed with result"""

    def fail_job(self, job_id: str, error: str):
        """Mark job as failed"""

    def cancel_job(self, job_id: str):
        """Cancel a running job"""

    def get_job(self, job_id: str) -> Job:
        """Get job by ID"""

    def list_jobs(self, status: Optional[JobStatus] = None) -> List[Job]:
        """List all jobs, optionally filtered by status"""

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove old completed/failed jobs"""
```

### 2. API Layer

#### New Endpoints
```python
# /api/jobs - Job management endpoints

GET  /api/jobs
     - List all jobs
     - Query params: ?status=running&limit=50
     - Returns: List[Job]

GET  /api/jobs/{job_id}
     - Get specific job details
     - Returns: Job

POST /api/jobs/{job_id}/cancel
     - Cancel a running job
     - Returns: Job (with cancelled status)

DELETE /api/jobs/{job_id}
     - Remove a completed/failed job from history
     - Returns: 204 No Content

GET  /api/jobs/stream
     - Server-Sent Events (SSE) endpoint for real-time updates
     - Streams job status changes
```

#### Modified Endpoints
```python
POST /api/analyze/{analyzer_name}
     - Add query param: ?async=true
     - If async=true: Return job_id immediately, process in background
     - If async=false: Block and return result (current behavior)
     - Response: { "job_id": "...", "status": "queued" }

POST /api/generate
     - Add query param: ?async=true
     - Same async behavior as analyze
```

### 3. Frontend: Floating Task Manager

#### Component Structure
```
<TaskManager>
  ├── <TaskManagerButton>     // Floating button with badge count
  ├── <TaskManagerPanel>      // Expandable panel
  │   ├── <TaskList>
  │   │   ├── <TaskItem>      // Individual task
  │   │   │   ├── Progress bar
  │   │   │   ├── Status icon
  │   │   │   ├── Task title
  │   │   │   ├── Cancel button
  │   │   │   └── Expand for details
  │   │   └── ...
  │   └── <TaskFilters>       // Filter by status
```

#### Task Manager Features
1. **Floating Button** (bottom-right corner)
   - Shows count of active tasks (badge)
   - Click to expand/collapse panel
   - Pulse animation when tasks are running
   - Different colors for different states:
     - Blue: running
     - Green: completed
     - Red: failed

2. **Task Panel** (slides in from bottom-right)
   - List of all tasks
   - Grouped by status (Running → Queued → Completed → Failed)
   - Each task shows:
     - Title
     - Progress bar with percentage
     - Time elapsed
     - Cancel button (if cancelable)
     - Dismiss button (for completed/failed)
   - Auto-dismiss completed tasks after 5 seconds
   - Keep failed tasks visible until dismissed

3. **Task Details** (expandable)
   - Full error message for failed tasks
   - Sub-tasks for comprehensive analysis
   - Result preview/link

#### Real-time Updates
Two options:

**Option A: Server-Sent Events (SSE)** ✅ Recommended
```javascript
const eventSource = new EventSource('/api/jobs/stream')
eventSource.onmessage = (event) => {
  const job = JSON.parse(event.data)
  updateTaskInUI(job)
}
```

**Option B: Polling**
```javascript
setInterval(() => {
  fetch('/api/jobs?status=running,queued')
    .then(res => res.json())
    .then(jobs => updateTasksInUI(jobs))
}, 2000)
```

### 4. Integration Points

#### Comprehensive Analyzer
```python
def analyze_comprehensive(image_path, selected_analyses, background_tasks):
    # Create parent job
    parent_job_id = job_manager.create_job(
        JobType.COMPREHENSIVE_ANALYZE,
        title=f"Comprehensive analysis",
        total_steps=len(selected_analyses)
    )

    # Create child jobs for each analysis
    for i, (analysis_type, enabled) in enumerate(selected_analyses.items()):
        if enabled:
            child_job_id = job_manager.create_job(
                JobType.ANALYZE,
                title=f"Analyzing {analysis_type}",
                parent_job_id=parent_job_id
            )

            # Queue the analysis
            background_tasks.add_task(
                run_analysis_job,
                child_job_id,
                analysis_type,
                image_path
            )

    return parent_job_id
```

#### Thumbnail Generation
```python
def generate_thumbnail(preset_id, category):
    job_id = job_manager.create_job(
        JobType.GENERATE_THUMBNAIL,
        title=f"Generating preview for {preset_id[:8]}..."
    )

    try:
        job_manager.start_job(job_id)

        # Generate thumbnail
        visualizer.visualize(...)

        job_manager.complete_job(job_id, {"preview_path": "..."})
    except Exception as e:
        job_manager.fail_job(job_id, str(e))
```

#### Modified Analyzer Workflow
```python
@router.post("/{analyzer_name}")
async def analyze_image(
    analyzer_name: str,
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    async_mode: bool = Query(False, description="Run async and return job_id")
):
    if async_mode:
        # Create job and return immediately
        job_id = job_manager.create_job(
            JobType.ANALYZE,
            title=f"Analyzing {analyzer_name}"
        )

        # Queue for background processing
        background_tasks.add_task(
            run_analyzer_job,
            job_id,
            analyzer_name,
            request
        )

        return {"job_id": job_id, "status": "queued"}
    else:
        # Synchronous (current behavior)
        result = analyzer_service.analyze(...)
        return result
```

---

## Implementation Phases

### Phase 1: Backend Foundation (Priority: High)
**Goal**: Job queue infrastructure

Tasks:
1. Create Job models and JobQueueManager service
2. Add job management endpoints (list, get, cancel, delete)
3. Implement in-memory job storage
4. Add SSE endpoint for real-time updates
5. Update comprehensive analyzer to create jobs
6. Update thumbnail generation to create jobs

**Estimated time**: 4-6 hours

### Phase 2: Frontend Core (Priority: High)
**Goal**: Basic floating task manager UI

Tasks:
1. Create TaskManager component
2. Create floating button with badge
3. Create task list panel
4. Implement SSE client for real-time updates
5. Add basic task items (progress bar, cancel button)
6. Style with slide-in/out animations

**Estimated time**: 3-4 hours

### Phase 3: Integration (Priority: High)
**Goal**: Make existing operations use the job queue

Tasks:
1. Add ?async=true support to analyzer endpoints
2. Update ComprehensiveAnalyzer.jsx to use async mode
3. Update OutfitAnalyzer.jsx to use async mode
4. Update GenericAnalyzer.jsx to use async mode
5. Test concurrent operations

**Estimated time**: 2-3 hours

### Phase 4: Enhanced Features (Priority: Medium)
**Goal**: Better UX and management

Tasks:
1. Add task grouping (by type, by status)
2. Add task filtering and search
3. Add "clear all completed" button
4. Add task history view
5. Add retry button for failed tasks
6. Add notifications for completed tasks
7. Persist jobs to disk (optional)

**Estimated time**: 3-4 hours

### Phase 5: Advanced Features (Priority: Low)
**Goal**: Polish and optimization

Tasks:
1. Add job priority system
2. Add job dependencies
3. Add rate limiting
4. Add estimated completion time
5. Add job statistics/analytics
6. Add export job results

**Estimated time**: 4-5 hours

---

## Technical Decisions

### Storage
**Phase 1**: In-memory (simple, fast)
- Pros: Easy to implement, no dependencies
- Cons: Lost on restart
- Good for: MVP, development

**Phase 2**: File-based (sqlite or JSON)
- Pros: Persistent, no external dependencies
- Cons: Single-server only
- Good for: Single-user deployments

**Phase 3**: Redis/Database
- Pros: Persistent, multi-server, scalable
- Cons: Additional infrastructure
- Good for: Production, multi-user

### Real-time Updates
**Recommended**: Server-Sent Events (SSE)
- Simpler than WebSockets
- Built-in reconnection
- One-way is sufficient (server → client)
- Better browser support

Alternative: WebSockets
- Use if we need bidirectional communication later
- More complex setup

### Concurrency
**Phase 1**: FastAPI BackgroundTasks
- Simple, built-in
- Limited to request lifecycle
- Good for: Short-lived tasks

**Phase 2**: Celery or similar
- Distributed task queue
- More robust
- Good for: Production, heavy workloads

---

## User Flows

### Flow 1: Single Analysis
1. User uploads image and selects analyzer
2. User clicks "Analyze"
3. Modal closes immediately
4. Task appears in floating task manager (bottom-right)
5. User continues working (can start other tasks)
6. Progress bar updates in real-time
7. When complete, notification shows "Analysis complete"
8. User can click to view results
9. Task auto-dismisses after 5 seconds

### Flow 2: Comprehensive Analysis
1. User uploads image and selects 6 analyses
2. User clicks "Run Selected Analyses"
3. Modal closes immediately
4. Parent task appears: "Comprehensive Analysis (0/6)"
5. 6 child tasks appear below it, each with own progress
6. As each completes, parent progress updates: "Comprehensive Analysis (3/6)"
7. Thumbnail generation tasks queue automatically
8. When all complete, notification shows "6 presets created"
9. Tasks auto-dismiss after 5 seconds

### Flow 3: Failed Task
1. Task fails (e.g., network error, invalid input)
2. Task turns red with error icon
3. Notification shows "Analysis failed"
4. User clicks to expand task
5. Sees full error message
6. Can retry or dismiss

### Flow 4: Concurrent Operations
1. User starts comprehensive analysis
2. Immediately starts another outfit analysis
3. Starts an image generation
4. All 3 show in task manager
5. All process concurrently
6. Each updates independently

---

## UI Mockup (Text)

```
┌─────────────────────────────────────────┐
│                                         │
│        Main Application Content         │
│                                         │
│                                    ┌────┤
│                                    │ ⚡ 3│  ← Floating button
│                                    └────┤
│                                         │
└─────────────────────────────────────────┘

When expanded:

┌─────────────────────────────────────────┐
│                                         │
│        Main Application Content         │
│                                         │
│                             ┌───────────┤
│                             │ Tasks (3) │
│                             ├───────────┤
│                             │ ⟳ Running │
│                             │           │
│                             │ • Compre..│
│                             │   [====  ]│
│                             │   4/7 ana.│
│                             │   [Cancel]│
│                             │           │
│                             │ • Generat.│
│                             │   [======]│
│                             │   80%     │
│                             │           │
│                             │ ✓ Complete│
│                             │           │
│                             │ • Outfit  │
│                             │   Done    │
│                             │   [Dismiss│
└─────────────────────────────┴───────────┘
```

---

## Benefits

1. **Better UX**
   - Non-blocking operations
   - Can work on other things while tasks run
   - Clear visibility into what's happening

2. **Concurrent Operations**
   - Analyze multiple images simultaneously
   - Generate while analyzing
   - Better resource utilization

3. **Error Handling**
   - Failed tasks don't block UI
   - Can retry failed operations
   - Clear error messages

4. **Scalability**
   - Foundation for batch operations
   - Can add job priorities later
   - Can distribute across workers

5. **User Confidence**
   - Always know what's happening
   - Progress feedback
   - Task history

---

## Next Steps

1. **Review this plan** - Confirm approach and priorities
2. **Start Phase 1** - Build backend job queue infrastructure
3. **Create prototype** - Simple floating task manager
4. **Test with comprehensive analyzer** - Validate the approach
5. **Iterate** - Add features based on usage

## Questions to Resolve

1. Should jobs persist across server restarts?
   - Phase 1: No (in-memory)
   - Later: Yes (file or DB)

2. What's the cleanup policy for old jobs?
   - Auto-delete after 24 hours?
   - Keep last 100 jobs?
   - Manual cleanup only?

3. Should we support job priorities?
   - Phase 1: No (FIFO)
   - Later: Yes (priority queue)

4. How to handle server restart with running jobs?
   - Mark all as failed?
   - Restart them?
   - Phase 1: Mark as failed

5. Should failed thumbnail generation fail the parent job?
   - No, thumbnail is optional
   - Show warning but mark parent as success
