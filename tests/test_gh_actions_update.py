# tests/test_gh_actions_update.py
"""
This module contains a pytest function for testing the find_github_actions
function.

It verifies that the function correctly identifies all GitHub Actions workflow
files in the .github/workflows/ directory.
"""

import os
import pytest
import argparse
from unittest.mock import patch, mock_open
from klingon_tools.gh_actions_update import (
    find_github_actions,
    get_latest_version,
    update_action_version,
    can_display_emojis,
    remove_emojis,
    build_action_dict,
)


def get_workflow_files(directory: str = ".github/workflows/") -> list[str]:
    """
    Retrieve all GitHub Actions workflow files from a specified directory.

    Args:
        directory (str): The directory to search for workflow files.
                         Defaults to ".github/workflows/".

    Returns:
        list[str]: A list of paths to the discovered workflow files.
    """
    workflow_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".yml", ".yaml")):
                workflow_files.append(os.path.join(root, file))
    return workflow_files


@pytest.fixture
def mock_args() -> argparse.Namespace:
    """
    Create a mock argparse.Namespace object for testing purposes.

    Returns:
        argparse.Namespace: An object containing default argument values.
    """
    return argparse.Namespace(
        file=None,
        owner=None,
        repo=None,
        job=None,
        action=None,
        no_emojis=False,
        quiet=True,
        debug=False,
    )


def test_find_github_actions(mock_args: argparse.Namespace):
    """
    Test the find_github_actions function to ensure it correctly identifies all
    workflow files.

    This test compares the files found by find_github_actions against a manual
    search of the .github/workflows/ directory.

    Args:
        mock_args (argparse.Namespace): A fixture providing mock command-line
        arguments.

    Raises:
        AssertionError: If any workflow file is not found by
        find_github_actions.
    """
    # Get the actual workflow files in .github/workflows/
    workflow_files = get_workflow_files()

    # Call the function under test
    actions = find_github_actions(mock_args)

    # Extract just the file paths from the actions dictionary keys
    action_files = set(key.split(":")[0] for key in actions.keys())

    # Check if all workflow files are in the action_files set
    missing_files = set(workflow_files) - action_files
    assert not missing_files, f"Workflow files not found: {missing_files}"

    # Check if there are any extra files in action_files that don't exist
    extra_files = [file for file in action_files if not os.path.exists(file)]
    assert not extra_files, f"Non-existent files in actions: {extra_files}"

    print(
        f"All {len(workflow_files)} workflow files were correctly identified."
    )

    # Optionally, print out the structure of the actions dictionary for
    # debugging
    print("Actions dictionary structure:")
    for key, value in actions.items():
        print(f"  {key}: {value}")


@patch("requests.get")
def test_get_latest_version(mock_get):
    """Test the get_latest_version function."""
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"tag_name": "v1.2.3"}

    assert get_latest_version("owner/repo") == "v1.2.3"

    mock_response.status_code = 404
    assert get_latest_version("owner/repo") is None


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="uses: actions/checkout@v2",
)
@patch("klingon_tools.gh_actions_update.YAML")
@patch("klingon_tools.gh_actions_update.log_message")
def test_update_action_version(mock_log_message, mock_yaml, mock_file):
    """Test the update_action_version function."""
    mock_yaml_instance = mock_yaml.return_value
    mock_yaml_instance.load.return_value = {
        "jobs": {"build": {"steps": [{"uses": "actions/checkout@v2"}]}}
    }

    update_action_version("workflow.yml", "actions/checkout", "v3")

    mock_yaml_instance.dump.assert_called_once()
    assert "actions/checkout@v3" in str(mock_yaml_instance.dump.call_args)
    mock_log_message.info.assert_called_once_with(
        message="Action actions/checkout updated to version v3 in file "
        "workflow.yml"
    )


def test_can_display_emojis(mock_args):
    """Test the can_display_emojis function."""
    with patch.dict(os.environ, {"LANG": "en_US.UTF-8"}):
        assert can_display_emojis(False, mock_args) is True

    with patch.dict(os.environ, {"LANG": "C"}):
        assert can_display_emojis(False, mock_args) is False

    assert can_display_emojis(True, mock_args) is False


def test_remove_emojis():
    """Test the remove_emojis function."""
    assert remove_emojis("Hello 👋 World 🌍") == "Hello  World "
    assert remove_emojis("No emojis here") == "No emojis here"


def test_build_action_dict():
    """Test the build_action_dict function."""
    result = build_action_dict(
        "workflow.yml", "actions/checkout", "v2", "Checkout 📦", "Build"
    )
    assert result == {
        "file_name": "workflow.yml",
        "action_owner": "actions",
        "action_repo": "checkout",
        "action_version_current": "v2",
        "action_name": "Checkout 📦",
        "action_name_clean": "Checkout",
        "job_name": "Build",
        "action_latest_version": None,
    }
