import os
import sys
import subprocess
import re
from typing import Optional, Tuple
import git
from git import (
    Repo,
    GitCommandError,
    InvalidGitRepositoryError,
    NoSuchPathError,
    exc as git_exc,
)
from klingon_tools.logger import logger
from klingon_tools.git_user_info import get_git_user_info
from klingon_tools.git_validate_commit import (
    is_commit_message_signed_off,
    is_conventional_commit,
)
from klingon_tools.openai_tools import generate_commit_message
from klingon_tools.git_push import git_push
from klingon_tools.git_validate_commit import validate_commit_messages

LOOP_MAX_PRE_COMMIT = 5


# Function to cleanup .lock file
def cleanup_lock_file(repo_path: str) -> None:
    """Cleans up the .lock file in the git repository.

    This function removes the .lock file if it exists in the git repository.

    Returns:
        None
    """
    lock_file_path = os.path.join(repo_path, ".git", "index.lock")
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)
        logger.info("Cleaned up .lock file.")


def git_get_toplevel() -> Optional[Repo]:
    """Initializes a git repository object and returns the top-level directory."""
    try:
        repo = Repo(".", search_parent_directories=True)
        toplevel_dir = repo.git.rev_parse("--show-toplevel")
        # Check if the current branch is a new branch and push it upstream if necessary
        current_branch = repo.active_branch
        tracking_branch = current_branch.tracking_branch()
        if tracking_branch is None:
            logger.info(
                message=f"New branch detected: {current_branch.name}", status="🌱"
            )
            repo.git.push("--set-upstream", "origin", current_branch.name)
            logger.info(
                message=f"Branch {current_branch.name} pushed upstream", status="✅"
            )
        return repo
    except (InvalidGitRepositoryError, NoSuchPathError) as e:
        logger.error(message="Error initializing git repository", status="❌")
        logger.exception(message=f"{e}")
        return None


def git_get_status(repo: Repo) -> None:
    """Retrieves the current status of the git repository."""
    global deleted_files, untracked_files, modified_files, staged_files, committed_not_pushed

    current_branch = repo.active_branch
    deleted_files = [
        item.a_path for item in repo.index.diff(None) if item.change_type == "D"
    ]
    untracked_files = repo.untracked_files
    modified_files = [
        item.a_path for item in repo.index.diff(None) if item.change_type == "M"
    ]
    staged_files = [item.a_path for item in repo.index.diff("HEAD")]
    committed_not_pushed = []

    try:
        for item in repo.head.commit.diff(f"origin/{current_branch}"):
            if hasattr(item, "a_blob") and hasattr(item, "b_blob"):
                committed_not_pushed.append(item.a_path)
    except ValueError as e:
        logger.error(message="Error processing diff-tree output:", status="❌")
        logger.exception(message=f"{e}")
    except Exception as e:
        logger.error(message=f"Unexpected error:", status="❌")
        logger.exception(message=f"{e}")

    return (
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    )


def git_commit_deletes(repo: Repo) -> None:
    """Commits deleted files in the given repository."""
    if deleted_files:
        all_deleted_files = list(
            set(
                deleted_files
                + [
                    item.a_path
                    for item in repo.index.diff("HEAD")
                    if item.change_type == "D"
                ]
            )
        )
        logger.info(message=f"Deleted files", status=f"{len(all_deleted_files)}")
        logger.debug(message=f"Deleted files: {all_deleted_files}", status="🐞")

        for file in all_deleted_files:
            repo.index.remove([file], working_tree=True)

        user_name, user_email = get_git_user_info()
        signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
        commit_message = "chore: Committing deleted files" + signoff
        if not is_commit_message_signed_off(commit_message):
            user_name, user_email = get_git_user_info()
            signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
            commit_message += signoff

        if not is_conventional_commit(commit_message):
            logger.warning(
                message="Commit message does not follow Conventional Commits standard. Regenerating commit message.",
                status="⚠️",
            )
            diff = repo.git.diff("HEAD")
            commit_message = generate_commit_message(diff)

        if not is_commit_message_signed_off(commit_message):
            user_name, user_email = get_git_user_info()
            signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
            commit_message += signoff

        if not is_conventional_commit(commit_message):
            logger.warning(
                message="Commit message does not follow Conventional Commits standard. Regenerating commit message.",
                status="⚠️",
            )
            diff = repo.git.diff("HEAD")
            commit_message = generate_commit_message(diff)

        if not is_commit_message_signed_off(commit_message):
            user_name, user_email = get_git_user_info()
            signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
            commit_message += signoff

        if not is_conventional_commit(commit_message):
            logger.warning(
                message="Commit message does not follow Conventional Commits standard. Regenerating commit message.",
                status="⚠️",
            )
            diff = repo.git.diff("HEAD")
            commit_message = generate_commit_message(diff)

        user_name, user_email = get_git_user_info()
        signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
        commit_message += signoff
        user_name, user_email = get_git_user_info()
        signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
        commit_message += signoff
        repo.git.commit("-S", "-m", commit_message)
        logger.info(
            message=f"Committed {len(all_deleted_files)} deleted files", status="✅"
        )
        git_push(repo)


def git_unstage_files(repo: Repo) -> None:
    """Unstages all staged files in the given repository."""
    logger.info(message="Un-staging all staged files", status="🔄")
    logger.debug(message="Staged files", status=f"{staged_files}")
    for file in staged_files:
        try:
            repo.git.reset(file)
            logger.info(message="Un-staging file", status=f"{file}")
        except git_exc.GitCommandError as e:
            logger.error(message="Error un-staging file", status=f"{file}")
            logger.exception(message=f"{e}")


def git_stage_diff(file_name: str, repo: Repo) -> str:
    """Stages a file, generates a diff, and returns the diff."""
    repo.index.add([file_name])
    staged_files = repo.git.diff("--cached", "--name-only").splitlines()
    logger.debug(message="Staged files", status=f"{staged_files}")

    if file_name in staged_files:
        logger.info(message="Staging file", status="✅")
    else:
        logger.error(message="Failed to stage file", status="❌")
        sys.exit(1)

    diff = repo.git.diff("HEAD", file_name)
    if diff:
        logger.info(message="Diff generated", status="✅")
    else:
        logger.error(message="Failed to generate diff", status="❌")

    return diff


def git_pre_commit(file_name: str, repo: Repo) -> bool:
    """Runs pre-commit hooks on a file."""
    attempt = 0

    while attempt < LOOP_MAX_PRE_COMMIT:
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        process = subprocess.Popen(
            ["pre-commit", "run", "--files", file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        stdout, stderr = [], []

        for line in process.stdout:
            sys.stdout.write(line)
            stdout.append(line)

        for line in process.stderr:
            sys.stderr.write(line)
            stderr.append(line)

        process.wait()
        result = subprocess.CompletedProcess(
            process.args, process.returncode, "".join(stdout), "".join(stderr)
        )

        if "files were modified by this hook" in result.stdout:
            logger.info(message=80 * "-", status="")
            logger.info(message="File modified by pre-commit, restaging", status=f"🔄")
            logger.info(message=80 * "-", status="")
            repo.index.add([file_name])
            attempt += 1
            if attempt == LOOP_MAX_PRE_COMMIT:
                logger.error(
                    f"Pre-commit hooks failed for {file_name} after {LOOP_MAX_PRE_COMMIT} attempts. Exiting script."
                )
                sys.exit(1)
        elif result.returncode == 0:
            logger.info(message=80 * "-", status="")
            logger.info(message="Pre-commit completed", status="✅")
            return True

    return False


def git_commit_file(file_name: str, commit_message: str, repo: Repo) -> None:
    """Commits a file with a given commit message."""
    repo.index.add([file_name])

    try:
        repo.index.commit(commit_message)
        logger.info(message="File committed", status="✅")
    except Exception as e:
        logger.error(message="Failed to commit file", status="❌")
        logger.exception(message=f"{e}")


def log_git_stats() -> None:
    """Logs git statistics."""
    logger.info(message=80 * "-", status="")
    logger.info(message="Deleted files", status=f"{len(deleted_files)}")
    logger.info(message="Untracked files", status=f"{len(untracked_files)}")
    logger.info(message="Modified files", status=f"{len(modified_files)}")
    logger.info(message="Staged files", status=f"{len(staged_files)}")
    logger.info(
        message="Committed not pushed files", status=f"{len(committed_not_pushed)}"
    )
    logger.info(message=80 * "-", status="")
