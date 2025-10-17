"""
Document RAG Preparer Tool

Converts PDF rulebooks into AI-queryable format using Docling and ChromaDB.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import hashlib

# Docling imports (PDF to Markdown conversion)
try:
    from docling import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("⚠️  Docling not available - PDF conversion will be limited")

# ChromaDB imports (vector database)
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not available - vector storage disabled")

from api.config import settings


class DocumentChunk:
    """Represents a chunk of document text with metadata"""

    def __init__(
        self,
        text: str,
        chunk_index: int,
        page: Optional[int] = None,
        section: Optional[str] = None,
        subsection: Optional[str] = None
    ):
        self.text = text
        self.chunk_index = chunk_index
        self.page = page
        self.section = section
        self.subsection = subsection
        self.chunk_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID for chunk based on content"""
        content_hash = hashlib.md5(self.text.encode()).hexdigest()[:8]
        return f"chunk-{self.chunk_index}-{content_hash}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "chunk_index": self.chunk_index,
            "page": self.page,
            "section": self.section,
            "subsection": self.subsection
        }


class DocumentRAGPreparer:
    """Tool for preparing documents for RAG (Retrieval Augmented Generation)"""

    def __init__(self):
        """Initialize the document preparer"""
        self.processed_dir = Path(settings.data_dir) / "processed"
        self.vector_db_dir = Path(settings.data_dir) / "vector_db"

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db_dir.mkdir(parents=True, exist_ok=True)

    def convert_pdf_to_markdown(self, pdf_path: Path) -> Tuple[str, Dict[str, Any]]:
        """
        Convert PDF to markdown using Docling

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (markdown_text, metadata)
        """
        if not DOCLING_AVAILABLE:
            return self._fallback_pdf_conversion(pdf_path)

        try:
            print(f"📄 Converting PDF to Markdown: {pdf_path.name}")

            # Initialize Docling converter
            converter = DocumentConverter()

            # Convert PDF to structured document
            result = converter.convert(str(pdf_path))

            # Extract markdown
            markdown_text = result.document.export_to_markdown()

            # Extract metadata
            metadata = {
                "page_count": len(result.document.pages) if hasattr(result.document, 'pages') else None,
                "has_tables": any(hasattr(page, 'tables') and page.tables for page in result.document.pages) if hasattr(result.document, 'pages') else False,
                "has_images": any(hasattr(page, 'images') and page.images for page in result.document.pages) if hasattr(result.document, 'pages') else False,
                "conversion_method": "docling"
            }

            print(f"✅ Converted to {len(markdown_text)} characters")

            return markdown_text, metadata

        except Exception as e:
            print(f"⚠️  Docling conversion failed: {e}, using fallback")
            return self._fallback_pdf_conversion(pdf_path)

    def _fallback_pdf_conversion(self, pdf_path: Path) -> Tuple[str, Dict[str, Any]]:
        """
        Fallback PDF conversion using PyPDF2 (basic text extraction)

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (text, metadata)
        """
        try:
            import PyPDF2

            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)

                text_parts = []
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    text_parts.append(f"# Page {i+1}\n\n{text}\n\n")

                full_text = "\n".join(text_parts)

                metadata = {
                    "page_count": len(reader.pages),
                    "has_tables": False,  # Can't detect with basic extraction
                    "has_images": False,
                    "conversion_method": "pypdf2_fallback"
                }

                return full_text, metadata

        except Exception as e:
            print(f"❌ PDF conversion failed completely: {e}")
            return f"ERROR: Could not convert PDF: {str(e)}", {"conversion_method": "failed"}

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[DocumentChunk]:
        """
        Chunk text into semantic segments

        Args:
            text: Markdown text to chunk
            chunk_size: Target size in characters
            overlap: Overlap between chunks in characters

        Returns:
            List of DocumentChunk objects
        """
        print(f"✂️  Chunking text ({len(text)} chars) with size={chunk_size}, overlap={overlap}")

        chunks = []

        # Split by sections first (headers)
        sections = self._split_by_headers(text)

        chunk_index = 0
        for section_name, section_text in sections:
            # If section is small enough, keep it as one chunk
            if len(section_text) <= chunk_size:
                chunk = DocumentChunk(
                    text=section_text,
                    chunk_index=chunk_index,
                    section=section_name
                )
                chunks.append(chunk)
                chunk_index += 1
            else:
                # Split large sections into smaller chunks
                start = 0
                while start < len(section_text):
                    end = start + chunk_size

                    # Try to break at sentence boundary
                    if end < len(section_text):
                        # Look for sentence end
                        for boundary in ['. ', '\n\n', '\n']:
                            pos = section_text.rfind(boundary, start, end)
                            if pos != -1:
                                end = pos + len(boundary)
                                break

                    chunk_text = section_text[start:end].strip()

                    if chunk_text:
                        chunk = DocumentChunk(
                            text=chunk_text,
                            chunk_index=chunk_index,
                            section=section_name
                        )
                        chunks.append(chunk)
                        chunk_index += 1

                    # Move to next chunk with overlap
                    start = end - overlap

        print(f"✅ Created {len(chunks)} chunks")
        return chunks

    def _split_by_headers(self, text: str) -> List[Tuple[str, str]]:
        """
        Split markdown text by headers

        Args:
            text: Markdown text

        Returns:
            List of (section_name, section_text) tuples
        """
        import re

        # Find all markdown headers (# Title)
        header_pattern = r'^(#{1,6})\s+(.+)$'
        lines = text.split('\n')

        sections = []
        current_section_name = "Introduction"
        current_section_lines = []

        for line in lines:
            match = re.match(header_pattern, line)
            if match:
                # Save previous section
                if current_section_lines:
                    sections.append((
                        current_section_name,
                        '\n'.join(current_section_lines).strip()
                    ))

                # Start new section
                current_section_name = match.group(2)
                current_section_lines = [line]  # Include header in section
            else:
                current_section_lines.append(line)

        # Add final section
        if current_section_lines:
            sections.append((
                current_section_name,
                '\n'.join(current_section_lines).strip()
            ))

        return sections

    def generate_embeddings(
        self,
        texts: List[str],
        model: str = "gemini-embedding-001"
    ) -> List[List[float]]:
        """
        Generate embeddings for text chunks using Gemini API

        Args:
            texts: List of text strings to embed
            model: Embedding model to use

        Returns:
            List of embedding vectors
        """
        print(f"🔢 Generating embeddings for {len(texts)} chunks using {model}")

        try:
            import google.generativeai as genai

            # Configure Gemini API
            genai.configure(api_key=settings.gemini_api_key)

            embeddings = []

            # Generate embeddings in batches
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]

                batch_embeddings = genai.embed_content(
                    model=model,
                    content=batch,
                    task_type="retrieval_document"
                )

                embeddings.extend(batch_embeddings['embedding'])

            print(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            print(f"⚠️  Gemini embedding failed: {e}, using fallback")
            return self._fallback_embeddings(texts)

    def _fallback_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Fallback embedding generation using sentence-transformers

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        try:
            from sentence_transformers import SentenceTransformer

            print("📦 Using sentence-transformers for embeddings")
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = model.encode(texts, show_progress_bar=True)

            return embeddings.tolist()

        except Exception as e:
            print(f"❌ All embedding methods failed: {e}")
            # Return zero vectors as last resort
            return [[0.0] * 384 for _ in texts]

    def store_in_vector_db(
        self,
        document_id: str,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]]
    ) -> str:
        """
        Store chunks and embeddings in ChromaDB

        Args:
            document_id: Unique document identifier
            chunks: List of document chunks
            embeddings: List of embedding vectors

        Returns:
            Path to vector database
        """
        if not CHROMADB_AVAILABLE:
            print("⚠️  ChromaDB not available, skipping vector storage")
            return ""

        print(f"💾 Storing {len(chunks)} chunks in ChromaDB for document {document_id}")

        try:
            # Initialize ChromaDB client
            db_path = self.vector_db_dir / document_id
            db_path.mkdir(parents=True, exist_ok=True)

            client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )

            # Create or get collection
            collection = client.get_or_create_collection(
                name=f"doc_{document_id}",
                metadata={"document_id": document_id}
            )

            # Prepare data for ChromaDB
            ids = [chunk.chunk_id for chunk in chunks]
            texts = [chunk.text for chunk in chunks]
            metadatas = [chunk.to_dict() for chunk in chunks]

            # Add to collection
            collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )

            print(f"✅ Stored {len(chunks)} chunks in vector database")
            return str(db_path)

        except Exception as e:
            print(f"❌ Vector storage failed: {e}")
            return ""

    def prepare_document(
        self,
        pdf_path: Path,
        document_id: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> Dict[str, Any]:
        """
        Complete document preparation pipeline

        Args:
            pdf_path: Path to PDF file
            document_id: Unique document identifier
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks

        Returns:
            Dict with processing results and paths
        """
        try:
            print(f"\n{'='*60}")
            print(f"📚 Preparing document: {pdf_path.name}")
            print(f"{'='*60}\n")

            # Step 1: Convert PDF to Markdown
            markdown_text, conversion_metadata = self.convert_pdf_to_markdown(pdf_path)

            # Save markdown
            markdown_path = self.processed_dir / f"{document_id}.md"
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_text)

            # Step 2: Chunk text
            chunks = self.chunk_text(markdown_text, chunk_size=chunk_size, overlap=overlap)

            # Step 3: Generate embeddings
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = self.generate_embeddings(chunk_texts)

            # Step 4: Store in vector database
            vector_db_path = self.store_in_vector_db(document_id, chunks, embeddings)

            # Step 5: Save metadata
            metadata = {
                "document_id": document_id,
                "pdf_path": str(pdf_path),
                "markdown_path": str(markdown_path),
                "vector_db_path": vector_db_path,
                "chunk_count": len(chunks),
                "conversion_metadata": conversion_metadata,
                "chunking_params": {
                    "chunk_size": chunk_size,
                    "overlap": overlap
                },
                "processing_status": "completed"
            }

            # Save metadata JSON
            metadata_path = self.processed_dir / f"{document_id}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            print(f"\n{'='*60}")
            print(f"✅ Document preparation complete!")
            print(f"   Chunks: {len(chunks)}")
            print(f"   Markdown: {markdown_path}")
            print(f"   Vector DB: {vector_db_path}")
            print(f"{'='*60}\n")

            return metadata

        except Exception as e:
            print(f"\n❌ Document preparation failed: {e}\n")
            return {
                "document_id": document_id,
                "processing_status": "failed",
                "error": str(e)
            }


# Tool metadata
TOOL_INFO = {
    "name": "document_rag_preparer",
    "display_name": "Document RAG Preparer",
    "category": "processing",
    "description": "Convert PDFs to searchable RAG format using Docling and ChromaDB",
    "requires_llm": True,  # For embeddings
    "estimated_cost": 0.001,  # Gemini embedding API
    "avg_time_seconds": 30.0  # Depends on document size
}
