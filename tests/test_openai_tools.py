# tests/test_openai_tools.py
"""Tests for the OpenAITools class and its methods.

This module contains pytest-style unit tests for the OpenAITools class from the
klingon_tools package. It covers initialization, PR summary generation, title
generation, and message formatting.
"""

import logging
from unittest.mock import patch, MagicMock

import pytest
from git import Repo

from klingon_tools.openai_tools import OpenAITools


@pytest.fixture(scope="module", autouse=True)
def disable_logging():
    """Disable logging for all tests in this module."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def openai_tools():
    """Fixture to create an instance of OpenAITools."""
    return OpenAITools(debug=True)


@patch("klingon_tools.openai_tools.get_commit_log")
def test_generate_pull_request_summary(mock_get_commit_log, openai_tools):
    """Test the generate_pull_request_summary method.

    Assertions:
    1. Check that generate_content is called once with "pull_request_summary"
    and "commit log content".
    2. Verify that the summary is "Generated PR Summary".
    """
    mock_get_commit_log.return_value.stdout = "commit log content"
    openai_tools.generate_content = MagicMock(
        return_value="Generated PR Summary"
    )

    summary = openai_tools.generate_pull_request_summary(
        Repo(), "diff content"
    )

    openai_tools.generate_content.assert_called_once_with(
        "pull_request_summary", "commit log content"
    )
    assert summary == "Generated PR Summary"


def test_init_with_valid_api_key(openai_tools):
    """Test initialization of OpenAITools with a valid API key.

    Assertions:
    1. Verify that debug is set to True.
    2. Ensure that client is not None.
    """
    assert openai_tools.debug is True
    assert openai_tools.client is not None


@patch("openai.ChatCompletion.create")
def test_generate_pull_request_title(mock_create, openai_tools):
    """Test the generate_pull_request_title method.

    Assertions:
    1. Verify that the title is a string.
    2. Ensure that the length of the title is less than or equal to 72
    characters.
    """
    mock_create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Generated PR title"))]
    )
    diff = "Some diff content"
    title = openai_tools.generate_pull_request_title(diff)

    assert isinstance(title, str)
    assert len(title) <= 72

    # Print the generated title
    print(f"LLM generated title: {title}")


@pytest.mark.parametrize(
    "message, expected, should_raise",
    [
        (
            "feat(klingon): add new feature",
            "✨ feat(klingon): add new feature",
            False,
        ),
        ("invalid message", None, True),
        (
            "feat: minimal valid message",
            None,
            True,
        ),  # This is now expected to raise an error
        (
            "feat(core): minimal valid message",
            "✨ feat(core): minimal valid message",
            False,
        ),  # New valid edge case
        (
            "fix(bug): fix critical issue",
            "🐛 fix(bug): fix critical issue",
            False,
        ),  # Additional valid case
    ],
)
def test_format_message(openai_tools, message, expected, should_raise):
    """Test the format_message method with valid, invalid, and edge case
    inputs.

    Assertions:
    1. If should_raise is True, verify that a ValueError is raised.
    2. If should_raise is False, check that the formatted message matches the
    expected value.
    """
    if should_raise:
        with pytest.raises(ValueError):
            openai_tools.format_message(message)
    else:
        formatted_message = openai_tools.format_message(message)
        assert formatted_message == expected

    # Print the result for debugging
    print(f"Input: {message}")
    print(f"Expected: {expected}")
    print(f"Should raise: {should_raise}")
    if not should_raise:
        print(f"Actual output: {openai_tools.format_message(message)}")
    print("---")


@pytest.mark.parametrize(
    "title, expected",
    [
        ("Short title", "Short title"),
        (
            "This is a very long title that exceeds the maximum character "
            "limit maybe, or does it? I don't know, but it's long.",
            "This is a very long title that exceeds the maximum character "
            "limit maybe...",
        ),
        ("Title   with   multiple   spaces", "Title with multiple spaces"),
        ("Title\nwith\nnewlines", "Title with newlines"),
    ],
)
def test_format_pr_title(openai_tools, title, expected):
    """Test the format_pr_title method with various inputs.

    Assertions:
    1. Verify that the formatted title matches the expected value.
    """
    formatted_title = openai_tools.format_pr_title(title)
    assert formatted_title == expected


if __name__ == "__main__":
    pytest.main(["-v"])
