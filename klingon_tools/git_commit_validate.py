# klingon_tools/git_commit_validate.py
"""
Module for validating Git commit messages.

This module provides functions to validate Git commit messages to ensure they
follow the Conventional Commits standard and are properly formatted.

Typical usage example:

    from klingon_tools.git_commit_validate import validate_commit_message
    from klingon_tools.logtools import LogTools

    log_message = LogTools().LogMessage("commit_validator")
    is_valid, fixed_message = validate_commit_message(commit_message, log_message)
    if not is_valid and fixed_message:
        # Handle the auto-fixed message accordingly
        pass
"""
from typing import Any, Optional, Tuple
import re
import textwrap

from click import style

from klingon_tools.git_commit_fix import fix_commit_message
from klingon_tools.log_msg import klog_hr


def is_commit_message_signed_off(commit_message: str) -> bool:
    """
    Check if the commit message is signed off.

    Args:
        commit_message: The commit message to check.

    Returns:
        True if the commit message is signed off, False otherwise.
    """
    return "Signed-off-by:" in commit_message.strip()


def check_prefix(
        commit_message: str,
        log_message: Any
) -> Tuple[str, Optional[str], str]:
    """
    Check for optional emoji prefix and remove if present.

    Args:
        commit_message: The commit message to check.
        log_message: Logger object for logging messages.

    Returns:
        A tuple containing the commit message without the prefix,
        the prefix if found (or None if no prefix was present),
        and the original commit message.
    """
    import emoji
    # Check for emoji at the start of the message
    match = re.match(r'^(\s*[^\w\s]+\s*)', commit_message)
    if match:
        prefix = match.group(1)
        if any(emoji.is_emoji(char) for char in prefix):
            # Log the emoji prefix
            log_message.info(
                message="Emoji prefix found",
                status=f"{prefix.strip()}"
            )
            # Remove the prefix and any immediately following space
            return commit_message[
                len(prefix):
            ].lstrip(), prefix.strip(), commit_message

    log_message.info(message="Emoji prefix not present", status="ℹ️")
    return commit_message, None, commit_message


def check_type(commit_message: str, log_message: Any) -> bool:
    """
    Check if the commit type is valid.

    Args:
        commit_message: The commit message to check.
        log_message: Logger object for logging messages.

    Returns:
        True if the commit type is valid, False otherwise.
    """
    # Valid commit types
    valid_types = [
        "feat", "fix", "chore", "doc", "docs", "style", "refactor",
        "perf", "test", "build", "ci", "revert", "wip"
    ]

    # Check if the commit type is valid
    match = re.match(r"^(\w+)\(", commit_message)
    if not match:
        log_message.error(
            message="Invalid commit type. Type must be one of: "
            f"{', '.join(valid_types)}.",
            status="❌"
        )
        return False
    commit_type = match.group(1)
    if commit_type not in valid_types:
        log_message.error(
            message=f"Invalid commit type: {commit_type}.",
            status="❌"
        )
        return False

    log_message.info(
        message="Commit type found",
        status=f"{commit_type}"
    )
    return True


def check_scope(commit_message: str, log_message: Any) -> bool:
    """Check if the scope is present and valid.

    Args:
        commit_message: The commit message to check.
        log_message: Logger object for logging messages.

    Returns:
        True if the scope is present and valid, False otherwise.
    """
    match = re.match(r"^\w+\(([^)]+)\):", commit_message)
    if not match:
        log_message.error("Commit message must include a valid scope in "
                          "the format (scope).", status="❌")
        return False
    scope = match.group(1)
    log_message.info(
        message="Scope found",
        status="✅"
    )
    log_message.debug(
        message="Scope",
        status=f"{scope}"
    )
    return True


def check_description(commit_message: str, log_message: Any) -> bool:
    """Check if the description is present and valid.

    Args:
        commit_message: The commit message to check.
        log_message: Logger object for logging messages.

    Returns:
        True if the description is present and valid, False otherwise.
    """
    match = re.match(r"^\w+\([^)]+\):\s+(.+)", commit_message)
    if not match:
        log_message.error("Commit message must include a description "
                          "after the scope.", status="❌")
        return False
    description = match.group(1)
    log_message.info(
        message="Description found",
        status="✅"
    )
    log_message.debug(
        message="Description",
        status=f"{description}"
    )
    return True


def check_line_length(
    commit_message: str,
    log_message: Any
) -> Tuple[bool, Optional[str]]:
    """Check if the first line of the commit message exceeds 72 characters.

    Args:
        commit_message: The commit message to check.
        log_message: Logger object for logging messages.

    Returns:
        A tuple where the first element is True if the first line length is valid,
        False otherwise, and the second element is the fixed message if auto-fixed.
    """
    first_line = commit_message.split('\n')[0]
    first_line_length = len(first_line)
    if first_line_length > 72:
        log_message.error(
            message="First line length is invalid",
            reason=f"{first_line_length} chars",
            status="❌"
        )
        fixed_message = fix_commit_message(first_line)
        log_message.info(
            message="Fixing first line length",
            status="🔧"
        )
        log_message.info(
            message=f"Auto-fixed message: {fixed_message}",
            status="✅"
        )
        return False, fixed_message
    log_message.info(
        message=f"First line length is valid ({first_line_length} chars)",
        status="✅"
    )
    return True, None


def check_body(commit_message_lines: list, log_message: Any) -> bool:
    """Check if the body (if present) is separated by a blank line and
    formatted correctly.

    Args:
        commit_message_lines: List of lines in the commit message.
        log_message: Logger object for logging messages.

    Returns:
        True if the body is properly formatted, False otherwise.
    """
    if len(commit_message_lines) > 1:
        if commit_message_lines[1].strip():
            log_message.error(
                message="Empty line not found between header & body",
                status="❌"
            )
            log_message.error(
                message=f"{commit_message_lines}",
                status="",
                style="none"
            )
            return False
        log_message.info(
            message="Empty line found between header & body",
            status="✅"
        )

        # Extract the body text
        body = "\n".join(commit_message_lines[2:])

        # Log the body details
        klog_hr.debug(char="-")
        log_message.debug(
            message=f"Body before checks:\n{body}",
            status="",
            style="none"
        )
        klog_hr.debug(char="-")

        # Check body width
        log_message.info(
            message="Checking body width",
            status="🔍"
        )
        body_lines = body.split("\n")
        for line in body_lines:
            if len(line) > 72:
                log_message.error(
                    message="Body width is invalid",
                    reason=f"{len(line)} chars",
                    status="❌"
                )
                log_message.info(
                    message="Fixing body wrapping",
                    status="🔧"
                )
                fixed_body = fix_body_wrapping(body)
                if fixed_body != body:
                    log_message.info(
                        message="Fixed body wrapping",
                        status="✅"
                    )
                    klog_hr.debug(char="-")
                    log_message.debug(
                        message=f"Fixed body\n{fixed_body}",
                        status="",
                        style="none"
                    )
                    klog_hr.debug(char="-")
                    # Update the commit message with fixed body
                    commit_message_lines[2:] = fixed_body.splitlines()
                else:
                    log_message.error(
                        message="Body wrapping not fixed",
                        status="❌"
                    )
                break  # Proceed without restarting
        else:
            log_message.info(
                message="Body width is valid",
                status="✅"
            )
    else:
        log_message.info(
            message="No body present",
            status="ℹ️"
        )
    return True


def check_footer(commit_message_lines: list, log_message: Any) -> bool:
    """Check for breaking changes in the footer.

    Args:
        commit_message_lines: List of lines in the commit message.
        log_message: Logger object for logging messages.

    Returns:
        True if the footer is properly formatted, False otherwise.
    """
    if len(commit_message_lines) > 2:
        footer_start = next(
            (i for i, line in enumerate(commit_message_lines[2:])
             if line.startswith("BREAKING CHANGE:")),
            None
        )
        if footer_start is not None:
            footer_start += 2  # Adjust for the offset
            log_message.info(
                message="Footer found",
                status="✅"
            )
            footer = "\n".join(commit_message_lines[footer_start:])
            log_message.debug(
                message=f"Footer before checks:\n{footer}",
                status="",
                style="none"
            )

            if (footer_start > 2 and
                    commit_message_lines[footer_start - 1].strip()):
                log_message.error(
                    message="Empty line not found between body & footer",
                    status="❌"
                )
                return False
            log_message.info(
                message="Empty line found between body & footer",
                status="✅"
            )

            log_message.info(
                message="Checking footer width",
                status="🔍"
            )
            footer_lines = footer.split("\n")
            for line in footer_lines:
                if len(line) > 72:
                    log_message.error(
                        message="Footer width is invalid",
                        reason=f"{len(line)} chars",
                        status="❌"
                    )
                    log_message.info(
                        message="Fixing footer wrapping",
                        status="🔧"
                    )
                    fixed_footer = fix_footer_wrapping(footer)
                    if fixed_footer != footer:
                        log_message.info(
                            message="Fixed footer wrapping",
                            status="✅"
                        )
                        log_message.debug(
                            message=f"Fixed footer\n{fixed_footer}",
                            status="",
                            style="none"
                        )
                        # Update the commit message with fixed footer
                        commit_message_lines[footer_start:] = fixed_footer.splitlines()
                    else:
                        log_message.error(
                            message="Footer wrapping not fixed",
                            status="❌"
                        )
                    break  # Proceed without restarting
            else:
                log_message.info(
                    message="Footer width is valid",
                    status="✅"
                )
        else:
            log_message.info(
                message="No footer present",
                status="🦶"
            )
    return True


def fix_body_wrapping(body: str) -> str:
    """Fix body wrapping to 72 characters.

    Args:
        body: The body text to wrap.

    Returns:
        The body text with proper wrapping.
    """
    fixed_lines = []
    for paragraph in body.split("\n\n"):
        if paragraph.startswith(("- ", "* ", "1. ")):
            # Treat as a single line for bullet points or numbered lists
            fixed_lines.append(
                textwrap.fill(
                    paragraph,
                    width=72,
                    subsequent_indent="  "
                )
            )
        else:
            # Wrap plain text
            fixed_lines.append(textwrap.fill(paragraph, width=72))
    return "\n\n".join(fixed_lines)


def fix_footer_wrapping(footer: str) -> str:
    """Fix footer wrapping to 72 characters.

    Args:
        footer: The footer text to wrap.

    Returns:
        The footer text with proper wrapping.
    """
    return fix_body_wrapping(footer)


def validate_commit_message(
    commit_message: str,
    log_message: Any
) -> Tuple[bool, Optional[str]]:
    """Perform step-by-step validation of a commit message.

    Args:
        commit_message: The commit message to validate.
        log_message: Logger object for logging messages.

    Returns:
        A tuple where the first element is True if the commit message passes all
        validation checks, False otherwise, and the second element is the
        fixed message if an auto-fix was applied.
    """
    fixed_message = commit_message  # Initialize with original message
    needs_fix = False

    if not commit_message:
        log_message.error(
            message="Received empty commit message",
            status="❌"
        )
        return False, None

    # Split the commit message into lines
    commit_message_without_prefix, prefix, original_message = check_prefix(
        commit_message, log_message
    )

    commit_lines = commit_message_without_prefix.splitlines()

    if not commit_lines:
        log_message.error(
            message="Commit message does not contain any content.",
            status="❌"
        )
        return False, None

    # Extract the header of the commit message without prefix
    header = commit_lines[0].strip()

    # Log the commit message parts before checks
    klog_hr.debug(char="-")
    log_message.debug(
        message=f"Header before checks:\n\n{header}",
        status="",
        style="none"
    )
    klog_hr.debug(char="-")

    if len(commit_lines) > 1:
        body = "\n".join(commit_lines[2:])
        # Removed duplicated "Body before checks" log message here
    else:
        body = ""
        log_message.info(
            message="No body present",
            status="ℹ️"
        )

    # Check for footer presence
    footer = ""
    for line in commit_lines[1:]:
        if line.startswith("BREAKING CHANGE:"):
            footer = line[len("BREAKING CHANGE:"):].strip()
            break

    if footer:
        klog_hr.debug(char="-")
        log_message.debug(
            message=f"Footer before checks:\n{footer}",
            status="",
            style="none"
        )
        klog_hr.debug(char="-")
    else:
        klog_hr.debug(char="-")
        log_message.info(
            message="No footer present",
            status="🦶"
        )

    validation_steps = [
        ("commit type", lambda: check_type(header, log_message)),
        ("scope", lambda: check_scope(header, log_message)),
        ("description", lambda: check_description(header, log_message)),
        ("first line length", lambda: check_line_length(header, log_message)),
        ("body", lambda: check_body(commit_lines, log_message)),
        ("footer", lambda: check_footer(commit_lines, log_message))
    ]

    for step_name, check_func in validation_steps:
        log_message.info(
            message=f"Checking for {step_name}",
            status="🔍"
        )
        if step_name == "first line length":
            is_valid, fixed = check_func()
            if not is_valid:
                if fixed:
                    # Replace the first line with the fixed message
                    fixed_message = fixed + "\n" + "\n".join(commit_lines[1:])
                    log_message.info(
                        message=f"First line auto-fixed: {fixed}",
                        status="✅"
                    )
                needs_fix = True
        else:
            result = check_func()
            if not result:
                needs_fix = True
                # Return immediately for validation failures except line length
                if step_name != "first line length":
                    return False, None

    if needs_fix and fixed_message != commit_message:
        log_message.info(
            message="Auto-fixes applied to commit message.",
            status="🔧"
        )
        return False, fixed_message

    log_message.info(
        message="Commit message passed all validation checks.",
        status="✅"
    )
    klog_hr.debug(char="-")
    return True, None
