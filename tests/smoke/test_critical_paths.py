"""
Smoke Tests for Critical Paths

Fast sanity checks that verify core functionality is working.
These tests should run in < 30 seconds total.

Purpose:
- Catch broken routes/endpoints
- Verify critical workflows aren't broken
- Quick feedback before running full test suite
- Safe to run in CI on every commit

Note: These tests use mocked LLM calls where possible to stay fast.
Authentication is disabled via conftest.py fixture.
"""

import pytest
from pathlib import Path

# Note: Using client fixture from conftest.py instead of creating here
# This ensures auth is properly disabled via the autouse fixture


class TestAPIHealth:
    """Test that API is running and responding"""

    def test_api_root_responds(self, client):
        """Test that API root endpoint is accessible"""
        response = client.get("/")
        assert response.status_code in [200, 404]  # Either root page or not found

    def test_docs_accessible(self, client):
        """Test that API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_spec_accessible(self, client):
        """Test that OpenAPI spec is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()


class TestPresetEndpoints:
    """Test that preset endpoints are working"""

    def test_list_preset_categories(self, client):
        """Test GET /presets/ - List categories"""
        response = client.get("/presets/")
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_list_presets_in_category(self, client):
        """Test GET /presets/{category} - List presets"""
        # Use a category we know exists
        response = client.get("/presets/story_themes")
        assert response.status_code == 200

        data = response.json()
        assert "category" in data
        assert "count" in data
        assert "presets" in data

    def test_get_batch_presets(self, client):
        """Test GET /presets/batch - Get all presets"""
        response = client.get("/presets/batch")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        # Should have at least one category
        assert len(data) > 0


class TestCharacterEndpoints:
    """Test that character endpoints are working"""

    def test_list_characters(self, client):
        """Test GET /characters/ - List characters"""
        response = client.get("/characters/")
        assert response.status_code == 200

        data = response.json()
        assert "count" in data
        assert "characters" in data

    @pytest.mark.skip(reason="Character presets endpoint not yet implemented")
    def test_get_character_presets(self, client):
        """Test GET /characters/presets - List character presets"""
        response = client.get("/characters/presets")
        assert response.status_code == 200

        # Should return list of character presets
        assert isinstance(response.json(), list)


class TestToolConfigEndpoints:
    """Test that tool configuration endpoints are working"""

    def test_list_tools(self, client):
        """Test GET /tool-configs/tools - List all tools"""
        response = client.get("/tool-configs/tools")
        assert response.status_code == 200

        data = response.json()
        assert "analyzers" in data
        assert "generators" in data
        assert "agents" in data

        # Should have some analyzers
        assert len(data["analyzers"]) > 0

    def test_get_tool_config(self, client):
        """Test GET /tool-configs/tools/{tool_name} - Get tool config"""
        response = client.get("/tool-configs/tools/outfit_analyzer")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "model" in data
        assert "temperature" in data

    def test_list_available_models(self, client):
        """Test GET /tool-configs/models - List available models"""
        response = client.get("/tool-configs/models")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)


class TestJobQueue:
    """Test that job queue is accessible"""

    def test_list_jobs(self, client):
        """Test GET /jobs - List jobs"""
        response = client.get("/jobs")
        assert response.status_code == 200

        # Should return list of jobs (may be empty)
        assert isinstance(response.json(), list)


class TestCriticalWorkflows:
    """Test critical workflows (mocked where possible)"""

    def test_create_story_theme_workflow(self, client):
        """Test creating a story theme (minimal data)"""
        # This tests the full workflow: API → Service → PresetManager → File I/O
        new_theme = {
            "name": "Test Smoke Theme",
            "data": {
                "suggested_name": "Test Smoke Theme",
                "description": "A test theme for smoke testing"
            },
            "notes": "Smoke test"
        }

        response = client.post("/presets/story_themes/", json=new_theme)

        # Should succeed or return specific error
        assert response.status_code in [200, 201, 400, 409]

        # If successful, verify we can retrieve it
        if response.status_code in [200, 201]:
            preset_id = response.json().get("preset_id")
            if preset_id:
                get_response = client.get(f"/presets/story_themes/{preset_id}")
                assert get_response.status_code == 200

                # Clean up
                delete_response = client.delete(f"/presets/story_themes/{preset_id}")
                assert delete_response.status_code in [200, 204]

    def test_update_tool_config_workflow(self, client):
        """Test updating tool configuration workflow"""
        # Save original config
        original = client.get("/tool-configs/tools/outfit_analyzer").json()

        # Update temperature
        update = {"temperature": 0.8}
        response = client.put("/tool-configs/tools/outfit_analyzer", json=update)
        assert response.status_code == 200

        # Verify update
        updated = client.get("/tool-configs/tools/outfit_analyzer").json()
        assert updated["temperature"] == 0.8

        # Restore original (cleanup)
        restore = {"temperature": original["temperature"]}
        client.put("/tool-configs/tools/outfit_analyzer", json=restore)


class TestErrorHandling:
    """Test that errors are handled gracefully"""

    def test_nonexistent_preset_category_404(self, client):
        """Test that requesting nonexistent category returns 404"""
        response = client.get("/presets/nonexistent_category")
        assert response.status_code in [400, 404]

    def test_nonexistent_preset_404(self, client):
        """Test that requesting nonexistent preset returns 404"""
        response = client.get("/presets/story_themes/nonexistent-preset-id")
        assert response.status_code == 404

    def test_nonexistent_tool_404(self, client):
        """Test that requesting nonexistent tool returns 404"""
        response = client.get("/tool-configs/tools/nonexistent_tool")
        assert response.status_code == 404

    def test_invalid_preset_data_400(self, client):
        """Test that invalid preset data returns 400"""
        invalid_data = {
            "name": "",  # Empty name should fail
            "data": {}
        }

        response = client.post("/presets/story_themes/", json=invalid_data)
        assert response.status_code in [400, 409, 422]  # 422 for Pydantic validation, 409 if duplicate exists


class TestTrailingSlashConsistency:
    """Test that trailing slash requirements are met"""

    def test_presets_create_with_trailing_slash(self, client):
        """Test POST /presets/{category}/ (with trailing slash)"""
        data = {
            "name": "Slash Test",
            "data": {"suggested_name": "Slash Test", "description": "Test"},
            "notes": "Test"
        }

        # With trailing slash (correct)
        response = client.post("/presets/story_themes/", json=data)
        assert response.status_code in [200, 201, 400, 409]
        # Should NOT be 307 (redirect)
        assert response.status_code != 307

        # Clean up if created
        if response.status_code in [200, 201]:
            preset_id = response.json().get("preset_id")
            if preset_id:
                client.delete(f"/presets/story_themes/{preset_id}")

    def test_characters_list_with_trailing_slash(self, client):
        """Test GET /characters/ (with trailing slash)"""
        response = client.get("/characters/")
        assert response.status_code == 200
        assert response.status_code != 307


class TestDataIntegrity:
    """Test that data is consistent and not corrupted"""

    def test_preset_roundtrip_preserves_data(self, client):
        """Test that create → read → delete preserves data structure"""
        original_data = {
            "name": "Roundtrip Test",
            "data": {
                "suggested_name": "Roundtrip Test",
                "description": "Testing data integrity",
                "tone": "Test Tone",
                "common_elements": ["element1", "element2"]
            },
            "notes": "Roundtrip test"
        }

        # Create
        create_response = client.post("/presets/story_themes/", json=original_data)
        if create_response.status_code not in [200, 201]:
            pytest.skip("Create failed, skipping roundtrip test")

        preset_id = create_response.json()["preset_id"]

        try:
            # Read
            get_response = client.get(f"/presets/story_themes/{preset_id}")
            assert get_response.status_code == 200

            retrieved_data = get_response.json()

            # Verify data preserved
            assert retrieved_data["suggested_name"] == original_data["data"]["suggested_name"]
            assert retrieved_data["description"] == original_data["data"]["description"]
            assert retrieved_data["tone"] == original_data["data"]["tone"]
            assert retrieved_data["common_elements"] == original_data["data"]["common_elements"]

            # Verify metadata added
            assert "_metadata" in retrieved_data
            assert retrieved_data["_metadata"]["preset_id"] == preset_id

        finally:
            # Clean up
            client.delete(f"/presets/story_themes/{preset_id}")


class TestPerformance:
    """Basic performance sanity checks"""

    def test_batch_load_completes_quickly(self, client):
        """Test that batch preset loading completes in reasonable time"""
        import time

        start = time.time()
        response = client.get("/presets/batch")
        duration = time.time() - start

        assert response.status_code == 200
        # Should complete in < 2 seconds (even with many presets)
        assert duration < 2.0

    def test_list_tools_completes_quickly(self, client):
        """Test that listing tools completes in reasonable time"""
        import time

        start = time.time()
        response = client.get("/tool-configs/tools")
        duration = time.time() - start

        assert response.status_code == 200
        # Should complete in < 1 second
        assert duration < 1.0


if __name__ == "__main__":
    # Allow running smoke tests directly
    pytest.main([__file__, "-v", "--tb=short"])
