"""
Cache Manager

Manages ephemeral cache for analysis results with TTL and file hash validation.
Cache is organized by tool type and uses file hashes as keys.
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Type, Dict, Any, List, Union
from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta


class CacheEntry(BaseModel):
    """Cache entry with metadata"""
    key: str
    tool_type: str
    data: Dict[str, Any]
    created_at: datetime
    expires_at: datetime
    source_file: Optional[str] = None
    source_hash: Optional[str] = None


class CacheStats(BaseModel):
    """Statistics about cache usage"""
    total_entries: int
    entries_by_type: Dict[str, int]
    total_size_bytes: int
    oldest_entry: Optional[datetime] = None
    newest_entry: Optional[datetime] = None


class CacheManager:
    """
    Manages ephemeral cache with TTL

    Cache files are organized by tool type:
    - cache/outfits/{hash}.json
    - cache/visual-styles/{hash}.json
    - etc.

    Each cache entry includes:
    - Cached data
    - Creation timestamp
    - Expiration timestamp (TTL)
    - Source file hash for validation
    """

    def __init__(
        self,
        cache_root: Optional[Path] = None,
        default_ttl: int = 604800  # 7 days in seconds
    ):
        """
        Initialize the cache manager

        Args:
            cache_root: Root directory for cache (default: project_root/cache)
            default_ttl: Default TTL in seconds (default: 7 days)
        """
        if cache_root is None:
            # Default to project root / cache
            self.cache_root = Path(__file__).parent.parent.parent / "cache"
        else:
            self.cache_root = Path(cache_root)

        self.default_ttl = default_ttl

        # Ensure cache root exists
        self.cache_root.mkdir(parents=True, exist_ok=True)

        # Create manifest file for tracking
        self.manifest_path = self.cache_root / "manifest.json"

    def _get_cache_dir(self, tool_type: str) -> Path:
        """Get the directory for a specific tool type's cache"""
        cache_dir = self.cache_root / tool_type
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def _get_cache_path(self, tool_type: str, key: str) -> Path:
        """Get the full path to a cache file"""
        return self._get_cache_dir(tool_type) / f"{key}.json"

    def compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of a file

        Args:
            file_path: Path to file

        Returns:
            Hex string of hash (first 16 chars for brevity)
        """
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            # Read in chunks for memory efficiency
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)

        # Return first 16 chars of hash
        return sha256.hexdigest()[:16]

    def compute_key(self, file_path: Path) -> str:
        """
        Compute cache key for a file (alias for compute_file_hash)

        Args:
            file_path: Path to file

        Returns:
            Cache key string
        """
        return self.compute_file_hash(file_path)

    def get(
        self,
        tool_type: str,
        key: str,
        spec_class: Optional[Type[BaseModel]] = None
    ) -> Optional[Union[BaseModel, Dict[str, Any]]]:
        """
        Get a value from cache

        Args:
            tool_type: Type of tool (e.g., "outfits")
            key: Cache key (usually file hash)
            spec_class: Optional Pydantic class to parse into

        Returns:
            Cached data (as Pydantic model or dict) or None if not found/expired
        """
        cache_path = self._get_cache_path(tool_type, key)

        if not cache_path.exists():
            return None

        # Load cache entry
        with open(cache_path, 'r') as f:
            entry_data = json.load(f)

        try:
            entry = CacheEntry.model_validate(entry_data)
        except ValidationError:
            # Invalid cache entry, delete it
            cache_path.unlink()
            return None

        # Check if expired
        if datetime.now() > entry.expires_at:
            # Expired, delete it
            cache_path.unlink()
            return None

        # Return data (parse into spec if provided)
        if spec_class:
            try:
                return spec_class.model_validate(entry.data)
            except ValidationError:
                # Data doesn't match spec, delete cache
                cache_path.unlink()
                return None
        else:
            return entry.data

    def set(
        self,
        tool_type: str,
        key: str,
        data: Union[BaseModel, Dict[str, Any]],
        ttl: Optional[int] = None,
        source_file: Optional[Path] = None
    ) -> Path:
        """
        Set a value in cache

        Args:
            tool_type: Type of tool
            key: Cache key
            data: Data to cache (Pydantic model or dict)
            ttl: Time to live in seconds (None = use default)
            source_file: Optional source file path

        Returns:
            Path to cache file
        """
        ttl = ttl or self.default_ttl

        # Convert data to dict if it's a Pydantic model
        if isinstance(data, BaseModel):
            data_dict = data.model_dump(mode='json')
        else:
            data_dict = data

        # Compute source hash if file provided
        source_hash = None
        source_file_str = None
        if source_file:
            source_hash = self.compute_file_hash(source_file)
            source_file_str = str(source_file)

        # Create cache entry
        entry = CacheEntry(
            key=key,
            tool_type=tool_type,
            data=data_dict,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=ttl),
            source_file=source_file_str,
            source_hash=source_hash
        )

        # Save to file
        cache_path = self._get_cache_path(tool_type, key)
        with open(cache_path, 'w') as f:
            json.dump(entry.model_dump(mode='json'), f, indent=2, default=str)

        return cache_path

    def get_for_file(
        self,
        tool_type: str,
        file_path: Path,
        spec_class: Optional[Type[BaseModel]] = None
    ) -> Optional[Union[BaseModel, Dict[str, Any]]]:
        """
        Get cached data for a specific file (with hash validation)

        Args:
            tool_type: Type of tool
            file_path: Source file path
            spec_class: Optional Pydantic class to parse into

        Returns:
            Cached data or None if not found/expired/hash mismatch
        """
        if not file_path.exists():
            return None

        # Compute key from file
        key = self.compute_key(file_path)

        # Get from cache
        result = self.get(tool_type, key, spec_class)

        if result is None:
            return None

        # Validate hash matches (if we have the cache entry)
        cache_path = self._get_cache_path(tool_type, key)
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                entry_data = json.load(f)
                entry = CacheEntry.model_validate(entry_data)

            # Recompute hash and compare
            current_hash = self.compute_file_hash(file_path)
            if entry.source_hash and entry.source_hash != current_hash:
                # File changed, invalidate cache
                cache_path.unlink()
                return None

        return result

    def set_for_file(
        self,
        tool_type: str,
        file_path: Path,
        data: Union[BaseModel, Dict[str, Any]],
        ttl: Optional[int] = None
    ) -> Path:
        """
        Cache data for a specific file

        Args:
            tool_type: Type of tool
            file_path: Source file path
            data: Data to cache
            ttl: Time to live in seconds

        Returns:
            Path to cache file
        """
        key = self.compute_key(file_path)
        return self.set(tool_type, key, data, ttl=ttl, source_file=file_path)

    def delete(self, tool_type: str, key: str) -> bool:
        """
        Delete a cache entry

        Args:
            tool_type: Type of tool
            key: Cache key

        Returns:
            True if deleted, False if didn't exist
        """
        cache_path = self._get_cache_path(tool_type, key)

        if not cache_path.exists():
            return False

        cache_path.unlink()
        return True

    def clear(self, tool_type: Optional[str] = None) -> int:
        """
        Clear cache entries

        Args:
            tool_type: Type of tool to clear (None = clear all)

        Returns:
            Number of entries deleted
        """
        count = 0

        if tool_type:
            # Clear specific tool type
            cache_dir = self._get_cache_dir(tool_type)
            if cache_dir.exists():
                for cache_file in cache_dir.glob("*.json"):
                    cache_file.unlink()
                    count += 1
        else:
            # Clear all cache
            for tool_dir in self.cache_root.iterdir():
                if tool_dir.is_dir() and tool_dir.name != "manifest.json":
                    for cache_file in tool_dir.glob("*.json"):
                        cache_file.unlink()
                        count += 1

        return count

    def clean_expired(self) -> int:
        """
        Remove all expired cache entries

        Returns:
            Number of entries removed
        """
        count = 0
        now = datetime.now()

        # Scan all cache directories
        for tool_dir in self.cache_root.iterdir():
            if not tool_dir.is_dir():
                continue

            for cache_file in tool_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        entry_data = json.load(f)
                        entry = CacheEntry.model_validate(entry_data)

                    if now > entry.expires_at:
                        cache_file.unlink()
                        count += 1
                except (json.JSONDecodeError, ValidationError):
                    # Invalid entry, delete it
                    cache_file.unlink()
                    count += 1

        return count

    def stats(self) -> CacheStats:
        """
        Get cache statistics

        Returns:
            CacheStats object
        """
        total_entries = 0
        entries_by_type: Dict[str, int] = {}
        total_size_bytes = 0
        oldest_entry: Optional[datetime] = None
        newest_entry: Optional[datetime] = None

        # Scan all cache directories
        for tool_dir in self.cache_root.iterdir():
            if not tool_dir.is_dir():
                continue

            tool_type = tool_dir.name
            type_count = 0

            for cache_file in tool_dir.glob("*.json"):
                total_entries += 1
                type_count += 1
                total_size_bytes += cache_file.stat().st_size

                # Read entry for timestamps
                try:
                    with open(cache_file, 'r') as f:
                        entry_data = json.load(f)
                        entry = CacheEntry.model_validate(entry_data)

                    if oldest_entry is None or entry.created_at < oldest_entry:
                        oldest_entry = entry.created_at

                    if newest_entry is None or entry.created_at > newest_entry:
                        newest_entry = entry.created_at
                except (json.JSONDecodeError, ValidationError):
                    pass

            if type_count > 0:
                entries_by_type[tool_type] = type_count

        return CacheStats(
            total_entries=total_entries,
            entries_by_type=entries_by_type,
            total_size_bytes=total_size_bytes,
            oldest_entry=oldest_entry,
            newest_entry=newest_entry
        )

    def list_entries(self, tool_type: str) -> List[Dict[str, Any]]:
        """
        List all cache entries for a tool type

        Args:
            tool_type: Type of tool

        Returns:
            List of entry info dicts
        """
        entries = []
        cache_dir = self._get_cache_dir(tool_type)

        if not cache_dir.exists():
            return entries

        for cache_file in cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    entry_data = json.load(f)
                    entry = CacheEntry.model_validate(entry_data)

                entries.append({
                    "key": entry.key,
                    "source_file": entry.source_file,
                    "created_at": entry.created_at.isoformat(),
                    "expires_at": entry.expires_at.isoformat(),
                    "expired": datetime.now() > entry.expires_at,
                    "size_bytes": cache_file.stat().st_size
                })
            except (json.JSONDecodeError, ValidationError):
                pass

        return sorted(entries, key=lambda x: x["created_at"], reverse=True)


# Convenience functions

_default_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get the default cache manager (singleton)"""
    global _default_manager
    if _default_manager is None:
        _default_manager = CacheManager()
    return _default_manager


def get_cached(
    tool_type: str,
    file_path: Path,
    spec_class: Optional[Type[BaseModel]] = None
) -> Optional[Union[BaseModel, Dict[str, Any]]]:
    """Quick function to get cached data for a file"""
    return get_cache_manager().get_for_file(tool_type, file_path, spec_class)


def set_cached(
    tool_type: str,
    file_path: Path,
    data: Union[BaseModel, Dict[str, Any]],
    ttl: Optional[int] = None
) -> Path:
    """Quick function to cache data for a file"""
    return get_cache_manager().set_for_file(tool_type, file_path, data, ttl)
