# tests/test_entrypoints.py

"""
This module contains pytest functions for testing the entrypoints module.

It includes tests for various GitHub pull request component generation
functions and the ktest function from the entrypoints module.
"""

import os
import sys
import pytest
import warnings
from unittest.mock import patch, MagicMock, ANY
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


@patch("klingon_tools.entrypoints.get_commit_log")
@patch("klingon_tools.entrypoints.LiteLLMTools")
def test_gh_pr_gen_summary(mock_litellm_tools, mock_get_commit_log):
    """
    Test the gh_pr_gen_summary function.

    Args:
        mock_litellm_tools (MagicMock): Mock for LiteLLMTools.
        mock_get_commit_log (MagicMock): Mock for get_commit_log function.
    """
    mock_get_commit_log.return_value = MagicMock(stdout="Test commit log")
    mock_litellm_tools.return_value.generate_pull_request_summary.\
        return_value = "Test PR Summary"

    with patch("sys.stdout", new=StringIO()) as fake_out:
        result = entrypoints.gh_pr_gen_summary()

    assert result == 0
    assert "Test PR Summary" in fake_out.getvalue()
    mock_get_commit_log.assert_called_once_with("origin/release")
    mock_litellm_tools.return_value.generate_pull_request_summary.\
        assert_called_once_with("Test commit log", dryrun=False)


@patch("klingon_tools.entrypoints.get_commit_log")
@patch("klingon_tools.entrypoints.LiteLLMTools")
def test_gh_pr_gen_context(mock_litellm_tools, mock_get_commit_log):
    """
    Test the gh_pr_gen_context function.

    Args:
        mock_litellm_tools (MagicMock): Mock for LiteLLMTools.
        mock_get_commit_log (MagicMock): Mock for get_commit_log function.
    """
    mock_get_commit_log.return_value = MagicMock(stdout="Test commit log")
    mock_litellm_tools.return_value.generate_pull_request_context.\
        return_value = "Test PR Context"

    with patch("sys.stdout", new=StringIO()) as fake_out:
        result = entrypoints.gh_pr_gen_context()

    assert result == 0
    assert "Test PR Context" in fake_out.getvalue()
    mock_get_commit_log.assert_called_once_with("origin/release")
    mock_litellm_tools.return_value.generate_pull_request_context.\
        assert_called_once_with("Test commit log", dryrun=False)


@patch("klingon_tools.entrypoints.pytest.main")
@patch("klingon_tools.entrypoints.set_default_style")
@patch("klingon_tools.entrypoints.set_log_level")
def test_ktest(mock_set_log_level, mock_set_default_style, mock_pytest_main):
    """
    Test the ktest function.

    Args:
        mock_set_log_level (MagicMock): Mock for set_log_level function.
        mock_set_default_style (MagicMock): Mock for set_default_style
        function.
        mock_pytest_main (MagicMock): Mock for pytest.main function.
    """
    mock_pytest_main.return_value = 0

    result = entrypoints.ktest()

    mock_set_default_style.assert_called_once_with("pre-commit")
    mock_set_log_level.assert_called_once_with("INFO")
    mock_pytest_main.assert_called_once_with(
        ["tests", "--tb=short"], plugins=[ANY]
    )
    assert isinstance(result, list)


@patch("klingon_tools.entrypoints.pytest.main")
@patch("klingon_tools.entrypoints.set_default_style")
@patch("klingon_tools.entrypoints.set_log_level")
def test_ktest_with_custom_loglevel(
    mock_set_log_level, mock_set_default_style, mock_pytest_main
):
    """
    Test the ktest function with a custom log level.

    Args:
        mock_set_log_level (MagicMock): Mock for set_log_level function.
        mock_set_default_style (MagicMock): Mock for set_default_style
        function.
        mock_pytest_main (MagicMock): Mock for pytest.main function.
    """
    mock_pytest_main.return_value = 0

    entrypoints.ktest(loglevel="DEBUG")

    mock_set_default_style.assert_called_once_with("pre-commit")
    mock_set_log_level.assert_called_once_with("DEBUG")
    mock_pytest_main.assert_called_once_with(
        ["tests", "--tb=short"], plugins=[ANY]
    )


if __name__ == "__main__":
    pytest.main([__file__])
