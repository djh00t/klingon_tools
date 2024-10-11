"""
This module contains unit tests for the git_commit_validate module.

It tests various functions related to commit message validation, including
checking for signed-off messages, commit message structure, and formatting.
"""

import pytest
import textwrap
from klingon_tools.git_commit_validate import (
    is_commit_message_signed_off,
    check_prefix,
    check_type,
    check_scope,
    check_description,
    check_line_length,
    check_body,
    check_footer,
    fix_body_wrapping,
    fix_footer_wrapping,
    validate_commit_message
)


class MockLogMessage:
    """A mock class for logging messages during tests."""

    def __init__(self):
        self.messages = []

    def info(self, message, status, reason=None):
        """Log an info message."""
        self.messages.append(f"INFO: {message} - {status}")

    def error(self, message, status, reason=None):
        """Log an error message."""
        self.messages.append(f"ERROR: {message} - {status}")

    def debug(self, message, status):
        """Log a debug message."""
        self.messages.append(f"DEBUG: {message} - {status}")


@pytest.fixture
def mock_log_message():
    """Fixture to create a MockLogMessage instance for tests."""
    return MockLogMessage()


def test_is_commit_message_signed_off():
    """Test the is_commit_message_signed_off function."""
    assert is_commit_message_signed_off(
        "This is a commit\n\nSigned-off-by: John Doe <john@example.com>"
    )
    assert not is_commit_message_signed_off(
        "This is a commit without sign-off"
    )


def test_check_prefix(mock_log_message):
    """Test the check_prefix function."""
    message, prefix, _ = check_prefix(
        "🚀 feat(core): add new feature", mock_log_message
    )
    assert message == "feat(core): add new feature"
    assert prefix == "🚀"

    message, prefix, _ = check_prefix(
        "feat(core): add new feature", mock_log_message
    )
    assert message == "feat(core): add new feature"
    assert prefix is None


def test_check_type(mock_log_message):
    """Test the check_type function."""
    assert check_type(
        "feat(core): add new feature", mock_log_message
    )
    assert not check_type(
        "invalid(core): add new feature", mock_log_message
    )


def test_check_scope(mock_log_message):
    """Test the check_scope function."""
    assert check_scope(
        "feat(core): add new feature", mock_log_message
    )
    assert not check_scope(
        "feat: add new feature", mock_log_message
    )


def test_check_description(mock_log_message):
    """Test the check_description function."""
    assert check_description(
        "feat(core): add new feature", mock_log_message
    )
    assert not check_description(
        "feat(core):", mock_log_message
    )


def test_check_line_length(mock_log_message):
    """Test the check_line_length function."""
    assert check_line_length(
        "feat(core): add new feature", mock_log_message
    )
    assert not check_line_length(
        "feat(core): " + "a" * 61, mock_log_message
    )  # This will make the total length 74 characters


def test_check_body(mock_log_message):
    """Test the check_body function."""
    valid_body = [
        "feat(core): add new feature",
        "",
        "This is the body of the commit message."
    ]
    assert check_body(valid_body, mock_log_message)

    invalid_body = [
        "feat(core): add new feature",
        "No empty line here",
        "This is the body."
    ]
    assert not check_body(invalid_body, mock_log_message)


def test_check_footer(mock_log_message):
    """Test the check_footer function."""
    valid_footer = [
        "feat(core): add new feature",
        "",
        "Body",
        "",
        "BREAKING CHANGE: This is a breaking change"
    ]
    assert check_footer(valid_footer, mock_log_message)

    invalid_footer = [
        "feat(core): add new feature",
        "",
        "Body",
        "BREAKING CHANGE: " + "a" * 100
    ]
    assert not check_footer(invalid_footer, mock_log_message)


def test_fix_body_wrapping():
    """Test the fix_body_wrapping function."""
    long_body = ("This is a very long body that exceeds the 72 character "
                 "limit and should be wrapped accordingly.")
    fixed_body = fix_body_wrapping(long_body)
    wrapped_body = "\n".join(textwrap.wrap(fixed_body, width=79))
    assert all(len(line) <= 79 for line in wrapped_body.split('\n'))


def test_fix_footer_wrapping():
    """Test the fix_footer_wrapping function."""
    long_footer = ("BREAKING CHANGE: This is a very long footer that "
                   "exceeds the 72 character limit and should be wrapped "
                   "accordingly.")
    fixed_footer = fix_footer_wrapping(long_footer)
    wrapped_footer = "\n".join(textwrap.wrap(fixed_footer, width=79))
    assert all(len(line) <= 79 for line in wrapped_footer.split('\n'))


def test_validate_commit_message(mock_log_message):
    """Test the validate_commit_message function."""
    valid_message = ("feat(core): add new feature\n\nThis is the body.\n\n"
                     "BREAKING CHANGE: This is a breaking change.")
    assert validate_commit_message(valid_message, mock_log_message)

    invalid_message = "invalid: this is not a valid commit message"
    assert not validate_commit_message(invalid_message, mock_log_message)
