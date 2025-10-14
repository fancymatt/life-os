"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path)


@pytest.fixture
def presets_dir(temp_dir):
    """Create a temporary presets directory"""
    presets_path = temp_dir / "presets"
    presets_path.mkdir(parents=True)
    return presets_path


@pytest.fixture
def cache_dir(temp_dir):
    """Create a temporary cache directory"""
    cache_path = temp_dir / "cache"
    cache_path.mkdir(parents=True)
    return cache_path


@pytest.fixture
def sample_image_file(temp_dir):
    """Create a sample image file for testing"""
    image_path = temp_dir / "test_image.jpg"
    # Create a minimal valid JPEG (1x1 pixel)
    jpeg_data = bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
        0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
        0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
        0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
        0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C,
        0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
        0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D,
        0x1A, 0x1C, 0x1C, 0x20, 0x24, 0x2E, 0x27, 0x20,
        0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
        0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27,
        0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34,
        0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
        0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4,
        0x00, 0x14, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x03, 0xFF, 0xC4, 0x00, 0x14,
        0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
        0x00, 0x00, 0x3F, 0x00, 0x37, 0xFF, 0xD9
    ])
    image_path.write_bytes(jpeg_data)
    return image_path


@pytest.fixture
def sample_outfit_data():
    """Sample outfit data for testing"""
    return {
        "clothing_items": [
            {
                "item": "suit jacket",
                "fabric": "wool",
                "color": "charcoal black",
                "details": "notch lapel, two-button, slim fit"
            },
            {
                "item": "dress shirt",
                "fabric": "cotton",
                "color": "white",
                "details": "point collar, French cuffs"
            }
        ],
        "style_genre": "modern professional",
        "formality": "business formal",
        "aesthetic": "contemporary minimalist"
    }


@pytest.fixture
def sample_outfit_data_with_metadata(sample_outfit_data):
    """Sample outfit data with metadata"""
    return {
        "_metadata": {
            "created_at": "2025-10-14T14:30:22Z",
            "tool": "outfit-analyzer",
            "tool_version": "1.0.0",
            "source_image": "test_image.jpg",
            "source_hash": "a3f8b92c",
            "model_used": "gemini-2.0-flash",
            "notes": "Test outfit"
        },
        **sample_outfit_data
    }


@pytest.fixture
def sample_visual_style_data():
    """Sample visual style data for testing"""
    return {
        "lighting_setup": "three-point lighting",
        "lighting_quality": "soft, diffused",
        "color_grading": "warm tones, slightly desaturated",
        "color_temperature": "warm",
        "composition": "rule of thirds, centered subject",
        "camera_angle": "eye level",
        "background": "plain white backdrop",
        "mood": "professional and approachable",
        "photography_style": "corporate headshot"
    }
