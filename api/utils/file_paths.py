"""
File Path Utilities

Handles common file path issues like:
- Container path normalization (/uploads/ vs /app/uploads/)
- Path validation
- Existence checks with helpful error messages
"""

from pathlib import Path
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


class FilePathError(Exception):
    """Raised when file path operations fail with detailed error info"""
    pass


def normalize_container_path(path: Union[str, Path]) -> Path:
    """
    Normalize file paths to work correctly inside Docker containers.

    Common issue: Paths saved as "/uploads/file.png" but actual container
    path is "/app/uploads/file.png"

    Args:
        path: File path (may be relative or absolute)

    Returns:
        Normalized Path object with correct container prefix

    Examples:
        "/uploads/image.png" -> "/app/uploads/image.png"
        "/app/uploads/image.png" -> "/app/uploads/image.png"
        "uploads/image.png" -> "/app/uploads/image.png"
    """
    if not path:
        return None

    path = Path(path)

    # Already has /app prefix - return as-is
    if str(path).startswith('/app/'):
        return path

    # Has absolute path starting with known directory
    if str(path).startswith('/uploads/'):
        return Path('/app') / path.relative_to('/')

    if str(path).startswith('/presets/'):
        return Path('/app') / path.relative_to('/')

    if str(path).startswith('/output/'):
        return Path('/app') / path.relative_to('/')

    # Relative path - assume it's relative to /app
    if not path.is_absolute():
        return Path('/app') / path

    # Already absolute and not in known directories - return as-is
    return path


def validate_file_exists(
    path: Union[str, Path],
    description: str = "File",
    auto_normalize: bool = True
) -> Path:
    """
    Validate that a file exists with helpful error messages.

    Args:
        path: File path to check
        description: Human-readable description for error messages
        auto_normalize: If True, try normalizing container paths

    Returns:
        Validated Path object

    Raises:
        FilePathError: With detailed error message if file not found

    Examples:
        >>> validate_file_exists("/uploads/image.png", "Reference image")
        FilePathError: Reference image not found: /uploads/image.png
        Did you mean: /app/uploads/image.png? (exists: True)
    """
    if not path:
        raise FilePathError(f"{description} path is empty or None")

    original_path = Path(path)

    # Try original path first
    if original_path.exists():
        return original_path

    # Try normalized path if enabled
    if auto_normalize:
        normalized = normalize_container_path(path)
        if normalized and normalized.exists():
            logger.warning(
                f"{description} found at normalized path. "
                f"Original: {path} -> Normalized: {normalized}. "
                f"Consider updating stored path to: {normalized}"
            )
            return normalized

    # File not found - provide helpful error
    error_parts = [f"{description} not found: {original_path}"]

    # Check if parent directory exists
    if not original_path.parent.exists():
        error_parts.append(f"Parent directory doesn't exist: {original_path.parent}")

    # Suggest normalized path if different
    if auto_normalize:
        normalized = normalize_container_path(path)
        if normalized != original_path:
            exists = "exists" if normalized.exists() else "also doesn't exist"
            error_parts.append(f"Normalized path: {normalized} ({exists})")

    # List similar files in parent directory
    if original_path.parent.exists():
        similar_files = list(original_path.parent.glob(f"*{original_path.stem}*"))
        if similar_files:
            error_parts.append(f"Similar files in {original_path.parent}:")
            for f in similar_files[:5]:  # Show first 5
                error_parts.append(f"  - {f.name}")

    raise FilePathError("\n".join(error_parts))


def get_app_relative_path(path: Union[str, Path]) -> str:
    """
    Get path relative to /app for storage in database/config files.

    When storing file paths in configs or database, use /app-relative paths
    so they work consistently whether accessed from inside or outside container.

    Args:
        path: Absolute file path

    Returns:
        String path relative to /app (e.g., "uploads/image.png")

    Examples:
        "/app/uploads/image.png" -> "uploads/image.png"
        "/uploads/image.png" -> "uploads/image.png"
    """
    path = Path(path)

    # Remove /app prefix if present
    if str(path).startswith('/app/'):
        return str(path.relative_to('/app'))

    # Remove leading slash if present
    if str(path).startswith('/'):
        return str(path).lstrip('/')

    return str(path)


def ensure_app_prefix(path: Union[str, Path]) -> str:
    """
    Ensure path has /app prefix for use in API responses and storage.

    This is the opposite of get_app_relative_path - adds /app prefix
    for paths that will be used by the visualizer or other internal tools.

    Args:
        path: File path (with or without /app prefix)

    Returns:
        String path with /app prefix

    Examples:
        "uploads/image.png" -> "/app/uploads/image.png"
        "/uploads/image.png" -> "/app/uploads/image.png"
        "/app/uploads/image.png" -> "/app/uploads/image.png"
    """
    normalized = normalize_container_path(path)
    return str(normalized) if normalized else None


# Convenience function for the most common use case
def fix_upload_path(path: Optional[str]) -> Optional[str]:
    """
    Quick fix for uploaded file paths.

    Use this when you have a path from user upload that needs to be
    normalized for internal use.

    Args:
        path: Uploaded file path (may be None)

    Returns:
        Normalized path with /app prefix, or None if input was None
    """
    if not path:
        return None
    return ensure_app_prefix(path)
