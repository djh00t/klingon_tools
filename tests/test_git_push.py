"""Unit tests for the git_push module."""

import pytest
from unittest.mock import Mock, patch, call
from git import Repo, GitCommandError
from klingon_tools.git_push import (
    git_push,
    push_changes,
    _handle_submodule,
    _is_submodule,
    _generate_and_commit_messages,
)
from klingon_tools.git_tools import (
    handle_file_deletions
    as
    _handle_file_deletions
)


@pytest.fixture
def mock_repo():
    """Creates a mock Git repository."""
    return Mock(spec=Repo)


@patch('klingon_tools.git_push._handle_file_deletions')
@patch('klingon_tools.git_push._generate_and_commit_messages')
@patch('klingon_tools.git_push._is_submodule')
@patch('klingon_tools.git_push.push_changes')
def test_git_push(mock_push_changes, mock_is_submodule, mock_generate,
                  mock_handle_deletions, mock_repo):
    """Tests the git_push function."""
    mock_is_submodule.return_value = False

    git_push(mock_repo)

    mock_repo.git.reset.assert_called_once()
    mock_handle_deletions.assert_called_once_with(mock_repo)
    mock_generate.assert_called_once()
    mock_is_submodule.assert_called_once_with(mock_repo)
    mock_push_changes.assert_called_once_with(mock_repo)


@patch('klingon_tools.git_push.subprocess.run')
def test_handle_file_deletions(mock_run, mock_repo):
    """Tests the _handle_file_deletions function."""
    mock_run.return_value.stdout = "file1.txt\nfile2.txt"

    _handle_file_deletions(mock_repo)

    assert mock_repo.index.remove.call_count == 2
    assert mock_repo.index.commit.call_count == 2


@patch('klingon_tools.git_push.subprocess.run')
def test_generate_and_commit_messages(mock_run, mock_repo):
    """Tests the _generate_and_commit_messages function."""
    mock_repo.untracked_files = ['file1.txt', 'file2.txt']
    mock_litellm_tools = Mock()

    _generate_and_commit_messages(mock_repo, mock_litellm_tools)

    assert mock_repo.git.add.call_count == 2
    assert mock_repo.index.commit.call_count == 2


def test_is_submodule(mock_repo):
    """Tests the _is_submodule function."""
    mock_repo.git.rev_parse.return_value = "/path/to/.git/modules"
    assert _is_submodule(mock_repo)

    mock_repo.git.rev_parse.return_value = "/path/to/repo"
    assert not _is_submodule(mock_repo)


@patch('klingon_tools.git_push.git.Repo')
def test_handle_submodule(mock_git_repo, mock_repo):
    """Tests the _handle_submodule function."""
    mock_repo.working_tree_dir = '/path/to/submodule'
    _handle_submodule(mock_repo)

    mock_repo.git.add.assert_called_once_with(".")
    mock_repo.index.commit.assert_called_once()
    mock_git_repo.assert_called_once()
    mock_git_repo.return_value.git.add.assert_called_once()
    mock_git_repo.return_value.index.commit.assert_called_once()
    mock_git_repo.return_value.remotes.origin.push.assert_called_once()


@patch('klingon_tools.git_push.log_message')
def test_push_changes(mock_log, mock_repo):
    """Tests the push_changes function."""
    mock_repo.is_dirty.return_value = True
    mock_repo.active_branch.name = "main"

    push_changes(mock_repo)

    mock_repo.remotes.origin.fetch.assert_called_once()
    assert mock_repo.git.stash.call_count == 2
    mock_repo.git.stash.assert_has_calls([
        call('save', '--include-untracked', 'Auto stash before rebase'),
        call('pop')
    ], any_order=True)
    mock_repo.git.rebase.assert_called_once_with("origin/main")
    mock_repo.git.stash.assert_called_with("pop")
    mock_repo.remotes.origin.push.assert_called_once()
    mock_log.info.assert_called_once()


@patch('klingon_tools.git_push.log_message')
def test_push_changes_error(mock_log, mock_repo):
    """Tests the push_changes function when an error occurs."""
    mock_repo.remotes.origin.push.side_effect = GitCommandError(
        "push", "error")

    push_changes(mock_repo)

    mock_log.error.assert_called_once()
