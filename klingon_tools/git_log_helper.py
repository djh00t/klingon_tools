# klingon_tools/git_log_helper.py
"""
Module: git_log_helper

This module provides functions for working with git commit logs.
Check if a branch exists in the repository.
Get the commit log for the specified branch.
"""
import subprocess
from klingon_tools.log_msg import log_message


def branch_exists(branch_name: str) -> bool:
    """Check if a branch exists in the repository.

    Args:
        branch_name: The name of the branch to check.

    Returns:
        True if the branch exists, False otherwise.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch_name],
        capture_output=True,
        text=True,
        # We don't want to raise an exception if the branch doesn't exist
        check=False
    )
    return result.returncode == 0


def get_commit_log(branch_name: str) -> subprocess.CompletedProcess:
    """Get the commit log for the specified branch.

    This function retrieves a log of all commits that the current HEAD is
    ahead of the specified branch by.

    Args:
        branch_name: The name of the branch to compare against HEAD.

    Returns:
        A CompletedProcess instance containing the commit log output.
        If the branch doesn't exist, returns an empty CompletedProcess.
    """
    if branch_exists(branch_name):
        commit_result = subprocess.run(
            [
                "git",
                "--no-pager",
                "log",
                f"{branch_name}..HEAD",
                "--pretty=format:%s",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    else:
        log_message.warning(f"The branch '{branch_name}' does not exist.")
        commit_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=""
        )
    return commit_result
