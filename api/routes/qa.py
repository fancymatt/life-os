"""
Q&A Routes

Generic Q&A endpoints supporting document-grounded and general knowledge questions.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel, Field

from api.services.qa_service import QAService
from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from ai_tools.document_qa import DocumentQA

router = APIRouter()


# Request/Response Models

class AskQuestionRequest(BaseModel):
    """Request to ask a question"""
    question: str = Field(..., min_length=1, description="The question to ask")
    game_id: Optional[str] = Field(None, description="Optional game context")
    document_ids: Optional[List[str]] = Field(None, description="Optional specific documents")
    context_type: str = Field("document", description="Context type: document, general, image, comparison")
    top_k: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve (document Q&A only)")
    model: str = Field("gemini/gemini-2.0-flash-exp", description="LLM model to use")


class CitationResponse(BaseModel):
    """Citation in answer"""
    text: str
    page: int
    section: str
    chunk_id: str
    document_id: str


class QAResponse(BaseModel):
    """Q&A response"""
    qa_id: str
    question: str
    answer: str
    context_type: str
    game_id: Optional[str] = None
    document_ids: List[str] = []
    citations: List[CitationResponse] = []
    confidence: float
    is_favorite: bool = False
    was_helpful: Optional[bool] = None
    user_notes: Optional[str] = None
    custom_tags: List[str] = []
    created_at: str
    updated_at: str
    metadata: dict = {}


class UpdateQARequest(BaseModel):
    """Request to update Q&A (user feedback)"""
    is_favorite: Optional[bool] = None
    was_helpful: Optional[bool] = None
    user_notes: Optional[str] = None
    custom_tags: Optional[List[str]] = None


class QAListResponse(BaseModel):
    """List of Q&As"""
    qas: List[QAResponse]
    total: int
    filters: dict = {}


# Routes

@router.post("/ask", response_model=QAResponse)
async def ask_question(
    request: AskQuestionRequest,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Ask a question (document-grounded or general knowledge)

    Context Types:
    - **document**: Answer using rulebook excerpts (requires game_id or document_ids)
    - **general**: General knowledge (no document context)
    - **image**: Image analysis (future)
    - **comparison**: Multi-document comparison (future)
    """
    # Initialize services
    qa_tool = DocumentQA()
    qa_service = QAService()

    try:
        # Ask question using Q&A tool
        result = qa_tool.ask_question(
            question=request.question,
            game_id=request.game_id,
            document_ids=request.document_ids,
            context_type=request.context_type,
            top_k=request.top_k,
            model=request.model
        )

        # Save Q&A to database
        citations = [
            {
                "text": c.text,
                "page": c.page,
                "section": c.section,
                "chunk_id": c.chunk_id,
                "document_id": c.document_id
            }
            for c in result.citations
        ]

        qa_entity = await qa_service.create_qa(
            question=result.question,
            answer=result.answer,
            context_type=result.context_type,
            game_id=result.game_id,
            document_ids=result.document_ids,
            citations=citations,
            confidence=result.confidence,
            metadata=result.metadata
        )

        # Convert to response
        return QAResponse(
            qa_id=qa_entity["qa_id"],
            question=qa_entity["question"],
            answer=qa_entity["answer"],
            context_type=qa_entity["context_type"],
            game_id=qa_entity.get("game_id"),
            document_ids=qa_entity.get("document_ids", []),
            citations=[CitationResponse(**c) for c in qa_entity.get("citations", [])],
            confidence=qa_entity.get("confidence", 0.0),
            is_favorite=qa_entity.get("is_favorite", False),
            was_helpful=qa_entity.get("was_helpful"),
            user_notes=qa_entity.get("user_notes"),
            custom_tags=qa_entity.get("custom_tags", []),
            created_at=qa_entity["created_at"],
            updated_at=qa_entity["updated_at"],
            metadata=qa_entity.get("metadata", {})
        )

    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")


@router.get("/", response_model=QAListResponse)
async def list_qas(
    game_id: Optional[str] = None,
    context_type: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all Q&As with optional filtering

    Filters:
    - **game_id**: Show only Q&As for specific game
    - **context_type**: Filter by context (document, general, image, comparison)
    - **is_favorite**: Show only favorites
    """
    qa_service = QAService()

    qas = await qa_service.list_qas(
        game_id=game_id,
        context_type=context_type,
        is_favorite=is_favorite
    )

    qa_responses = [
        QAResponse(
            qa_id=qa["qa_id"],
            question=qa["question"],
            answer=qa["answer"],
            context_type=qa["context_type"],
            game_id=qa.get("game_id"),
            document_ids=qa.get("document_ids", []),
            citations=[CitationResponse(**c) for c in qa.get("citations", [])],
            confidence=qa.get("confidence", 0.0),
            is_favorite=qa.get("is_favorite", False),
            was_helpful=qa.get("was_helpful"),
            user_notes=qa.get("user_notes"),
            custom_tags=qa.get("custom_tags", []),
            created_at=qa["created_at"],
            updated_at=qa["updated_at"],
            metadata=qa.get("metadata", {})
        )
        for qa in qas
    ]

    return QAListResponse(
        qas=qa_responses,
        total=len(qa_responses),
        filters={
            "game_id": game_id,
            "context_type": context_type,
            "is_favorite": is_favorite
        }
    )


@router.get("/{qa_id}", response_model=QAResponse)
async def get_qa(
    qa_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get specific Q&A by ID
    """
    qa_service = QAService()

    qa = await qa_service.get_qa(qa_id)

    if not qa:
        raise HTTPException(status_code=404, detail=f"Q&A {qa_id} not found")

    return QAResponse(
        qa_id=qa["qa_id"],
        question=qa["question"],
        answer=qa["answer"],
        context_type=qa["context_type"],
        game_id=qa.get("game_id"),
        document_ids=qa.get("document_ids", []),
        citations=[CitationResponse(**c) for c in qa.get("citations", [])],
        confidence=qa.get("confidence", 0.0),
        is_favorite=qa.get("is_favorite", False),
        was_helpful=qa.get("was_helpful"),
        user_notes=qa.get("user_notes"),
        custom_tags=qa.get("custom_tags", []),
        created_at=qa["created_at"],
        updated_at=qa["updated_at"],
        metadata=qa.get("metadata", {})
    )


@router.put("/{qa_id}", response_model=QAResponse)
async def update_qa(
    qa_id: str,
    request: UpdateQARequest,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update Q&A (mark as favorite, provide feedback, add notes/tags)
    """
    qa_service = QAService()

    updated = await qa_service.update_qa(
        qa_id=qa_id,
        is_favorite=request.is_favorite,
        was_helpful=request.was_helpful,
        user_notes=request.user_notes,
        custom_tags=request.custom_tags
    )

    if not updated:
        raise HTTPException(status_code=404, detail=f"Q&A {qa_id} not found")

    return QAResponse(
        qa_id=updated["qa_id"],
        question=updated["question"],
        answer=updated["answer"],
        context_type=updated["context_type"],
        game_id=updated.get("game_id"),
        document_ids=updated.get("document_ids", []),
        citations=[CitationResponse(**c) for c in updated.get("citations", [])],
        confidence=updated.get("confidence", 0.0),
        is_favorite=updated.get("is_favorite", False),
        was_helpful=updated.get("was_helpful"),
        user_notes=updated.get("user_notes"),
        custom_tags=updated.get("custom_tags", []),
        created_at=updated["created_at"],
        updated_at=updated["updated_at"],
        metadata=updated.get("metadata", {})
    )


@router.delete("/{qa_id}")
async def delete_qa(
    qa_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete Q&A
    """
    qa_service = QAService()

    success = await qa_service.delete_qa(qa_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Q&A {qa_id} not found")

    return {"message": f"Q&A {qa_id} deleted successfully"}


@router.get("/search", response_model=QAListResponse)
async def search_qas(
    query: str,
    game_id: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Search Q&As by question or answer content
    """
    qa_service = QAService()

    qas = await qa_service.search_qas(query=query, game_id=game_id)

    qa_responses = [
        QAResponse(
            qa_id=qa["qa_id"],
            question=qa["question"],
            answer=qa["answer"],
            context_type=qa["context_type"],
            game_id=qa.get("game_id"),
            document_ids=qa.get("document_ids", []),
            citations=[CitationResponse(**c) for c in qa.get("citations", [])],
            confidence=qa.get("confidence", 0.0),
            is_favorite=qa.get("is_favorite", False),
            was_helpful=qa.get("was_helpful"),
            user_notes=qa.get("user_notes"),
            custom_tags=qa.get("custom_tags", []),
            created_at=qa["created_at"],
            updated_at=qa["updated_at"],
            metadata=qa.get("metadata", {})
        )
        for qa in qas
    ]

    return QAListResponse(
        qas=qa_responses,
        total=len(qa_responses),
        filters={"query": query, "game_id": game_id}
    )
