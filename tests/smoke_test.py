"""
Smoke Tests - Quick checks that critical functionality works

Run these before asking the user to test:
    pytest tests/smoke_test.py -v
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestAPIHealth:
    """Verify API is running and healthy"""

    def test_health_endpoint(self):
        """Health check returns 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestCriticalEndpoints:
    """Verify critical API endpoints return expected responses"""

    def test_jobs_list(self):
        """Jobs endpoint is accessible"""
        response = client.get("/jobs")
        assert response.status_code in [200, 401]  # 200 if no auth, 401 if auth required

    def test_story_workflow_endpoint_exists(self):
        """Story workflow endpoint exists (may require auth)"""
        response = client.post("/workflows/story", json={
            "title": "Test Story",
            "theme": "Adventure"
        })
        # Accept any of: 200 (success), 401 (needs auth), 422 (validation error)
        assert response.status_code in [200, 401, 422]

    def test_characters_list(self):
        """Characters endpoint is accessible"""
        response = client.get("/characters/")
        assert response.status_code in [200, 401]


class TestModelConfiguration:
    """Verify model configuration is valid"""

    def test_models_yaml_exists(self):
        """models.yaml file exists"""
        import os
        assert os.path.exists("configs/models.yaml")

    def test_gemini_model_names(self):
        """Verify Gemini model names are correct"""
        import yaml
        with open("configs/models.yaml") as f:
            config = yaml.safe_load(f)

        # Image generation models should use gemini-2.5-flash-image
        image_tools = [
            "outfit_generator",
            "style_transfer_generator",
            "modular_image_generator",
            "art_style_generator",
            "style_guide_generator"
        ]

        for tool in image_tools:
            if tool in config:
                model = config[tool]
                # Should be the dedicated image generation model
                assert "gemini-2.5-flash-image" in model, \
                    f"{tool} uses {model}, should use gemini-2.5-flash-image"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
