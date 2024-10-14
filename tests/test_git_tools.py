import pytest
from unittest.mock import patch, MagicMock
from klingon_tools.git_tools import (
    branch_exists,
    cleanup_lock_file,
    git_get_toplevel,
    git_get_status,
)


@pytest.fixture
def mock_repo():
    return MagicMock()


def test_branch_exists():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        assert branch_exists('main')

        mock_run.return_value.returncode = 1
        assert not branch_exists('non_existent_branch')


def test_cleanup_lock_file(tmp_path):
    lock_file = tmp_path / '.git' / 'index.lock'
    lock_file.parent.mkdir(parents=True)
    lock_file.touch()

    with patch('psutil.process_iter') as mock_process_iter:
        mock_process_iter.return_value = []
        cleanup_lock_file(str(tmp_path))
        assert not lock_file.exists()


def test_git_get_toplevel():
    with patch('git.Repo') as mock_repo:
        mock_repo.return_value.active_branch.tracking_branch.return_value = (
            None
        )
        result = git_get_toplevel()
        assert result is not None


def test_git_get_status(mock_repo):
    mock_repo.index.diff.return_value = []
    mock_repo.untracked_files = []
    result = git_get_status(mock_repo)
    assert len(result) == 5
    assert all(isinstance(item, list) for item in result)
