# klingon_tools/git_commit_validate.py
"""Module for validating Git commit messages.

This module provides functions to validate Git commit messages to ensure they
are signed off and follow the Conventional Commits standard.

Typical usage example:

    from klingon_tools.git_validate_commit import validate_commit_messages repo
    = Repo('/path/to/repo') is_valid = validate_commit_messages(repo)
"""

from typing import Any
import re
from klingon_tools.git_commit_fix import fix_commit_message


def is_commit_message_signed_off(commit_message: str) -> bool:
    """Check if the commit message is signed off.

    Args:
        commit_message (str): The commit message to check.

    Returns:
        bool: True if the commit message is signed off, False otherwise.
    """
    return "Signed-off-by:" in commit_message


def check_prefix(commit_message: str, log_message: Any) -> str:
    """Check for optional 2-character prefix and remove if present."""
    if len(commit_message) > 2 and commit_message[1] == " ":
        log_message.info("Detected optional prefix, removing it.", status="")
        return commit_message[2:].strip()
    return commit_message


def check_type(commit_message: str, log_message: Any) -> bool:
    """Check if the commit type is valid."""
    valid_types = [
        "feat", "fix", "chore", "doc", "docs", "style", "refactor",
        "perf", "test", "build", "ci", "revert", "wip"
    ]
    match = re.match(r"^(\w+)\(", commit_message)
    if not match:
        log_message.error("Invalid commit type. Type must be one of: "
                          f"{', '.join(valid_types)}.", status="")
        return False
    commit_type = match.group(1)
    if commit_type not in valid_types:
        log_message.error(f"Invalid commit type: {commit_type}.", status="")
        return False
    log_message.info(f"Commit type '{commit_type}' is valid.", status="")
    return True


def check_scope(commit_message: str, log_message: Any) -> bool:
    """Check if the scope is present and valid."""
    match = re.match(r"^\w+\(([^)]+)\):", commit_message)
    if not match:
        log_message.error("Commit message must include a valid scope in "
                          "the format (scope).", status="")
        return False
    scope = match.group(1)
    log_message.info(f"Commit scope '{scope}' is valid.", status="")
    return True


def check_description(commit_message: str, log_message: Any) -> bool:
    """Check if the description is present and valid."""
    match = re.match(r"^\w+\([^)]+\):\s+(.+)", commit_message)
    if not match:
        log_message.error("Commit message must include a description "
                          "after the scope.", status="")
        return False
    description = match.group(1)
    log_message.info(
        f"Commit description '{description}' is valid.",
        status="")
    return True


def check_line_length(commit_message: str, log_message: Any) -> bool:
    """Check if the first line of the commit message exceeds 72 characters."""
    if len(commit_message) > 72:
        log_message.error(
            "First line of the commit message exceeds 72 characters.",
            status="")
        fixed_message = fix_commit_message(commit_message)
        log_message.info(f"Auto-fixed message: {fixed_message}", status="")
        return False
    log_message.info("First line length is within the limit.", status="")
    return True


def check_body(commit_message_lines: list, log_message: Any) -> bool:
    """Check if the body (if present) is separated by a blank line and
    formatted correctly."""
    if len(commit_message_lines) > 1 and commit_message_lines[1].strip():
        log_message.error(
            "Body must be separated from the header by a blank line.",
            status="")
        return False
    log_message.info("Body separation is valid (if present).", status="")
    return True


def check_footer(commit_message_lines: list, log_message: Any) -> bool:
    """Check for breaking changes in the footer."""
    for line in commit_message_lines[2:]:
        if line.startswith("BREAKING CHANGE:") and len(line) > 72:
            log_message.error(
                "BREAKING CHANGE footer exceeds 72 characters.",
                status="")
            return False
    log_message.info("Footer (if present) is valid.", status="")
    return True


def validate_commit_message(commit_message: str, log_message: Any) -> bool:
    """Perform step-by-step validation of a commit message."""

    commit_lines = commit_message.splitlines()
    header = commit_lines[0].strip()

    # Step 1: Check for optional prefix
    header = check_prefix(header, log_message)

    # Step 2: Check commit type
    if not check_type(header, log_message):
        return False

    # Step 3: Check scope
    if not check_scope(header, log_message):
        return False

    # Step 4: Check description
    if not check_description(header, log_message):
        return False

    # Step 5: Check first line length
    if not check_line_length(header, log_message):
        return False

    # Step 6: Check body
    if not check_body(commit_lines, log_message):
        return False

    # Step 7: Check footer (Breaking changes)
    if not check_footer(commit_lines, log_message):
        return False

    log_message.info("Commit message passed all validation checks.", status="")
    return True
