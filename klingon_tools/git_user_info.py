"""
This module provides functionality to retrieve the user's name and email from git configuration.

The main function in this module, `get_git_user_info`, attempts to retrieve the user's name and email
from the local and global git configuration. If the values are not set or are set to default values,
it logs an error and exits the program.

Functions:
    - get_git_user_info: Retrieves the user's name and email from git configuration.

Usage Example:
    user_name, user_email = get_git_user_info()
"""

import subprocess
import git
import sys
from typing import Tuple
from klingon_tools.logger import logger
from git import GitCommandError


def get_git_user_info() -> Tuple[str, str]:
    """Retrieves the user's name and email from git configuration.

    This function attempts to retrieve the user's name and email from the local
    and global git configuration. If the values are not set or are set to default
    values, it logs an error and exits the program.

    Returns:
        Tuple[str, str]: A tuple containing the user's name and email.

    Raises:
        SystemExit: If the git user name or email is not set or is set to default values.
    """

    def get_config_value(command: str) -> str:
        """Helper function to get a git config value."""
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            logger.error(f"Failed to get git config value for command: {command}")
            raise GitCommandError(command, result.returncode, result.stderr)
        return result.stdout.strip()

    try:
        user_name = get_config_value("git config --get user.name")
        user_email = get_config_value("git config --get user.email")

        # Check if user name or email are set to default values
        if not user_name or user_name == "Your Name":
            logger.error("Git user name is not set or is set to default value.")
            raise ValueError("Git user name is not set or is set to default value.")
        if not user_email or user_email == "your.email@example.com":
            logger.error("Git user email is not set or is set to default value.")
            raise ValueError("Git user email is not set or is set to default value.")

        return user_name, user_email
    except GitCommandError as e:
        logger.error(f"Error retrieving git user info: {e}")
        raise
    except ValueError as e:
        logger.error(f"Error: {e}")
        raise
