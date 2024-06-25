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
import sys
from typing import Tuple
from klingon_tools.logger import logger


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
        """Executes a git config command and returns the result.

        Args:
            command (str): The git config command to execute.

        Returns:
            str: The result of the git config command, or an empty string if the command fails.
        """
        try:
            return subprocess.check_output(command.split()).decode().strip()
        except subprocess.CalledProcessError:
            return ""

    # Retrieve the user's name from the local or global git configuration
    user_name = get_config_value("git config --get user.name") or get_config_value(
        "git config --global --get user.name"
    )
    # Retrieve the user's email from the local or global git configuration
    user_email = get_config_value("git config --get user.email") or get_config_value(
        "git config --global --get user.email"
    )

    # Check if the user name or email is not set or is set to default values
    if (
        not user_name
        or user_name == "Your Name"
        or not user_email
        or user_email == "your.email@example.com"
    ):
        logger.error(
            "Git user name and email are not set or are set to default values."
        )
        logger.info(
            "Please set your git user name and email using the following commands:"
        )
        logger.info("  git config --global user.name 'Your Name'")
        logger.info("  git config --global user.email 'your.email@example.com'")
        sys.exit(1)

    return user_name, user_email
