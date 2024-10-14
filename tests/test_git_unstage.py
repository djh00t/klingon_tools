"""Unit tests for the git_unstage module."""

import pytest
from git import Repo
from git.exc import GitCommandError
from unittest.mock import Mock, patch
from klingon_tools.git_unstage import git_unstage_files


@pytest.fixture
def mock_repo():
    """Create a mock Repo object."""
    return Mock(spec=Repo)


@patch('klingon_tools.git_unstage.log_message')
def test_git_unstage_files_no_staged_files(mock_log, mock_repo):
    """Test unstaging when there are no staged files."""
    mock_repo.git.diff.return_value = ""

    git_unstage_files(mock_repo)

    mock_log.info.assert_any_call(message="Unstaging staged files", status="🔁")
    mock_log.info.assert_any_call(message="No files to unstage", status="ℹ️")
    mock_repo.git.reset.assert_not_called()


@patch('klingon_tools.git_unstage.log_message')
def test_git_unstage_files_success(mock_log, mock_repo):
    """Test successful unstaging of files."""
    mock_repo.git.diff.return_value = "file1.txt\nfile2.txt"

    git_unstage_files(mock_repo)

    mock_log.info.assert_any_call(message="Unstaging staged files", status="🔁")
    mock_repo.git.reset.assert_any_call("HEAD", "file1.txt")
    mock_repo.git.reset.assert_any_call("HEAD", "file2.txt")
    mock_log.info.assert_any_call(message="All files unstaged", status="✅")


@patch('klingon_tools.git_unstage.log_message')
def test_git_unstage_files_error(mock_log, mock_repo):
    """Test error handling when unstaging files."""
    mock_repo.git.diff.return_value = "file1.txt\nfile2.txt"
    mock_repo.git.reset.side_effect = [None, GitCommandError("cmd", 1)]

    git_unstage_files(mock_repo)

    mock_log.info.assert_any_call(message="Unstaging staged files", status="🔁")
    mock_repo.git.reset.assert_any_call("HEAD", "file1.txt")
    mock_repo.git.reset.assert_any_call("HEAD", "file2.txt")
    mock_log.error.assert_called_once_with(
        message="Error unstaging file", status="file2.txt"
    )
    mock_log.exception.assert_called_once()
