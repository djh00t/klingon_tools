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


def cleanup_lock_file(repo_path: str) -> None:
    """Cleans up the .lock file in the git repository.

    This function removes the .lock file if it exists in the git repository.

    Args:
        repo_path: The path to the git repository.

    Returns:
        None
    """
    # Construct the path to the .lock file
    lock_file_path = os.path.join(repo_path, ".git", "index.lock")

    # Check if the .lock file exists and remove it
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)
        logger.info("Cleaned up .lock file.")


def git_get_toplevel() -> Optional[Repo]:
    """Initializes a git repository object and returns the top-level directory.

    This function attempts to initialize a git repository object and retrieve
    the top-level directory of the repository. If the current branch is new,
    it pushes the branch upstream.

    Returns:
        An instance of the git.Repo object if successful, otherwise None.
    """
    try:
        # Initialize the git repository object
        repo = Repo(".", search_parent_directories=True)
        # Retrieve the top-level directory of the repository
        toplevel_dir = repo.git.rev_parse("--show-toplevel")
        # Check if the current branch is a new branch
        current_branch = repo.active_branch
        tracking_branch = current_branch.tracking_branch()
        if tracking_branch is None:
            logger.info(
                message=f"New branch detected: {current_branch.name}", status="🌱"
            )
            # Push the new branch upstream
            repo.git.push("--set-upstream", "origin", current_branch.name)
            logger.info(
                message=f"Branch {current_branch.name} pushed upstream", status="✅"
            )
        # Return the initialized repository object
        return repo
    except (InvalidGitRepositoryError, NoSuchPathError) as e:
        # Log an error message if the repository initialization fails
        logger.error(message="Error initializing git repository", status="❌")
        logger.exception(message=f"{e}")
        # Return None if the repository initialization fails
        return None


def git_get_status(repo: Repo) -> Tuple[list, list, list, list, list]:
    """Retrieves the current status of the git repository.

    This function collects and returns the status of the git repository,
    including deleted files, untracked files, modified files, staged files,
    and committed but not pushed files.

    Args:
        repo: An instance of the git.Repo object representing the repository.

    Returns:
        A tuple containing lists of deleted files, untracked files, modified files,
        staged files, and committed but not pushed files.
    """
    global deleted_files, untracked_files, modified_files, staged_files, committed_not_pushed

    # Get the current branch of the repository
    current_branch = repo.active_branch

    # Initialize lists to store the status of files
    deleted_files = [
        # List of deleted files
        item.a_path
        for item in repo.index.diff(None)
        if item.change_type == "D"
    ]
    untracked_files = repo.untracked_files  # List of untracked files
    modified_files = [
        # List of modified files
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
                # Add the file to the committed but not pushed list
                committed_not_pushed.append(item.a_path)
    except ValueError as e:
        # Log an error message if there is an issue processing the diff-tree output
        logger.error(message="Error processing diff-tree output:", status="❌")
        logger.exception(message=f"{e}")
    except Exception as e:
        # Log an error message for any unexpected errors
        logger.error(message=f"Unexpected error:", status="❌")
        logger.exception(message=f"{e}")

    # Return the collected status information
    return (
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    )


def git_commit_deletes(repo: Repo) -> None:
    """Commits deleted files in the given repository.

    This function identifies deleted files in the repository, stages them for
    commit, generates a commit message, and commits the changes. It ensures
    that the commit message follows the Conventional Commits standard and is
    signed off by the user.

    Args:
        repo: An instance of the git.Repo object representing the repository.

    Returns:
        None
    """
    if deleted_files:
        # Combine deleted files from the global list and the repository index
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
        # Log the number of deleted files
        logger.info(message="Deleted files", status=f"{len(all_deleted_files)}")
        logger.debug(message=f"Deleted files: {all_deleted_files}", status="🐞")

        # Stage the deleted files for commit
        for file in all_deleted_files:
            repo.index.remove([file], working_tree=True)

        # Generate the initial commit message
        commit_message = "chore: Committing deleted files"

        # Ensure the commit message is signed off
        if not is_commit_message_signed_off(commit_message):
            user_name, user_email = get_git_user_info()
            signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
            commit_message += signoff

        # Ensure the commit message follows the Conventional Commits standard
        if not is_conventional_commit(commit_message):
            logger.warning(
                message="Commit message does not follow Conventional Commits standard. Regenerating commit message.",
                status="⚠️",
            )
            diff = repo.git.diff("HEAD")
            # Generate the commit message using the diff
            commit_message = generate_commit_message(diff)

        # Re-check and sign off the commit message if necessary
        if not is_commit_message_signed_off(commit_message):
            user_name, user_email = get_git_user_info()
            signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
            commit_message += signoff

        # Re-check and regenerate the commit message if necessary
        if not is_conventional_commit(commit_message):
            logger.warning(
                message="Commit message does not follow Conventional Commits standard. Regenerating commit message.",
                status="⚠️",
            )
            diff = repo.git.diff("HEAD")
            commit_message = generate_commit_message(diff)
        # Commit the deleted files with the generated commit message
        repo.git.commit("-S", "-m", commit_message)

        # Log the successful commit
        logger.info(
            message=f"Committed {len(all_deleted_files)} deleted files", status="✅"
        )

        # Push the commit to the remote repository
        git_push(repo)


def git_unstage_files(repo: Repo) -> None:
    """Unstages all staged files in the given repository.

    This function iterates over all staged files in the repository and
    un-stages them. It logs the status of each file as it is un-staged.

    Args:
        repo: An instance of the git.Repo object representing the repository.

    Returns:
        None
    """
    logger.info(message="Un-staging all staged files", status="🔄")
    logger.debug(message="Staged files", status=f"{staged_files}")

    # Iterate over each staged file and un-stage it
    for file in staged_files:
        try:
            repo.git.reset(file)
            logger.info(message="Un-staging file", status=f"{file}")
        except git_exc.GitCommandError as e:
            logger.error(message="Error un-staging file", status=f"{file}")
            logger.exception(message=f"{e}")


def git_stage_diff(file_name: str, repo: Repo) -> str:
    """Stages a file, generates a diff, and returns the diff.

    This function stages the specified file in the repository, generates a diff
    for the staged file, and returns the diff as a string. It logs the status
    of the staging and diff generation processes.

    Args:
        file_name: The name of the file to be staged and diffed.
        repo: An instance of the git.Repo object representing the repository.

    Returns:
        A string containing the diff of the staged file.
    """
    # Stage the specified file
    # Stage the specified file
    repo.index.add([file_name])
    staged_files = repo.git.diff("--cached", "--name-only").splitlines()
    logger.debug(message="Staged files", status=f"{staged_files}")

    # Check if the file was successfully staged
    if file_name in staged_files:
        logger.info(message="Staging file", status="✅")
    else:
        logger.error(message="Failed to stage file", status="❌")
        sys.exit(1)

    # Generate the diff for the staged file
    diff = repo.git.diff("HEAD", file_name)
    if diff:
        logger.info(message="Diff generated", status="✅")
    else:
        logger.error(message="Failed to generate diff", status="❌")

    return diff


def git_pre_commit(file_name: str, repo: Repo) -> bool:
    """Runs pre-commit hooks on a file.

    This function runs pre-commit hooks on the specified file. If the hooks
    modify the file, it re-stages the file and re-runs the hooks up to a
    maximum number of attempts. If the hooks pass without modifying the file,
    it returns True. If the hooks fail after the maximum number of attempts,
    it exits the script.

    Args:
        file_name: The name of the file to run pre-commit hooks on.
        repo: An instance of the git.Repo object representing the repository.

    Returns:
        True if the pre-commit hooks pass without modifying the file, otherwise
        exits the script after the maximum number of attempts.
    """
    attempt = 0  # Initialize the attempt counter

    while attempt < LOOP_MAX_PRE_COMMIT:
        env = os.environ.copy()  # Copy the current environment variables
        env["PYTHONUNBUFFERED"] = "1"  # Set PYTHONUNBUFFERED to ensure real-time output

        process = subprocess.Popen(  # Run the pre-commit hooks
            ["pre-commit", "run", "--files", file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        stdout, stderr = [], []  # Initialize lists to capture stdout and stderr

        for line in process.stdout:  # Capture stdout line by line
            sys.stdout.write(line)
            stdout.append(line)

        for line in process.stderr:  # Capture stderr line by line
            sys.stderr.write(line)
            stderr.append(line)

        process.wait()  # Wait for the process to complete
        result = subprocess.CompletedProcess(  # Create a CompletedProcess instance
            process.args, process.returncode, "".join(stdout), "".join(stderr)
        )

        if "files were modified by this hook" in result.stdout:
            # Log that the file was modified by the pre-commit hook
            logger.info(message=80 * "-", status="")
            logger.info(message="File modified by pre-commit, restaging", status="🔄")
            logger.info(message=80 * "-", status="")
            repo.index.add([file_name])  # Re-stage the modified file
            attempt += 1  # Increment the attempt counter
            if attempt == LOOP_MAX_PRE_COMMIT:  # Check if maximum attempts reached
                logger.error(
                    message=f"Pre-commit hooks failed for {file_name} after {LOOP_MAX_PRE_COMMIT} attempts. Exiting script.",
                    status="❌",
                )
                sys.exit(1)  # Exit the script if maximum attempts reached
        elif result.returncode == 0:  # Check if pre-commit hooks passed
            logger.info(message=80 * "-", status="")
            logger.info(message="Pre-commit completed", status="✅")
            return True  # Return True if hooks passed

    return False  # Return False if pre-commit hooks did not pass


def git_commit_file(file_name: str, repo: Repo) -> None:
    """Commits a file with a generated commit message.

    This function stages the specified file, generates a commit message using
    the diff of the file, and commits the file to the repository. It logs the
    status of each step and handles exceptions that may occur during the process.

    Args:
        file_name: The name of the file to be committed.
        repo: An instance of the git.Repo object representing the repository.

    Returns:
        None
    """
    repo.index.add([file_name])

    try:
        # Generate the diff for the staged file
        diff = repo.git.diff("HEAD", file_name)
        try:
            commit_message = generate_commit_message(diff)
            # Commit the file with the generated commit message
            repo.index.commit(commit_message.strip())
            # Log the successful commit
            logger.info(message="File committed", status="✅")
        except ValueError as ve:
            # Log an error message if the commit message format is invalid
            logger.error(message="Commit message format error", status="❌")
            logger.exception(message=f"{ve}")
        except Exception as e:
            # Log an error message if the commit fails
            logger.error(message="Failed to commit file", status="❌")
            logger.exception(message=f"{e}")
    except Exception as e:
        # Log an error message if adding the file to the index fails
        logger.error(message="Failed to add file to index", status="❌")
        logger.exception(message=f"{e}")


def log_git_stats() -> None:
    """Logs git statistics.

    This function logs the number of deleted files, untracked files, modified files,
    staged files, and committed but not pushed files in the repository.

    Returns:
        None
    """
    # Log a separator line
    logger.info(message=80 * "-", status="")
    # Log the number of deleted files
    logger.info(message="Deleted files", status=f"{len(deleted_files)}")
    # Log the number of untracked files
    logger.info(message="Untracked files", status=f"{len(untracked_files)}")
    # Log the number of modified files
    logger.info(message="Modified files", status=f"{len(modified_files)}")
    # Log the number of staged files
    logger.info(message="Staged files", status=f"{len(staged_files)}")
    # Log the number of committed but not pushed files
    logger.info(
        message="Committed not pushed files", status=f"{len(committed_not_pushed)}"
    )
    logger.info(message=80 * "-", status="")
