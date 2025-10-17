"""
Document Q&A Tool

Answers questions using prepared rulebooks (RAG) or general knowledge.

Features:
- Document-grounded Q&A with semantic search and citations
- General knowledge Q&A without citations
- Context type detection (document, general, image, comparison)
- Citation parsing and validation
- Confidence scoring
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from ai_tools.shared.router import LLMRouter


TOOL_INFO = {
    "name": "document_qa",
    "display_name": "Document Q&A",
    "description": "Answer questions using rulebooks or general knowledge",
    "category": "board_games",
    "version": "1.0.0",
    "supports_batch": False,
    "requires_image": False
}


@dataclass
class Citation:
    """Citation reference for document-grounded answers"""
    text: str  # Quoted text from document
    page: int  # Page number
    section: str  # Section heading
    chunk_id: str  # Chunk identifier
    document_id: str  # Source document


@dataclass
class QAResponse:
    """Response from Q&A system"""
    question: str
    answer: str
    context_type: str  # "document" | "general" | "image" | "comparison"
    game_id: Optional[str] = None
    document_ids: List[str] = None
    citations: List[Citation] = None
    confidence: float = 0.0
    asked_at: str = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.document_ids is None:
            self.document_ids = []
        if self.citations is None:
            self.citations = []
        if self.asked_at is None:
            self.asked_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


class DocumentQA:
    """
    Generic Q&A tool supporting multiple context types

    Context Types:
    - document: Document-grounded Q&A with citations (MVP)
    - general: General knowledge without citations (MVP)
    - image: Image analysis Q&A (future)
    - comparison: Multi-document comparison (future)
    """

    def __init__(self, base_dir: Path = None):
        """
        Initialize Document Q&A tool

        Args:
            base_dir: Base directory for data (defaults to /app/data)
        """
        if base_dir is None:
            base_dir = Path("/app/data")

        self.base_dir = Path(base_dir)
        self.vector_db_dir = self.base_dir / "vector_db"
        self.router = LLMRouter()

        # Check dependencies
        if not CHROMADB_AVAILABLE:
            print("⚠️  ChromaDB not available - document Q&A will be limited")

        if not GEMINI_AVAILABLE:
            print("⚠️  Gemini API not available - embeddings will use fallback")

    def ask_question(
        self,
        question: str,
        game_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        context_type: str = "document",
        top_k: int = 5,
        model: str = "gemini/gemini-2.0-flash-exp"
    ) -> QAResponse:
        """
        Answer a question with optional document grounding

        Args:
            question: The question to answer
            game_id: Optional game to search within
            document_ids: Optional specific documents to search
            context_type: Type of Q&A ("document", "general", "image", "comparison")
            top_k: Number of chunks to retrieve for context
            model: LLM model to use

        Returns:
            QAResponse with answer and optional citations
        """
        # Route based on context type
        if context_type == "document":
            return self._document_grounded_qa(
                question=question,
                game_id=game_id,
                document_ids=document_ids,
                top_k=top_k,
                model=model
            )
        elif context_type == "general":
            return self._general_knowledge_qa(
                question=question,
                model=model
            )
        elif context_type == "image":
            raise NotImplementedError("Image Q&A not yet implemented")
        elif context_type == "comparison":
            raise NotImplementedError("Comparison Q&A not yet implemented")
        else:
            raise ValueError(f"Unknown context_type: {context_type}")

    def _document_grounded_qa(
        self,
        question: str,
        game_id: Optional[str],
        document_ids: Optional[List[str]],
        top_k: int,
        model: str
    ) -> QAResponse:
        """
        Answer question using document retrieval (RAG)

        Steps:
        1. Load vector database for game/documents
        2. Generate question embedding
        3. Semantic search for relevant chunks
        4. Build context from chunks
        5. Send to LLM with citation requirements
        6. Parse response and extract citations
        """
        if not CHROMADB_AVAILABLE:
            return QAResponse(
                question=question,
                answer="ChromaDB not available. Cannot perform document-grounded Q&A.",
                context_type="document",
                confidence=0.0
            )

        # Determine which documents to search
        if document_ids:
            docs_to_search = document_ids
        elif game_id:
            # Search all documents for this game
            docs_to_search = self._get_game_documents(game_id)
        else:
            return QAResponse(
                question=question,
                answer="No game_id or document_ids provided. Cannot perform document-grounded Q&A.",
                context_type="document",
                confidence=0.0
            )

        if not docs_to_search:
            return QAResponse(
                question=question,
                answer=f"No documents found for game_id={game_id}",
                context_type="document",
                game_id=game_id,
                confidence=0.0
            )

        # Retrieve relevant chunks from documents
        chunks = self._semantic_search(question, docs_to_search, top_k)

        if not chunks:
            return QAResponse(
                question=question,
                answer="I couldn't find any relevant information in the rulebook for this question.",
                context_type="document",
                game_id=game_id,
                document_ids=docs_to_search,
                confidence=0.0
            )

        # Build context from chunks
        context = self._build_context(chunks)

        # Generate answer with citations
        prompt = self._build_document_qa_prompt(question, context)

        # Call LLM
        llm_response = self.router.generate_text(
            prompt=prompt,
            model=model,
            temperature=0.1,  # Low temperature for factual answers
            max_tokens=1000
        )

        # Parse answer and extract citations
        answer, citations = self._parse_answer_with_citations(
            llm_response,
            chunks
        )

        # Calculate confidence based on citation quality
        confidence = self._calculate_confidence(answer, citations)

        return QAResponse(
            question=question,
            answer=answer,
            context_type="document",
            game_id=game_id,
            document_ids=docs_to_search,
            citations=citations,
            confidence=confidence,
            metadata={
                "chunks_retrieved": len(chunks),
                "model": model
            }
        )

    def _general_knowledge_qa(
        self,
        question: str,
        model: str
    ) -> QAResponse:
        """
        Answer general knowledge question (no document grounding)

        This is for questions like:
        - "What is worker placement?"
        - "Who designed Wingspan?"
        - "What are the most popular board game mechanics?"
        """
        prompt = f"""You are a board game expert. Answer this question clearly and concisely.

Question: {question}

Answer:"""

        # Call LLM
        answer = self.router.generate_text(
            prompt=prompt,
            model=model,
            temperature=0.3,  # Slightly higher for general knowledge
            max_tokens=500
        )

        return QAResponse(
            question=question,
            answer=answer.strip(),
            context_type="general",
            confidence=0.8,  # General knowledge has inherent uncertainty
            metadata={
                "model": model
            }
        )

    def _get_game_documents(self, game_id: str) -> List[str]:
        """
        Get all processed document IDs for a game

        Args:
            game_id: Game identifier

        Returns:
            List of document IDs
        """
        # Look for vector DB directories for this game
        game_vector_dir = self.vector_db_dir / game_id

        if not game_vector_dir.exists():
            return []

        # Find all document collections
        document_ids = []
        for item in game_vector_dir.iterdir():
            if item.is_dir():
                document_ids.append(item.name)

        return document_ids

    def _semantic_search(
        self,
        question: str,
        document_ids: List[str],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search across documents

        Args:
            question: Question to search for
            document_ids: Documents to search
            top_k: Number of results per document

        Returns:
            List of chunk dictionaries with metadata
        """
        if not CHROMADB_AVAILABLE:
            return []

        all_chunks = []

        for doc_id in document_ids:
            try:
                # Load ChromaDB collection for document
                collection = self._load_collection(doc_id)

                if not collection:
                    continue

                # Generate question embedding
                question_embedding = self._generate_query_embedding(question)

                # Search
                results = collection.query(
                    query_embeddings=[question_embedding],
                    n_results=top_k
                )

                # Parse results
                for i, (chunk_id, text, metadata, distance) in enumerate(zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    all_chunks.append({
                        "chunk_id": chunk_id,
                        "text": text,
                        "document_id": doc_id,
                        "page": metadata.get("page", 0),
                        "section": metadata.get("section", ""),
                        "subsection": metadata.get("subsection", ""),
                        "distance": distance,
                        "relevance": 1.0 - distance  # Convert distance to relevance
                    })

            except Exception as e:
                print(f"Error searching document {doc_id}: {e}")
                continue

        # Sort by relevance and return top_k overall
        all_chunks.sort(key=lambda x: x["relevance"], reverse=True)
        return all_chunks[:top_k]

    def _load_collection(self, document_id: str) -> Optional[Any]:
        """
        Load ChromaDB collection for a document

        Args:
            document_id: Document identifier

        Returns:
            ChromaDB collection or None
        """
        if not CHROMADB_AVAILABLE:
            return None

        try:
            # Find collection path
            collection_path = None

            # Search in vector_db directory
            for game_dir in self.vector_db_dir.iterdir():
                if not game_dir.is_dir():
                    continue
                doc_path = game_dir / document_id
                if doc_path.exists():
                    collection_path = doc_path
                    break

            if not collection_path:
                return None

            # Load ChromaDB client
            client = chromadb.PersistentClient(
                path=str(collection_path),
                settings=Settings(anonymized_telemetry=False)
            )

            # Get collection
            collection = client.get_collection(name=document_id)
            return collection

        except Exception as e:
            print(f"Error loading collection for {document_id}: {e}")
            return None

    def _generate_query_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for query text

        Args:
            text: Query text

        Returns:
            Embedding vector
        """
        # Try Gemini API first
        if GEMINI_AVAILABLE:
            try:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_query"
                )
                return result["embedding"]
            except Exception as e:
                print(f"Gemini embedding failed: {e}")

        # Fallback to sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Sentence-transformers embedding failed: {e}")
            # Return zero vector as last resort
            return [0.0] * 384

    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Build context string from chunks

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, chunk in enumerate(chunks, 1):
            page = chunk.get("page", "?")
            section = chunk.get("section", "Unknown Section")
            text = chunk.get("text", "")

            context_parts.append(
                f"[Excerpt {i} - Page {page}, Section \"{section}\"]\n{text}\n"
            )

        return "\n".join(context_parts)

    def _build_document_qa_prompt(self, question: str, context: str) -> str:
        """
        Build prompt for document-grounded Q&A

        Args:
            question: Question to answer
            context: Retrieved context from documents

        Returns:
            Formatted prompt
        """
        return f"""You are a board game rules expert. Answer the following question using ONLY the rulebook excerpts provided below.

CRITICAL RULES:
1. ONLY use information from the excerpts
2. ALWAYS cite the page number and section for each statement using the format: (Page X, Section "Y")
3. If the answer is not in the excerpts, say "I don't see this information in the provided rulebook excerpts"
4. Quote exact text when possible
5. If there are multiple interpretations, present both
6. Be concise but complete

Question: {question}

Rulebook Excerpts:
{context}

Answer (with citations):"""

    def _parse_answer_with_citations(
        self,
        llm_response: str,
        chunks: List[Dict[str, Any]]
    ) -> tuple[str, List[Citation]]:
        """
        Parse LLM response and extract citations

        Args:
            llm_response: Raw LLM response
            chunks: Original chunks for citation validation

        Returns:
            (answer_text, list_of_citations)
        """
        answer = llm_response.strip()
        citations = []

        # Extract citation references: (Page X, Section "Y") or (Page X)
        citation_pattern = r'\(Page\s+(\d+)(?:,\s+Section\s+"([^"]+)")?\)'
        matches = re.finditer(citation_pattern, answer)

        for match in matches:
            page_num = int(match.group(1))
            section = match.group(2) if match.group(2) else ""

            # Find corresponding chunk
            for chunk in chunks:
                if chunk.get("page") == page_num:
                    # Extract quoted text near the citation
                    citation_text = self._extract_citation_text(answer, match.start())

                    citations.append(Citation(
                        text=citation_text,
                        page=page_num,
                        section=section or chunk.get("section", ""),
                        chunk_id=chunk.get("chunk_id", ""),
                        document_id=chunk.get("document_id", "")
                    ))
                    break

        return answer, citations

    def _extract_citation_text(self, answer: str, citation_pos: int) -> str:
        """
        Extract the quoted text near a citation

        Args:
            answer: Full answer text
            citation_pos: Position of citation in text

        Returns:
            Extracted quoted text or nearby context
        """
        # Look for quoted text before citation
        text_before = answer[:citation_pos]

        # Find last quote before citation
        quote_match = re.search(r'"([^"]+)"\s*$', text_before)
        if quote_match:
            return quote_match.group(1)

        # Fallback: return last 100 chars
        return text_before[-100:].strip()

    def _calculate_confidence(
        self,
        answer: str,
        citations: List[Citation]
    ) -> float:
        """
        Calculate confidence score for answer

        Factors:
        - Number of citations (more = better)
        - Answer length (too short = suspicious)
        - Presence of uncertainty phrases

        Args:
            answer: Generated answer
            citations: Parsed citations

        Returns:
            Confidence score (0.0 - 1.0)
        """
        confidence = 0.5  # Base confidence

        # More citations = higher confidence
        citation_bonus = min(len(citations) * 0.1, 0.3)
        confidence += citation_bonus

        # Reasonable length = higher confidence
        if 50 < len(answer) < 500:
            confidence += 0.1

        # Check for uncertainty phrases (lower confidence)
        uncertainty_phrases = [
            "i don't see",
            "not found",
            "unclear",
            "ambiguous",
            "might",
            "possibly",
            "perhaps"
        ]

        answer_lower = answer.lower()
        for phrase in uncertainty_phrases:
            if phrase in answer_lower:
                confidence -= 0.2
                break

        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))
