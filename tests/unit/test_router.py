"""
Tests for ai-tools/shared/router.py (LLMRouter)

Note: These tests focus on router initialization and configuration.
Integration tests that make actual API calls are in tests/integration/
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_tools.shared.router import (
    LLMRouter,
    RouterConfig,
)
from ai_capabilities.specs import OutfitSpec


@pytest.mark.unit
class TestRouterConfig:
    """Tests for RouterConfig"""

    def test_init_with_default_path(self):
        """Test initialization with default config path"""
        config = RouterConfig()
        assert config.config_path is not None
        assert isinstance(config.config, dict)

    def test_get_model_for_tool(self):
        """Test getting model for a specific tool"""
        config = RouterConfig()

        # Should return default or configured model
        model = config.get_model_for_tool("outfit_analyzer")
        assert isinstance(model, str)
        assert len(model) > 0

    def test_get_routing_config(self):
        """Test getting routing configuration"""
        config = RouterConfig()

        routing = config.get_routing_config()
        assert isinstance(routing, dict)
        assert "timeout" in routing
        assert "retries" in routing


@pytest.mark.unit
class TestLLMRouter:
    """Tests for LLMRouter"""

    def test_init_with_default_model(self):
        """Test initialization with default model"""
        router = LLMRouter()
        assert router.model == "gemini-2.0-flash"
        assert router.config is not None

    def test_init_with_custom_model(self):
        """Test initialization with custom model"""
        router = LLMRouter(model="gpt-4o")
        assert router.model == "gpt-4o"

    def test_encode_image(self, sample_image_file):
        """Test encoding image to base64"""
        router = LLMRouter()
        encoded = router.encode_image(sample_image_file)

        assert isinstance(encoded, str)
        assert len(encoded) > 0

    def test_encode_nonexistent_image(self, temp_dir):
        """Test encoding nonexistent image raises error"""
        router = LLMRouter()
        nonexistent = temp_dir / "nonexistent.jpg"

        with pytest.raises(FileNotFoundError):
            router.encode_image(nonexistent)

    def test_create_image_message(self, sample_image_file):
        """Test creating image message for API"""
        router = LLMRouter()
        message = router.create_image_message(sample_image_file)

        assert isinstance(message, dict)
        assert "type" in message
        assert message["type"] == "image_url"
        assert "image_url" in message

    def test_create_image_message_with_nonexistent_file(self, temp_dir):
        """Test creating image message with nonexistent file"""
        router = LLMRouter()
        nonexistent = temp_dir / "nonexistent.jpg"

        with pytest.raises(FileNotFoundError):
            router.create_image_message(nonexistent)

    @patch('ai_tools.shared.router.completion')
    def test_call_text_only(self, mock_completion):
        """Test calling LLM with text only"""
        # Setup mock
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_completion.return_value = mock_response

        router = LLMRouter()
        response = router.call("Test prompt")

        assert response == "Test response"
        mock_completion.assert_called_once()

        # Verify call arguments
        call_args = mock_completion.call_args
        assert call_args[1]["model"] == "gemini-2.0-flash"
        assert len(call_args[1]["messages"]) == 1
        assert call_args[1]["messages"][0]["role"] == "user"

    @patch('ai_tools.shared.router.completion')
    def test_call_with_system_prompt(self, mock_completion):
        """Test calling LLM with system prompt"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_completion.return_value = mock_response

        router = LLMRouter()
        response = router.call("User prompt", system="System prompt")

        # Verify system message was included
        call_args = mock_completion.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "System prompt"

    @patch('ai_tools.shared.router.completion')
    def test_call_with_custom_model(self, mock_completion):
        """Test calling with custom model"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_completion.return_value = mock_response

        router = LLMRouter()
        response = router.call("Test prompt", model="gpt-4o")

        # Verify custom model was used
        call_args = mock_completion.call_args
        assert call_args[1]["model"] == "gpt-4o"

    @patch('ai_tools.shared.router.completion')
    def test_call_structured(self, mock_completion, sample_outfit_data):
        """Test calling with structured output"""
        # Setup mock to return JSON
        import json
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(sample_outfit_data)
        mock_completion.return_value = mock_response

        router = LLMRouter()
        result = router.call_structured(
            "Analyze this outfit",
            OutfitSpec
        )

        assert isinstance(result, OutfitSpec)
        assert result.style_genre == "modern professional"

    @patch('ai_tools.shared.router.completion')
    def test_call_structured_with_markdown_json(self, mock_completion, sample_outfit_data):
        """Test call_structured handles JSON in markdown code blocks"""
        import json

        # Mock returns JSON wrapped in markdown
        mock_response = Mock()
        mock_response.choices = [Mock()]
        json_str = json.dumps(sample_outfit_data)
        mock_response.choices[0].message.content = f"```json\n{json_str}\n```"
        mock_completion.return_value = mock_response

        router = LLMRouter()
        result = router.call_structured(
            "Analyze this outfit",
            OutfitSpec
        )

        assert isinstance(result, OutfitSpec)
        assert result.style_genre == "modern professional"

    def test_get_cost_estimate(self):
        """Test getting cost estimate"""
        router = LLMRouter()

        # Test with known model (may return 0 if not in litellm's database)
        cost = router.get_cost_estimate("gpt-4o", 1000, 500)
        assert isinstance(cost, float)
        assert cost >= 0


@pytest.mark.unit
class TestConvenienceFunctions:
    """Tests for convenience functions"""

    @patch('ai_tools.shared.router.completion')
    def test_call_llm(self, mock_completion):
        """Test call_llm convenience function"""
        from ai_tools.shared.router import call_llm

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_completion.return_value = mock_response

        response = call_llm("Test prompt", model="gemini-2.0-flash")
        assert response == "Test response"

    @patch('ai_tools.shared.router.completion')
    def test_call_llm_structured(self, mock_completion, sample_outfit_data):
        """Test call_llm_structured convenience function"""
        from ai_tools.shared.router import call_llm_structured
        import json

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(sample_outfit_data)
        mock_completion.return_value = mock_response

        result = call_llm_structured(
            "Test prompt",
            OutfitSpec,
            model="gemini-2.0-flash"
        )

        assert isinstance(result, OutfitSpec)
