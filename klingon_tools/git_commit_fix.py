# klingon_tools/git_commit_fix.py


def fix_commit_message(commit_message: str) -> str:
    """
    Automatically fix simple issues in the commit message (line length,
    formatting).
    """
    # Split message into lines and wrap lines longer than 72 characters
    fixed_lines = []
    for line in commit_message.splitlines():
        while len(line) > 72:
            fixed_lines.append(line[:72])
            line = line[72:].strip()
        fixed_lines.append(line)
    return "\n".join(fixed_lines)
