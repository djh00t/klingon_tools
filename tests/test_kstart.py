# tests/test_kstart.py
"""
This module contains pytest functions for testing the kstart module.

It includes tests for git configuration, user prompts, and the main
functionality of the kstart module.
"""

import os
import sys
import pytest
import warnings
from unittest.mock import patch, MagicMock
from io import StringIO
from datetime import datetime

# Add the parent directory to sys.path to import kstart
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from klingon_tools import kstart  # noqa: E402

# Filter out specific warnings
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="pydantic"
)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="imghdr")
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="importlib_resources"
)


@patch("builtins.input")
@patch("klingon_tools.kstart.subprocess.run")
def test_check_git_config(mock_subprocess_run, mock_input):
    """
    Test the entrypoint of the kstart module.

    This test verifies that the main function of the kstart module is called
    when the module is executed.

    Assertions:
        - Asserts that the main function is called once.
    Test the main function with an invalid issue type input.

    This test verifies that the main function correctly handles an invalid
    issue type input by using the default issue type and proceeds with branch
    creation and pushing.

    Assertions:
        - Asserts that the output contains "Invalid choice. Using default:
          'feature'."
        - Asserts that the output contains "Pushed branch:".
        - Asserts that the input function is called four times.
    Test the main function of kstart.

    This test verifies that the main function correctly handles user input,
    creates a new branch, and pushes it to the remote repository.

    Assertions:
        - Asserts that the output contains "Pushed branch:".
        - Asserts that the input function is called four times.
    Test the check_git_config function.

    This test verifies that the check_git_config function correctly checks and
    sets the Git configuration for user.name and user.email.

    Assertions:
        - Asserts that subprocess.run is called three times.
        - Asserts that subprocess.run is called with the correct arguments to
          check user.name.
        - Asserts that subprocess.run is called with the correct arguments to
          check user.email.
        - Asserts that subprocess.run is called with the correct arguments to
          set user.name.
    Test the check_git_config function.

    Args:
        mock_subprocess_run (MagicMock): Mock for subprocess.run.
        mock_input (MagicMock): Mock for builtins.input.
    """
    mock_input.side_effect = ["Test User", "test@example.com"]

    # Mock the subprocess.run calls for checking and setting config
    mock_subprocess_run.side_effect = [
        MagicMock(stdout=""),  # Simulate no existing user.name
        MagicMock(stdout=""),  # Simulate no existing user.email
        MagicMock(returncode=0),  # Simulate setting user.name
    ]

    kstart.check_git_config()

    assert mock_subprocess_run.call_count == 3
    mock_subprocess_run.assert_any_call(
        ["git", "config", "--global", "user.name"],
        capture_output=True,
        text=True,
        check=True
    )
    mock_subprocess_run.assert_any_call(
        ["git", "config", "--global", "user.email"],
        capture_output=True,
        text=True,
        check=True
    )
    mock_subprocess_run.assert_any_call(
        ["git", "config", "--global", "user.name", "Test User"],
        check=True
    )


def test_prompt_with_default():
    """
    Test the prompt_with_default function.

    This test verifies that the prompt_with_default function correctly returns
    the default value when no input is provided and returns the user input when
    provided.

    Assertions:
        - Asserts that the function returns the default value when no input is
          provided.
        - Asserts that the function returns the user input when provided.
    """
    with patch("builtins.input", return_value=""):
        result = kstart.prompt_with_default("Test prompt", "default_value")
        assert result == "default_value"

    with patch("builtins.input", return_value="user_input"):
        result = kstart.prompt_with_default("Test prompt", "default_value")
        assert result == "user_input"


@patch("builtins.input")
@patch("klingon_tools.kstart.subprocess.run")
@patch("klingon_tools.kstart.configparser.ConfigParser")
@patch("klingon_tools.kstart.datetime")
@patch("os.path.exists")
def test_main(
    mock_exists,
    mock_datetime,
    mock_configparser,
    mock_subprocess_run,
    mock_input,
):
    """
    Test the main function of kstart.

    Args:
        mock_exists (MagicMock): Mock for os.path.exists.
        mock_datetime (MagicMock): Mock for datetime.
        mock_configparser (MagicMock): Mock for ConfigParser.
        mock_subprocess_run (MagicMock): Mock for subprocess.run.
        mock_input (MagicMock): Mock for builtins.input.
    """
    mock_exists.return_value = False
    mock_input.side_effect = [
        "testuser",  # GitHub username
        "c",  # Issue type choice (feature)
        "Test Feature",  # Feature branch title
        "123,456",  # Linked issues
    ]
    mock_datetime.now.return_value = datetime(2024, 1, 1)
    mock_config = MagicMock()
    mock_configparser.return_value = mock_config
    mock_config.__getitem__.return_value = {}

    with patch("builtins.open", MagicMock()):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            kstart.main()

    assert "Pushed branch:" in fake_out.getvalue()
    assert mock_input.call_count == 4


@patch("builtins.input")
@patch("klingon_tools.kstart.subprocess.run")
@patch("klingon_tools.kstart.configparser.ConfigParser")
@patch("klingon_tools.kstart.datetime")
@patch("os.path.exists")
def test_main_invalid_issue_type(
    mock_exists,
    mock_datetime,
    mock_configparser,
    mock_subprocess_run,
    mock_input,
):
    """
    Test the main function with an invalid issue type input.

    Args:
        mock_exists (MagicMock): Mock for os.path.exists.
        mock_datetime (MagicMock): Mock for datetime.
        mock_configparser (MagicMock): Mock for ConfigParser.
        mock_subprocess_run (MagicMock): Mock for subprocess.run.
        mock_input (MagicMock): Mock for builtins.input.
    """
    mock_exists.return_value = False
    mock_input.side_effect = [
        "testuser",  # GitHub username
        "d",  # Invalid issue type choice
        "Test Feature",  # Feature branch title
        "123,456",  # Linked issues
    ]
    mock_datetime.now.return_value = datetime(2024, 1, 1)
    mock_config = MagicMock()
    mock_configparser.return_value = mock_config
    mock_config.__getitem__.return_value = {"ISSUE_TYPE": "feature"}

    with patch("builtins.open", MagicMock()):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            kstart.main()

    assert "Invalid choice. Using default: 'feature'." in fake_out.getvalue()
    assert "Pushed branch:" in fake_out.getvalue()
    assert mock_input.call_count == 4


@patch("klingon_tools.kstart.main")
def test_entrypoint(mock_main):
    """
    Test the entrypoint of the kstart module.

    Args:
        mock_main (MagicMock): Mock for kstart.main function.
    """
    kstart.main()
    mock_main.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
