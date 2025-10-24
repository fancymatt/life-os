"""
Integration Tests for Clothing Items API

Tests critical functionality including test image generation with character lookup.
"""
import pytest


class TestClothingItemsAPI:
    """Test clothing items API endpoints"""

    def test_list_clothing_items(self, client):
        """Verify clothing items list endpoint is accessible"""
        response = client.get("/clothing-items/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "count" in data

    def test_get_categories_summary(self, client):
        """Verify categories summary endpoint works"""
        response = client.get("/clothing-items/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "total_items" in data


class TestClothingItemTestImageGeneration:
    """
    Regression test for clothing item test image generation.

    This test ensures that test image generation from the clothing item entity page
    works correctly with character lookup by ID.

    ISSUE: Test image generation was broken because:
    1. Frontend was passing 'jenny' as character_id (string name)
    2. Backend was trying to call get_character_by_name() which didn't exist

    FIX: Updated to use character UUID lookup with get_character() method.
    """

    def test_generate_test_image_endpoint_exists(self, client):
        """Verify test image generation endpoint exists and accepts requests"""
        # Create a test clothing item first
        create_response = client.post("/clothing-items/", json={
            "category": "tops",
            "item": "Test T-Shirt",
            "fabric": "cotton",
            "color": "blue",
            "details": "Test details"
        })

        assert create_response.status_code == 200, f"Failed to create test item: {create_response.text}"
        item_data = create_response.json()
        item_id = item_data["item_id"]

        # Verify Jenny character exists by querying the database
        characters_response = client.get("/characters/")
        assert characters_response.status_code == 200, "Failed to get characters list"
        characters = characters_response.json()

        # Find Jenny (case-insensitive)
        jenny = None
        if "characters" in characters:
            jenny = next((c for c in characters["characters"] if c.get("name", "").lower() == "jenny"), None)

        # If Jenny doesn't exist, skip this test
        if not jenny:
            pytest.skip("Jenny character not found in database")

        jenny_id = jenny["character_id"]

        # Try to generate test image using Jenny's UUID
        test_image_response = client.post(
            f"/clothing-items/{item_id}/generate-test-image",
            json={
                "character_id": jenny_id,  # Use actual Jenny UUID
                "visual_style": "b1ed9953-a91d-4257-98de-bf8b2f256293"  # White Studio style
            }
        )

        # Should return 200 with job_id (even if job fails later due to missing images)
        assert test_image_response.status_code == 200, f"Test image generation failed: {test_image_response.text}"

        job_data = test_image_response.json()
        assert "job_id" in job_data, "Response missing job_id"
        assert "status" in job_data, "Response missing status"
        assert job_data["status"] == "queued", f"Expected status 'queued', got {job_data['status']}"

        # Cleanup: archive the test item
        client.post(f"/clothing-items/{item_id}/archive")

    def test_generate_test_image_with_invalid_character(self, client):
        """Verify test image generation fails gracefully with invalid character ID"""
        # Create a test clothing item
        create_response = client.post("/clothing-items/", json={
            "category": "tops",
            "item": "Test T-Shirt 2",
            "fabric": "cotton",
            "color": "red",
            "details": "Test details"
        })

        assert create_response.status_code == 200
        item_data = create_response.json()
        item_id = item_data["item_id"]

        # Try with non-existent character ID
        test_image_response = client.post(
            f"/clothing-items/{item_id}/generate-test-image",
            json={
                "character_id": "nonexistent-character-id-12345",
                "visual_style": "b1ed9953-a91d-4257-98de-bf8b2f256293"
            }
        )

        # Should still return 200 (job is queued, failure happens in background)
        assert test_image_response.status_code == 200

        # Job should be created (will fail in background task)
        job_data = test_image_response.json()
        assert "job_id" in job_data

        # Cleanup
        client.post(f"/clothing-items/{item_id}/archive")

    def test_generate_test_image_with_invalid_item(self, client):
        """Verify test image generation fails gracefully with invalid item ID"""
        test_image_response = client.post(
            f"/clothing-items/nonexistent-item-id/generate-test-image",
            json={
                "character_id": "e1f4fe53",  # Jenny's ID (assuming she exists)
                "visual_style": "b1ed9953-a91d-4257-98de-bf8b2f256293"
            }
        )

        # Should still return 200 (job is queued, will fail in background)
        assert test_image_response.status_code == 200
        job_data = test_image_response.json()
        assert "job_id" in job_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
