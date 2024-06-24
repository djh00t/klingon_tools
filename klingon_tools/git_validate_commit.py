import re
from git import Repo
from klingon_tools.logger import logger


def is_commit_message_signed_off(commit_message: str) -> bool:
    """Check if the commit message is signed off."""
    return "Signed-off-by:" in commit_message


def is_conventional_commit(commit_message: str) -> bool:
    """Check if the commit message follows the Conventional Commits standard."""
    conventional_commit_pattern = r"^(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert|wip)(\(\w+\))?: .+"
    return re.match(conventional_commit_pattern, commit_message) is not None


def validate_commit_messages(repo: Repo) -> bool:
    """Validate all commit messages to ensure they are signed off and follow the Conventional Commits standard."""
    for commit in repo.iter_commits("HEAD"):
        commit_message = commit.message
        if not is_commit_message_signed_off(commit_message):
            logger.error(
                message=f"Commit {commit.hexsha} is not signed off.", status="❌"
            )
            return False
        if not is_conventional_commit(commit_message):
            logger.error(
                message=f"Commit {commit.hexsha} does not follow Conventional Commits standard.",
                status="❌",
            )
            return False
    return True
