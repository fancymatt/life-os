"""
Document Routes

Endpoints for document processing and RAG preparation.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
from pathlib import Path
import time

from api.models.responses import DocumentInfo, DocumentProcessResponse
from api.services.document_service import DocumentService
from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from ai_tools.document_rag_preparer import DocumentRAGPreparer

router = APIRouter()


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
async def process_document(
    document_id: str,
    chunk_size: int = 500,
    overlap: int = 50,
    background_tasks: BackgroundTasks = None,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Process a document for RAG (convert PDF → chunks → embeddings → vector DB)

    This converts the document PDF into a searchable format:
    1. PDF → Markdown (using Docling)
    2. Markdown → Chunks (~500 chars each)
    3. Chunks → Embeddings (using Gemini API)
    4. Store in ChromaDB vector database

    The processing happens synchronously and may take 10-30 seconds.
    """
    document_service = DocumentService()

    # Get document
    document_data = document_service.get_document(document_id)
    if not document_data:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

    # Check if document has a file path
    if not document_data.get('file_path'):
        raise HTTPException(status_code=400, detail="Document has no file path")

    file_path = Path(document_data['file_path'])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Document file not found: {file_path}")

    try:
        start_time = time.time()

        # Process document
        preparer = DocumentRAGPreparer()
        result = preparer.prepare_document(
            pdf_path=file_path,
            document_id=document_id,
            chunk_size=chunk_size,
            overlap=overlap
        )

        processing_time = time.time() - start_time

        # Update document entity with processing results
        document_service.update_document(
            document_id=document_id,
            processed=True,
            markdown_path=result.get('markdown_path'),
            vector_ids=result.get('vector_db_path', '').split('/') if result.get('vector_db_path') else [],
            metadata={
                'chunk_count': result.get('chunk_count', 0),
                'processing_time': processing_time,
                'conversion_method': result.get('conversion_metadata', {}).get('conversion_method', 'unknown')
            }
        )

        # Get updated document
        updated_doc = document_service.get_document(document_id)

        return DocumentProcessResponse(
            status="completed",
            document=DocumentInfo(
                document_id=updated_doc['document_id'],
                game_id=updated_doc.get('game_id'),
                title=updated_doc['title'],
                source_type=updated_doc['source_type'],
                source_url=updated_doc.get('source_url'),
                file_path=updated_doc.get('file_path'),
                page_count=updated_doc.get('page_count'),
                file_size_bytes=updated_doc.get('file_size_bytes'),
                processed=updated_doc.get('processed', False),
                processed_at=updated_doc.get('processed_at'),
                markdown_path=updated_doc.get('markdown_path'),
                vector_ids=updated_doc.get('vector_ids', []),
                created_at=updated_doc.get('created_at'),
                metadata=updated_doc.get('metadata', {})
            ),
            markdown_path=result.get('markdown_path'),
            chunk_count=result.get('chunk_count', 0),
            processing_time=processing_time
        )

    except Exception as e:
        # Update document with error status
        document_service.update_document(
            document_id=document_id,
            processed=False,
            metadata={'processing_error': str(e)}
        )

        return DocumentProcessResponse(
            status="failed",
            error=str(e)
        )


@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(
    document_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get document details including processing status
    """
    document_service = DocumentService()
    document_data = document_service.get_document(document_id)

    if not document_data:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

    return DocumentInfo(
        document_id=document_data['document_id'],
        game_id=document_data.get('game_id'),
        title=document_data['title'],
        source_type=document_data['source_type'],
        source_url=document_data.get('source_url'),
        file_path=document_data.get('file_path'),
        page_count=document_data.get('page_count'),
        file_size_bytes=document_data.get('file_size_bytes'),
        processed=document_data.get('processed', False),
        processed_at=document_data.get('processed_at'),
        markdown_path=document_data.get('markdown_path'),
        vector_ids=document_data.get('vector_ids', []),
        created_at=document_data.get('created_at'),
        metadata=document_data.get('metadata', {})
    )


@router.post("/{document_id}/reprocess", response_model=DocumentProcessResponse)
async def reprocess_document(
    document_id: str,
    chunk_size: int = 500,
    overlap: int = 50,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Reprocess an already-processed document with different parameters

    Useful for:
    - Trying different chunk sizes
    - Regenerating embeddings with a different model
    - Fixing processing errors
    """
    # Same as process_document, but allows reprocessing
    return await process_document(
        document_id=document_id,
        chunk_size=chunk_size,
        overlap=overlap,
        current_user=current_user
    )
