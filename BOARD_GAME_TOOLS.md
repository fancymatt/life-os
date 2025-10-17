# Board Game Tools & Workflows for Life-OS

**Created**: 2025-10-16
**Updated**: 2025-10-16
**Status**: MVP in Planning
**Implementation Phase**: Phase 2 (Immediate Priority - 3-4 weeks)

---

## Vision

Transform Life-OS into a comprehensive board game companion that assists with **playing**, **discovering**, **teaching**, **analyzing**, and **designing** board games using AI-powered tools and the entity-centric architecture.

---

## MVP: Rules Assistant System (Phase 2 - Immediate Priority)

**Goal**: Create an intelligent rules assistant that can answer questions about board games using official rulebooks as sources.

**Timeline**: 3-4 weeks
**Effort**: 25-30 hours

### Why This MVP?

This focused approach:
1. **Solves a real problem**: Rules disputes and forgotten rules during gameplay
2. **Validates RAG architecture**: Tests document processing and Q&A system
3. **Builds foundation**: Infrastructure for teaching guides, FAQs, and more
4. **Quick value**: Immediately useful for game nights
5. **Iterative**: Each component can be improved independently
6. **Generic Q&A architecture**: Q&A entity designed to support multiple contexts (documents, general knowledge, images, comparisons) - not just chatting with documents

---

### MVP Components

#### 1. Board Game Rules Gatherer
**Tool**: `ai_tools/board_game_rules_gatherer/`

**Purpose**: Fetch and store official rulebooks from BoardGameGeek

**Functionality**:
- Input: Board game title or BGG ID
- Process:
  1. Search BGG for game (if title provided)
  2. Fetch game page HTML
  3. Extract rulebook PDF links (files section)
  4. Download PDFs (core rulebook, expansions, FAQs, player aids)
  5. Save to `data/board_games/{game_id}/rulebooks/`
  6. Store metadata (filename, version, language, source URL)
- Output: List of downloaded rulebook files

**Technical Details**:
```python
# ai_tools/board_game_rules_gatherer/tool.py
class BoardGameRulesGatherer:
    def gather_rules(self, game_title: str = None, bgg_id: int = None) -> RulebookSet:
        """
        Fetch all official rulebooks from BGG

        Returns:
            RulebookSet with downloaded PDF paths and metadata
        """
        # 1. Search BGG API for game
        # 2. Extract BGG ID
        # 3. Fetch game files page
        # 4. Parse PDF links (filter for rulebooks)
        # 5. Download PDFs with proper naming
        # 6. Return metadata
```

**BGG Integration**:
- **XML API**: `https://boardgamegeek.com/xmlapi2/thing?id={bgg_id}`
- **Files Page**: `https://boardgamegeek.com/boardgame/{bgg_id}/files`
- **Scraping**: BeautifulSoup for file links (no API for files)
- **Rate Limiting**: Respect BGG's rate limits (1 req/sec)

**File Structure**:
```
data/board_games/
└── wingspan-266192/
    ├── game.json              # Game metadata
    └── rulebooks/
        ├── wingspan-rulebook-v2.0-en.pdf
        ├── wingspan-european-expansion-v1.0-en.pdf
        ├── wingspan-faq-v1.2-en.pdf
        └── wingspan-player-aid-en.pdf
```

---

#### 2. Document RAG Preparer
**Tool**: `ai_tools/document_rag_preparer/`

**Purpose**: Convert PDF rulebooks into AI-queryable format using Docling

**Functionality**:
- Input: PDF file path
- Process:
  1. Convert PDF to structured markdown using Docling
  2. Extract sections, headings, tables, images
  3. Chunk text into semantically meaningful segments
  4. Generate embeddings for each chunk
  5. Store in vector database (ChromaDB or FAISS)
  6. Preserve section metadata (page number, heading hierarchy)
- Output: Searchable document index

**Technical Details**:
```python
# ai_tools/document_rag_preparer/tool.py
from docling import DocumentConverter

class DocumentRAGPreparer:
    def prepare_document(self, pdf_path: Path) -> DocumentIndex:
        """
        Convert PDF to RAG-ready format

        Steps:
        1. Docling: PDF → Markdown with structure
        2. Chunk text (semantic chunking, ~500 tokens)
        3. Generate embeddings (Gemini or local model)
        4. Store in vector DB
        5. Build metadata index (page, section, heading)

        Returns:
            DocumentIndex with vector DB path and metadata
        """
```

**Docling Integration**:
- **Library**: `pip install docling`
- **Features**:
  - PDF → Markdown conversion
  - Preserves document structure (headings, lists, tables)
  - Extracts images with context
  - Handles multi-column layouts
- **Output**: Clean markdown with metadata

**Chunking Strategy**:
- **Semantic Chunking**: Split by sections/subsections
- **Size**: ~500 tokens per chunk (balance context vs precision)
- **Overlap**: 50 tokens overlap between chunks
- **Metadata**: Each chunk tagged with:
  - Page number
  - Section heading
  - Subsection heading
  - Chunk index

**Vector Database**:
- **Option 1**: ChromaDB (simple, local, persistent)
- **Option 2**: FAISS (faster, more scalable)
- **Embeddings**: Gemini embedding API or local model
- **Storage**: `data/board_games/{game_id}/vector_db/`

**File Structure**:
```
data/board_games/wingspan-266192/
├── game.json
├── rulebooks/
│   └── wingspan-rulebook-v2.0-en.pdf
├── processed/
│   └── wingspan-rulebook-v2.0-en.md     # Docling output
└── vector_db/
    ├── chroma/                           # Vector database
    └── metadata.json                     # Chunk metadata
```

---

#### 3. Document Q&A
**Tool**: `ai_tools/document_qa/`

**Purpose**: Answer questions using prepared rulebooks or general knowledge

**Functionality**:
- Input: Question + optional Game ID + optional Document IDs
- Process:
  1. **If document-grounded** (game ID provided):
     - Load game's vector database
     - Generate embedding for question
     - Semantic search for relevant chunks (top 5-10)
     - Build context from chunks
     - Send to LLM with prompt: "Answer using only these rulebook excerpts"
     - Parse response and extract citations
  2. **If general knowledge** (no game ID):
     - Send question directly to LLM
     - No citation requirements
     - Mark as general knowledge answer
  3. Save Q&A to database
- Output: Answer with optional citations (page numbers, sections)

**Technical Details**:
```python
# ai_tools/document_qa/tool.py
class DocumentQA:
    def ask_question(
        self,
        question: str,
        game_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        context_type: str = "document"  # "document" | "general" | "image" | "comparison"
    ) -> QAResponse:
        """
        Answer question with optional document grounding

        Args:
            question: The question to answer
            game_id: Optional game to search within
            document_ids: Optional specific documents to search
            context_type: Type of Q&A (document, general, image, comparison)

        Returns:
            QAResponse with answer and optional citations
        """
        # 1. Determine answer strategy based on context_type
        # 2. If document-grounded: semantic search + RAG
        # 3. If general: direct LLM query
        # 4. If image: vision model analysis (future)
        # 5. If comparison: multi-document search (future)
        # 6. Save Q&A with context metadata
```

**LLM Prompt Template**:
```
You are a board game rules expert. Answer the following question using ONLY the rulebook excerpts provided below.

CRITICAL RULES:
1. ONLY use information from the excerpts
2. ALWAYS cite the page number and section for each statement
3. If the answer is not in the excerpts, say "I don't see this in the rulebook"
4. Quote exact text when possible
5. If there are multiple interpretations, present both

Question: {question}

Rulebook Excerpts:
[Chunk 1 - Page 5, Section "Setup"]
{chunk_1_text}

[Chunk 2 - Page 12, Section "Turn Actions"]
{chunk_2_text}

Answer format:
- Direct answer first
- Supporting quotes with citations: (Page X, Section Y)
- Uncertainty indicators if applicable
```

**Citation Format**:
```json
{
  "answer": "You draw 2 bird cards from the deck...",
  "citations": [
    {
      "text": "Draw 2 bird cards from the deck",
      "page": 5,
      "section": "Setup",
      "chunk_id": "wingspan-chunk-12"
    }
  ],
  "confidence": 0.95,
  "sources": ["wingspan-rulebook-v2.0-en.pdf"]
}
```

---

### Q&A System Architecture (Generic & Extensible)

The Q&A entity is designed as a **generic, reusable component** that works across multiple contexts - not just document-based questions. This architectural decision enables future expansion without redesigning the data model.

**MVP Focus** (Phase 2): Document-grounded Q&A
- Questions answered using rulebook excerpts
- Citations with page numbers and sections
- High confidence answers from source material

**Future Expansion** (Post-MVP):

1. **General Knowledge Q&A**
   - "What is worker placement?" (no game context)
   - No citations required
   - Useful for learning game design concepts

2. **Image-Based Q&A**
   - "How many meeples are in this photo?"
   - "What game is this?"
   - Uses vision models (Gemini 2.0 Flash)
   - References image_ids instead of document_ids

3. **Comparison Q&A**
   - "How is worker placement different in Agricola vs Stone Age?"
   - Multi-document search across multiple rulebooks
   - Cross-game citations

4. **Hybrid Q&A**
   - Combines document context with general knowledge
   - "Why is this rule designed this way?" (rules + design theory)
   - Uses both RAG and general LLM knowledge

**Key Benefits of Generic Architecture**:
- ✅ Single Q&A entity handles all question types
- ✅ Consistent UI for all question-answer interactions
- ✅ Favorites, tags, notes work across all Q&A types
- ✅ Easy to filter (show only document Q&A, only general, etc.)
- ✅ Future-proof for new question types (audio, video, etc.)

---

### MVP Entities

#### Board Game Entity
```json
{
  "game_id": "wingspan-266192",
  "name": "Wingspan",
  "bgg_id": 266192,
  "designer": "Elizabeth Hargrave",
  "publisher": "Stonemaier Games",
  "year": 2019,
  "description": "...",
  "box_art_url": "https://cf.geekdo-images.com/...",
  "player_count": [1, 2, 3, 4, 5],
  "playtime_min": 40,
  "playtime_max": 70,
  "complexity": 2.4,
  "rulebooks": [
    {
      "filename": "wingspan-rulebook-v2.0-en.pdf",
      "version": "2.0",
      "language": "en",
      "type": "Core Rulebook",
      "source_url": "https://boardgamegeek.com/...",
      "downloaded_at": "2025-10-16T10:30:00Z",
      "processed": true,
      "vector_db_path": "data/board_games/wingspan-266192/vector_db/"
    }
  ],
  "qa_count": 15,
  "created_at": "2025-10-16T10:00:00Z",
  "updated_at": "2025-10-16T10:30:00Z"
}
```

#### Document Entity
```json
{
  "document_id": "wingspan-rulebook-v2.0-en",
  "game_id": "wingspan-266192",
  "filename": "wingspan-rulebook-v2.0-en.pdf",
  "type": "rulebook",
  "version": "2.0",
  "language": "en",
  "page_count": 20,
  "file_size_bytes": 5242880,
  "source_url": "https://boardgamegeek.com/filepage/178923",
  "downloaded_at": "2025-10-16T10:30:00Z",
  "processed_at": "2025-10-16T10:35:00Z",
  "processed_status": "success",
  "markdown_path": "data/board_games/wingspan-266192/processed/wingspan-rulebook-v2.0-en.md",
  "vector_db_path": "data/board_games/wingspan-266192/vector_db/",
  "chunk_count": 87,
  "embedding_model": "gemini-embedding-001"
}
```

#### Q&A Entity
**Purpose**: Generic question-answer pairs for any context (documents, general knowledge, images, comparisons)

```json
{
  "qa_id": "uuid",
  "question": "How many bird cards do you draw during setup?",
  "answer": "Each player draws 5 bird cards from the deck during setup. You will keep all 5 cards.",

  // Context (flexible - can be null for general questions)
  "context_type": "document",  // "document" | "general" | "image" | "comparison" | "custom"
  "game_id": "wingspan-266192",  // Optional: associated game
  "document_ids": ["wingspan-rulebook-v2.0-en"],  // Optional: source documents
  "image_ids": [],  // Optional: analyzed images (future)

  // Citations (only for document-grounded Q&A)
  "citations": [
    {
      "text": "Each player draws 5 bird cards",
      "page": 5,
      "section": "Setup - Step 4",
      "chunk_id": "wingspan-chunk-12",
      "document_id": "wingspan-rulebook-v2.0-en"
    }
  ],

  // Metadata
  "confidence": 0.98,
  "asked_at": "2025-10-16T20:15:00Z",
  "asked_by": "user-id",  // Optional: user tracking

  // User organization
  "is_favorite": false,
  "tags": ["setup", "cards"],
  "custom_tags": [],  // User-defined tags

  // Community features
  "upvotes": 0,
  "downvotes": 0,
  "was_helpful": null,  // true | false | null
  "user_notes": "",  // Personal notes on this Q&A

  // Relationships
  "related_questions": ["qa-uuid-2", "qa-uuid-5"],
  "parent_qa_id": null,  // For follow-up questions

  // System
  "created_at": "2025-10-16T20:15:00Z",
  "updated_at": "2025-10-16T20:15:00Z"
}
```

**Example Use Cases**:

1. **Document-grounded** (MVP):
```json
{
  "question": "How many eggs do you start with?",
  "context_type": "document",
  "game_id": "wingspan-266192",
  "citations": [...]
}
```

2. **General knowledge**:
```json
{
  "question": "What is worker placement?",
  "context_type": "general",
  "game_id": null,
  "citations": []
}
```

3. **Image analysis** (future):
```json
{
  "question": "How many meeples are in this photo?",
  "context_type": "image",
  "game_id": "carcassonne-822",
  "image_ids": ["img-uuid"],
  "citations": []
}
```

4. **Game comparison** (future):
```json
{
  "question": "How is worker placement different in Agricola vs Stone Age?",
  "context_type": "comparison",
  "game_id": null,
  "document_ids": ["agricola-rulebook", "stone-age-rulebook"],
  "citations": [...]
}
```

---

### MVP Workflows

#### Workflow 1: Add New Game to System
**User Action**: "Add Wingspan to my collection"

**Steps**:
1. **User Input**: Game title ("Wingspan") or BGG ID (266192)
2. **Rules Gatherer**:
   - Search BGG for "Wingspan"
   - Find BGG ID: 266192
   - Fetch game metadata
   - Download 4 rulebook PDFs
   - Create game entity
3. **Document Preparer**: (Background job)
   - Convert each PDF to markdown (Docling)
   - Chunk text semantically
   - Generate embeddings
   - Build vector database
   - Update game entity (processed: true)
4. **User Notification**: "Wingspan ready! Ask me anything about the rules."

**UI**:
- Form: "Add Board Game" (text input + search button)
- Loading state: "Downloading rulebooks... (2/4)"
- Processing state: "Preparing rulebooks for search... (45%)"
- Success: "Wingspan added! 4 rulebooks processed, 342 chunks indexed"

---

#### Workflow 2: Ask Rules Question
**User Action**: "How many eggs do you start with in Wingspan?"

**Steps**:
1. **User Input**: Question + select game (Wingspan)
2. **Document Q&A**:
   - Detect context_type: "document" (game selected)
   - Generate question embedding
   - Search vector DB for relevant chunks
   - Retrieve top 5 chunks (pages 5, 6, 9)
   - Build context for LLM
   - Send prompt to Gemini with citation requirements
   - Parse response with citations
3. **Save Q&A**: Store question, answer, citations, context_type="document"
4. **Display Answer**:
   - "You don't start with any eggs. You gain eggs by taking the 'Lay Eggs' action during your turn. (Page 9, Section 'Actions')"
   - Show citations as expandable sections
   - "Was this helpful?" feedback buttons
   - "Favorite" button

**UI**:
```
┌─────────────────────────────────────────────┐
│ Wingspan Rules Assistant                    │
├─────────────────────────────────────────────┤
│                                             │
│ Q: How many eggs do you start with?        │
│                                             │
│ A: You don't start with any eggs. You      │
│    gain eggs by taking the 'Lay Eggs'      │
│    action during your turn.                 │
│                                             │
│ 📖 Sources:                                 │
│    └─ Wingspan Rulebook v2.0, Page 9       │
│       Section: "Actions - Lay Eggs"         │
│       "Take 2 eggs from the supply and      │
│        place them on any birds..."          │
│                                             │
│ Was this helpful? 👍 👎  ⭐ Favorite       │
└─────────────────────────────────────────────┘
```

---

#### Workflow 3: Browse Previous Q&As
**User Action**: Navigate to game detail page

**UI**:
```
┌──────────────────────────────────────────────────┐
│ Wingspan                                         │
├──────────────────────────────────────────────────┤
│ [Box Art]  Designer: Elizabeth Hargrave          │
│            Players: 1-5 | Time: 40-70 min        │
│            Complexity: 2.4/5                     │
│                                                  │
│ 📚 Rulebooks (4)                                 │
│    ✓ Core Rulebook v2.0 (20 pages)              │
│    ✓ European Expansion v1.0 (8 pages)          │
│    ✓ FAQ v1.2 (6 pages)                         │
│    ✓ Player Aid (2 pages)                       │
│                                                  │
│ ❓ Questions (15) [Filter: All | Favorites]      │
│                                                  │
│ ⭐ How many eggs do you start with?              │
│    Asked 3 days ago | 5 upvotes                 │
│                                                  │
│ ⭐ When do bird powers activate?                 │
│    Asked 5 days ago | 3 upvotes                 │
│                                                  │
│ Can you discard eggs to gain food?              │
│    Asked 1 week ago | 1 upvote                  │
│                                                  │
│ [+ Ask New Question]                             │
└──────────────────────────────────────────────────┘
```

---

### MVP Implementation Plan

#### Week 1: Infrastructure & Rules Gatherer (8-10 hours)
**Backend**:
- [ ] Board game entity model (`api/models/board_game.py`)
- [ ] Document entity model (`api/models/document.py`)
- [ ] Q&A entity model (`api/models/qa.py`)
- [ ] Board game service (`api/services/board_game_service.py`)
- [ ] BGG integration service (`api/services/bgg_service.py`)
- [ ] Rules gatherer tool (`ai_tools/board_game_rules_gatherer/`)
- [ ] Routes: `/api/board-games` (CRUD)
- [ ] Route: `/api/board-games/{id}/gather-rules` (POST)

**Testing**:
- [ ] Test BGG search and metadata fetch
- [ ] Test PDF download from BGG files
- [ ] Test with 3 different games (simple, medium, complex)

**Deliverable**: Can add a game and download its rulebooks

---

#### Week 2: RAG Preparation (10-12 hours)
**Backend**:
- [ ] Install and configure Docling
- [ ] Document RAG preparer tool (`ai_tools/document_rag_preparer/`)
- [ ] ChromaDB setup and integration
- [ ] Chunking strategy implementation
- [ ] Embedding generation (Gemini API)
- [ ] Background job for document processing
- [ ] Route: `/api/board-games/{id}/process-rules` (POST)
- [ ] Route: `/api/board-games/{id}/processing-status` (GET)

**Testing**:
- [ ] Test Docling PDF → Markdown conversion
- [ ] Test chunking quality (manual review)
- [ ] Test embedding generation
- [ ] Test vector search (similarity queries)

**Deliverable**: Rulebooks converted to searchable format

---

#### Week 3: Document Q&A (6-8 hours)
**Backend**:
- [ ] Document Q&A tool (`ai_tools/document_qa/`)
- [ ] Q&A service (`api/services/qa_service.py`)
- [ ] Context type detection (document vs general)
- [ ] LLM prompt engineering (citation requirements for document-grounded)
- [ ] Citation parsing and validation
- [ ] Routes:
  - `/api/qa/ask` (POST) - Ask question (generic, can specify game_id)
  - `/api/board-games/{id}/qa` (GET) - List Q&As for a game
  - `/api/qa` (GET) - List all Q&As (filterable by context_type, game_id, tags)
  - `/api/qa/{id}` (GET) - Get specific Q&A
  - `/api/qa/{id}` (PUT) - Update (favorite, feedback, tags, notes)
  - `/api/qa/{id}` (DELETE) - Delete Q&A

**Testing**:
- [ ] Test with 20 document-grounded questions per game
- [ ] Test 10 general knowledge questions (no game context)
- [ ] Verify citation accuracy for document Q&A (manual review)
- [ ] Test edge cases (ambiguous questions, not in rulebook)
- [ ] Test follow-up questions (parent_qa_id linking)

**Deliverable**: Working Q&A system supporting both document-grounded and general questions

---

#### Week 4: Frontend & Polish (6-8 hours)
**Frontend**:
- [ ] Board game entity browser (`/board-games`)
- [ ] Add game modal (search BGG, select, add)
- [ ] Game detail page (`/board-games/{id}`)
  - Metadata display
  - Rulebook list with processing status
  - Q&A list (with favorites, filters)
  - Ask question interface
- [ ] Q&A display component (answer + expandable citations)
- [ ] Feedback buttons (helpful, favorite)

**Polish**:
- [ ] Loading states for all async operations
- [ ] Error handling (BGG down, PDF download failed, etc.)
- [ ] Success notifications
- [ ] Keyboard shortcuts (Cmd+K to focus question input)
- [ ] Mobile responsive design

**Testing**:
- [ ] End-to-end test: Add game → Process → Ask questions
- [ ] Test with real game night scenario
- [ ] Gather feedback from 2-3 users

**Deliverable**: Fully functional MVP ready for use

---

### Future Enhancements (Post-MVP)

#### Auto-Generated Common Questions
- Analyze rulebook structure
- Identify commonly confused rules (complex timing, exceptions)
- Generate 10-20 common questions per game
- Pre-compute answers and store as Q&As
- Display as "Common Questions" in game detail

#### Tricky Rules Detector
- LLM analyzes rulebook
- Identifies rules with:
  - Many exceptions or edge cases
  - Complex timing/sequencing
  - Contradictions or ambiguities
  - BGG forum discussion frequency (via BGG forum scraping)
- Flags these in game detail with warnings

#### Teaching Guide Integration
- Use Q&As to identify what's confusing
- Auto-generate teaching guide sections addressing common questions
- "New players often ask about X" callouts
- Build FAQ section in teaching guide from top Q&As

#### Multi-Game Context
- "How is worker placement different in Agricola vs Stone Age?"
- Compare mechanics across games
- Cross-game citation and comparison

#### Voice Interface
- "Alexa, ask Wingspan rules how eggs work"
- Voice-to-text → Document chat → Text-to-speech
- Great for during-game questions (hands-free)

---

### Technical Stack Summary

**Backend**:
- Python 3.9+
- FastAPI (routes)
- Docling (PDF → Markdown)
- ChromaDB or FAISS (vector database)
- Gemini API (embeddings + LLM)
- BeautifulSoup (BGG scraping)
- aiohttp (async HTTP for BGG API)

**Frontend**:
- React 18.2
- Vite 5.0
- Markdown renderer (for answers)
- Syntax highlighting (for rulebook quotes)

**Storage**:
```
data/board_games/
└── {game_slug}-{bgg_id}/
    ├── game.json              # Game metadata
    ├── rulebooks/             # Original PDFs
    ├── processed/             # Docling markdown
    └── vector_db/             # ChromaDB index
```

---

### Success Metrics (MVP)

**Adoption**:
- [ ] 10+ games added to system
- [ ] 50+ questions asked
- [ ] 10+ favorited Q&As

**Quality**:
- [ ] 90%+ citation accuracy (manual review of 50 Q&As)
- [ ] 80%+ "helpful" rating from users
- [ ] <5 second response time per question

**Technical**:
- [ ] 95%+ uptime
- [ ] <100MB storage per game (vector DB)
- [ ] Successful processing of all tested games

---

### Risks & Mitigations (MVP)

#### Risk 1: BGG Rate Limits / Blocking
**Mitigation**:
- Respect 1 req/sec limit
- Add User-Agent header
- Cache aggressively
- Manual PDF upload fallback

#### Risk 2: PDF Download Failures
**Mitigation**:
- Retry logic (3 attempts)
- Manual upload option
- Clear error messages

#### Risk 3: Docling Conversion Quality
**Mitigation**:
- Test with diverse rulebooks (simple, complex, multi-column)
- Manual markdown editing option
- Fallback to OCR if Docling fails

#### Risk 4: LLM Hallucination (Wrong Citations)
**Mitigation**:
- Strict prompt engineering (citation requirements)
- Confidence scores
- "Verify in rulebook" warnings
- User feedback loop (downvote wrong answers)

#### Risk 5: Vector Search Misses Relevant Chunks
**Mitigation**:
- Tuning chunk size (test 300, 500, 700 tokens)
- Increase top-k chunks (test 5, 10, 15)
- Hybrid search (semantic + keyword)
- Manual review of search quality

---

### Example Games for Testing

**Simple** (Quick setup validation):
- Sushi Go! - 2-page rulebook
- Love Letter - 1-page rulebook

**Medium** (Typical case):
- Wingspan - 20-page rulebook + expansions
- Ticket to Ride - 12-page rulebook

**Complex** (Stress test):
- Twilight Imperium 4th Edition - 32-page rulebook + reference
- Spirit Island - 24-page rulebook + extensive FAQ

---

## Core Principles

1. **Entity-Centric Design**: Games, mechanics, sessions, players are all first-class entities
2. **Multi-Modal AI**: Use vision models to analyze game components, rulebooks, board states
3. **Knowledge Graph**: Build relationships between games, mechanics, designers, themes
4. **Community Integration**: Connect with BoardGameGeek, import collections, sync ratings
5. **Designer-Friendly**: Tools for both players and game designers

---

## Full Feature Set (Long-Term Vision)

## Use Case 1: Playing Board Games

### Problem
- Hard to remember rules between sessions
- Complex scoring systems require calculators
- Forgetting where you left off in campaign games
- Rules disputes during gameplay
- Tracking stats across many plays

### Solutions

#### Entities
**Game Sessions**
```json
{
  "session_id": "uuid",
  "game_id": "game-uuid",
  "date": "2025-10-16",
  "players": ["Alice", "Bob", "Charlie"],
  "scores": {"Alice": 87, "Bob": 92, "Charlie": 78},
  "winner": "Bob",
  "duration_minutes": 120,
  "photos": ["setup.jpg", "midgame.jpg", "final_state.jpg"],
  "notes": "First time playing with expansion",
  "location": "Home",
  "campaign_progress": {
    "chapter": 3,
    "unlocked_components": ["blue_deck", "advanced_tiles"]
  }
}
```

**Players**
```json
{
  "player_id": "uuid",
  "name": "Alice",
  "favorite_games": ["game-1", "game-2"],
  "play_style": "Competitive",
  "preferences": {
    "complexity": "Medium-Heavy",
    "player_count": "3-4",
    "duration": "90-120 min",
    "mechanics": ["Engine Building", "Worker Placement"]
  },
  "stats": {
    "games_played": 156,
    "win_rate": 0.42,
    "favorite_mechanic": "Deck Building"
  }
}
```

#### Tools

**🎲 Session Logger**
- Quick session entry with photo upload
- Auto-score calculator using OCR (photo of score track)
- Stats dashboard (win rate by game, favorite games, etc.)
- Play history timeline
- "What should we play next?" recommender based on past sessions

**📸 Game State Analyzer**
- Take photo of board state
- AI describes current game state in text
- "Resume game" helper (explains whose turn, what happened last)
- Campaign progress tracker (automatically detects unlocked content)

**📖 Rules Assistant (Chat Interface)**
- "How does X work in [Game Name]?"
- Context-aware: knows which game you're playing
- Cites rulebook page numbers
- Common rules mistakes database
- House rules storage per game

**⏱️ Game Timer & Turn Tracker**
- Configurable timers (per turn, per player, total game)
- Turn order visualization
- "Whose turn?" indicator
- Alerts when game is taking longer than expected

**🧮 Score Calculator**
- Game-specific calculators (Agricola, Terraforming Mars, etc.)
- Photo-based scoring (point tokens, score tracks)
- Real-time score updates during game
- Export final scores to session log

---

## Use Case 2: Discovering Board Games

### Problem
- Overwhelming choice (150,000+ games on BGG)
- Hard to find games that match group preferences
- Don't know what's in your own collection
- Miss great games because of poor discovery

### Solutions

#### Entities

**Games**
```json
{
  "game_id": "uuid",
  "name": "Wingspan",
  "year": 2019,
  "designer": "Elizabeth Hargrave",
  "publisher": "Stonemaier Games",
  "bgg_id": 266192,
  "player_count": [1, 2, 3, 4, 5],
  "best_player_count": 3,
  "playtime_min": 40,
  "playtime_max": 70,
  "complexity": 2.4,
  "mechanics": ["Hand Management", "Set Collection", "Engine Building"],
  "themes": ["Animals", "Nature"],
  "categories": ["Strategy", "Card Game"],
  "description": "...",
  "box_art_url": "...",
  "rulebook_pdf": "...",
  "ownership_status": "Owned",
  "purchase_date": "2020-03-15",
  "purchase_price": 55.00,
  "current_value": 45.00,
  "location": "Shelf B3",
  "play_count": 23,
  "rating": 8.5,
  "tags": ["Favorite", "Easy to Teach"]
}
```

**Game Mechanics**
```json
{
  "mechanic_id": "uuid",
  "name": "Worker Placement",
  "aliases": ["Worker Placement", "Action Drafting"],
  "description": "Players take turns placing workers on action spaces...",
  "complexity_factor": 3,
  "interaction_level": "High",
  "examples": ["Agricola", "Stone Age", "Lords of Waterdeep"],
  "parent_mechanic": "Action Selection",
  "sub_mechanics": ["Blocked Action Spaces", "Worker Placement with Dice"],
  "commonly_paired_with": ["Resource Management", "Set Collection"],
  "invented_year": 1982,
  "popularized_by": "Caylus (2005)"
}
```

#### Tools

**🔍 Game Recommender**
- "What should we play tonight?"
  - Inputs: Player count, time available, complexity preference
  - Output: Ranked list from your collection + suggestions to buy
- "Games like X" (similarity search)
- "Mechanics I haven't tried" discovery
- "Hidden gems" finder (underrated games in collection)
- Player preference matcher (find games everyone will enjoy)

**📚 Collection Manager**
- Import from BoardGameGeek
- Barcode scanner for quick entry
- Shelf location tracker ("Where did I put Gloomhaven?")
- Value tracker (purchase price vs current market value)
- Play frequency analysis (games collecting dust)
- "Should I sell this?" advisor

**🎯 Game Night Planner**
- "I have 4 players for 2 hours" → suggests games
- Player preference aggregator (everyone votes)
- Multiple games suggestion (warm-up + main + filler)
- Rotation tracker (ensures variety over time)
- "Never played" games highlighter

**📊 Collection Analyzer**
- Mechanics distribution (pie chart)
- Designer diversity
- Gap analysis ("You don't own any auction games")
- Redundancy detector ("You have 5 deck builders")
- Cost per play calculator
- BGG rating comparison (your collection vs top 100)

**🛒 Wishlist Manager**
- Price tracking (alert when game goes on sale)
- Priority ranking
- "You might like based on collection" suggestions
- Crowdfunding tracker (Kickstarter alerts)
- Availability checker (in stock at local stores)

---

## Use Case 3: Teaching Board Games

### Problem
- Rules explanations are overwhelming for new players
- Hard to remember all rules when teaching
- New players feel lost and don't enjoy first play
- Difficulty balancing completeness vs simplicity

### Solutions

#### Entities

**Teaching Guides**
```json
{
  "guide_id": "uuid",
  "game_id": "game-uuid",
  "teaching_style": "Bottom-Up", // vs Top-Down
  "target_audience": "Beginners",
  "duration_minutes": 15,
  "sections": [
    {
      "order": 1,
      "title": "Game Overview",
      "content": "In Wingspan, you're bird enthusiasts...",
      "duration_minutes": 2,
      "visual_aids": ["box_art.jpg"],
      "key_points": ["Goal: Most points wins", "Play birds, get points"]
    },
    {
      "order": 2,
      "title": "Core Actions",
      "content": "On your turn, you'll do one of four actions...",
      "duration_minutes": 5,
      "visual_aids": ["player_mat.jpg"],
      "key_points": ["Play a bird", "Gain food", "Lay eggs", "Draw cards"],
      "common_mistakes": ["Forgetting to activate bird powers"]
    }
  ],
  "first_game_simplifications": [
    "Skip bonus cards in first game",
    "Use only the green bird powers"
  ],
  "rules_to_skip_until_needed": [
    "Egg-laying powers",
    "Bonus card scoring"
  ]
}
```

**Quick Reference Cards**
```json
{
  "reference_card_id": "uuid",
  "game_id": "game-uuid",
  "card_type": "Player Aid",
  "layout": "Double-sided",
  "front_content": {
    "title": "Turn Summary",
    "sections": [
      {"heading": "1. Choose Action", "bullets": ["Play Bird", "Gain Food", "..."]}
    ]
  },
  "back_content": {
    "title": "End Game Scoring",
    "sections": [...]
  },
  "target_audience": "First-time players",
  "print_size": "Poker card"
}
```

#### Tools

**📖 Teaching Guide Generator**
- Input: Game rulebook (PDF or OCR from photos)
- Output: Step-by-step teaching script
- Configurable:
  - Teaching style (top-down overview vs bottom-up mechanics)
  - Audience (new to gaming vs experienced)
  - Time available (5 min quick vs 20 min thorough)
- Includes suggested first-turn example
- Highlights common mistakes to warn about

**🎴 Quick Reference Card Generator**
- Auto-extracts key info from rulebook
- Generates print-ready PDFs
- Templates: Player aids, turn summaries, scoring references
- Multi-language support
- Icons and visual hierarchy

**🎬 Teaching Video Script Generator**
- Generates script for teaching video
- Suggests shots/angles for each section
- Timeline with duration targets
- Component close-up callouts
- "Watch It Played" style formatting

**🖼️ Visual Component Guide Generator**
- Photos of components with labels
- Setup diagram generator (overhead photo → labeled diagram)
- "What is this token?" quick reference
- Component count checker (ensuring all pieces present)

**🎓 First-Game Simplifier**
- Analyzes rulebook complexity
- Suggests rules to omit in first game
- Generates simplified player aids
- "Full rules" reminder list (for game 2)
- Difficulty progression path (games 1-5)

**❓ Common Questions Database**
- Crowdsourced FAQ per game
- "Wait, how does X work again?" quick lookup
- Rules disputes resolver (official rulings)
- Edge case explanations
- Timing clarifications ("When exactly does this trigger?")

---

## Use Case 4: Categorizing & Studying Mechanics

### Problem
- Hard to understand what makes games similar/different
- No systematic way to learn game design patterns
- Mechanic taxonomy is messy and inconsistent
- Can't easily find examples of specific mechanics

### Solutions

#### Entities

**Mechanic Taxonomy**
```json
{
  "taxonomy_id": "uuid",
  "name": "Worker Placement",
  "level": "Primary Mechanic",
  "category": "Action Selection",
  "description": "Players take turns placing meeples on action spaces to claim those actions",
  "formal_definition": "...",
  "aliases": ["Worker Placement", "Action Claiming"],
  "characteristics": {
    "player_interaction": "High",
    "decision_complexity": "Medium-High",
    "learning_curve": "Medium",
    "luck_factor": "Low",
    "analysis_paralysis_risk": "High"
  },
  "sub_types": [
    "Worker Placement with Dice",
    "Blocked Action Spaces",
    "Variable Action Spaces"
  ],
  "parent_mechanics": ["Action Selection"],
  "commonly_combined_with": [
    "Resource Management",
    "Set Collection",
    "Engine Building"
  ],
  "invented_by": "Unknown",
  "first_major_game": "Keydom (1998)",
  "popularized_by": "Caylus (2005)",
  "evolution_timeline": [...],
  "example_games": [
    {"game": "Agricola", "implementation_notes": "Multiple spaces, family growth"},
    {"game": "Stone Age", "implementation_notes": "Dice determine output"}
  ]
}
```

#### Tools

**🔬 Mechanic Analyzer**
- Input: Rulebook or game description
- Output: List of mechanics with confidence scores
- Explains how each mechanic is implemented
- Identifies unique twists on standard mechanics
- Suggests mechanic tags for cataloging

**📊 Mechanic Browser**
- Visual taxonomy tree (collapsible hierarchy)
- Filter by characteristics (interaction level, complexity, etc.)
- "Show me all engine building games"
- Mechanic combination explorer (2D matrix)
- Historical evolution view (mechanics over time)

**🎓 Mechanic Deep Dive Generator**
- Input: Mechanic name
- Output: Comprehensive article covering:
  - Formal definition
  - Historical context
  - Canonical examples
  - Common implementations
  - Design considerations
  - Common pitfalls
  - Notable innovations
  - Pairing suggestions

**🔗 Mechanic Relationship Mapper**
- Visual graph of mechanic relationships
- "Games that combine X and Y" finder
- Mechanic compatibility scorer
- Underexplored combinations suggester
- "This mechanic usually pairs with..." insights

**📚 Mechanic Study Guide**
- Curated learning path through mechanics
- "Mechanic of the Week" deep dives
- Quiz yourself on mechanic identification
- "Spot the mechanic" from game photos
- Designer patterns recognition exercises

---

## Use Case 5: Designing Game Mechanics

### Problem
- Hard to come up with novel mechanic combinations
- Don't know if idea has been done before
- Difficult to balance mechanics mathematically
- Need playtest feedback analysis
- Struggle to match mechanics to theme

### Solutions

#### Entities

**Game Prototypes**
```json
{
  "prototype_id": "uuid",
  "name": "Project Firefly (working title)",
  "designer": "user-id",
  "status": "Playtesting",
  "version": "0.8",
  "core_mechanics": ["Deck Building", "Area Control"],
  "theme": "Firefly wrangling in a magical forest",
  "player_count": [2, 3, 4],
  "target_playtime": 45,
  "target_complexity": 2.5,
  "design_goals": [
    "Fast-paced deck builder",
    "Meaningful player interaction",
    "Beautiful table presence"
  ],
  "current_challenges": [
    "Runaway leader problem in late game",
    "First player advantage too strong"
  ],
  "playtests": [
    {
      "date": "2025-10-10",
      "players": 4,
      "feedback": "...",
      "issues": ["Game too long", "Combat confusing"],
      "successes": ["Theme came through", "Deck building felt good"]
    }
  ],
  "components": {
    "cards": 120,
    "tokens": 50,
    "board": "Modular tiles"
  }
}
```

**Mechanic Combinations**
```json
{
  "combination_id": "uuid",
  "mechanics": ["Deck Building", "Area Control"],
  "synergy_score": 8.5,
  "examples": ["Tyrants of the Underdark", "Dune: Imperium"],
  "design_notes": "Deck building drives area control actions",
  "common_implementation": "Cards provide area control actions or influence",
  "pitfalls": "Can feel like two games stapled together if not integrated well",
  "innovation_opportunities": [
    "Area control affects deck building options",
    "Territory provides card draw/filtering"
  ]
}
```

#### Tools

**💡 Mechanic Brainstorming Assistant**
- "I want to make a game about X theme" → mechanic suggestions
- "What mechanics haven't been combined yet?" (gap finder)
- "Twist on X mechanic" generator
- "Make X mechanic more interesting" suggester
- Random mechanic combination generator (with synergy analysis)

**🎯 Theme-Mechanic Matcher**
- Input: Theme (e.g., "Space exploration")
- Output: Mechanics that naturally fit the theme
- Explains thematic connection
- Example implementations from existing games
- "Surprising but effective" unusual pairings

**⚖️ Balance Calculator**
- Input: Game parameters (actions, costs, payoffs)
- Output: Mathematical balance analysis
- Expected value calculations
- Nash equilibrium solver (simple cases)
- Strategy dominance checker
- Cost curve visualizations

**🧪 Playtesting Feedback Analyzer**
- Input: Playtest notes (text or audio transcription)
- Output: Structured feedback summary
  - Positive themes (what's working)
  - Issues by severity
  - Suggested fixes
  - Blind spot detection (issues mentioned by multiple testers)
- Tracks feedback across versions (progress over time)

**🃏 Prototype Component Generator**
- Generate print-and-play PDFs
- Card layouts from templates
- Token designs
- Board tiles
- Quick reference cards
- Version control (auto-labels cards with version number)

**📐 Game Math Assistant**
- "How many cards should I include?" (deck composition advisor)
- "What should this cost?" (pricing suggester based on power level)
- "How long will my game take?" (duration estimator)
- "Is first player advantage too strong?" (turn order analyzer)
- Resource economy simulator

**🔄 Iteration Tracker**
- Version history (what changed in each version)
- A/B testing tracker (which variant worked better)
- Feedback trend analysis (improving or getting worse?)
- Change impact analyzer ("This change fixed X but broke Y")

---

## Workflow Examples

### Workflow 1: New Game Night
**Goal**: Pick the perfect game for tonight's group

**Steps**:
1. **Input Group Info**
   - Players: Alice, Bob, Charlie, Dana
   - Time available: 90 minutes
   - Complexity: Medium (Dana is new to modern games)

2. **AI Recommendation**
   - Analyzes each player's preferences from past sessions
   - Filters collection by time and complexity
   - Scores games by predicted group enjoyment
   - Suggests: "Wingspan" (87% match score)
   - Reasoning: "Everyone rated medium complexity games highly, Alice loves engine builders, good for teaching Dana"

3. **Teaching Preparation**
   - Generates 10-minute teaching script for Wingspan
   - Identifies that Dana is new → suggests skipping bonus cards first game
   - Creates quick reference card focused on core actions
   - Suggests YouTube teaching video (if available)

4. **During Game**
   - Rules Assistant available for questions
   - Turn tracker shows turn order
   - Score calculator ready for end game

5. **Post-Game**
   - Quick session log (photo of final board, scores from OCR)
   - "How was it?" rating for each player
   - Updates recommendation engine with new data

### Workflow 2: Teaching a Heavy Game
**Goal**: Teach "Twilight Imperium" to 5 players (3 new to the game)

**Steps**:
1. **Generate Teaching Materials** (1 week before)
   - Teaching guide generator creates 45-minute script
   - Breaks into sections: Setup (10m), Core Turn (15m), Combat (10m), Objectives (5m), Strategy Cards (5m)
   - Identifies rules to save for later ("Save Agenda Phase for round 2")
   - Creates player reference cards (1-page turn summary)

2. **Visual Aids**
   - Component guide with photos (What is this plastic piece?)
   - Setup diagram (overhead photo with annotations)
   - Board geography overview (regions, key systems)

3. **Pre-Game Prep**
   - Sends digital reference cards to players
   - Suggests YouTube rules videos (specific timestamps)
   - Sets up Rules Assistant with TI4 rulebook loaded

4. **Game Day**
   - Projects teaching script on TV (slide-by-slide)
   - Visual aids for each section
   - Rules Assistant answers questions during teach
   - First turn walkthrough (AI suggests optimal first moves for learning)

5. **During 8-Hour Game**
   - Rules Assistant on standby (common questions pre-loaded)
   - Turn tracker (especially important in 6-player game)
   - Photo log every round (board state tracker)
   - Score tracker (victory point calculator)

6. **Post-Game**
   - Session log with story highlights
   - "What was confusing?" feedback collection
   - Updates teaching guide based on actual questions asked
   - Schedules next game night (automatic reminders)

### Workflow 3: Designing a New Game
**Goal**: Design a deck-building game about botanical gardens

**Steps**:
1. **Concept Phase**
   - Theme-Mechanic Matcher: "Botanical gardens" → suggests Deck Building, Set Collection, Engine Building
   - Mechanic Brainstormer: "Deck Building + Set Collection" → examples like "Dominion + splotter games"
   - Innovation suggester: "What if flower colors/types provided combos?"

2. **Initial Design**
   - Design goals: 30-45 min, 2-4 players, medium complexity
   - Core loop: Plant flowers (cards) → Attract visitors (points) → Expand garden (engine building)
   - Prototype Component Generator: Creates 80 starting cards

3. **First Playtest**
   - Print-and-play PDFs generated
   - Playtest with 3 people
   - Record feedback (voice → transcription → structured analysis)

4. **Analysis**
   - Playtesting Feedback Analyzer:
     - ✅ "Theme came through really well"
     - ⚠️ "Too many cards to track"
     - ❌ "Visitor scoring was confusing"
   - Balance Calculator: Identifies dominant strategy (roses too strong)
   - Game Math Assistant: Suggests "Need 10% more variety in flowers"

5. **Iteration**
   - Version 0.2: Reduce deck to 60 cards, simplify visitor scoring, nerf roses
   - Iteration Tracker: Logs changes and reasoning
   - Regenerate print-and-play with "v0.2" watermark

6. **Ongoing**
   - Repeat playtests every 2 weeks
   - Track feedback trends (Are issues being fixed?)
   - A/B test different card costs
   - When ready: Export to professional printing service

---

## Entity Relationships

### Core Entity Graph
```
Game
  ├─ has_many: Mechanics
  ├─ has_many: Sessions
  ├─ belongs_to: Designer
  ├─ belongs_to: Publisher
  ├─ has_many: Teaching Guides
  ├─ has_many: Quick Reference Cards
  └─ has_many: Prototypes (if designing)

Player
  ├─ participates_in: Sessions
  ├─ owns: Games (collection)
  ├─ has_preferences: Mechanics, Themes, Complexity
  └─ has_stats: Win rate, favorite games, etc.

Session
  ├─ belongs_to: Game
  ├─ has_many: Players
  ├─ has_many: Photos (board state, setup, end)
  └─ belongs_to: Location

Mechanic
  ├─ used_in: Games
  ├─ parent: Mechanic (taxonomy)
  ├─ children: Mechanics (sub-types)
  ├─ commonly_paired_with: Mechanics
  └─ has_many: Examples (games)

Prototype
  ├─ designed_by: Player
  ├─ uses: Mechanics
  ├─ has_many: Playtests
  └─ has_many: Components

Teaching Guide
  ├─ belongs_to: Game
  ├─ has_many: Sections
  └─ has_many: Visual Aids
```

---

## Technical Architecture

### Backend Components

**New Services**:
- `api/services/bgg_service.py` - BoardGameGeek API integration
- `api/services/game_service.py` - Game CRUD and analysis
- `api/services/session_service.py` - Session logging and stats
- `api/services/teaching_service.py` - Teaching guide generation
- `api/services/mechanic_service.py` - Mechanic taxonomy and analysis
- `api/services/design_service.py` - Prototype management and playtesting

**New Routes**:
- `/api/games` - Game CRUD, collection management
- `/api/sessions` - Session logging, stats queries
- `/api/mechanics` - Mechanic browser, relationships
- `/api/teaching` - Generate teaching materials
- `/api/prototypes` - Prototype management
- `/api/playtests` - Playtest logging and analysis

**New AI Tools**:
- `ai_tools/board_game_rules_gatherer/` - Fetch rulebooks from BGG (MVP)
- `ai_tools/document_rag_preparer/` - Convert PDFs to searchable format (MVP)
- `ai_tools/document_qa/` - Generic Q&A system (document, general, image, comparison) (MVP)
- `ai_tools/game_recommender/` - Recommendation engine
- `ai_tools/teaching_guide_generator/` - Generate teaching scripts
- `ai_tools/mechanic_analyzer/` - Extract mechanics from rulebooks
- `ai_tools/balance_calculator/` - Game math and balance
- `ai_tools/board_state_analyzer/` - Vision model for game photos
- `ai_tools/feedback_analyzer/` - Parse playtest feedback

### Frontend Components

**New Pages**:
- `/games` - Collection browser (grid view with filters)
- `/games/:id` - Game detail page
- `/sessions` - Session log (timeline view)
- `/sessions/new` - Quick session entry
- `/teach/:game_id` - Teaching guide viewer
- `/mechanics` - Mechanic taxonomy browser
- `/mechanics/:id` - Mechanic deep dive
- `/prototypes` - Prototype manager (designer tools)
- `/prototypes/:id` - Prototype editor
- `/recommend` - Game recommendation tool

**New Components**:
- `GameCard.jsx` - Game display card (box art, info)
- `SessionEntry.jsx` - Quick session log form
- `QAInterface.jsx` - Question-answer interface (supports document and general Q&A)
- `QADisplay.jsx` - Display Q&A with expandable citations
- `MechanicGraph.jsx` - Visual mechanic relationship map
- `TeachingScript.jsx` - Step-by-step teaching UI
- `PlaytestLogger.jsx` - Structured playtest feedback

---

## Data Sources & Integrations

### BoardGameGeek (BGG) Integration
- **Import Collection**: Fetch user's collection via XML API
- **Sync Ratings**: Keep ratings in sync
- **Fetch Game Data**: Metadata, ratings, complexity, mechanics
- **Images**: Box art, component photos
- **Forums**: Common questions and rulings

### Other Potential Integrations
- **Tabletop Simulator**: Export prototypes as TTS mods
- **Google Sheets**: Import/export session logs
- **Kickstarter**: Track crowdfunding projects
- **FLGS Inventory**: Check local store availability
- **Printing Services**: Export components for professional printing

---

## AI Model Requirements

### Vision Models
- **Board State Recognition**: Gemini 2.0 Flash (multimodal)
  - Identify game from photo
  - Read score tracks and point tokens
  - Detect component counts
  - Analyze setup vs current state

- **Rulebook OCR**: Gemini 2.0 Flash
  - Extract text from rulebook photos/PDFs
  - Identify sections (setup, gameplay, scoring)
  - Preserve formatting and structure

### Language Models
- **Document Q&A (MVP)**: Gemini 2.0 Flash or local LLM
  - Question-answer interface (not conversational chat)
  - Supports document-grounded Q&A (with citations) and general knowledge
  - Context types: document, general, image (future), comparison (future)
  - Cite rulebook pages, sections, exact quotes

- **Teaching Guide Generator**: Gemini 2.0 Flash
  - Input: Rulebook text
  - Output: Structured teaching script
  - Customizable by audience and style

- **Mechanic Analyzer**: Gemini 2.0 Flash or local LLM
  - Input: Game description or rulebook
  - Output: List of mechanics with explanations
  - Confidence scoring

- **Feedback Analyzer**: Gemini 2.0 Flash or local LLM
  - Input: Playtest notes (text or transcription)
  - Output: Structured feedback (positives, issues, suggestions)
  - Sentiment analysis

- **Recommendation Engine**: Embeddings + similarity search
  - Game embeddings (mechanics, themes, complexity)
  - Player preference embeddings
  - Cosine similarity for matching

---

## Implementation Phases

### Phase 1: Foundation (4-5 weeks)
**Goal**: Basic game collection and session logging

- [ ] Game entity (CRUD, BGG import)
- [ ] Session entity (CRUD, photo upload)
- [ ] Player entity (CRUD, preferences)
- [ ] Collection browser UI
- [ ] Session logger UI
- [ ] Basic stats dashboard (games played, win rate)

### Phase 2: Discovery & Recommendation (3-4 weeks)
**Goal**: Intelligent game selection

- [ ] Game recommender tool
- [ ] "What should we play?" workflow
- [ ] Player preference learning
- [ ] Collection analyzer
- [ ] Wishlist with price tracking
- [ ] BGG integration (ratings, metadata)

### Phase 3: Teaching Tools (4-5 weeks)
**Goal**: Help teach games to new players

- [ ] Teaching guide generator
- [ ] Quick reference card generator
- [ ] Rules assistant (chat interface)
- [ ] Component photo labeler
- [ ] Common questions database
- [ ] Teaching guide browser UI

### Phase 4: Mechanics Analysis (3-4 weeks)
**Goal**: Understand and categorize mechanics

- [ ] Mechanic taxonomy (entity + browser)
- [ ] Mechanic analyzer tool
- [ ] Mechanic relationship mapper
- [ ] Deep dive article generator
- [ ] Mechanic study guides
- [ ] Game-mechanic tagging

### Phase 5: Designer Tools (5-6 weeks)
**Goal**: Support game designers

- [ ] Prototype entity (CRUD, versioning)
- [ ] Playtest logger
- [ ] Feedback analyzer
- [ ] Mechanic brainstorming assistant
- [ ] Balance calculator
- [ ] Component generator (print-and-play)
- [ ] Theme-mechanic matcher
- [ ] Iteration tracker

---

## Success Metrics

### Adoption Metrics
- 50+ games in collection
- 100+ sessions logged
- 10+ teaching guides generated
- 5+ prototypes created (if designer)

### Engagement Metrics
- Weekly active use (session logging)
- Rules assistant queries per game night
- Teaching guide views before game nights
- Recommendation acceptance rate (Did they play the suggested game?)

### Value Metrics
- Time saved teaching games (before/after comparison)
- Discovery satisfaction (Found games they love)
- Collection ROI (Cost per play, games collecting dust)
- Design iteration speed (playtests per month)

---

## Unique Value Propositions

### For Players
1. **Never Forget Rules**: Rules assistant + teaching guides + quick reference
2. **Perfect Game Selection**: AI recommender based on group preferences and past plays
3. **Rich Play History**: Photo-enhanced session logs with stats
4. **Teach with Confidence**: Generated teaching materials for any game
5. **Maximize Collection**: Play everything you own, discover hidden gems

### For Teachers
1. **Instant Teaching Prep**: Generate materials in minutes vs hours of prep
2. **Personalized Scripts**: Adapt to audience (beginners, experienced, kids)
3. **Visual Aids**: Component guides and setup diagrams from photos
4. **First-Game Simplification**: Know exactly what to skip in first play
5. **Common Questions Pre-Answered**: FAQ database prevents rules lookups

### For Designers
1. **Accelerated Ideation**: Mechanic brainstorming with AI
2. **Mathematical Validation**: Balance calculator catches issues early
3. **Structured Feedback**: Playtest analyzer extracts actionable insights
4. **Rapid Prototyping**: Generate print-and-play materials in seconds
5. **Design Knowledge**: Learn from 50+ years of mechanic evolution

### For Collectors
1. **Collection Intelligence**: Know what you own, what gaps exist, what's collecting dust
2. **Financial Tracking**: Purchase price, current value, cost per play
3. **Rotation Optimization**: Ensure variety, play games before they collect dust
4. **Discovery Engine**: Find games you'll love based on your collection patterns
5. **Social Insights**: See what friends own, coordinate group purchases

---

## Risks & Mitigations

### Risk 1: BGG API Rate Limits
**Mitigation**: Cache aggressively, batch imports, respect rate limits, consider scraping as backup

### Risk 2: Rulebook Copyright
**Mitigation**: Use user-uploaded rulebooks, cite sources, fair use for personal teaching guides, avoid redistribution

### Risk 3: Vision Model Accuracy (Board State)
**Mitigation**: Start with simple cases (score tracks), allow manual correction, improve with feedback loop

### Risk 4: Document Q&A Hallucination (Wrong Answers/Citations)
**Mitigation**: Strict prompt engineering with citation requirements, confidence scores, "I don't see this in the rulebook" responses for missing info, user feedback loop (helpful/not helpful), human verification encouraged

### Risk 5: Designer Tool Complexity
**Mitigation**: Start simple (playtest logger), progressive disclosure, tutorials, example prototypes

---

## Future Expansions

### Advanced Features
- **Augmented Reality**: Point phone at game, see rules overlay
- **Live Score Tracking**: App replaces physical score track
- **Social Features**: Share session photos, compare collections with friends
- **Tournament Organizer**: Swiss pairings, bracket management
- **Convention Planner**: Schedule games at conventions, find players
- **Print-on-Demand**: Direct integration with printing services
- **3D Component Viewer**: Rotate and inspect components in AR
- **Video Analysis**: Upload teaching video, get critique and suggestions
- **Multiplayer Sync**: All players see turn tracker on their phones
- **Voice Assistant**: "Alexa, what are the rules for worker placement in Agricola?"

### Community Features
- **Teaching Guide Sharing**: Community-contributed teaching materials
- **House Rules Database**: Popular variants and house rules
- **Playtest Network**: Connect designers with playtesters
- **Mechanic Wiki**: Community-edited mechanic encyclopedia
- **Designer Interviews**: Learn from successful designers
- **Game Design Challenges**: Monthly prompts and peer review

---

## Conclusion

Board game tools in Life-OS represent a comprehensive approach to the entire board gaming lifecycle: **discovering** great games, **teaching** them effectively, **playing** with enhanced experience, **studying** the craft of design, and **creating** new games.

The entity-centric architecture (Games, Sessions, Mechanics, Prototypes, Players) combined with AI-powered tools (recommenders, analyzers, generators) creates a platform that grows more valuable with use. Every session logged improves recommendations, every teaching guide generated adds to the knowledge base, every mechanic analyzed deepens the taxonomy.

This isn't just a board game database—it's an intelligent companion for the entire board gaming journey.

---

**Ready for implementation in Phase 5 (6-8 months out)**
**Estimated Total Effort**: 80-100 hours across 5 implementation phases
**Expected Impact**: Transform Life-OS into the most comprehensive board game companion tool available
