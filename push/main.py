import os
import sys
import argparse
import logging
import subprocess
from git import Repo
from git_utils import (
    git_get_toplevel,
    get_git_user_info,
    git_get_status,
    git_commit_deletes,
    git_unstage_files,
    git_stage_diff,
    git_pre_commit,
    git_commit_file,
    log_git_stats,
    git_push,
    cleanup_lock_file,
)
from openai_utils import generate_commit_message
from logging_utils import logger, log_tools

deleted_files = []
untracked_files = []
modified_files = []
staged_files = []
committed_not_pushed = []


def check_software_requirements() -> None:
    """Checks and installs required software."""
    try:
        subprocess.run(
            ["pre-commit", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info(message="Checking for software requirements", status="✅")
    except subprocess.CalledProcessError:
        logger.warning(message="pre-commit is not installed.", status="Installing")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pre-commit"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info(message="Installed pre-commit", status="✅")


def workflow_process_file(file_name: str, repo: Repo) -> None:
    """Processes a single file through the workflow."""
    # Generate a diff for the file
    diff = git_stage_diff(file_name, repo)

    # Generate a commit message from the diff
    commit_message = generate_commit_message(diff)

    # Run pre-commit hooks on the file
    success = git_pre_commit(file_name, repo)

    if success:
        # Commit the file
        git_commit_file(file_name, commit_message, repo)
        # Push the commit
        git_push(repo)
    else:
        # Log pre-commit hook failure
        logger.error(message="Pre-commit hooks failed. Exiting script.", status="❌")
        # Log git status
        (
            deleted_files,
            untracked_files,
            modified_files,
            staged_files,
            committed_not_pushed,
        ) = git_get_status(repo)
        # Log git stats
        log_git_stats()
        # Exit script
        sys.exit(1)

    if args.debug:
        logger.debug(message=f"Debug mode enabled", status="🐞 ")
        git_get_status(repo)
        log_git_stats()


def startup_tasks() -> None:
    """Runs startup maintenance tasks."""
    parser = argparse.ArgumentParser(
        description="Git repository status checker and committer."
    )
    parser.add_argument(
        "--repo-path", type=str, default=".", help="Path to the git repository"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--file-name", type=str, help="File name to stage and commit")
    parser.add_argument(
        "--oneshot",
        action="store_true",
        help="Process and commit only one file then exit",
    )
    global args
    args = parser.parse_args()

    logging.getLogger("httpx").setLevel(logging.WARNING)

    if args.debug:
        log_tools.set_default_style("pre-commit")
        logger.setLevel(logging.DEBUG)

    check_software_requirements()

    user_name, user_email = get_git_user_info()
    logger.info(message="Using git user name:", status=f"{user_name}")
    logger.info(message="Using git user email:", status=f"{user_email}")

    global repo_path
    repo_path = args.repo_path
    os.chdir(repo_path)

    global repo, untracked_files, modified_files
    repo = git_get_toplevel()

    if repo is None:
        logger.error("Failed to initialize git repository.")
        sys.exit(1)

    (
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    ) = git_get_status(repo)
    log_git_stats()
    cleanup_lock_file(repo_path)


if __name__ == "__main__":
    # Run startup tasks
    startup_tasks()

    # If --file-name is provided
    if args.file_name:
        # Log processing mode
        logger.info("File name mode enabled", status=args.file_name)

        # Unstage any staged files
        git_unstage_files(repo)

        # Set file name
        file = args.file_name

        # Log processing mode
        logger.info(message="Processing single file", status=f"{file}")

        # Process File
        workflow_process_file(file, repo)

    # If --oneshot is provided
    elif args.oneshot:
        # Log processing mode
        logger.info("One-shot mode enabled", status="🎯")

        # Unstage any staged files
        git_unstage_files(repo)

        # Merge untracked and modified files
        files_to_process = untracked_files + modified_files

        # Get first file in files_to_process
        file = files_to_process[0]

        # Make sure that there are files to process
        if not files_to_process:
            logger.info("No untracked or modified files to process.")
        else:
            # Log processing mode
            logger.info(message="Processing first file", status=f"{file}")

            # Process File
            workflow_process_file(file, repo)

    # If no file selector arguments exist
    else:
        # Log processing mode
        logger.info("Batch mode enabled", status="📦 ")

        # Unstage any staged files
        git_unstage_files(repo)

        # Commit deleted files
        git_commit_deletes(repo)

        # Process untracked and modified files
        for file in untracked_files + modified_files:
            # Log file processing
            logger.info(message="Processing file", status=f"{file}")

            # Process file
            workflow_process_file(file, repo)

    # Log script completion
    logger.info(
        message="All files processed. Script completed successfully.",
        status="🚀 ",
    )
    logger.info(message=80 * "=", status="")
