# klingon_tools/git_commit_fix.py
"""Module for fixing Git commit messages."""


def fix_commit_message(commit_message: str) -> str:
    """Automatically fix simple issues in the commit message.

    This function addresses issues related to line length and formatting
    in Git commit messages.

    Args:
        commit_message: The original commit message.

    Returns:
        A string containing the fixed commit message.
    """
    fixed_lines = []
    for line in commit_message.splitlines():
        while len(line) > 72:
            split_index = line[:72].rfind(' ')
            if split_index == -1:  # No space found, force split at 72
                split_index = 72
            fixed_lines.append(line[:split_index])
            line = line[split_index:].strip()
        fixed_lines.append(line)
    return "\n".join(fixed_lines)
