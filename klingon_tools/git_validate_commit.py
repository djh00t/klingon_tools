# klingon_tools/git_validate_commit.py
"""Module for validating Git commit messages.

This module provides functions to validate Git commit messages to ensure they
are signed off and follow the Conventional Commits standard.

Typical usage example:

    from klingon_tools.git_validate_commit import validate_commit_messages repo
    = Repo('/path/to/repo') is_valid = validate_commit_messages(repo)
"""

import re
from git import Repo


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
    # Combine all lines into one to handle multi-line commit message headers
    combined_message = ' '.join(commit_message.strip().splitlines())

    # Regex pattern for conventional commit with optional emoji at the start
    conventional_commit_pattern = (
        r"(?i)"  # Case-insensitive flag at the start of the expression
        r"^[\u2600-\u26FF\u2700-\u27BF\U0001F300-\U0001F5FF"
        r"\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF]?\s*"
        r"(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert|wip)"
        r"\([\w\/-]+\):\s"
        r".{10,}"  # At least 10 characters after the colon
    )

    # Check if the commit message matches the conventional commit pattern
    if not re.match(conventional_commit_pattern, combined_message, re.UNICODE):
        return False

    # Check for the presence of a sign-off line
    sign_off_pattern = r"^Signed-off-by: .+ <.+@.+>$"
    if not any(re.match(sign_off_pattern, line.strip(), re.IGNORECASE)
               for line in commit_message.splitlines()):
        return False

    return True


def validate_commit_messages(repo: Repo) -> bool:
    """Validate all commit messages to ensure they are signed off and follow
    the Conventional Commits standard.

    Args:
        repo (Repo): The Git repository to validate commit messages for.

    Returns:
        bool: True if all commit messages are valid, False otherwise.
    """
    for commit in repo.iter_commits("HEAD"):
        if not validate_single_commit_message(commit.message):
            return False
    return True


def validate_single_commit_message(commit_message: str) -> bool:
    """Validate a single commit message.

    Args:
        commit_message (str): The commit message to validate.

    Returns:
        bool: True if the commit message is valid, False otherwise.
    """
    return is_commit_message_signed_off(
        commit_message
        ) and is_conventional_commit(
            commit_message)
