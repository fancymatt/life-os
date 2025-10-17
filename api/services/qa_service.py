"""
Q&A Service

Handles Q&A entity storage, retrieval, and management.
Q&As can be document-grounded, general knowledge, image-based, or comparison.
"""

import json
import uuid
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from api.config import settings


class QAService:
    """Service for managing Q&A entities"""

    def __init__(self):
        """Initialize Q&A service"""
        self.qas_dir = Path(settings.data_dir) / "qas"
        self.qas_dir.mkdir(parents=True, exist_ok=True)

    def _get_qa_path(self, qa_id: str) -> Path:
        """Get path to Q&A JSON file"""
        return self.qas_dir / f"{qa_id}.json"

    async def create_qa(
        self,
        question: str,
        answer: str,
        context_type: str = "general",  # "document", "general", "image", "comparison"
        game_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        image_url: Optional[str] = None,
        citations: Optional[List[Dict[str, Any]]] = None,
        confidence: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Q&A

        Args:
            question: The question asked
            answer: The answer generated
            context_type: Type of Q&A ("document", "general", "image", "comparison")
            game_id: Associated board game ID (optional)
            document_ids: List of document IDs used for context (optional)
            image_url: URL of image for image-based Q&A (optional)
            citations: List of citations with document_id, page, excerpt (optional)
            confidence: Confidence score (0.0 - 1.0)
            metadata: Additional metadata

        Returns:
            Q&A data dict
        """
        qa_id = str(uuid.uuid4())[:8]

        qa_data = {
            "qa_id": qa_id,
            "question": question,
            "answer": answer,
            "context_type": context_type,
            "game_id": game_id,
            "document_ids": document_ids or [],
            "image_url": image_url,
            "citations": citations or [],
            "confidence": confidence,
            "is_favorite": False,
            "was_helpful": None,
            "user_notes": None,
            "custom_tags": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        # Save Q&A data (async)
        qa_file = self._get_qa_path(qa_id)
        async with aiofiles.open(qa_file, 'w') as f:
            await f.write(json.dumps(qa_data, indent=2))

        return qa_data

    async def get_qa(self, qa_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a Q&A by ID

        Args:
            qa_id: Q&A ID

        Returns:
            Q&A data dict or None if not found
        """
        qa_file = self._get_qa_path(qa_id)

        if not qa_file.exists():
            return None

        async with aiofiles.open(qa_file, 'r') as f:
            content = await f.read()
            return json.loads(content)

    async def list_qas(
        self,
        game_id: Optional[str] = None,
        context_type: Optional[str] = None,
        is_favorite: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        List Q&As with optional filters

        Args:
            game_id: Filter by board game ID (optional)
            context_type: Filter by context type (optional)
            is_favorite: Filter by favorite status (optional)

        Returns:
            List of Q&A data dicts
        """
        qas = []

        for file_path in self.qas_dir.glob("*.json"):
            try:
                async with aiofiles.open(file_path, 'r') as f:
                    content = await f.read()
                    qa_data = json.loads(content)

                    # Apply filters
                    if game_id and qa_data.get('game_id') != game_id:
                        continue
                    if context_type and qa_data.get('context_type') != context_type:
                        continue
                    if is_favorite is not None and qa_data.get('is_favorite') != is_favorite:
                        continue

                    qas.append(qa_data)
            except Exception as e:
                print(f"Error loading Q&A {file_path}: {e}")
                continue

        # Sort by created_at (newest first)
        qas.sort(
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )

        return qas

    async def update_qa(
        self,
        qa_id: str,
        is_favorite: Optional[bool] = None,
        was_helpful: Optional[bool] = None,
        user_notes: Optional[str] = None,
        custom_tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a Q&A (typically user feedback)

        Args:
            qa_id: Q&A ID
            is_favorite: Mark as favorite (optional)
            was_helpful: Mark as helpful or not (optional)
            user_notes: Personal notes (optional)
            custom_tags: Custom tags (optional)
            metadata: New metadata (optional)

        Returns:
            Updated Q&A data dict or None if not found
        """
        qa_data = await self.get_qa(qa_id)

        if not qa_data:
            return None

        # Update fields if provided
        if is_favorite is not None:
            qa_data['is_favorite'] = is_favorite
        if was_helpful is not None:
            qa_data['was_helpful'] = was_helpful
        if user_notes is not None:
            qa_data['user_notes'] = user_notes
        if custom_tags is not None:
            qa_data['custom_tags'] = custom_tags
        if metadata is not None:
            qa_data['metadata'].update(metadata)

        qa_data['updated_at'] = datetime.utcnow().isoformat()

        # Save updated data (async)
        qa_file = self._get_qa_path(qa_id)
        async with aiofiles.open(qa_file, 'w') as f:
            await f.write(json.dumps(qa_data, indent=2))

        return qa_data

    def delete_qa(self, qa_id: str) -> bool:
        """
        Delete a Q&A

        Args:
            qa_id: Q&A ID

        Returns:
            True if deleted, False if not found
        """
        qa_file = self._get_qa_path(qa_id)

        if not qa_file.exists():
            return False

        # Delete Q&A file
        qa_file.unlink()

        return True

    async def search_qas(self, query: str, game_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search Q&As by question or answer content

        Args:
            query: Search query
            game_id: Filter by board game ID (optional)

        Returns:
            List of matching Q&A data dicts
        """
        query_lower = query.lower()
        matching_qas = []

        for file_path in self.qas_dir.glob("*.json"):
            try:
                async with aiofiles.open(file_path, 'r') as f:
                    content = await f.read()
                    qa_data = json.loads(content)

                    # Filter by game_id if provided
                    if game_id and qa_data.get('game_id') != game_id:
                        continue

                    # Check if query matches question or answer
                    question = qa_data.get('question', '').lower()
                    answer = qa_data.get('answer', '').lower()

                    if query_lower in question or query_lower in answer:
                        matching_qas.append(qa_data)
            except Exception as e:
                print(f"Error searching Q&A {file_path}: {e}")
                continue

        # Sort by created_at (newest first)
        matching_qas.sort(
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )

        return matching_qas
