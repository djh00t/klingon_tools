import pytest
import os
from unittest.mock import patch, MagicMock
from klingon_tools.push import (
    find_git_root,
    check_software_requirements,
    ensure_pre_commit_config,
    parse_arguments,
    run_tests,
    process_files,
    run_push_prep,
    workflow_process_file,
    expand_file_patterns,
    filter_git_files,
    run_tests_and_confirm,
    process_changes,
    startup_tasks,
    main,
)

def test_find_git_root():
    with patch('os.path.isdir') as mock_isdir:
        mock_isdir.return_value = True
        assert find_git_root('/path/to/repo') == '/path/to/repo'

    with patch('os.path.isdir') as mock_isdir:
        mock_isdir.side_effect = [False, False, True]
        assert find_git_root('/path/to/repo') == '/path'

def test_check_software_requirements():
    mock_log = MagicMock()
    with patch('subprocess.run') as mock_run:
        check_software_requirements('/path/to/repo', mock_log)
        mock_run.assert_called_once()

def test_ensure_pre_commit_config():
    mock_log = MagicMock()
    with patch('os.path.exists') as mock_exists, \
         patch('requests.get') as mock_get, \
         patch('builtins.open', create=True) as mock_open:
        mock_exists.return_value = False
        mock_get.return_value.text = 'config content'
        ensure_pre_commit_config('/path/to/repo', mock_log)
        mock_open.assert_called_once_with('/path/to/repo/.pre-commit-config.yaml', 'w')

def test_parse_arguments():
    with patch('sys.argv', ['push.py', '--debug']):
        args = parse_arguments()
        assert args.debug == True

def test_parse_arguments_with_file_name():
    with patch('sys.argv', ['push.py', '--file-name', 'file1.py', '*.txt']):
        args = parse_arguments()
        assert args.file_name == ['file1.py', '*.txt']

def test_run_tests():
    mock_log = MagicMock()
    with patch('subprocess.Popen') as mock_popen:
        mock_popen.return_value.wait.return_value = 0
        assert run_tests(mock_log, False) == True

def test_process_files():
    mock_repo = MagicMock()
    mock_args = MagicMock()
    mock_log = MagicMock()
    mock_litellm = MagicMock()
    with patch('klingon_tools.push.workflow_process_file') as mock_workflow, \
         patch('os.path.exists', return_value=True):
        result = process_files(['file1.py'], mock_repo, mock_args, mock_log, mock_litellm)
        mock_workflow.assert_called_once_with('file1.py', ['file1.py'], mock_repo, mock_args, mock_log, mock_litellm, 1)
        assert result == True

def test_run_push_prep():
    mock_log = MagicMock()
    with patch('os.path.exists') as mock_exists, \
         patch('builtins.open', create=True) as mock_open, \
         patch('subprocess.run') as mock_run:
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = 'push-prep:'
        run_push_prep(mock_log)
        mock_run.assert_called_once_with(['make', 'push-prep'], check=True)

def test_workflow_process_file():
    mock_repo = MagicMock()
    mock_args = MagicMock()
    mock_log = MagicMock()
    mock_litellm = MagicMock()
    mock_litellm.generate_commit_message.return_value = "feat: Add new feature"
    with patch('klingon_tools.push.git_pre_commit') as mock_pre_commit, \
         patch('klingon_tools.push.git_commit_file') as mock_commit, \
         patch('klingon_tools.push.validate_commit_message', return_value=True), \
         patch('klingon_tools.push.committed_not_pushed', []):
        mock_pre_commit.return_value = (True, None)
        mock_args.dryrun = False
        workflow_process_file('file1.py', [], mock_repo, mock_args, mock_log, mock_litellm, 1)
        mock_commit.assert_called_once()

def test_expand_file_patterns():
    with patch('glob.glob') as mock_glob:
        mock_glob.side_effect = [['file1.py', 'file2.py'], ['test1.txt', 'test2.txt']]
        result = expand_file_patterns(['*.py', '*.txt'])
        assert set(result) == {'file1.py', 'file2.py', 'test1.txt', 'test2.txt'}

def test_filter_git_files():
    all_files = ['file1.py', 'file2.py', 'test1.txt', 'test2.txt']
    filter_files = ['file1.py', 'test1.txt']
    result = filter_git_files(all_files, filter_files)
    assert result == ['file1.py', 'test1.txt']

def test_run_tests_and_confirm():
    mock_log = MagicMock()
    with patch('klingon_tools.push.run_tests') as mock_run_tests, \
         patch('builtins.input', return_value='y'):
        mock_run_tests.return_value = False
        assert run_tests_and_confirm(mock_log, False) == True

import pytest
from unittest.mock import patch, MagicMock
from klingon_tools.push import process_changes

def test_process_changes():
    # Setup
    mock_repo = MagicMock()
    mock_args = MagicMock(oneshot=False)
    mock_litellm = MagicMock()
    mock_log_message = MagicMock()

    # Mock the global variables
    with patch('klingon_tools.push.untracked_files', ['file1.py']), \
         patch('klingon_tools.push.modified_files', ['file2.py']), \
         patch('klingon_tools.push.deleted_files', ['file3.py']), \
         patch('klingon_tools.push.workflow_process_file') as mock_workflow, \
         patch('klingon_tools.push.git_commit_deletes') as mock_commit_deletes, \
         patch('klingon_tools.push.process_files') as mock_process_files, \
         patch('klingon_tools.push.log_message', mock_log_message):

        # Set return values
        mock_process_files.return_value = True

        # Execute
        result = process_changes(mock_repo, mock_args, mock_litellm)

        # Assert
        assert result == True
        mock_commit_deletes.assert_called_once_with(mock_repo, ['file3.py'])
        mock_process_files.assert_called_once_with(['file1.py', 'file2.py'], mock_repo, mock_args, mock_log_message, mock_litellm)

    # Test with .pre-commit-config.yaml
    with patch('klingon_tools.push.untracked_files', ['.pre-commit-config.yaml', 'file1.py']), \
         patch('klingon_tools.push.modified_files', ['file2.py']), \
         patch('klingon_tools.push.deleted_files', []), \
         patch('klingon_tools.push.workflow_process_file') as mock_workflow, \
         patch('klingon_tools.push.process_files') as mock_process_files, \
         patch('klingon_tools.push.log_message', mock_log_message):

        mock_process_files.return_value = True

        result = process_changes(mock_repo, mock_args, mock_litellm)

        assert result == True
        mock_workflow.assert_called_once_with('.pre-commit-config.yaml', ['.pre-commit-config.yaml'], mock_repo, mock_args, mock_log_message, mock_litellm, 0)
        mock_process_files.assert_called_once_with(['file1.py', 'file2.py'], mock_repo, mock_args, mock_log_message, mock_litellm)

    # Test oneshot mode
    mock_args.oneshot = True
    with patch('klingon_tools.push.untracked_files', ['file1.py']), \
         patch('klingon_tools.push.modified_files', ['file2.py']), \
         patch('klingon_tools.push.deleted_files', []), \
         patch('klingon_tools.push.process_files') as mock_process_files, \
         patch('klingon_tools.push.log_message', mock_log_message):

        mock_process_files.return_value = True

        result = process_changes(mock_repo, mock_args, mock_litellm)

        assert result == True
        mock_process_files.assert_called_once_with(['file1.py'], mock_repo, mock_args, mock_log_message, mock_litellm)

    # Test with no changes
    mock_args.oneshot = False
    with patch('klingon_tools.push.untracked_files', []), \
         patch('klingon_tools.push.modified_files', []), \
         patch('klingon_tools.push.deleted_files', []), \
         patch('klingon_tools.push.process_files') as mock_process_files, \
         patch('klingon_tools.push.log_message', mock_log_message):

        result = process_changes(mock_repo, mock_args, mock_litellm)

        assert result == False
        mock_process_files.assert_not_called()

def test_startup_tasks():
    mock_args = MagicMock()
    with patch('klingon_tools.push.find_git_root') as mock_find_root, \
         patch('klingon_tools.push.cleanup_lock_file') as mock_cleanup, \
         patch('klingon_tools.push.ensure_pre_commit_config') as mock_ensure, \
         patch('klingon_tools.push.run_push_prep') as mock_push_prep, \
         patch('klingon_tools.push.check_software_requirements') as mock_check, \
         patch('klingon_tools.push.get_git_user_info') as mock_get_user, \
         patch('klingon_tools.push.git_get_toplevel') as mock_get_toplevel:
        mock_find_root.return_value = os.getcwd()
        mock_get_user.return_value = ('John Doe', 'john@example.com')
        mock_get_toplevel.return_value = MagicMock()
        repo, user_name, user_email = startup_tasks(mock_args)
        assert user_name == 'John Doe'
        assert user_email == 'john@example.com'

def test_main():
    with patch('klingon_tools.push.parse_arguments') as mock_parse, \
         patch('klingon_tools.push.get_supported_models') as mock_get_models, \
         patch('klingon_tools.push.LiteLLMTools') as mock_litellm, \
         patch('klingon_tools.push.set_log_level') as mock_set_log, \
         patch('klingon_tools.push.expand_file_patterns') as mock_expand, \
         patch('klingon_tools.push.startup_tasks') as mock_startup, \
         patch('klingon_tools.push.git_get_status') as mock_get_status, \
         patch('klingon_tools.push.log_git_stats') as mock_log_stats, \
         patch('klingon_tools.push.run_tests_and_confirm') as mock_run_tests, \
         patch('klingon_tools.push.process_changes') as mock_process, \
         patch('klingon_tools.push.push_changes_if_needed') as mock_push:
        mock_parse.return_value = MagicMock(models_list=False, no_tests=True, file_name=['*.py'])
        mock_startup.return_value = (MagicMock(), 'John Doe', 'john@example.com')
        mock_get_status.return_value = ([], [], ['file1.py', 'file2.txt'], [], [])
        mock_expand.return_value = ['file1.py']
        mock_process.return_value = True
        assert main() == 0
        mock_process.assert_called_once()
        args, kwargs = mock_process.call_args
        assert args[1].file_name == ['*.py']

if __name__ == '__main__':
    pytest.main()