"""
Document Service

Handles document entity storage, retrieval, and management.
Documents can be PDFs, URLs, or text, and are associated with board games.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from api.config import settings


class DocumentService:
    """Service for managing document entities"""

    def __init__(self):
        """Initialize document service"""
        self.documents_dir = Path(settings.base_dir) / "data" / "documents"
        self.documents_dir.mkdir(parents=True, exist_ok=True)

    def _get_document_path(self, document_id: str) -> Path:
        """Get path to document JSON file"""
        return self.documents_dir / f"{document_id}.json"

    def create_document(
        self,
        title: str,
        source_type: str,  # "pdf", "url", "text"
        game_id: Optional[str] = None,
        source_url: Optional[str] = None,
        file_path: Optional[str] = None,
        page_count: Optional[int] = None,
        file_size_bytes: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new document

        Args:
            title: Document title
            source_type: Type of document ("pdf", "url", "text")
            game_id: Associated board game ID (optional)
            source_url: Original URL (for PDFs from BGG or other sources)
            file_path: Path to stored file
            page_count: Number of pages (for PDFs)
            file_size_bytes: File size in bytes
            metadata: Additional metadata

        Returns:
            Document data dict
        """
        document_id = str(uuid.uuid4())[:8]

        document_data = {
            "document_id": document_id,
            "game_id": game_id,
            "title": title,
            "source_type": source_type,
            "source_url": source_url,
            "file_path": file_path,
            "page_count": page_count,
            "file_size_bytes": file_size_bytes,
            "processed": False,
            "processed_at": None,
            "markdown_path": None,
            "vector_ids": [],  # ChromaDB vector IDs after processing
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        # Save document data
        document_file = self._get_document_path(document_id)
        with open(document_file, 'w') as f:
            json.dump(document_data, f, indent=2)

        return document_data

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID

        Args:
            document_id: Document ID

        Returns:
            Document data dict or None if not found
        """
        document_file = self._get_document_path(document_id)

        if not document_file.exists():
            return None

        with open(document_file, 'r') as f:
            return json.load(f)

    def list_documents(self, game_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all documents, optionally filtered by game

        Args:
            game_id: Filter by board game ID (optional)

        Returns:
            List of document data dicts
        """
        documents = []

        for file_path in self.documents_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    document_data = json.load(f)

                    # Filter by game_id if provided
                    if game_id and document_data.get('game_id') != game_id:
                        continue

                    documents.append(document_data)
            except Exception as e:
                print(f"Error loading document {file_path}: {e}")
                continue

        # Sort by created_at (newest first)
        documents.sort(
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )

        return documents

    def update_document(
        self,
        document_id: str,
        title: Optional[str] = None,
        processed: Optional[bool] = None,
        markdown_path: Optional[str] = None,
        vector_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a document

        Args:
            document_id: Document ID
            title: New title (optional)
            processed: Processing status (optional)
            markdown_path: Path to processed markdown (optional)
            vector_ids: ChromaDB vector IDs (optional)
            metadata: New metadata (optional)

        Returns:
            Updated document data dict or None if not found
        """
        document_data = self.get_document(document_id)

        if not document_data:
            return None

        # Update fields if provided
        if title is not None:
            document_data['title'] = title
        if processed is not None:
            document_data['processed'] = processed
            if processed:
                document_data['processed_at'] = datetime.utcnow().isoformat()
        if markdown_path is not None:
            document_data['markdown_path'] = markdown_path
        if vector_ids is not None:
            document_data['vector_ids'] = vector_ids
        if metadata is not None:
            document_data['metadata'].update(metadata)

        document_data['updated_at'] = datetime.utcnow().isoformat()

        # Save updated data
        document_file = self._get_document_path(document_id)
        with open(document_file, 'w') as f:
            json.dump(document_data, f, indent=2)

        return document_data

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        document_file = self._get_document_path(document_id)

        if not document_file.exists():
            return False

        # Delete document file
        document_file.unlink()

        # TODO: Also delete associated files (PDF, markdown, etc.)
        # and remove vectors from ChromaDB

        return True
