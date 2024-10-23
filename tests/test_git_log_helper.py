from unittest.mock import patch, MagicMock
from klingon_tools.git_log_helper import branch_exists, get_commit_log


@patch('subprocess.run')
def test_branch_exists_true(mock_run):
    mock_run.return_value.returncode = 0
    assert branch_exists("existing_branch") is True


@patch('subprocess.run')
def test_branch_exists_false(mock_run):
    mock_run.return_value.returncode = 1
    assert branch_exists("non_existing_branch") is False


@patch('klingon_tools.git_log_helper.branch_exists')
@patch('subprocess.run')
def test_get_commit_log_existing_branch(mock_run, mock_branch_exists):
    mock_branch_exists.return_value = True
    mock_run.return_value = MagicMock(stdout="Commit 1\nCommit 2")
    result = get_commit_log("existing_branch")
    assert result.stdout == "Commit 1\nCommit 2"


@patch('klingon_tools.git_log_helper.branch_exists')
@patch('klingon_tools.log_msg.log_message.warning')
def test_get_commit_log_non_existing_branch(mock_warning, mock_branch_exists):
    mock_branch_exists.return_value = False
    result = get_commit_log("non_existing_branch")
    assert result.stdout == ""
    mock_warning.assert_called_once_with(
        "The branch 'non_existing_branch' does not exist."
    )
