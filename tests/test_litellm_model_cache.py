"""Unit tests for the litellm_model_cache module."""

import os
import json
import pytest
from unittest.mock import patch, mock_open
from klingon_tools.litellm_model_cache import (
    fetch_model_data,
    filter_models,
    update_env_variable,
    get_supported_models,
)


@pytest.fixture
def mock_response():
    """Fixture to mock the requests.get response."""
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("HTTP Error")

    return MockResponse({"model1": {}, "model2": {}}, 200)


@pytest.fixture
def mock_file_content():
    """Fixture to provide mock file content."""
    return json.dumps({"model1": {}, "model2": {}})


def test_fetch_model_data(mock_response, mock_file_content):
    """Test the fetch_model_data function."""
    with patch("os.path.exists") as mock_exists:
        with patch("requests.get", return_value=mock_response):
            with patch(
                "builtins.open", mock_open(
                    read_data=mock_file_content
                )
            ) as mock_file:
                # Test when cache file exists
                mock_exists.return_value = True
                result = fetch_model_data()
                assert result == {"model1": {}, "model2": {}}
                mock_file.assert_called_once_with(
                    "/tmp/klingon_models_cache.json", "r", encoding='utf-8'
                )

                # Test when cache file doesn't exist
                mock_exists.return_value = False
                result = fetch_model_data()
                assert result == {"model1": {}, "model2": {}}
                mock_file.assert_called_with(
                    "/tmp/klingon_models_cache.json", "w", encoding='utf-8'
                )


def test_filter_models():
    """Test the filter_models function."""
    models = {
        "gpt-4": {},
        "gpt-3.5-turbo": {},
        "claude-2": {},
        "sample_spec": {},
    }
    allowed_regexes = {"openai": r"gpt-.*", "anthropic": r"claude.*"}
    ignored_regexes = [r"sample_spec"]

    result = filter_models(models, allowed_regexes, ignored_regexes)
    assert result == {"gpt-4": {}, "gpt-3.5-turbo": {}, "claude-2": {}}


def test_update_env_variable():
    """Test the update_env_variable function."""
    model_list = ["model1", "model2", "model3"]
    update_env_variable(model_list)
    assert os.environ["KLINGON_MODELS"] == "model1,model2,model3"


@patch("klingon_tools.litellm_model_cache.fetch_model_data")
@patch("klingon_tools.litellm_model_cache.filter_models")
@patch("klingon_tools.litellm_model_cache.update_env_variable")
def test_get_supported_models(
    mock_update_env, mock_filter, mock_fetch
):
    """Test the get_supported_models function."""
    mock_fetch.return_value = {"model1": {}, "model2": {}, "model3": {}}
    mock_filter.return_value = {"model1": {}, "model2": {}}

    result = get_supported_models()

    assert result == {"model1": {}, "model2": {}}
    mock_fetch.assert_called_once()
    mock_filter.assert_called_once()
    mock_update_env.assert_called_once_with(["model1", "model2"])


if __name__ == "__main__":
    pytest.main()
