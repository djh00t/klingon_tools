import subprocess
from klingon_tools.logger import logger


def branch_exists(branch_name: str) -> bool:
    """Check if a branch exists in the repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch_name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def get_commit_log(branch_name: str) -> subprocess.CompletedProcess:
    """Get the commit log for the specified branch."""
    if branch_exists(branch_name):
        # Get a log of all changes that this branch is ahead of release by.
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
        logger.warning(f"The branch '{branch_name}' does not exist.")
        commit_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=""
        )
    return commit_result
