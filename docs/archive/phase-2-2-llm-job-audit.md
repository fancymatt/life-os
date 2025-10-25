# Phase 2.2: LLM Job Audit Report

**Date**: 2025-10-24
**Status**: IN PROGRESS
**Goal**: Ensure all LLM-calling endpoints spawn background jobs (never block UI)

---

## Core Principle

> **Every LLM call must spawn an RQ job. Nothing should block the UI.**

**Why This Matters**:
- LLM calls take 30+ seconds
- Blocking freezes UI and causes timeouts
- No progress tracking for users
- Poor scalability under load

**Success Criteria**:
- ✅ 100% of LLM endpoints spawn jobs
- ✅ All endpoints return job_id in <1 second
- ✅ Zero blocking LLM calls in production
- ✅ Automated test prevents regressions

---

## Audit Results

### ✅ COMPLIANT ENDPOINTS (2/5)

#### 1. Story Generation Workflow
**File**: `api/routes/workflows.py:56-222`
**Endpoint**: `POST /api/workflows/story-generation/execute`
**Status**: ✅ FULLY COMPLIANT

**Evidence**:
```python
# Creates job immediately (line 71-77)
job_id = job_manager.create_job(
    job_type=JobType.WORKFLOW,
    title=f"Generate Story: {character_name}",
    description=f"{request.theme_id.capitalize()} story with {request.max_illustrations} illustrations",
    total_steps=3,
    cancelable=False
)

# Returns job_id immediately (line 216-222)
background_tasks.add_task(execute_workflow)
return {
    "message": "Story generation started",
    "status": "queued",
    "job_id": job_id
}
```

**Response Time**: ~50ms (job creation only)
**LLM Execution**: Fully async in background
**No Changes Needed**: ✅

---

#### 2. Modular Image Generator
**File**: `api/routes/generators.py:36-303`
**Endpoint**: `POST /api/generate/modular`
**Status**: ✅ FULLY COMPLIANT

**Evidence**:
```python
# Creates job immediately (line 91-97)
job_id = job_manager.create_job(
    job_type=JobType.BATCH_GENERATE,
    title=f"Generate {request.variations} variation(s)",
    description=f"Modular generation from {request.subject_image}",
    total_steps=request.variations,
    cancelable=True
)

# Returns job_id immediately (line 297-303)
background_tasks.add_task(generate_variations)
return {
    "message": "Modular generation started",
    "status": "queued",
    "job_id": job_id,
    "variations": request.variations
}
```

**Response Time**: ~50ms (job creation only)
**LLM Execution**: Fully async in background
**No Changes Needed**: ✅

---

### ⚠️ PARTIAL COMPLIANCE (1/5)

#### 3. Analyzer Tools (with Sync Fallback)
**File**: `api/routes/tools.py:283-437`
**Endpoint**: `POST /api/tools/analyzers/{analyzer_name}`
**Status**: ⚠️ PARTIAL COMPLIANCE

**Evidence**:
```python
# HAS async_mode parameter (default True)
async def run_analyzer(
    analyzer_name: str,
    image: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    async_mode: bool = Query(True, description="Run analysis in background and return job_id"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
```

**✅ Async Mode (Default)**: Lines 324-346
- Creates job
- Returns job_id immediately
- Fully compliant

**❌ Synchronous Mode (Optional)**: Lines 348-437
- Runs LLM synchronously
- Blocks for 30+ seconds
- Returns result immediately
- **VIOLATION**: When `async_mode=False`

**Decision Needed**:
1. **Option A (Recommended)**: Remove synchronous mode entirely
   - Enforces job spawning 100% of the time
   - Simpler codebase (delete 90 lines of duplicate logic)
   - No risk of timeouts
2. **Option B (Keep)**: Keep sync mode for testing/debugging
   - Add warning in docs about timeouts
   - Add timeout limit (max 60s)
   - Not recommended for production use

**Recommendation**: **Remove synchronous mode** (Option A)

---

### ❌ VIOLATIONS (2/5)

#### 4. Legacy Generator Endpoint
**File**: `api/routes/generators.py:329-406`
**Endpoint**: `POST /api/generate/{generator_name}`
**Status**: ❌ VIOLATION

**Evidence**:
```python
@router.post("/{generator_name}", response_model=GenerateResponse)
async def generate_image(generator_name: str, request: GenerateRequest):
    """Generate an image with a specific generator"""

    # NO async_mode parameter
    # NO job creation
    # BLOCKS on LLM call (line 369)
    result = generator_service.generate(
        generator_name,
        subject_path,
        settings.output_dir,
        **specs
    )

    # Returns result immediately (line 387-395)
    return GenerateResponse(
        status="completed",
        result={"image_url": result.get('image_url')}
    )
```

**Problems**:
- ❌ No `async_mode` parameter
- ❌ No job creation
- ❌ Blocks for 30+ seconds on LLM call
- ❌ No progress tracking
- ❌ Will timeout on slow connections

**Impact**: HIGH - This endpoint is likely used by frontend

**Fix Required**:
1. Add `async_mode` parameter (default True)
2. Create job when `async_mode=True`
3. Use BackgroundTasks
4. Return job_id immediately
5. Remove synchronous mode or deprecate with warning

**Estimated Fix Time**: 30 minutes

---

#### 5. Merge Analysis Endpoint (Human-in-the-Loop Case)
**File**: `api/routes/merge.py:102-147`
**Endpoint**: `POST /api/merge/analyze`
**Status**: ❌ VIOLATION (Special Case)

**Evidence**:
```python
@router.post("/analyze", response_model=MergeAnalysisResponse)
async def analyze_merge(
    request: AnalyzeMergeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Use AI to analyze two entities and generate merged version.

    The merged data can be edited by user before executing the merge.
    """
    # NO async_mode parameter
    # NO job creation
    # BLOCKS on LLM call (line 116-120)
    merged_data = await service.analyze_merge(
        request.entity_type,
        request.source_entity,
        request.target_entity
    )

    # Returns merged_data immediately (line 138-142)
    return MergeAnalysisResponse(
        merged_data=merged_data,
        changes_summary=changes_summary
    )
```

**Problems**:
- ❌ No job creation
- ❌ Blocks for 30+ seconds on LLM analysis
- ❌ No progress tracking
- ❌ Cannot cancel mid-analysis
- ⚠️ **BUT**: Legitimately needs user review before proceeding

**Special Consideration**:
This is the **exact example** the user mentioned:
> "there's an example of a blocking workflow when we merge clothing items... we run a prompt to analyze two entities and create a merged version, and then we review the merged version and can make changes before ultimately clicking save. this is a blocking workflow but it is not necessarily wrong from a technical point of view."

**Proposed Fix (Aligns with ROADMAP.md Phase 8-9)**:

Instead of blocking, use **"awaiting_input" job state** pattern:

```python
# 1. Create job immediately
job_id = job_manager.create_job(
    job_type=JobType.ANALYZE,
    title=f"Analyze Merge: {entity_type}",
    description="Generating merge preview..."
)

# 2. Run analysis in background
background_tasks.add_task(analyze_and_pause_for_input, job_id, ...)

# 3. Return job_id immediately
return {"job_id": job_id, "status": "queued"}

# 4. When analysis completes, pause job in "awaiting_input" state
async def analyze_and_pause_for_input(job_id, ...):
    merged_data = await service.analyze_merge(...)

    # Pause for user review (new state)
    job_manager.pause_for_input(
        job_id,
        awaiting_data={
            "merged_data": merged_data,
            "changes_summary": summary
        },
        brief_card={
            "title": "Merge Preview Ready",
            "description": "Review and approve merged entity",
            "actions": ["approve", "edit", "cancel"]
        }
    )

# 5. User reviews via Brief card or UI
# 6. User approves/edits/cancels
# 7. Job resumes with user's decision
```

**Benefits**:
- ✅ Non-blocking (returns job_id immediately)
- ✅ Progress tracking during analysis
- ✅ User can see "Analyzing merge..." message
- ✅ Pause for review without blocking UI
- ✅ Aligns with ROADMAP.md "propose-first" pattern
- ✅ Foundation for future agentic workflows

**Estimated Fix Time**: 2-3 hours (includes implementing "awaiting_input" state)

---

## Endpoint Compliance Summary

| Endpoint | File | Status | Response Time | Action Required |
|----------|------|--------|---------------|-----------------|
| Story Generation | workflows.py | ✅ Compliant | ~50ms | None |
| Modular Generator | generators.py | ✅ Compliant | ~50ms | None |
| Analyzer Tools (async) | tools.py | ✅ Compliant | ~50ms | None |
| Analyzer Tools (sync) | tools.py | ⚠️ Partial | 30-60s | Remove or deprecate sync mode |
| Legacy Generator | generators.py | ❌ Violation | 30-60s | Add async_mode + job spawning |
| Merge Analysis | merge.py | ❌ Violation | 30-60s | Implement "awaiting_input" pattern |

**Compliance Rate**: 40% fully compliant (2/5), 20% partial (1/5), 40% violations (2/5)

---

## Action Plan

### Phase 1: Fix Critical Violations (2-3 hours)

1. **Fix Legacy Generator Endpoint** (30 min)
   - Add `async_mode` parameter (default True)
   - Create job when async_mode=True
   - Use BackgroundTasks
   - Return job_id immediately
   - Test with frontend

2. **Implement "awaiting_input" Job State** (1.5 hours)
   - Add `AWAITING_INPUT` to JobStatus enum
   - Add `pause_for_input()` method to JobQueueManager
   - Add `resume_with_input()` method
   - Test state transitions

3. **Fix Merge Analysis Endpoint** (1 hour)
   - Convert to job-based workflow
   - Use "awaiting_input" state for user review
   - Update frontend to poll job status
   - Show preview in UI when job pauses

### Phase 2: Remove Partial Compliance (30 min)

4. **Remove Synchronous Mode from Analyzers** (30 min)
   - Delete lines 348-437 in tools.py
   - Remove `async_mode` parameter (always async now)
   - Update tests
   - Update frontend (if using sync mode)

### Phase 3: Testing & Validation (1 hour)

5. **Write Automated Test** (1 hour)
   - `test_llm_calls_never_block()` in tests/
   - Tests all LLM endpoints
   - Asserts response time < 1 second
   - Asserts job_id returned
   - Runs in CI/CD

---

## Future Considerations

### "Awaiting Input" Job State Architecture

Based on ROADMAP.md Phase 8-9 patterns, here's the proposed architecture:

```python
# api/models/jobs.py
class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_INPUT = "awaiting_input"  # NEW STATE
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

# api/services/job_queue.py
class JobQueueManager:
    def pause_for_input(
        self,
        job_id: str,
        awaiting_data: Dict[str, Any],
        brief_card: Optional[Dict[str, Any]] = None
    ):
        """
        Pause job and wait for user input.

        Args:
            job_id: Job to pause
            awaiting_data: Data for user to review
            brief_card: Optional Brief card to surface to user
        """
        job = self.get_job(job_id)
        job.status = JobStatus.AWAITING_INPUT
        job.awaiting_data = awaiting_data

        # Surface in Brief (Phase 8)
        if brief_card:
            self._create_brief_card(job_id, brief_card)

    def resume_with_input(
        self,
        job_id: str,
        user_input: Dict[str, Any]
    ):
        """Resume paused job with user's decision"""
        job = self.get_job(job_id)
        job.status = JobStatus.RUNNING
        job.user_input = user_input
        # Trigger resume callback
```

**Frontend Integration**:
- Jobs in "awaiting_input" state show in separate section
- Alert/notification when input needed
- Preview modal with approve/edit/cancel actions
- Resume job when user responds

**Phase 8 Integration**:
- Awaiting input jobs surface as Brief cards
- "Review merge preview" card appears in morning Brief
- One-tap approve/edit/cancel actions
- Seamless integration with Auto-Prep/Auto-Tidy

---

## Testing Strategy

### Unit Tests
```python
def test_analyzer_spawns_job():
    """Test analyzer creates job and returns job_id"""
    response = client.post(
        "/api/tools/analyzers/outfit",
        files={'image': dummy_image}
    )
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert response.json()["status"] == "queued"

def test_generator_spawns_job():
    """Test legacy generator creates job"""
    response = client.post(
        "/api/generate/style-transfer",
        json={"subject_image": "test.jpg", "visual_style": "vintage"}
    )
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_merge_analysis_spawns_job():
    """Test merge analysis creates job"""
    response = client.post(
        "/api/merge/analyze",
        json={
            "entity_type": "clothing_item",
            "source_entity": {...},
            "target_entity": {...}
        }
    )
    assert response.status_code == 200
    assert "job_id" in response.json()
```

### Performance Tests
```python
def test_llm_calls_never_block():
    """Test that no LLM endpoint blocks the request/response"""
    import time

    endpoints = [
        ("/api/tools/analyzers/outfit", {'files': {'image': dummy_image}}),
        ("/api/generate/modular", {'json': {...}}),
        ("/api/workflows/story-generation/execute", {'json': {...}}),
        ("/api/merge/analyze", {'json': {...}})
    ]

    for endpoint, kwargs in endpoints:
        start_time = time.time()
        response = client.post(endpoint, **kwargs)
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"{endpoint} took {elapsed}s - likely blocking on LLM"
        assert "job_id" in response.json(), f"{endpoint} didn't return job_id"
```

---

## Success Metrics

- ✅ 100% of LLM endpoints spawn jobs (currently 40%)
- ✅ All endpoint response times < 1 second (currently 60% compliant)
- ✅ Zero blocking LLM calls in production
- ✅ Automated test prevents regressions
- ✅ "Awaiting input" state enables human-in-the-loop workflows
- ✅ Foundation for Phase 8-9 autonomy features

---

## Next Steps

1. ✅ Complete audit (DONE)
2. ⏳ Fix legacy generator endpoint
3. ⏳ Implement "awaiting_input" job state
4. ⏳ Fix merge analysis endpoint
5. ⏳ Remove synchronous mode from analyzers
6. ⏳ Write automated test
7. ⏳ Update ENTITY_PREVIEW_MIGRATION_PLAN.md (mark Phase 2.2 complete)

---

**Audit Completed**: 2025-10-24
**Next Review**: After fixes implemented
**Estimated Fix Time**: 3-4 hours total
