# Life-OS Development Roadmap

**Last Updated**: 2025-10-22
**Status**: Reorganized for maintainability, reliability, and code quality
**Version**: 2.0

---

## Overview

Life-OS is evolving from a specialized **AI image generation platform** into a **comprehensive personal AI assistant**. This roadmap consolidates all future development plans into clear, actionable phases with a **strong emphasis on infrastructure, testing, and reliability**.

**Current State** (October 2025):
- ✅ 17 entity types with consistent UI
- ✅ 8 image analyzers + 6 generators
- ✅ Story generation workflow
- ✅ Characters system with appearance analyzer
- ✅ Testing infrastructure (66 tests, 56 passing)
- ✅ Mobile responsive design

**Key Principle**: **Infrastructure before features**. Build a solid foundation before adding complexity.

---

## Phase 1: Foundation & Critical Fixes (6-8 weeks)

**Goal**: Stable, scalable foundation with proper data layer, testing, and deployment

### 1.1 Database Migration (CRITICAL - 2-3 weeks)

**Current Problem**: All data stored as JSON files
- Does not scale beyond ~1000 entities per type
- Race conditions with concurrent writes
- No ACID guarantees, no full-text search, no efficient filtering

**Solution**: PostgreSQL + SQLAlchemy async ORM

**Prerequisites** (MUST DO FIRST):
- [ ] **Feature flags system** (LaunchDarkly or simple Redis-based)
- [ ] **Full backup** of all JSON files to external storage
- [ ] **Rollback script** (PostgreSQL → JSON if migration fails)
- [ ] **Backup & restoration testing** (verify backups work)

**Implementation**:
- [ ] Create SQLAlchemy models for all 17 entity types
- [ ] Add Alembic for schema migrations
- [ ] Migration script to import existing JSON data
  - [ ] Validate data integrity (check all required fields)
  - [ ] Handle missing/malformed data gracefully
  - [ ] Generate migration report (success/failure per entity)
- [ ] Update service layer to use async ORM queries
- [ ] Add database connection pooling (asyncpg)
- [ ] Update tests to use in-memory SQLite for speed
- [ ] **Gradual rollout**: 10% → 50% → 100% via feature flag
- [ ] **Automated PostgreSQL backups** (daily full, hourly incremental)
- [ ] **Point-in-time recovery** capability

**Migration Safety Checklist**:
- [ ] All tests pass with PostgreSQL backend
- [ ] Performance benchmarks (PostgreSQL ≥ JSON file speed)
- [ ] Backup restoration tested successfully
- [ ] Rollback script tested (PostgreSQL → JSON works)
- [ ] Feature flag kill switch working
- [ ] Migration monitoring dashboard (success rate, errors)

**Impact**: 10-100x faster queries, enables pagination, full-text search, relational queries

**Risk Mitigation**:
- 🔴 **HIGH RISK**: Data loss during migration
  - Mitigation: Multiple backups, gradual rollout, rollback script
- 🔴 **HIGH RISK**: Breaking changes affecting production
  - Mitigation: Feature flags, shadow testing (run both backends in parallel)

---

### 1.2 Performance Optimizations (1-2 weeks)

**Backend Pagination**:
- [ ] Add limit/offset to all list endpoints
- [ ] Return total count with paginated results
- [ ] Standard pagination params (default: 50 items, max: 200)
- [ ] Cursor-based pagination for large datasets (optional)

**Response Caching**:
- [ ] Add Redis-based caching for read endpoints
- [ ] Cache TTL: 60 seconds for lists, 5 minutes for details
- [ ] Cache invalidation on write operations (create/update/delete)
- [ ] Cache key strategy (include user_id, filters, sort order)
- [ ] Cache hit rate monitoring (target: >80%)

**Virtual Scrolling** (Frontend):
- [ ] Use react-window for entity lists (200+ items)
- [ ] Only render visible items (10-20 at a time)
- [ ] Smooth scrolling with 1000+ entities
- [ ] Preserve scroll position on navigation

**Performance Budgets**:
- [ ] Backend: p95 latency <500ms for list endpoints
- [ ] Backend: p95 latency <300ms for detail endpoints
- [ ] Frontend: Initial bundle <500KB gzipped
- [ ] Frontend: Time to Interactive <3s on 3G

**Success Criteria**:
- Lists of 500+ entities load in <500ms
- Paginated responses in <300ms
- No memory leaks with large datasets
- Cache hit rate >80%

---

### 1.3 Code Quality Improvements (1-2 weeks)

**Logging Infrastructure** (CRITICAL):
- [ ] Replace all `print()` with proper logging
- [ ] Structured JSON logs with correlation IDs
- [ ] Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- [ ] Request ID propagation (frontend → backend → LLM)
- [ ] Log aggregation (consider Loki or CloudWatch)
- [ ] Sensitive data filtering (passwords, API keys)

**Error Handling Standardization**:
- [ ] Create standardized error response models
  ```python
  {
    "error": {
      "code": "ENTITY_NOT_FOUND",
      "message": "Character abc123 not found",
      "details": {...},
      "request_id": "req_xyz789"
    }
  }
  ```
- [ ] Error codes for programmatic handling (50+ error types)
- [ ] Consistent error format across all endpoints
- [ ] Global error handler middleware
- [ ] User-friendly error messages (no stack traces to user)
- [ ] Error tracking integration (Sentry optional)

**Component Refactoring**:
- [ ] Split Composer.jsx (910 lines → ~300 lines + subcomponents)
  - [ ] PresetLibrary.jsx (200 lines)
  - [ ] PresetCanvas.jsx (200 lines)
  - [ ] AppliedPresetsStack.jsx (150 lines)
  - [ ] CompositionManager.jsx (150 lines)
- [ ] Unify OutfitAnalyzer + GenericAnalyzer (eliminate ~500 line duplication)
  - [ ] Create BaseAnalyzer.jsx (shared logic)
  - [ ] OutfitAnalyzer extends BaseAnalyzer
  - [ ] GenericAnalyzer extends BaseAnalyzer
- [ ] Create shared component library
  - [ ] Modal.jsx (reusable modal)
  - [ ] FormField.jsx (consistent form inputs)
  - [ ] LoadingSpinner.jsx (unified loading states)
  - [ ] Toast.jsx (notifications)
  - [ ] Button.jsx (consistent button styles)

**Success Criteria**:
- No component over 500 lines
- Zero `print()` statements in production code
- Consistent error responses across all endpoints
- All shared components documented with JSDoc

---

### 1.4 Testing Expansion (1-2 weeks)

**Backend Testing**:
- [ ] Fix 10 failing smoke tests (add auth fixtures)
- [ ] Integration tests for new features
  - [ ] Story presets CRUD
  - [ ] Tool configuration
  - [ ] Workflow execution end-to-end
- [ ] Database migration tests (JSON → PostgreSQL → JSON)
- [ ] API contract tests (ensure backward compatibility)
- [ ] Load tests (100 concurrent users, 1000 requests/min)
- [ ] Target: 80% coverage for service layer
- [ ] Target: 60% coverage for routes

**Frontend Testing**:
- [ ] Setup Vitest + React Testing Library
- [ ] EntityBrowser component tests
  - [ ] List view rendering
  - [ ] Detail view rendering
  - [ ] Edit mode functionality
  - [ ] Search and filtering
- [ ] Character import flow tests (critical path)
- [ ] Story workflow UI tests (critical path)
- [ ] Image generation UI tests (critical path)
- [ ] Accessibility tests (a11y-testing-library)
- [ ] Target: 40% coverage overall
- [ ] Target: 80% coverage for critical paths

**Test Infrastructure**:
- [ ] Parallel test execution (split backend/frontend)
- [ ] Test data factories (generate consistent test data)
- [ ] Visual regression tests (Percy or Chromatic - optional)
- [ ] Performance regression tests (track bundle size)

**Success Criteria**:
- All smoke tests passing (100%)
- Backend coverage >80% for services
- Frontend coverage >40% overall
- Frontend coverage >80% for critical paths
- No flaky tests (all tests deterministic)

---

### 1.5 CI/CD & DevOps (NEW - 1-2 weeks)

**Why This is CRITICAL**: Automated testing and deployment prevent regressions and enable safe, rapid iteration.

**GitHub Actions Workflows**:
- [ ] **Backend CI** (`.github/workflows/backend-ci.yml`)
  - [ ] Run pytest on every PR
  - [ ] Run linting (ruff)
  - [ ] Run type checking (mypy)
  - [ ] Check test coverage (fail if <80% for services)
  - [ ] Run security scanning (bandit)
- [ ] **Frontend CI** (`.github/workflows/frontend-ci.yml`)
  - [ ] Run Vitest on every PR
  - [ ] Run ESLint
  - [ ] Run type checking (if TypeScript)
  - [ ] Check bundle size (fail if >500KB)
  - [ ] Run accessibility tests
- [ ] **Dependency Security** (Dependabot)
  - [ ] Auto-update dependencies weekly
  - [ ] Security vulnerability scanning
  - [ ] Automated PR creation for updates
- [ ] **Database Migration CI**
  - [ ] Test migrations on every PR
  - [ ] Verify rollback works
  - [ ] Check for breaking changes

**Code Review Process**:
- [ ] PR template with checklist
  - [ ] Tests added/updated
  - [ ] Documentation updated
  - [ ] Breaking changes noted
  - [ ] Migration plan (if needed)
- [ ] Required reviews (1 approval before merge)
- [ ] Branch protection rules
  - [ ] No direct commits to main
  - [ ] Require PR reviews
  - [ ] Require status checks (tests pass)
- [ ] Code coverage reports in PRs (codecov)

**Deployment Automation**:
- [ ] Staging environment (mirror of production)
- [ ] Automated deployment to staging on merge to main
- [ ] Manual approval for production deployment
- [ ] Deployment rollback capability (1-click)
- [ ] Blue-green deployment strategy (zero downtime)

**Success Criteria**:
- All PRs run automated tests
- No merging without passing tests
- Deployment to staging automated
- Rollback tested and working
- Average PR merge time <24 hours

**Why Now**: Database migration (Phase 1.1) is high-risk. We need automated testing and safe deployment before attempting it.

---

### 1.6 TypeScript Migration (OPTIONAL - 1-2 weeks)

**Why TypeScript**: Frontend is growing (17 entity types, complex state management). TypeScript prevents runtime errors and improves maintainability.

**Incremental Migration Strategy**:
- [ ] Add TypeScript to Vite config
- [ ] Create type definitions for API responses
  - [ ] Character types
  - [ ] Story types
  - [ ] Preset types
  - [ ] Image types
  - [ ] All 17 entity types
- [ ] Migrate shared utilities first (.js → .ts)
- [ ] Migrate components incrementally (.jsx → .tsx)
  - [ ] Start with leaf components (no dependencies)
  - [ ] Work up to root components
- [ ] Add type checking to CI/CD pipeline
- [ ] Target: 80% type coverage

**Benefits**:
- Catch errors at compile time, not runtime
- Better IDE autocomplete and refactoring
- Self-documenting code (types as documentation)
- Easier onboarding for new developers

**Success Criteria**:
- 80% of codebase is TypeScript
- Zero `any` types (use `unknown` instead)
- All API responses have types
- Type checking in CI passes

---

## Phase 2: Infrastructure Hardening (3-4 weeks)

**Goal**: Robust, secure, observable infrastructure before adding complex features

**Why Before Board Game Assistant**: Building on unstable infrastructure leads to cascading failures. Get the foundation right first.

---

### 2.1 Local LLM Integration (1.5-2 weeks)

**Backend**:
- [ ] Add llama-cpp-python dependency
- [ ] LocalLLMProvider class (compatible with LLMRouter interface)
- [ ] Local model management routes
  - [ ] `GET /api/local-models` (list installed models)
  - [ ] `POST /api/local-models/download` (download from HuggingFace)
  - [ ] `DELETE /api/local-models/{id}` (delete model)
  - [ ] `GET /api/local-models/{id}/info` (model metadata, size, speed)
- [ ] Update LLMRouter for `local://` prefix
  - [ ] `local://tinyllama-1.1b` routes to LocalLLMProvider
- [ ] Model catalog (HuggingFace links with metadata)
- [ ] Inference optimization (GPU support if available)

**Frontend**:
- [ ] Local Models page (`/local-models`)
- [ ] Download models from catalog with progress bar
- [ ] Model info cards (size, speed, quality rating)
- [ ] Disk usage display and warnings
- [ ] Local models appear in tool config dropdowns
- [ ] Clear labeling (local vs cloud models)

**Recommended Starter Models**:
- **TinyLlama 1.1B** (637 MB) - Fast, testing, low quality
- **Phi-2 2.7B** (1.6 GB) - Balanced speed/quality
- **LLaMA 2 7B** (4.0 GB) - High quality, slower

**Success Criteria**:
- Can download and use TinyLlama
- Tools work with local models (outfit_analyzer, etc.)
- Inference <10s for analysis (TinyLlama)
- Inference <5s for analysis (with GPU)
- Cost tracking shows $0 for local model usage

**Why Now**: Enables cheaper document Q&A in Phase 4 (Board Game Assistant).

---

### 2.2 Monitoring & Observability (1 week)

**Metrics & Monitoring**:
- [ ] Prometheus metrics endpoint (`/metrics`)
- [ ] Track key metrics:
  - [ ] Request count by endpoint
  - [ ] Request latency (p50, p95, p99)
  - [ ] Error rate by endpoint
  - [ ] LLM API costs (by provider, tool, user)
  - [ ] Database query latency
  - [ ] Job queue depth
  - [ ] Cache hit rate
- [ ] Grafana dashboards
  - [ ] System health overview
  - [ ] API performance
  - [ ] LLM cost breakdown
  - [ ] Job queue status
  - [ ] Error rate trends
- [ ] Alerting (PagerDuty, email, Slack)
  - [ ] Error rate >5% (critical)
  - [ ] p95 latency >1s (warning)
  - [ ] Job queue depth >100 (warning)
  - [ ] LLM costs >$50/day (warning)
- [ ] Cost tracking dashboard
  - [ ] Daily/weekly/monthly LLM API costs
  - [ ] Cost per user
  - [ ] Cost per tool
  - [ ] Budget alerts

**Distributed Tracing**:
- [ ] OpenTelemetry integration
- [ ] Trace request flows (frontend → API → LLM)
- [ ] Identify slow operations
- [ ] Correlation IDs across services

**Health Checks**:
- [ ] `/health/ready` (service is ready to accept traffic)
- [ ] `/health/live` (service is alive, restart if not)
- [ ] Database connectivity check
- [ ] Redis connectivity check
- [ ] External API connectivity check (Gemini, OpenAI)

**Success Criteria**:
- Prometheus scraping metrics every 15s
- Grafana dashboards visualize all key metrics
- Alerts trigger within 1 minute of threshold
- Cost tracking accurate to within $0.10/day
- All health checks passing

**Why Now**: Can't maintain what you can't measure. Need visibility before adding complexity.

---

### 2.3 Security Hardening (1 week)

**SQL Injection Prevention**:
- [ ] Audit all database queries (use parameterized queries only)
- [ ] Add SQL injection tests (sqlmap or custom tests)
- [ ] Input validation on all endpoints (Pydantic models)
- [ ] Query complexity limits (prevent expensive queries)

**XSS & CSRF Protection**:
- [ ] Content Security Policy (CSP) headers
- [ ] X-Frame-Options header (prevent clickjacking)
- [ ] X-Content-Type-Options header
- [ ] XSS vulnerability scanning (OWASP ZAP or similar)
- [ ] CSRF token validation for state-changing operations

**Authentication & Authorization**:
- [ ] JWT token expiration testing (tokens expire after 24h)
- [ ] Refresh token implementation
- [ ] Session management (logout invalidates tokens)
- [ ] Password complexity requirements
- [ ] Rate limiting on login endpoint (prevent brute force)

**Secrets Management**:
- [ ] Secrets rotation strategy (rotate API keys quarterly)
- [ ] Environment variable validation (fail fast if missing)
- [ ] No secrets in logs (filter sensitive data)
- [ ] No secrets in error messages
- [ ] Secrets scanning in CI (prevent accidental commits)

**API Rate Limiting**:
- [ ] Add slowapi middleware
- [ ] Rate limits:
  - [ ] 10 generations/minute per user
  - [ ] 100 API calls/minute per user
  - [ ] 1000 API calls/hour per IP
- [ ] Per-IP and per-user rate limiting
- [ ] Rate limit headers (`X-RateLimit-Remaining`)
- [ ] Clear error messages when rate limited

**Security Headers**:
- [ ] Strict-Transport-Security (HSTS)
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] Content-Security-Policy
- [ ] Referrer-Policy

**Success Criteria**:
- No SQL injection vulnerabilities (tested with sqlmap)
- No XSS vulnerabilities (tested with ZAP)
- All security headers present
- Rate limiting effective (tested with load tests)
- Security audit passing (external audit optional)

**Why Now**: Security is foundational. Fix vulnerabilities before they become exploits.

---

### 2.4 Backup & Disaster Recovery (1 week)

**Automated Backups**:
- [ ] PostgreSQL backups
  - [ ] Daily full backups (retain 30 days)
  - [ ] Hourly incremental backups (retain 7 days)
  - [ ] Backup to external storage (S3 or similar)
  - [ ] Encrypted backups (AES-256)
- [ ] Redis backups (job queue state)
  - [ ] Daily snapshots (retain 7 days)
- [ ] File storage backups (images, uploads)
  - [ ] Daily backups (retain 30 days)
- [ ] Configuration backups (YAML, JSON configs)
  - [ ] Version controlled in Git

**Backup Testing**:
- [ ] Quarterly restoration drills
  - [ ] Restore PostgreSQL from backup
  - [ ] Restore Redis from backup
  - [ ] Restore file storage from backup
  - [ ] Verify data integrity
- [ ] Automated restoration tests (monthly)
- [ ] Document restoration procedures

**Point-in-Time Recovery**:
- [ ] PostgreSQL WAL archiving
- [ ] Ability to restore to any point in last 7 days
- [ ] Test PITR restoration

**Disaster Recovery Plan**:
- [ ] Document recovery procedures
- [ ] Recovery Time Objective (RTO): <4 hours
- [ ] Recovery Point Objective (RPO): <1 hour
- [ ] Failover plan (manual or automated)
- [ ] Communication plan (who to notify)

**Success Criteria**:
- Backups run automatically every day
- Restoration tested successfully quarterly
- PITR works (tested)
- RTO <4 hours (tested)
- RPO <1 hour (verified with WAL)

**Why Now**: Database migration (Phase 1.1) requires solid backup strategy. Need backups BEFORE touching production data.

---

### 2.5 Load & Performance Testing (1 week)

**Load Testing Tools**:
- [ ] Locust or k6 for load generation
- [ ] Test scenarios:
  - [ ] 100 concurrent users browsing entities
  - [ ] 50 concurrent users generating images
  - [ ] 1000 entities in database (pagination test)
  - [ ] 10,000 entities in database (scale test)
- [ ] Stress testing (push to failure point)
- [ ] Spike testing (sudden traffic increase)

**Performance Profiling**:
- [ ] Database query profiling (identify slow queries)
  - [ ] Use EXPLAIN ANALYZE on slow queries
  - [ ] Add indexes where needed
- [ ] Python profiling (cProfile)
  - [ ] Identify slow Python code
  - [ ] Optimize hot paths
- [ ] Frontend profiling (Chrome DevTools)
  - [ ] Identify slow renders
  - [ ] Optimize re-renders with React.memo

**Performance Budgets**:
- [ ] Backend: p95 latency <500ms for list endpoints
- [ ] Backend: p95 latency <300ms for detail endpoints
- [ ] Backend: Handle 100 concurrent users
- [ ] Frontend: Initial bundle <500KB gzipped
- [ ] Frontend: Time to Interactive <3s on 3G
- [ ] Database: Query latency <100ms (p95)

**Performance Regression Tests**:
- [ ] Automated performance tests in CI
- [ ] Fail if performance degrades >10%
- [ ] Track performance trends over time

**Success Criteria**:
- Can handle 100 concurrent users with <1% error rate
- Can handle 1000 entities with <500ms latency
- All performance budgets met
- No performance regressions in CI

**Why Now**: Validate Phase 1.2 (Performance Optimizations) actually work under load.

---

## Phase 3: Extensibility & Architecture (4-6 weeks)

**Goal**: Plugin architecture and advanced workflows for future expansion

**Why Now**: With solid infrastructure (Phase 1-2), we can build extensibility the right way.

---

### 3.1 Plugin Architecture (3-4 weeks)

**Core Infrastructure**:
- [ ] Plugin manifest schema (`plugin.json`)
  ```json
  {
    "name": "image-generation",
    "version": "1.0.0",
    "entities": ["visual_styles", "art_styles"],
    "tools": ["outfit_analyzer", "style_transfer"],
    "workflows": ["style_transfer_workflow"],
    "dependencies": ["pillow", "torch"]
  }
  ```
- [ ] Plugin discovery system (scan `plugins/` directory)
- [ ] Plugin loading system (dynamic import)
- [ ] Plugin API (register entities, tools, workflows)
  - [ ] `register_entity(name, config)`
  - [ ] `register_tool(name, tool_class)`
  - [ ] `register_workflow(name, workflow_def)`
- [ ] Plugin lifecycle management
  - [ ] `load()` - Initialize plugin
  - [ ] `unload()` - Cleanup plugin
  - [ ] `reload()` - Hot-reload during development
- [ ] Plugin isolation (sandboxing optional)
- [ ] Plugin dependencies management
- [ ] Plugin health checks (verify plugin works)

**Example Plugin Structure**:
```
plugins/
├── image_generation/
│   ├── plugin.json           # Manifest
│   ├── plugin.py             # Plugin entry point
│   ├── entities/
│   │   ├── visual_styles.json
│   │   └── art_styles.json
│   ├── tools/
│   │   ├── outfit_analyzer.py
│   │   └── style_transfer.py
│   ├── workflows/
│   │   └── style_transfer_workflow.py
│   └── README.md
└── board_games/              # Phase 4 plugin
    ├── plugin.json
    └── ...
```

**Refactor Existing Features as Plugins**:
- [ ] Image generation plugin
  - [ ] Move outfit_analyzer, visual_style_analyzer, etc.
  - [ ] Move modular_image_generator
  - [ ] Move all image-related entities
- [ ] Story generation plugin
  - [ ] Move story_planner, story_writer, story_illustrator
  - [ ] Move story workflow
  - [ ] Move story-related entities
- [ ] Core plugin (minimal base)
  - [ ] User management
  - [ ] Authentication
  - [ ] Job queue
  - [ ] Basic UI components

**Plugin UI**:
- [ ] Plugin management page (`/plugins`)
- [ ] List installed plugins
- [ ] Enable/disable plugins
- [ ] Plugin settings per plugin
- [ ] Plugin marketplace (future)

**Success Criteria**:
- 3+ plugins created (core, image, story)
- Plugins can be loaded/unloaded without restart
- Plugin hot-reload works in development
- All existing features work as plugins

**Why This Matters**: Board Game Assistant (Phase 4) will be the first external plugin. Validates the plugin architecture works.

---

### 3.2 Workflow Engine Enhancements (2-3 weeks)

**Advanced Features**:
- [ ] Conditional branching (if/else in workflows)
  ```yaml
  - if: ${ character.age == "child" }
    then: use_simple_language
    else: use_normal_language
  ```
- [ ] Parallel step execution
  - [ ] Run multiple agents simultaneously
  - [ ] Aggregate results
- [ ] Error handling and retry logic
  - [ ] Retry failed steps (exponential backoff)
  - [ ] Fallback to different tool/model
  - [ ] Continue workflow on non-critical errors
- [ ] Workflow templates (save/load definitions)
  - [ ] `POST /api/workflows/templates` (save template)
  - [ ] `GET /api/workflows/templates` (list templates)
  - [ ] `POST /api/workflows/execute-template` (run template)
- [ ] Visual workflow builder UI (drag-and-drop nodes)
  - [ ] React Flow for node graph
  - [ ] Node types: Agent, Tool, Condition, Parallel
  - [ ] Connections define data flow
  - [ ] Export as JSON workflow definition

**Workflow Monitoring**:
- [ ] Step-by-step progress tracking
- [ ] Execution timeline visualization
- [ ] Error logs per step
- [ ] Retry failed steps from UI
- [ ] Workflow analytics (success rate, avg duration)

**Workflow DSL** (optional):
```yaml
workflow: story_generation
steps:
  - id: plan
    agent: story_planner
    input: { character: $input.character }
  - id: write
    agent: story_writer
    input: { plan: $plan.output }
    retry: 3
  - id: illustrate
    agent: story_illustrator
    input: { story: $write.output }
    parallel: true  # Generate all images in parallel
```

**Success Criteria**:
- Workflows support conditionals, parallelism, retries
- Visual workflow builder functional
- Workflow templates working
- Workflow monitoring dashboard shows progress

---

### 3.3 Context Management System (1-2 weeks)

**Features**:
- [ ] User preferences storage
  - [ ] Favorite models per tool
  - [ ] Default parameters per tool
  - [ ] UI preferences (theme, layout)
- [ ] Cross-session memory
  - [ ] Conversation history
  - [ ] User patterns and preferences
  - [ ] Recently used entities
- [ ] Entity relationships graph
  - [ ] Characters in stories
  - [ ] Items in collections
  - [ ] Presets used together
- [ ] Context API
  - [ ] `GET /api/context/relevant` (get relevant context for query)
  - [ ] Inject context into tool prompts automatically
- [ ] Smart context selection
  - [ ] Retrieve 5 most relevant entities
  - [ ] Use vector similarity for relevance
  - [ ] Limit context size (fit in prompt)

**Context Injection Example**:
```python
# User asks: "Create a story with Luna"
# Context manager automatically injects:
context = {
  "character": luna_character_data,
  "recent_stories": [story1, story2],  # Stories with Luna
  "user_preferences": { "tone": "dark", "length": "short" }
}
```

**Success Criteria**:
- User preferences persist across sessions
- Context API returns relevant entities
- Tools automatically receive relevant context
- Context size limited to fit in prompts

---

### 3.4 API Versioning (1 week)

**Why Now**: Database migration (Phase 1.1) changes data schema. Need versioned API to avoid breaking clients.

**Implementation**:
- [ ] API v1 endpoints (current API, read-only)
  - [ ] `/api/v1/characters/` (JSON files)
  - [ ] Deprecated warnings in responses
  - [ ] Sunset timeline (6 months after v2 launch)
- [ ] API v2 endpoints (new database schema)
  - [ ] `/api/v2/characters/` (PostgreSQL)
  - [ ] New features only in v2
  - [ ] Better performance, more features
- [ ] Client version detection
  - [ ] `X-API-Version` header
  - [ ] Auto-route to correct version
- [ ] API version middleware
  - [ ] Parse version from URL or header
  - [ ] Route to correct handler
- [ ] Deprecation strategy
  - [ ] Announce v1 deprecation (6 months notice)
  - [ ] Warn users on every v1 request
  - [ ] Disable v1 after sunset (return 410 Gone)

**Migration Path**:
```
Month 0: Launch v2, v1 still works
Month 1-6: Both v1 and v2 work, v1 shows deprecation warnings
Month 6: Disable v1, only v2 works
```

**Success Criteria**:
- Both v1 and v2 APIs work simultaneously
- Clients can opt into v2 explicitly
- Deprecation warnings clear and actionable
- No breaking changes for v1 users (until sunset)

**Why This Matters**: Allows us to evolve the API without breaking existing clients.

---

## Phase 4: Board Game Assistant (3-4 weeks)

**Goal**: MVP rules assistant that validates plugin architecture

**Why Phase 4 (Not Phase 2)**:
- Built on solid infrastructure (Phase 1-2)
- Uses plugin architecture (Phase 3)
- Uses local LLMs for cheaper document processing (Phase 2.1)
- Safer to build complex feature after foundation is stable

**Implementation as PLUGIN**:
- [ ] Create `plugins/board_games/` plugin
- [ ] Validates plugin architecture works
- [ ] Demonstrates how to add new domain

---

### 4.1 Rules Gatherer (1 week)

**Backend**:
- [ ] Board game entity model (via plugin)
- [ ] BGG integration service
  - [ ] Search BGG for game
  - [ ] Fetch game metadata (designer, year, player count, etc.)
  - [ ] Download rulebook PDFs from BGG files page
  - [ ] Rate limiting (1 req/sec to BGG)
- [ ] Rulebook storage (`data/board_games/{game_id}/rulebooks/`)
- [ ] API routes:
  - [ ] `POST /api/board-games/` (create game)
  - [ ] `GET /api/board-games/` (list games)
  - [ ] `GET /api/board-games/{id}` (get game details)
  - [ ] `POST /api/board-games/{id}/gather-rules` (download rulebooks)
  - [ ] `DELETE /api/board-games/{id}` (delete game)

**Frontend**:
- [ ] Board game entity browser (`/board-games`)
- [ ] Add game modal (search BGG by title)
- [ ] Download rulebooks with progress bar
- [ ] Rulebook list with metadata (version, language, page count)

**Success Criteria**:
- Can search BGG and add games
- Can download rulebooks from BGG
- 10+ games added successfully
- Respects BGG rate limits

**Risks**:
- 🔴 **HIGH RISK**: BGG blocks scraping or changes HTML
  - Mitigation: Manual PDF upload fallback, aggressive caching

---

### 4.2 Document RAG Preparer (1 week)

**Backend**:
- [ ] Docling integration (PDF → Markdown)
  ```python
  pip install docling
  ```
- [ ] Semantic text chunking
  - [ ] Chunk by sections/subsections
  - [ ] ~500 tokens per chunk
  - [ ] 50 tokens overlap between chunks
- [ ] Embedding generation
  - [ ] Use local model (Phase 2.1) for cost savings
  - [ ] Or Gemini embeddings if quality needed
- [ ] ChromaDB vector database setup
  - [ ] Create collection per game
  - [ ] Store chunks with metadata (page, section, heading)
- [ ] Background job for document processing
  - [ ] Queue PDF processing
  - [ ] Track progress (0-100%)
  - [ ] Store processing errors

**API Routes**:
- [ ] `POST /api/board-games/{id}/process-rules` (start processing)
- [ ] `GET /api/board-games/{id}/processing-status` (get progress)

**Success Criteria**:
- PDFs convert to markdown successfully
- Chunks are semantically meaningful
- Embeddings generated and indexed
- Processing completes in <5 minutes for 20-page rulebook

**Risks**:
- 🟡 **MEDIUM RISK**: Docling fails on complex PDFs
  - Mitigation: Manual markdown upload fallback, OCR fallback

---

### 4.3 Document Q&A System (1-2 weeks)

**Backend**:
- [ ] Q&A entity model (generic: document, general, image, comparison)
  ```json
  {
    "qa_id": "uuid",
    "question": "How many eggs do you start with?",
    "answer": "You don't start with any eggs...",
    "context_type": "document",  // or "general", "image", "comparison"
    "game_id": "wingspan-266192",
    "document_ids": ["wingspan-rulebook-v2.0-en"],
    "citations": [
      {
        "text": "Take 2 eggs from the supply...",
        "page": 9,
        "section": "Actions - Lay Eggs"
      }
    ],
    "confidence": 0.98,
    "was_helpful": null  // user feedback
  }
  ```
- [ ] Semantic search for relevant chunks
  - [ ] Generate embedding for question
  - [ ] Search ChromaDB for top 5-10 chunks
  - [ ] Retrieve chunks with metadata
- [ ] LLM prompt with strict citation requirements
  ```
  You are a rules expert. Answer using ONLY the rulebook excerpts.
  CRITICAL: Cite page number and section for each statement.
  If not in excerpts, say "I don't see this in the rulebook."
  ```
- [ ] Citation parsing (extract page numbers from response)
- [ ] API routes:
  - [ ] `POST /api/qa/ask` (ask question, optional game_id)
  - [ ] `GET /api/board-games/{id}/qa` (list Q&As for game)
  - [ ] `GET /api/qa/` (list all Q&As, filterable by context_type, game_id, tags)
  - [ ] `GET /api/qa/{id}` (get specific Q&A)
  - [ ] `PUT /api/qa/{id}` (update: favorite, feedback, tags, notes)
  - [ ] `DELETE /api/qa/{id}` (delete Q&A)

**Frontend**:
- [ ] Game detail page (shows rulebooks and Q&As)
- [ ] Ask question interface
  - [ ] Game selector (optional for general questions)
  - [ ] Question input
  - [ ] Submit button
- [ ] Q&A display component
  - [ ] Answer text
  - [ ] Expandable citations (show rulebook excerpt)
  - [ ] Helpful/not helpful buttons
  - [ ] Favorite button
- [ ] Q&A list (filter by game, favorites, tags)

**Success Criteria**:
- 50+ questions answered with 90%+ citation accuracy (manual review)
- 80%+ helpful rating from users
- <5 second response time per question
- Citations accurate (point to correct page/section)

**Risks**:
- 🔴 **HIGH RISK**: LLM hallucinates wrong citations
  - Mitigation: Strict prompts, confidence scores, user feedback loop, "verify in rulebook" warnings

---

### 4.4 Tool Configuration UI (overlaps with 4.1-4.3)

**Backend** (if not already done):
- [ ] Tool configuration model (tool_id, model, parameters)
- [ ] Tool config CRUD routes
- [ ] Update LLMRouter to respect configs
- [ ] Available models endpoint

**Frontend**:
- [ ] Tool Configuration page (`/tool-configs`)
- [ ] List all tools
- [ ] Model selection dropdown per tool
- [ ] Parameter editors (temperature, max_tokens)
- [ ] Test tool button with image upload
- [ ] Reset to defaults

**Success Criteria**:
- All tools configurable from UI
- Model selection works
- Parameter changes affect tool behavior
- Test tool works for all tools

---

## Phase 5: Agent Framework (5-6 weeks)

**Goal**: Semi-autonomous agents that proactively help users

---

### 5.1 Agent Core (2-3 weeks)

**Base Agent System**:
- [ ] Base agent class with planning loop
  ```python
  class BaseAgent:
      def plan(self, goal: str) -> List[Task]
      def execute_task(self, task: Task) -> TaskResult
      def monitor_progress(self) -> Progress
      def handle_error(self, error: Exception) -> ErrorHandling
  ```
- [ ] Goal decomposition (break down goals into tasks)
- [ ] Tool selection (choose appropriate tools for each task)
- [ ] Multi-step execution with state management
- [ ] Agent types:
  - [ ] ImageAgent (image analysis and generation)
  - [ ] StoryAgent (story creation and illustration)
  - [ ] CharacterAgent (character creation and management)
  - [ ] ResearchAgent (gather information from web/docs)
  - [ ] CodeAgent (code analysis and generation)
  - [ ] BoardGameAgent (rules questions and game analysis)

**Example**: Story Agent
```
User: "Create a mystery story with Luna in a Victorian setting"
Agent Plan:
  1. Fetch character data (Luna)
  2. Generate plot outline (mystery, Victorian)
  3. Write story (using plot and character)
  4. Generate illustrations (story scenes)
  5. Return complete story
Agent Execution:
  - Step 1: GET /api/characters/{luna_id}
  - Step 2: POST /api/agents/story-planner (story_planner tool)
  - Step 3: POST /api/agents/story-writer (story_writer tool)
  - Step 4: POST /api/agents/story-illustrator (story_illustrator tool)
  - Step 5: Return { story, illustrations }
```

**Success Criteria**:
- 3+ agent types implemented
- Agents can decompose complex goals
- Agents execute multi-step plans successfully
- Agents handle errors gracefully (retry, fallback)

---

### 5.2 Task Planner (1-2 weeks)

**Features**:
- [ ] Task dependency resolution
  ```
  Task A: Fetch character
  Task B: Generate plot (depends on A)
  Task C: Write story (depends on B)
  Task D: Illustrate story (depends on C)
  ```
- [ ] Resource estimation
  - [ ] Time: Estimate task duration
  - [ ] Cost: Estimate LLM API costs
  - [ ] API calls: Count required API calls
- [ ] Execution monitoring
  - [ ] Track task states (pending, running, completed, failed)
  - [ ] Update progress in real-time
- [ ] Adaptive planning
  - [ ] Adjust plan based on results
  - [ ] Skip optional tasks if time/budget exceeded
  - [ ] Add recovery tasks if errors occur

**Success Criteria**:
- Task dependencies resolved correctly (DAG)
- Resource estimates within 20% of actual
- Execution monitoring shows real-time progress
- Adaptive planning adjusts to errors/results

---

### 5.3 Safety & Permissions (1-2 weeks)

**Safety Features**:
- [ ] Risk assessment
  - [ ] Low risk: Read data, analyze images
  - [ ] Medium risk: Create/update entities
  - [ ] High risk: Delete data, API calls >$1
- [ ] Approval for high-risk actions
  - [ ] Prompt user for confirmation
  - [ ] Show estimated cost/impact
  - [ ] Allow/deny/delay decision
- [ ] Audit trail
  - [ ] Log all agent actions with timestamps
  - [ ] Store user decisions (allow/deny)
  - [ ] Queryable audit log
- [ ] Rollback capabilities
  - [ ] Undo entity creation/update
  - [ ] Undo entity deletion (soft delete)
  - [ ] Revert to previous state
- [ ] Resource limits
  - [ ] Max API cost per agent run (default: $5)
  - [ ] Max duration per agent run (default: 10 minutes)
  - [ ] Max tasks per agent run (default: 50)

**Permission System**:
- [ ] User-defined permission levels
  - [ ] `read-only`: Can read data, no modifications
  - [ ] `standard`: Can create/update, no delete
  - [ ] `admin`: Can do anything
- [ ] Per-agent permissions
  - [ ] Agent X can only access entity type Y
  - [ ] Agent Z requires approval for all actions
- [ ] Approval workflows
  - [ ] Agent proposes action
  - [ ] User approves/denies
  - [ ] Agent executes if approved

**Success Criteria**:
- All high-risk actions require approval
- Audit trail records all agent actions
- Rollback works for all reversible actions
- Resource limits prevent runaway costs

---

## Phase 6: Domain Expansion (Ongoing)

**Goal**: Extend Life-OS to new domains using plugin architecture

### Planned Domains (12-15 weeks each)

Each domain becomes a plugin following the same pattern as Board Games (Phase 4).

**Video Generation**:
- Sora integration
- Video prompt enhancement
- Video editing workflows
- Storyboard generation

**Code Management**:
- Project analysis
- Code refactoring suggestions
- Documentation generation
- Test generation

**Life Planning**:
- Task management
- Calendar integration
- Habit tracking
- Goal setting and progress

**Home Automation**:
- Home Assistant integration
- Automation workflows
- Device control
- Energy monitoring

**Educational Content**:
- Lesson plan generation
- Video script creation
- Quiz generation
- Learning path recommendations

**Board Games** (full suite, after Phase 4 MVP):
- Collection management
- Session logging
- Teaching guide generation
- Mechanic analysis
- Prototype design tools

---

## Implementation Priorities (Next 4 Months)

### Month 1: Foundation (Weeks 1-4)
**Week 1**: Database Migration Prerequisites (feature flags, backups, rollback script)
**Week 2**: Database Migration (PostgreSQL, Alembic, migration script)
**Week 3**: Performance Optimizations (pagination, caching, virtual scrolling)
**Week 4**: Code Quality (logging, error handling, refactoring)

### Month 2: Infrastructure (Weeks 5-8)
**Week 5**: Testing Expansion (fix failing tests, add frontend tests)
**Week 6**: CI/CD & DevOps (GitHub Actions, code review, deployment automation)
**Week 7**: TypeScript Migration (optional, can defer)
**Week 8**: Local LLMs (llama-cpp-python, model management)

### Month 3: Hardening (Weeks 9-12)
**Week 9**: Monitoring & Observability (Prometheus, Grafana, alerts)
**Week 10**: Security Hardening (SQL injection, XSS, rate limiting, secrets)
**Week 11**: Backup & Disaster Recovery (automated backups, restoration testing)
**Week 12**: Load Testing (Locust, performance profiling, regression tests)

### Month 4: Extensibility (Weeks 13-16)
**Week 13-14**: Plugin Architecture (manifest, discovery, loading, lifecycle)
**Week 15**: Refactor existing features as plugins (image, story, core)
**Week 16**: Plugin UI and testing

---

## Success Metrics by Phase

**Phase 1 (Foundation)**:
- [ ] All entities use database (zero JSON file reads)
- [ ] Backend test coverage >80% for services
- [ ] Frontend test coverage >40% overall
- [ ] Lists of 500+ entities load in <500ms
- [ ] Zero `print()` statements
- [ ] Smoke tests at 90%+ pass rate
- [ ] Database migration successful with zero data loss

**Phase 2 (Infrastructure Hardening)**:
- [ ] 3+ local models available and working
- [ ] Prometheus metrics collected every 15s
- [ ] Grafana dashboards visualize key metrics
- [ ] Zero security vulnerabilities (tested)
- [ ] Backups automated and tested (restoration works)
- [ ] Can handle 100 concurrent users with <1% error rate

**Phase 3 (Extensibility)**:
- [ ] 3+ plugins created (core, image, story)
- [ ] Plugins can be loaded/unloaded without restart
- [ ] Plugin hot-reload works in development
- [ ] Workflow templates working
- [ ] Visual workflow builder functional
- [ ] API v2 launched, v1 deprecated

**Phase 4 (Board Game Assistant)**:
- [ ] 10+ games with processed rulebooks
- [ ] 50+ Q&As with 90%+ citation accuracy
- [ ] 80%+ helpful rating from users
- [ ] <5 second response time per question
- [ ] Board Games plugin validates plugin architecture

**Phase 5 (Agents)**:
- [ ] 3+ agent types implemented
- [ ] Agents complete multi-step tasks successfully
- [ ] Permission system active and tested
- [ ] Audit trail complete and queryable
- [ ] Resource limits prevent runaway costs

**Phase 6 (Domain Expansion)**:
- [ ] 2+ new domain plugins created
- [ ] Each plugin follows established patterns
- [ ] Cross-domain context working
- [ ] User satisfaction >80%

---

## Risk Assessment

### High Risk 🔴

1. **Database Migration Complexity**: 2-3 weeks of careful migration work
   - **Mitigation**:
     - Multiple backups before migration
     - Gradual rollout (10% → 50% → 100%) via feature flags
     - Rollback script tested and ready
     - Shadow testing (run both backends in parallel)
     - Data integrity validation after migration

2. **Breaking Changes During Migration**: Existing clients stop working
   - **Mitigation**:
     - API versioning (v1 continues to work)
     - 6 month deprecation timeline for v1
     - Clear migration guide for users
     - Automated client version detection

3. **LLM Hallucination in Q&A**: Wrong citations, fabricated answers
   - **Mitigation**:
     - Strict prompt engineering (citation requirements)
     - Confidence scores shown to users
     - User feedback loop (helpful/not helpful)
     - "Verify in rulebook" warnings
     - Manual review of first 50 Q&As

4. **Security Vulnerabilities**: SQL injection, XSS, etc.
   - **Mitigation**:
     - Security audit (Phase 2.3)
     - Automated security scanning in CI
     - Regular dependency updates (Dependabot)
     - Rate limiting on all endpoints
     - Secrets rotation strategy

### Medium Risk 🟡

1. **Performance at Scale**: Unknown limits with large datasets
   - **Mitigation**:
     - Pagination from start
     - Virtual scrolling for large lists
     - Load testing (Phase 2.5)
     - Performance budgets in CI
     - Database query profiling

2. **Local LLM Quality**: May not match cloud models
   - **Mitigation**:
     - User choice (local vs cloud)
     - Clear quality expectations
     - Cloud model fallback
     - Quality comparison testing

3. **Plugin System Complexity**: Hard to get abstraction right
   - **Mitigation**:
     - Start simple, iterate
     - Build 3 plugins before declaring success
     - Plugin developer documentation
     - Example plugin as template

4. **BGG API Stability**: Rate limits, blocking, HTML changes
   - **Mitigation**:
     - Aggressive caching (cache BGG responses 7 days)
     - Manual PDF upload fallback
     - Respect rate limits (1 req/sec)
     - Error handling for HTML changes

### Low Risk 🟢

1. **CI/CD Setup**: Time-consuming but well-understood
   - **Mitigation**: Use GitHub Actions (well-documented, free)

2. **TypeScript Migration**: Optional, can defer
   - **Mitigation**: Incremental migration, no deadline

3. **Monitoring Setup**: Prometheus/Grafana are mature
   - **Mitigation**: Use official guides, start simple

---

## Long-Term Vision (12-18 months)

**Life-OS as Comprehensive AI Assistant**:
- 20+ entity types across multiple domains
- 50+ standalone tools, all frontend-configurable
- Hybrid cloud + local LLM architecture
- Plugin ecosystem for extensions
- Semi-autonomous agents for routine tasks
- Cross-domain intelligence and context

**User Experience**:
- Create once, use everywhere (characters, styles, workflows)
- Everything keyboard-accessible
- Fast and responsive (feels local-first)
- Intelligent and learns preferences
- Powerful bulk operations
- Beautiful and intuitive UI

---

## Design Principles (Maintained Throughout)

1. **Infrastructure Before Features**: Solid foundation enables rapid iteration
2. **Testing First**: Write tests before merging, fix failing tests immediately
3. **Security by Default**: Rate limiting, input validation, secrets management from start
4. **Observable by Design**: Metrics, logging, tracing for all features
5. **Backwards Compatible**: API versioning, graceful deprecation
6. **Entity-First Design**: Always consider entity approach before adding features
7. **Modularity Over Monoliths**: Discrete fields, not large text blobs
8. **Configuration Over Code**: Editable prompts, models, parameters
9. **User Agency**: Manual triggers, editable results, transparency
10. **Performance by Default**: Pagination, lazy loading, caching from start
11. **State Persistence**: Save user preferences and UI state
12. **Progressive Enhancement**: Core features work, optimizations enhance

---

## Key Architecture Decisions

**Why Database Migration First (Phase 1.1)?**
- Enables scaling to 10,000+ entities
- Full-text search without reading all files
- Proper indexing for fast filtering/sorting
- Transactions for data integrity
- Relational queries (find all stories with character X)
- Foundational for all future features

**Why CI/CD Before Features (Phase 1.5)?**
- Prevents regressions
- Enables safe, rapid iteration
- Automated testing catches bugs early
- Deployment automation reduces human error
- Code review improves quality

**Why Monitoring Early (Phase 2.2)?**
- Can't maintain what you can't measure
- Identify issues before users complain
- Track costs to avoid surprises
- Performance regression detection

**Why Local LLMs (Phase 2.1)?**
- Cost savings (no API fees)
- Privacy (sensitive data stays local)
- Offline capability
- Faster iteration during development
- Enables cheaper document Q&A

**Why Plugins (Phase 3.1)?**
- Domain-specific features without bloating core
- Community contributions possible
- Hot-reload during development
- Clear separation of concerns
- Board Game Assistant (Phase 4) validates the architecture

**Why Board Game Assistant as Phase 4 (Not Phase 2)?**
- Built on solid infrastructure (Phase 1-2)
- Uses plugin architecture (Phase 3)
- Uses local LLMs for cost savings (Phase 2.1)
- Safer to build complex feature after foundation is stable
- Validates plugin architecture works before domain expansion

**Why Document Q&A?**
- Validates RAG architecture for future features
- Solves real problem (rules questions during games)
- Foundation for teaching guides, FAQs, documentation
- Generic Q&A entity supports multiple contexts (documents, general, images, comparison)

---

## Notes

- **This roadmap supersedes**: All previous planning documents (v1.0 roadmap, DEVELOPMENT_PLAN.md, OPTIMIZATION_ROADMAP.md, ARCHITECTURE_IMPROVEMENTS.md, BOARD_GAME_TOOLS.md)
- **Keep as reference**: DESIGN_PATTERNS.md, README.md, CLAUDE.md, API_ARCHITECTURE.md
- **Historical**: Completed features documented in git history

**Version History**:
- v1.0 (2025-10-22): Initial consolidation
- v2.0 (2025-10-22): Reorganized for infrastructure-first approach

**Next Update**: After completing Phase 1 (Foundation), reassess priorities and timelines.
