"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime
from fastapi.testclient import TestClient


# Disable authentication for tests by default
@pytest.fixture(scope="session", autouse=True)
def disable_auth_for_tests():
    """
    Disable authentication for all tests by default.

    This allows tests to run without needing JWT tokens.
    Individual tests can override this by setting REQUIRE_AUTH=true.
    """
    os.environ["REQUIRE_AUTH"] = "false"
    yield
    # Restore after tests (though not strictly necessary)
    os.environ.pop("REQUIRE_AUTH", None)


@pytest.fixture
def client():
    """
    Test client for API requests

    Returns TestClient with authentication disabled.
    """
    from api.main import app
    return TestClient(app)


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
        "suggested_name": "Business Professional Suit",
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
        "suggested_name": "Corporate Headshot Style",
        "subject_action": "Standing upright with confident posture, facing the camera directly. Head held high with chin slightly tilted down, creating an approachable yet authoritative stance. Eyes making direct contact with the lens, conveying engagement and professionalism. Shoulders squared and relaxed, not hunched. Arms positioned naturally at sides, not crossing or in pockets. Body language open and welcoming, projecting competence and trustworthiness. Slight forward lean suggesting attentiveness and engagement with the viewer.",
        "setting": "Professional studio environment with clean, uncluttered aesthetic. Crisp white backdrop extending seamlessly from floor to ceiling, providing neutral canvas that eliminates distractions. Background completely even without shadows, gradients, or texture variations. Studio walls and floor blend imperceptibly, creating infinity curve effect. Lighting equipment positioned strategically but invisible in frame. Climate-controlled space maintaining consistent temperature and humidity. Acoustically treated to minimize echo and ambient noise during direction. Professional-grade backdrop paper or seamless material ensuring perfect uniformity.",
        "framing": "medium shot",
        "camera_angle": "eye level",
        "lighting": "Classic three-point lighting setup with key light positioned at 45-degree angle from subject, providing main illumination and defining facial structure with gentle shadows. Fill light opposite key light at lower intensity, softening shadows without eliminating them entirely, maintaining dimension. Back light (rim light) positioned behind and above subject, separating them from background and adding subtle halo effect around edges. All lights softbox-modified for even, diffused quality. Color temperature balanced at 5500K daylight standard. Light ratio approximately 3:1 between key and fill, creating professional depth while remaining flattering.",
        "mood": "Professional, confident, and approachable atmosphere that balances authority with warmth. Image conveys competence and trustworthiness without appearing cold or distant. Lighting and composition work together to create sense of clarity and focus. Overall feeling suggests reliability and expertise while maintaining human connection. Environment feels controlled and polished yet authentic, avoiding overly sterile or artificial appearance. Emotional tone projects readiness, capability, and engagement without intimidation."
    }
