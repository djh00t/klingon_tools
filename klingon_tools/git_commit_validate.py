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
from typing import Any
from klingon_tools.git_commit_fix import fix_commit_message


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
    """Check if the commit message follows the custom Conventional Commits
    standard.

    Args:
        commit_message (str): The commit message to check.

    Returns:
        bool: True if the commit message follows the Conventional Commits
        standard, False otherwise.
    """

    # Split the commit message into header (first line) and body (remaining
    # lines)
    commit_lines = commit_message.strip().splitlines()
    if len(commit_lines) == 0:
        return False, "Commit message cannot be empty."

    # Step 1: Check for optional 2-character prefix
    header = commit_lines[0].strip()
    if len(header) > 2 and header[1] == " ":
        header = header[2:].strip()

    # Step 2: Validate the type
    type_scope_desc_match = re.match(
        r"^(feat|fix|chore|doc|docs|style|refactor|"
        r"perf|test|build|ci|revert|wip)"
        r"\(([^)]+)\): (.+)",
        header,
    )
    if not type_scope_desc_match:
        return False, (
            "Invalid commit message format. Expected format: <type>(<scope>): "
            "<description>."
        )

    commit_type, scope, description = type_scope_desc_match.groups()

    # Step 3: Ensure type, scope, and description do not exceed 72 characters
    if len(commit_type) + len(scope) + len(description) + 4 > 72:
        return (
            False,
            "The first line of the commit message should not exceed 72 "
            "characters.",
        )

    # Step 4: Check for optional body (must be separated by a blank line)
    if len(commit_lines) > 1 and commit_lines[1].strip() != "":
        return (
            False,
            "The body of the commit message must be separated from the"
            " header by a blank line.",
        )

    # Check body width if present
    for line in commit_lines[2:]:
        if len(line) > 72:
            return (
                False,
                "Commit message body lines should not exceed "
                "72 characters.",
            )

    # Step 5: Check for the footer, including breaking changes
    if any(
        line.startswith("BREAKING CHANGE:") and len(line) > 72
        for line in commit_lines[2:]
    ):
        return (
            False,
            "Footer lines (including BREAKING CHANGE:) "
            "should not exceed 72 characters.",
        )

    # Everything checks out
    return True, "Commit message is valid."


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


def validate_single_commit_message(
        commit_message: str, log_message: Any) -> bool:
    """Validate a single commit message.

    Args:
        commit_message (str): The commit message to validate.
        log_message (Any): Logger instance to capture messages.

    Returns:
        bool: True if the commit message is valid, False otherwise.
    """
    is_valid, error_message = is_conventional_commit(commit_message)

    if not is_valid:
        # Log the invalid commit message and the error
        log_message.info("=" * 80, status="", style=None)
        log_message.info(
            f"Invalid commit message: {error_message}\n{commit_message}",
            status="",
            style=None
        )
        log_message.info("=" * 80, status="", style=None)

        # Attempt to auto-fix the commit message if possible
        fixed_message = fix_commit_message(commit_message)
        log_message.info("=" * 80, status="", style=None)
        log_message.info(
            f"Auto-fixed commit message:\n{fixed_message}",
            status="",
            style=None
        )
        log_message.info("=" * 80, status="", style=None)

        # Return validation result of the fixed message if needed
        is_valid_fixed, _ = is_conventional_commit(fixed_message)

        if not is_valid_fixed:
            log_message.info("=" * 80, status="", style=None)
            log_message.info(
                "Auto-fix could not resolve the issue.",
                status="",
                style=None
            )
            log_message.info("=" * 80, status="", style=None)
            return False

    return is_valid
