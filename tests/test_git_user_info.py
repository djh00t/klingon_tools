"""Unit tests for the git_user_info module."""

import os
import pytest
from unittest.mock import patch
from git import GitCommandError
from klingon_tools.git_user_info import get_git_user_info


@pytest.fixture
def mock_subprocess_run():
    """Fixture to mock subprocess.run."""
    with patch("subprocess.run") as mock_run:
        yield mock_run


def test_get_git_user_info_success(mock_subprocess_run):
    """Test successful retrieval of git user info."""
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = "John Doe\n"

    with patch.dict(os.environ, {"GITHUB_ACTIONS": ""}):
        name, email = get_git_user_info()

    assert name == "John Doe"
    assert email == "John Doe"


def test_get_git_user_info_github_actions():
    """Test git user info retrieval in GitHub Actions environment."""
    with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
        name, email = get_git_user_info()

    assert name == "github-actions"
    assert email == "github-actions@github.com"


def test_get_git_user_info_command_error(mock_subprocess_run):
    """Test handling of GitCommandError."""
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stderr = "Command failed"

    with patch.dict(os.environ, {"GITHUB_ACTIONS": ""}):
        with pytest.raises(GitCommandError):
            get_git_user_info()


def test_get_git_user_info_default_name(mock_subprocess_run):
    """Test handling of default git user name."""
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.side_effect = [
        type("obj", (object,), {"returncode": 0, "stdout": "Your Name\n"})(),
        type("obj", (object,), {"returncode": 0, "stdout": "valid@email.com\n"})(),
    ]

    with patch.dict(os.environ, {"GITHUB_ACTIONS": ""}):
        with pytest.raises(ValueError, match="Git user name is not set"):
            get_git_user_info()


def test_get_git_user_info_default_email(mock_subprocess_run):
    """Test handling of default git user email."""
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.side_effect = [
        type("obj", (object,), {"returncode": 0, "stdout": "John Doe\n"})(),
        type("obj", (object,), {"returncode": 0, "stdout": "your.email@example.com\n"})(),
    ]

    with patch.dict(os.environ, {"GITHUB_ACTIONS": ""}):
        with pytest.raises(ValueError, match="Git user email is not set"):
            get_git_user_info()
