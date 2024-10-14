"""
Provides functionality to retrieve the user's name and email from git config.

This module contains a function to get the user's name and email from the local
and global git configuration. If the values are not set or are set to default
values, it logs an error and raises an exception.

Example:
    user_name, user_email = get_git_user_info()
"""

import os
import subprocess
from typing import Tuple
from git import GitCommandError
from klingon_tools.log_msg import log_message


def get_git_user_info() -> Tuple[str, str]:
    """Retrieves the user's name and email from git configuration.

    Attempts to get the user's name and email from the local and global git
    configuration. If the values are not set or are set to default values,
    it logs an error and raises an exception.

    Returns:
        A tuple containing the user's name and email.

    Raises:
        GitCommandError: If there's an error executing git commands.
        ValueError: If the git user name or email is not set or is set to
            default values.
    """

    def get_config_value(command: str) -> str:
        """Helper function to get a git config value.

        Args:
            command: The git command to execute.

        Returns:
            The output of the git command.

        Raises:
            GitCommandError: If the git command fails.
        """
        result = subprocess.run(
            command.split(), capture_output=True, text=True, check=True
        )
        if result.returncode != 0:
            log_message.error(
                f"Failed to get git config value for command: {command}"
            )
            raise GitCommandError(command, result.returncode, result.stderr)
        return result.stdout.strip()

    try:
        if os.getenv("GITHUB_ACTIONS"):
            return "github-actions", "github-actions@github.com"

        user_name = get_config_value("git config --get user.name")
        user_email = get_config_value("git config --get user.email")

        if not user_name or user_name == "Your Name":
            raise ValueError("Git user name is not set or is set to default.")
        if not user_email or user_email == "your.email@example.com":
            raise ValueError("Git user email is not set or is set to default.")

        return user_name, user_email
    except GitCommandError as e:
        log_message.error(f"Error retrieving git user info: {e}")
        raise
    except ValueError as e:
        log_message.error(f"Error: {e}")
        raise
