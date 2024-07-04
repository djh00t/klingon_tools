"""Module for validating Git commit messages.

This module provides functions to validate Git commit messages to ensure they
are signed off and follow the Conventional Commits standard.

Typical usage example:

    from klingon_tools.git_validate_commit import validate_commit_messages repo
    = Repo('/path/to/repo') is_valid = validate_commit_messages(repo)
"""

import re

from git import Repo
from klingon_tools.openai_tools import OpenAITools


def is_commit_message_signed_off(commit_message: str) -> bool:
    """Check if the commit message is signed off.

    Args:
        commit_message (str): The commit message to check.

    Returns:
        bool: True if the commit message is signed off, False otherwise.
    """
    # Check for the "Signed-off-by:" string in the commit message
    return "Signed-off-by:" in commit_message.strip()


def is_conventional_commit(commit_message: str) -> bool:
    """Check if the commit message follows the Conventional Commits standard.

    Args:
        commit_message (str): The commit message to check.

    Returns:
        bool: True if the commit message follows the Conventional Commits
        standard, False otherwise.
    """
    # Define the regex pattern for Conventional Commits
    conventional_commit_pattern = (
        r"^(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert|wip)"
        r"(\(\w+\))?: .+"
    )
    return re.match(conventional_commit_pattern, commit_message) is not None


def validate_commit_messages(repo: Repo, openai_tools: OpenAITools) -> bool:
    """Validate all commit messages to ensure they are signed off and follow
    the Conventional Commits standard.

    Args:
        repo (Repo): The Git repository to validate commit messages for.

    Returns:
        bool: True if all commit messages are valid, False otherwise.
    """
    # Iterate over all commits in the repository
    for commit in repo.iter_commits("HEAD"):
        commit_message = commit.message
        if not is_commit_message_signed_off(commit_message):
            return False
        if not is_conventional_commit(commit_message):
            return False
    return True
