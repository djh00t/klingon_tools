# tests/test_entrypoints.py

"""
This module contains pytest functions for testing the entrypoints module.

It includes tests for various GitHub pull request component generation
functions from the entrypoints module.
"""

import os
import sys
import pytest
import warnings
from unittest.mock import patch, MagicMock
from io import StringIO

# Add the parent directory to sys.path to import entrypoints
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from klingon_tools import entrypoints  # noqa: E402

# Filter out specific warnings
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="pydantic")
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="imghdr")
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="importlib_resources"
)


@patch("klingon_tools.entrypoints.get_commit_log")
@patch("klingon_tools.entrypoints.LiteLLMTools")
def test_gh_pr_gen_title(mock_litellm_tools, mock_get_commit_log):
    """
    Test the gh_pr_gen_title function.

    This test verifies that the gh_pr_gen_title function correctly generates
    a pull request title based on the commit log.

    Assertions:
        - Asserts that the function returns 0.
        - Asserts that the generated pull request title is in the output.
        - Asserts that get_commit_log is called once with the correct argument.
        - Asserts that generate_pull_request_title is called once with the
          correct arguments.

    Args:
        mock_litellm_tools (MagicMock): Mock for LiteLLMTools.
        mock_get_commit_log (MagicMock): Mock for get_commit_log function.
    """
    mock_get_commit_log.return_value = MagicMock(stdout="Test commit log")
    mock_litellm_tools.return_value.\
        generate_pull_request_title.\
        return_value = "Test PR Title"

    with patch("sys.stdout", new=StringIO()) as fake_out:
        result = entrypoints.gh_pr_gen_title()

    assert result == 0
    assert "Test PR Title" in fake_out.getvalue()
    mock_get_commit_log.assert_called_once_with("origin/release")
    mock_litellm_tools.return_value.generate_pull_request_title.\
        assert_called_once_with("Test commit log")


@patch("klingon_tools.entrypoints.LiteLLMTools")
def test_gh_pr_gen_summary(mock_litellm_tools):
    """
    Test the gh_pr_gen_summary function.

    Args:
        mock_litellm_tools (MagicMock): Mock for LiteLLMTools.
    """
    mock_litellm_tools.return_value.generate_pull_request_summary.\
        return_value = "Test PR Summary"

    with patch("sys.stdout", new=StringIO()) as fake_out:
        result = entrypoints.gh_pr_gen_summary()

    assert result == 0
    assert "Test PR Summary" in fake_out.getvalue()
    mock_litellm_tools.return_value.generate_pull_request_summary.\
        assert_called_once_with()


@patch("klingon_tools.entrypoints.LiteLLMTools")
def test_gh_pr_gen_context(mock_litellm_tools):
    """
    Test the gh_pr_gen_context function.

    Args:
        mock_litellm_tools (MagicMock): Mock for LiteLLMTools.
    """
    mock_litellm_tools.return_value.generate_pull_request_context.\
        return_value = "Test PR Context"

    with patch("sys.stdout", new=StringIO()) as fake_out:
        result = entrypoints.gh_pr_gen_context()

    assert result == 0
    assert "Test PR Context" in fake_out.getvalue()
    mock_litellm_tools.return_value.generate_pull_request_context.\
        assert_called_once_with()


if __name__ == "__main__":
    pytest.main([__file__])
