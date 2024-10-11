"""Module for various Git operations and utilities.

This module provides functions to interact with a Git repository, including
staging, committing, pushing changes, and running pre-commit hooks. It also
includes functions to retrieve the status of the repository and handle deleted
files.

Typical usage example:

    from klingon_tools.git_tools import git_get_toplevel, git_commit_file

    repo = git_get_toplevel()
    if repo:
        git_commit_file('example.txt', repo)
"""

import os
import subprocess
import sys
from typing import Optional, Tuple
import psutil
from git import (
    Repo,
    InvalidGitRepositoryError,
    NoSuchPathError,
    GitCommandError
)
from klingon_tools.git_push_helper import git_push
from klingon_tools.log_msg import log_message

LOOP_MAX_PRE_COMMIT = 10


def branch_exists(branch_name: str) -> bool:
    """Check if a branch exists in the repository.

    Args:
        branch_name: The name of the branch to check.

    Returns:
        bool: True if the branch exists, False otherwise.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch_name],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def cleanup_lock_file(repo_path: str) -> None:
    """Clean up the .lock file in the git repository.

    This function checks for running `push` or `git` processes and removes the
    .lock file if it exists in the git repository and no conflicting processes
    are found.

    Args:
        repo_path: The path to the git repository.
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
    except (GitCommandError, TypeError, AttributeError) as e:
        log_message.error(
            message="Error processing repository data:",
            status="❌"
        )
        log_message.exception(message=f"{e}")
    except OSError as e:
        log_message.error(message="OS error occurred:", status="❌")
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
        # Stage and commit the deleted files
        for file in deleted_files:
            try:
                # Remove the file from the working tree
                repo.index.remove([file], working_tree=True)

                # Set the commit message for the deleted file
                commit_message = f"chore({file}): deleted file"

                # Commit the deleted file
                repo.index.commit(commit_message)

                # Remove the file from the list of deleted files
                deleted_files.remove(file)

                # Log the status of the commit operation
                log_message.info(
                    message=f"Committed deleted file: {file}",
                    status="✅"
                )

            # Handle any exceptions that occur during the commit operation
            except GitCommandError as e:
                log_message.error(
                    message=f"Failed to commit deleted file {file}",
                    status="❌"
                )
                log_message.exception(message=f"{e}")
                continue


def git_stage_diff(file_name: str, repo: Repo) -> str:
    """
    Stages a file, generates a diff, and returns the diff.

    This function stages the specified file in the repository, generates a diff
    for the file, and returns the diff as a string. It logs the status
    of the staging and diff generation processes.

    Args:
        file_name: The name of the file to be staged and diffed.
        repo: An instance of the git.Repo object representing the repository.
        modified_files: A list of modified files in the repository.

    Returns:
        A string containing the diff of the staged file.
    """
    # Attempt to stage the file in the repository's index
    try:
        log_message.debug(
            message="Staging file in repo",
            status=f"{repo.working_dir}"
            )

        # Stage the file in the repository's index, report success/failure
        staged = repo.index.add([file_name])
        if staged:
            log_message.debug(
                message="File staged successfully in repo.",
                status="✅"
                )
        else:
            log_message.error(
                f"Failed to stage file: {file_name}",
                status="❌"
                )
            sys.exit(1)

    # Handle any exceptions that occur during the staging process
    except GitCommandError as e:
        log_message.error(f"Git error staging file: {file_name}", status="❌")
        log_message.exception(message=f"{e}")
        sys.exit(1)
    except OSError as e:
        log_message.error(f"OS error staging file: {file_name}", status="❌")
        log_message.exception(message=f"{e}")
        sys.exit(1)

    # Now generate diff for the staged file
    try:
        # Log the start of the diff generation process
        log_message.info(
            message="Generating diff for file",
            status=f"{file_name}",
            )

        # Generate the diff of the staged file against the HEAD commit
        diff = repo.git.diff("HEAD", file_name)

        # Check if the diff was successfully generated and log the status
        if diff:
            log_message.info(message="Diff generated", status="✅")
        else:
            log_message.error(message="Failed to generate diff", status="❌")

    # Handle any exceptions that occur during the diff generation process
    except GitCommandError as e:
        log_message.error(message="Git error generating diff", status="❌")
        log_message.exception(message=f"{e}")
        sys.exit(1)
    except OSError as e:
        log_message.error(message="OS error generating diff", status="❌")
        log_message.exception(message=f"{e}")
        sys.exit(1)

    # Return the generated diff as a string
    return diff


def git_pre_commit(
    file_name: str, repo: Repo
) -> Tuple[bool, str]:
    """Runs pre-commit hooks on a file.

    This function runs pre-commit hooks on the specified file. If the hooks
    modify the file, it re-stages the file and re-runs the hooks up to a
    maximum number of attempts. If the hooks pass without modifying the file,
    it returns True. If the hooks fail after the maximum number of attempts, it
    exits the script.

    Args:
        file_name: The name of the file to run pre-commit hooks on. repo: An
        instance of the git.Repo object representing the repository.

    Returns:
        A tuple containing a boolean indicating if the pre-commit hooks passed,
        and the diff of the file if it was modified.
    """
    attempt = 0  # Initialize the attempt counter
    diff = ""  # Initialize diff as an empty string
    log_message.info(80 * "-", status="", style="none")
    log_message.info("Starting pre-commit hooks for", status=f"{file_name}")

    while attempt < LOOP_MAX_PRE_COMMIT:
        # Log start of attempt number
        log_message.info(
            message="Running pre-commit attempt",
            status=f"{attempt + 1}/{LOOP_MAX_PRE_COMMIT}",
        )
        env = os.environ.copy()  # Copy the current environment variables
        # Set PYTHONUNBUFFERED to ensure real-time output
        env["PYTHONUNBUFFERED"] = "1"

        with subprocess.Popen(  # Run the pre-commit hooks
            ["pre-commit", "run", "--files", file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        ) as process:
            stdout, stderr = (
                [],
                [],
            )  # Initialize lists to capture stdout and stderr

            for line in process.stdout:  # Capture stdout line by line
                # Replace specific strings with emoticons
                modified_line = (
                    line.replace("Passed", "✅")
                    .replace("Skipped", "⏭️")
                    .replace("Failed", "❌")
                )
                sys.stdout.write(modified_line)
                stdout.append(modified_line)

            for line in process.stderr:  # Capture stderr line by line
                # Replace specific strings with emoticons
                modified_line = (
                    line.replace("Passed", "✅")
                    .replace("Skipped", "⏭️")
                    .replace("Failed", "❌")
                )
                sys.stderr.write(modified_line)
                stderr.append(modified_line)

            process.wait()  # Wait for the process to complete
        result = (
            subprocess.CompletedProcess(  # Create a CompletedProcess instance
                process.args,
                process.returncode,
                "".join(stdout),
                "".join(stderr),
            )
        )

        log_message.debug(
            message="Pre-commit hooks completed with return code",
            status=f"{result.returncode}",
        )
        if (
            "files were modified by this hook" in result.stdout
            or "Fixing" in result.stdout
        ):
            # Log that the file was modified by the pre-commit hook
            log_message.info(message=80 * "-", status="", style="none")
            log_message.info(
                f"File {file_name} was modified by pre-commit hooks",
                status="🔄",
            )
            log_message.info(
                message=("File modified by pre-commit, restaging"),
                status="🔄",
            )
            log_message.info(message=80 * "-", status="", style="none")

            # Re-stage the file and generate a new diff
            diff = git_stage_diff(file_name, repo)

            # Increment the attempt counter
            attempt += 1  # Increment the attempt counter
            if (
                attempt == LOOP_MAX_PRE_COMMIT
            ):  # Check if maximum attempts reached
                log_message.error(
                    message=(f"Pre-commit hooks failed for {file_name} after "
                             f"{LOOP_MAX_PRE_COMMIT} attempts. Exiting script."
                             ),
                    status="❌",
                )
                # Return False and the last diff if max attempts reached
                return False, diff
        elif result.returncode == 0:  # Check if pre-commit hooks passed
            log_message.info(
                f"Pre-commit hooks passed for {file_name}", status="✅"
            )
            return True, diff  # Return True and the diff if hooks passed
        elif (
            result.returncode == 1
            and "files were modified by this hook" not in result.stdout
            and "Fixing" not in result.stdout
        ):
            log_message.error(
                message=("Pre-commit hooks failed without modifying files. "
                         "Exiting push."),
                status="❌"
            )
            log_message.debug(
                message=f"Pre-commit stdout: {result.stdout}", status=""
            )
            log_message.debug(
                message=f"Pre-commit stderr: {result.stderr}", status=""
            )
            log_message.info(80 * "-", status="", style="none")
            # Return False and the last diff if hooks failed
            return False, diff

    log_message.error(
        message=(f"Pre-commit hooks did not pass for {file_name} after "
                 f"{LOOP_MAX_PRE_COMMIT} attempts"),
        status="❌",
    )
    # Return False and the last diff if pre-commit hooks did not pass
    return False, diff


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
        log_message.debug(message=f"Commit message error details: {ve}")
    except GitCommandError as ge:
        log_message.error(
            message=f"Git command error: {ge}", status="❌")
        log_message.debug(message=f"Git command error details: {ge}")
    except (OSError, IOError) as e:
        log_message.error(
            message=f"File system error during commit: {e}",
            status="❌"
        )
        log_message.debug(message=f"File system error details: {e}")

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
    All values are padded with spaces to align with the longest value.

    Returns:
        None
    """
    # Create a list of tuples with message and count
    stats = [
        ("Deleted files", len(deleted_files)),
        ("Untracked files", len(untracked_files)),
        ("Modified files", len(modified_files)),
        ("Staged files", len(staged_files)),
        ("Committed not pushed files", len(committed_not_pushed))
    ]

    # Find the length of the longest count
    max_count_length = max(len(str(count)) for _, count in stats)

    # Add 1 extra space if max count length is 1 character
    if max_count_length == 1:
        max_count_length += 1

    # Log a separator line
    log_message.info(message="-" * 79, status="", style="none")

    # Log each statistic with padded count
    for message, count in stats:
        # Right justify count with spaces based on max_count_length
        padded_count = str(count).ljust(max_count_length)
        log_message.info(message=message, status=padded_count)

    log_message.info(message=79 * "-", status="", style="none")


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
    # Update git status variables so we have a count of files to push from
    # committed_not_pushed
    committed_not_pushed = git_get_status(repo)[-1]

    def push_submodules(repo: Repo):
        """Recursively push changes in submodules."""
        for submodule in repo.submodules:
            submodule_repo = submodule.module()
            if submodule_repo.is_dirty(untracked_files=True):
                submodule_repo.git.add(A=True)
                submodule_repo.index.commit("Update submodule")
                push_submodules(submodule_repo)
            submodule_repo.remotes.origin.push()

    try:
        # Check if there are new commits to push
        if (
            repo.is_dirty(index=True, working_tree=False)
            or committed_not_pushed
        ):
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
        elif committed_not_pushed:
            log_message.info(
                message="Committing not pushed files found. Pushing changes.",
                status="🚀"
            )
            git_push(repo)
            # Push changes in submodules
            push_submodules(repo)
        else:
            log_message.info(
                message="No new commits to push. Skipping push.", status="🚫"
            )
    except (GitCommandError, OSError) as e:
        log_message.error(message="Failed to push changes", status="❌")
        log_message.exception(message=f"{e}")
