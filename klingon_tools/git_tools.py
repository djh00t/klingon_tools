"""
Module for various Git operations and utilities.

This module provides functions to interact with a Git repository, including
staging, committing, pushing changes, and running pre-commit hooks. It also
includes functions to retrieve the status of the repository and handle deleted
files.

Typical usage example:

    from klingon_tools.git_tools import git_get_toplevel, git_commit_file

    repo = git_get_toplevel() if repo:
        git_commit_file('example.txt', repo)
"""

import os
import subprocess
import sys
from typing import Optional, Tuple
import psutil
from git import (
    GitCommandError,
    InvalidGitRepositoryError,
    NoSuchPathError,
    Repo,
    exc as git_exc,
)

from klingon_tools.git_push import git_push
from klingon_tools.git_user_info import get_git_user_info
from klingon_tools.log_msg import log_message


def branch_exists(branch_name: str) -> bool:
    """Check if a branch exists in the repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch_name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def cleanup_lock_file(repo_path: str) -> None:
    """Cleans up the .lock file in the git repository.

    This function checks for running `push` or `git` processes and removes the
    .lock file if it exists in the git repository and no conflicting processes
    are found.

    Args:
        repo_path: The path to the git repository.

    Returns:
        None
    """
    # Construct the path to the .lock file
    lock_file_path = os.path.join(repo_path, ".git", "index.lock")

    # Check if the .lock file exists
    if os.path.exists(lock_file_path):
        # Check for running `push` or `git` processes
        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"] in ["push", "git"]:
                log_message.error(
                    message=f"Conflicting process '{proc.info['name']}' with"
                    f"PID {proc.info['pid']} is running. Exiting.",
                    status="❌",
                )
                sys.exit(1)
        # Remove the .lock file if no conflicting processes are found
        os.remove(lock_file_path)
        log_message.info("Cleaned up .lock file.")


def git_get_toplevel() -> Optional[Repo]:
    """Initializes a git repository object and returns the top-level directory.

    This function attempts to initialize a git repository object and retrieve
    the top-level directory of the repository. If the current branch is new, it
    pushes the branch upstream.

    Returns:
        An instance of the git.Repo object if successful, otherwise None.
    """
    try:
        # Initialize the git repository object
        repo = Repo(".", search_parent_directories=True)
        # Retrieve the top-level directory of the repository toplevel_dir =
        # repo.git.rev_parse("--show-toplevel") Check if the current branch is
        # a new branch
        current_branch = repo.active_branch
        tracking_branch = current_branch.tracking_branch()
        if tracking_branch is None:
            log_message.info(
                message=f"New branch detected: {current_branch.name}",
                status="🌱",
            )
            # Push the new branch upstream
            repo.git.push("--set-upstream", "origin", current_branch.name)
            log_message.info(
                message=f"Branch {current_branch.name} pushed upstream",
                status="✅",
            )
        # Return the initialized repository object
        return repo
    except (InvalidGitRepositoryError, NoSuchPathError) as e:
        # Log an error message if the repository initialization fails
        log_message.error(
            message="Error initializing git repository", status="❌"
        )
        log_message.exception(message=f"{e}")
        # Return None if the repository initialization fails
        return None


def git_get_status(repo: Repo) -> Tuple[list, list, list, list, list]:
    """Retrieves the current status of the git repository.

    This function collects and returns the status of the git repository,
    including deleted files, untracked files, modified files, staged files, and
    committed but not pushed files.

    Args:
        repo: An instance of the git.Repo object representing the repository.

    Returns:
        A tuple containing lists of deleted files, untracked files, modified
        files, staged files, and committed but not pushed files.
    """
    deleted_files = []
    untracked_files = []
    modified_files = []
    staged_files = []
    committed_not_pushed = []

    # Get the current branch of the repository
    current_branch = repo.active_branch

    # Initialize lists to store the status of files
    deleted_files = [
        item.a_path
        for item in repo.index.diff(None)
        if item.change_type == "D"
    ]
    untracked_files = repo.untracked_files
    modified_files = [
        item.a_path
        for item in repo.index.diff(None)
        if item.change_type == "M"
    ]
    staged_files = [
        item.a_path for item in repo.index.diff("HEAD")
    ]  # List of staged files
    committed_not_pushed = []  # List of committed but not pushed files

    try:
        # Check for committed but not pushed files
        for item in repo.head.commit.diff(f"origin/{current_branch}"):
            if hasattr(item, "a_blob") and hasattr(item, "b_blob"):
                committed_not_pushed.append(item.a_path)
    except ValueError as e:
        log_message.error(
            message="Error processing diff-tree output:", status="❌"
        )
        log_message.exception(message=f"{e}")
    except Exception as e:
        log_message.error(message="Unexpected error:", status="❌")
        log_message.exception(message=f"{e}")

    return (
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    )


def git_commit_deletes(repo: Repo, deleted_files: list) -> None:
    """Commits deleted files in the given repository.

    This function identifies deleted files in the repository, stages them for
    commit, generates a commit message, and commits the changes. It ensures
    that the commit message is signed off by the user.

    Args:
        repo: An instance of the git.Repo object representing the repository.
        deleted_files: A list of deleted files to be committed.

    Returns:
        None
    """
    if deleted_files:
        # Log the number of deleted files
        log_message.info(
            message="Processing deleted files",
            status=f"{len(deleted_files)}",
        )
        log_message.debug(
            message=f"Deleted files: {deleted_files}", status="🐞"
        )

        successfully_staged = []
        # Stage the deleted files for commit using git rm
        for file in deleted_files:
            try:
                # Use git rm to properly stage the deletion
                repo.git.rm(file)
                successfully_staged.append(file)
                log_message.info(
                    message=f"Staged deletion of {file}",
                    status="✅"
                )
            except git_exc.GitCommandError as e:
                if "did not match any files" in str(e):
                    # File is already deleted, try to stage it
                    try:
                        repo.git.add(file)
                        successfully_staged.append(file)
                        log_message.info(
                            message=f"Staged already deleted file {file}",
                            status="✅"
                        )
                    except git_exc.GitCommandError as inner_e:
                        log_message.error(
                            message=f"Failed to stage deleted file {file}",
                            status="❌",
                        )
                        log_message.exception(message=f"{inner_e}")
                        continue
                else:
                    log_message.error(
                        message=f"Failed to remove file {file}",
                        status="❌",
                    )
                    log_message.exception(message=f"{e}")
                    continue

        if successfully_staged:
            # Generate the commit message with scope
            commit_message = (
                f"chore: Delete {len(successfully_staged)}"
                f" file(s)"
            )

            # Add sign-off if it doesn't exist
            if "Signed-off-by:" not in commit_message:
                user_name, user_email = get_git_user_info()
                signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
                commit_message += signoff

            # Commit the deleted files with the generated commit message
            try:
                repo.index.commit(commit_message.strip())
                log_message.info(
                    message=f"Committed {len(successfully_staged)} deleted "
                    "file(s)",
                    status="✅"
                )
            except GitCommandError as e:
                if "gpg failed to sign the data" in str(e):
                    log_message.warning(
                        message=(
                            "GPG signing failed. Retrying commit without GPG "
                            "signing."
                        ),
                        status="👾",
                    )
                    try:
                        repo.index.commit(commit_message.strip())
                    except GitCommandError as inner_e:
                        log_message.error(
                            message="Failed to commit deleted files",
                            status="❌",
                        )
                        log_message.exception(message=f"{inner_e}")
                        raise
                else:
                    log_message.error(
                        message="Failed to commit deleted files", status="❌"
                    )
                    log_message.exception(message=f"{e}")
                    raise

            # Push the commit to the remote repository
            git_push(repo)
        else:
            log_message.info(message="No deleted files to commit", status="ℹ️")


def git_commit_file(
    file_name: str, repo: Repo, commit_message: Optional[str] = None
) -> bool:
    """Commits a file with a validated commit message.

    This function stages the specified file and commits it to the repository
    using a commit message provided by push.py after validation.

    Args:
        file_name (str): The name of the file to be committed.
        repo (Repo): An instance of the git.Repo object representing the
        repository.
        commit_message (Optional[str]): The commit message to use (validated
        externally).

    Returns:
        bool: True if the commit was successful, False otherwise.
    """
    try:
        # Stage the file
        repo.index.add([file_name])
        log_message.info(message=f"File staged: {file_name}", status="✅")

        # Ensure commit message is not None or empty
        if not commit_message:
            raise ValueError("Commit message cannot be empty")

        # Commit the file
        repo.index.commit(commit_message.strip())
        log_message.info(message=f"File committed: {file_name}", status="✅")
        return True

    except ValueError as ve:
        log_message.error(
            message=f"Commit message error: {ve}", status="❌")
    except GitCommandError as ge:
        log_message.error(
            message=f"Git command error: {ge}", status="❌")
    except Exception as e:
        log_message.error(
            message=f"Unexpected error during commit: {e}",
            status="❌")

    return False


def log_git_stats(
    deleted_files: list,
    untracked_files: list,
    modified_files: list,
    staged_files: list,
    committed_not_pushed: list,
) -> None:
    """Logs git statistics.

    This function logs the number of deleted files, untracked files, modified
    files, staged files, and committed but not pushed files in the repository.

    Returns:
        None
    """
    # Log a separator line
    log_message.info(message=80 * "-", status="", style="none")
    # Log the number of deleted files
    log_message.info(message="Deleted files", status=f"{len(deleted_files)}")
    # Log the number of untracked files
    log_message.info(
        message="Untracked files", status=f"{len(untracked_files)}"
    )
    # Log the number of modified files
    log_message.info(message="Modified files", status=f"{len(modified_files)}")
    # Log the number of staged files
    log_message.info(message="Staged files", status=f"{len(staged_files)}")
    # Log the number of committed but not pushed files
    log_message.info(
        message="Committed not pushed files",
        status=f"{len(committed_not_pushed)}",
    )
    log_message.info(message=80 * "-", status="", style="none")


def push_changes_if_needed(repo: Repo, args) -> None:
    """Push changes to the remote repository if there are new commits.

    This function checks if there are new commits to push to the remote
    repository. If there are, it pushes the changes. It also handles dry run
    mode and performs cleanup after the push operation.

    Args:
        repo: An instance of the git.Repo object representing the repository.
        args: Command-line arguments.

    Returns:
        None
    """
    def push_submodules(repo: Repo):
        """Recursively push changes in submodules."""
        for submodule in repo.submodules:
            submodule_repo = submodule.module()
            if submodule_repo.is_dirty(untracked_files=True):
                submodule_repo.git.add(A=True)
                submodule_repo.index.commit("Update submodule")
                push_submodules(submodule_repo)
            submodule_repo.remotes.origin.push()

    # Retrieve the current status of the repository
    _, _, _, _, committed_not_pushed = git_get_status(repo)

    try:
        # Check if there are new commits to push
        if committed_not_pushed:
            log_message.info(
                message="Committing not pushed files found. Pushing changes.",
                status="🚀",
            )
            if args.dryrun:
                log_message.info(
                    message="Dry run mode enabled. Skipping push.", status="🚫"
                )
            else:
                # Push the commit
                git_push(repo)
                # Push changes in submodules
                push_submodules(repo)

                # Perform cleanup after push operation
                cleanup_lock_file(args.repo_path)
        else:
            log_message.info(
                message="No new commits to push. Skipping push.", status="🚫"
            )
    except Exception as e:
        log_message.error(message="Failed to push changes", status="❌")
        log_message.error(
            message=f"{e}",
            status="",
            style="none",
        )


def fix_commit_message(commit_message: str) -> str:
    """
    Fixes the commit message by ensuring it follows the conventional format.
    """
    if not commit_message.startswith("chore:"):
        commit_message = "chore: " + commit_message

    # Split the message into lines
    lines = commit_message.splitlines()
    fixed_lines = []

    for line in lines:
        if len(line) <= 72:
            fixed_lines.append(line)
        else:
            while len(line) > 72:
                # Find the last space within the first 72 characters
                split_pos = line.rfind(' ', 0, 72)
                if split_pos == -1:
                    # If no space is found, split at 72 characters
                    split_pos = 72
                fixed_lines.append(line[:split_pos].rstrip())
                line = line[split_pos:].lstrip()
            fixed_lines.append(line)

    return 'chore: ' + '\n'.join(fixed_lines)


def handle_file_deletions(repo: Repo) -> None:
    """Handles file deletions in the repository."""
    deleted_files = subprocess.run(
        ["git", "ls-files", "--deleted"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()

    for file in deleted_files:
        try:
            repo.index.remove([file], working_tree=True)
            commit_message = f"chore({file}): Cleanup deleted items"
            repo.index.commit(commit_message)
        except GitCommandError as e:
            log_message.error(f"Failed to handle deletion for {file}: {e}")
