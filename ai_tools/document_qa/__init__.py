"""
Document Q&A Tool

Generic question-answer tool supporting multiple context types:
- Document-grounded Q&A (with citations)
- General knowledge Q&A
- Image-based Q&A (future)
- Comparison Q&A (future)
"""

from .tool import DocumentQA, QAResponse, Citation, TOOL_INFO

__all__ = ["DocumentQA", "QAResponse", "Citation", "TOOL_INFO"]
