# klingon_tools/git_push_helper.py
"""
Unit tests for the git_push_helper module.
"""

import pytest
from git import GitCommandError, Repo
from unittest.mock import Mock, patch
from klingon_tools.git_push_helper import git_push


@pytest.fixture
def mock_repo():
    """Create a mock Repo object for testing."""
    repo = Mock(spec=Repo)
    repo.remotes.origin = Mock()
    repo.active_branch = Mock()
    repo.active_branch.name = "main"
    repo.is_dirty.return_value = False
    return repo


@patch("klingon_tools.git_push_helper.log_message")
def test_git_push_success(mock_log, mock_repo):
    """Test successful git push operation."""
    git_push(mock_repo)

    mock_repo.remotes.origin.fetch.assert_called_once()
    mock_repo.git.rebase.assert_called_once_with("origin/main")
    mock_repo.remotes.origin.push.assert_called_once()
    mock_log.info.assert_called_once_with(
        "Pushed changes to remote repository", status="✅"
    )


@patch("klingon_tools.git_push_helper.log_message")
def test_git_push_with_stash(mock_log, mock_repo):
    """Test git push with stashing changes."""
    mock_repo.is_dirty.return_value = True

    git_push(mock_repo)

    mock_repo.git.stash.assert_any_call(
        "save", "--include-untracked", "Auto stash before rebase"
    )
    mock_repo.git.stash.assert_called_with("pop")


@patch("klingon_tools.git_push_helper.log_message")
def test_git_push_stash_conflict(mock_log, mock_repo):
    """Test git push with stash conflict."""
    mock_repo.is_dirty.return_value = True
    mock_repo.git.stash.side_effect = [None, GitCommandError("stash pop")]

    git_push(mock_repo)

    mock_log.error.assert_called_once_with(
        "Failed to apply stashed changes",
        status="❌",
        reason="stash pop",
    )


@patch("klingon_tools.git_push_helper.log_message")
def test_git_push_command_error(mock_log, mock_repo):
    """Test git push with GitCommandError."""
    mock_repo.remotes.origin.push.side_effect = GitCommandError(
        "push",
        "Push failed"
        )

    git_push(mock_repo)

    # Check if error was logged
    assert mock_log.error.called

    # Get the arguments of the last call to mock_log.error
    call_args = mock_log.error.call_args

    # Check the message
    assert call_args[0][0] == "Failed to push changes to remote repository"

    # Check the status
    assert call_args[1]['status'] == "❌"

    # Check if the reason contains 'push' and the error details
    reason = call_args[1]['reason']
    assert 'push' in reason
    assert 'Cmd(\'push\') failed' in reason

    # Optionally, you can print the actual reason for debugging
    print(f"Actual reason: {reason}")


@patch("klingon_tools.git_push_helper.log_message")
def test_git_push_unexpected_error(mock_log, mock_repo):
    """Test git push with unexpected error."""
    mock_repo.remotes.origin.fetch.side_effect = Exception("Unexpected")

    git_push(mock_repo)

    mock_log.error.assert_called_once_with(
        "An unexpected error occurred",
        status="❌",
        reason="Unexpected"
    )
