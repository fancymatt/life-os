"""
Tests for ai-tools/shared/cache.py (CacheManager)
"""

import pytest
import time
from pathlib import Path
from datetime import datetime, timedelta

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.shared.cache import (
    CacheManager,
    CacheEntry,
    CacheStats,
)
from ai_capabilities.specs import OutfitSpec, VisualStyleSpec


@pytest.mark.unit
class TestCacheManager:
    """Tests for CacheManager"""

    def test_init_with_custom_root(self, cache_dir):
        """Test initialization with custom cache root"""
        manager = CacheManager(cache_root=cache_dir)
        assert manager.cache_root == cache_dir
        assert manager.cache_root.exists()
        assert manager.default_ttl == 604800  # 7 days

    def test_init_with_custom_ttl(self, cache_dir):
        """Test initialization with custom TTL"""
        manager = CacheManager(cache_root=cache_dir, default_ttl=3600)
        assert manager.default_ttl == 3600

    def test_compute_file_hash(self, cache_dir, sample_image_file):
        """Test computing file hash"""
        manager = CacheManager(cache_root=cache_dir)
        hash1 = manager.compute_file_hash(sample_image_file)

        assert isinstance(hash1, str)
        assert len(hash1) == 16  # First 16 chars of SHA256

        # Hash should be deterministic
        hash2 = manager.compute_file_hash(sample_image_file)
        assert hash1 == hash2

    def test_compute_file_hash_changes_with_content(self, cache_dir, temp_dir):
        """Test that hash changes when file content changes"""
        manager = CacheManager(cache_root=cache_dir)

        # Create two different files
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"

        file1.write_text("content 1")
        file2.write_text("content 2")

        hash1 = manager.compute_file_hash(file1)
        hash2 = manager.compute_file_hash(file2)

        assert hash1 != hash2

    def test_set_and_get(self, cache_dir, sample_outfit_data):
        """Test setting and getting cache"""
        manager = CacheManager(cache_root=cache_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        # Set cache
        cache_path = manager.set("outfits", "test_key", outfit)
        assert cache_path.exists()

        # Get cache
        cached_outfit = manager.get("outfits", "test_key", OutfitSpec)
        assert cached_outfit is not None
        assert cached_outfit.style_genre == outfit.style_genre

    def test_get_nonexistent(self, cache_dir):
        """Test getting nonexistent cache entry"""
        manager = CacheManager(cache_root=cache_dir)

        result = manager.get("outfits", "nonexistent", OutfitSpec)
        assert result is None

    def test_get_expired(self, cache_dir, sample_outfit_data):
        """Test that expired cache returns None"""
        manager = CacheManager(cache_root=cache_dir, default_ttl=1)  # 1 second TTL
        outfit = OutfitSpec(**sample_outfit_data)

        # Set cache
        manager.set("outfits", "test_key", outfit)

        # Wait for expiration
        time.sleep(2)

        # Should return None
        result = manager.get("outfits", "test_key", OutfitSpec)
        assert result is None

    def test_set_with_custom_ttl(self, cache_dir, sample_outfit_data):
        """Test setting cache with custom TTL"""
        manager = CacheManager(cache_root=cache_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        manager.set("outfits", "test_key", outfit, ttl=3600)

        # Verify cache entry has correct expiration
        cache_path = manager._get_cache_path("outfits", "test_key")
        import json
        with open(cache_path) as f:
            entry_data = json.load(f)
            entry = CacheEntry.model_validate(entry_data)

        # Check expiration is approximately 1 hour from now
        expected_expires = datetime.now() + timedelta(seconds=3600)
        time_diff = abs((entry.expires_at - expected_expires).total_seconds())
        assert time_diff < 5  # Within 5 seconds

    def test_set_for_file(self, cache_dir, sample_image_file, sample_outfit_data):
        """Test setting cache for a specific file"""
        manager = CacheManager(cache_root=cache_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        cache_path = manager.set_for_file("outfits", sample_image_file, outfit)
        assert cache_path.exists()

        # Verify source hash is stored
        import json
        with open(cache_path) as f:
            entry_data = json.load(f)
            entry = CacheEntry.model_validate(entry_data)

        assert entry.source_hash is not None
        assert entry.source_file == str(sample_image_file)

    def test_get_for_file(self, cache_dir, sample_image_file, sample_outfit_data):
        """Test getting cache for a specific file"""
        manager = CacheManager(cache_root=cache_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        # Set cache
        manager.set_for_file("outfits", sample_image_file, outfit)

        # Get cache
        cached_outfit = manager.get_for_file("outfits", sample_image_file, OutfitSpec)
        assert cached_outfit is not None
        assert cached_outfit.style_genre == outfit.style_genre

    def test_get_for_file_with_hash_validation(self, cache_dir, sample_image_file, sample_outfit_data):
        """Test that cache is invalidated when file changes"""
        manager = CacheManager(cache_root=cache_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        # Set cache
        manager.set_for_file("outfits", sample_image_file, outfit)

        # Modify file
        with open(sample_image_file, 'ab') as f:
            f.write(b'modified')

        # Should return None due to hash mismatch
        cached_outfit = manager.get_for_file("outfits", sample_image_file, OutfitSpec)
        assert cached_outfit is None

    def test_delete(self, cache_dir, sample_outfit_data):
        """Test deleting cache entry"""
        manager = CacheManager(cache_root=cache_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        manager.set("outfits", "test_key", outfit)
        assert manager.get("outfits", "test_key", OutfitSpec) is not None

        # Delete
        result = manager.delete("outfits", "test_key")
        assert result is True
        assert manager.get("outfits", "test_key", OutfitSpec) is None

        # Delete nonexistent
        result = manager.delete("outfits", "test_key")
        assert result is False

    def test_clear_specific_type(self, cache_dir, sample_outfit_data, sample_visual_style_data):
        """Test clearing cache for specific tool type"""
        manager = CacheManager(cache_root=cache_dir)
        outfit = OutfitSpec(**sample_outfit_data)
        style = VisualStyleSpec(**sample_visual_style_data)

        # Set multiple cache entries
        manager.set("outfits", "key1", outfit)
        manager.set("outfits", "key2", outfit)
        manager.set("visual-styles", "key3", style)

        # Clear outfits only
        count = manager.clear("outfits")
        assert count == 2

        # Outfits should be gone
        assert manager.get("outfits", "key1", OutfitSpec) is None
        assert manager.get("outfits", "key2", OutfitSpec) is None

        # Visual styles should remain
        assert manager.get("visual-styles", "key3", VisualStyleSpec) is not None

    def test_clear_all(self, cache_dir, sample_outfit_data, sample_visual_style_data):
        """Test clearing all cache"""
        manager = CacheManager(cache_root=cache_dir)
        outfit = OutfitSpec(**sample_outfit_data)
        style = VisualStyleSpec(**sample_visual_style_data)

        # Set multiple cache entries
        manager.set("outfits", "key1", outfit)
        manager.set("visual-styles", "key2", style)

        # Clear all
        count = manager.clear()
        assert count == 2

        # All should be gone
        assert manager.get("outfits", "key1", OutfitSpec) is None
        assert manager.get("visual-styles", "key2", VisualStyleSpec) is None

    def test_clean_expired(self, cache_dir, sample_outfit_data):
        """Test cleaning expired entries"""
        manager = CacheManager(cache_root=cache_dir, default_ttl=1)
        outfit = OutfitSpec(**sample_outfit_data)

        # Set multiple entries
        manager.set("outfits", "key1", outfit)
        manager.set("outfits", "key2", outfit)

        # Wait for expiration
        time.sleep(2)

        # Clean expired
        count = manager.clean_expired()
        assert count == 2

    def test_stats(self, cache_dir, sample_outfit_data, sample_visual_style_data):
        """Test getting cache statistics"""
        manager = CacheManager(cache_root=cache_dir)
        outfit = OutfitSpec(**sample_outfit_data)
        style = VisualStyleSpec(**sample_visual_style_data)

        # Initially empty
        stats = manager.stats()
        assert stats.total_entries == 0

        # Add some entries
        manager.set("outfits", "key1", outfit)
        manager.set("outfits", "key2", outfit)
        manager.set("visual-styles", "key3", style)

        # Check stats
        stats = manager.stats()
        assert stats.total_entries == 3
        assert stats.entries_by_type["outfits"] == 2
        assert stats.entries_by_type["visual-styles"] == 1
        assert stats.total_size_bytes > 0
        assert stats.oldest_entry is not None
        assert stats.newest_entry is not None

    def test_list_entries(self, cache_dir, sample_outfit_data):
        """Test listing cache entries"""
        manager = CacheManager(cache_root=cache_dir)
        outfit = OutfitSpec(**sample_outfit_data)

        # Initially empty
        entries = manager.list_entries("outfits")
        assert len(entries) == 0

        # Add entries
        manager.set("outfits", "key1", outfit)
        manager.set("outfits", "key2", outfit)

        # List
        entries = manager.list_entries("outfits")
        assert len(entries) == 2

        # Check entry structure
        entry = entries[0]
        assert "key" in entry
        assert "created_at" in entry
        assert "expires_at" in entry
        assert "expired" in entry
        assert "size_bytes" in entry

    def test_cache_with_dict(self, cache_dir):
        """Test caching dict data (not Pydantic model)"""
        manager = CacheManager(cache_root=cache_dir)

        data = {"test": "data", "number": 42}
        manager.set("test", "key1", data)

        # Get without spec class
        cached_data = manager.get("test", "key1")
        assert cached_data is not None
        assert cached_data["test"] == "data"
        assert cached_data["number"] == 42

    def test_cache_entry_model(self):
        """Test CacheEntry Pydantic model"""
        entry = CacheEntry(
            key="test_key",
            tool_type="outfits",
            data={"test": "data"},
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7)
        )

        assert entry.key == "test_key"
        assert entry.tool_type == "outfits"
        assert entry.data["test"] == "data"

    def test_cache_stats_model(self):
        """Test CacheStats Pydantic model"""
        stats = CacheStats(
            total_entries=10,
            entries_by_type={"outfits": 5, "styles": 5},
            total_size_bytes=1024,
            oldest_entry=datetime.now(),
            newest_entry=datetime.now()
        )

        assert stats.total_entries == 10
        assert stats.total_size_bytes == 1024


@pytest.mark.unit
class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_get_cache_manager_singleton(self):
        """Test that get_cache_manager returns singleton"""
        from ai_tools.shared.cache import get_cache_manager

        manager1 = get_cache_manager()
        manager2 = get_cache_manager()

        assert manager1 is manager2
