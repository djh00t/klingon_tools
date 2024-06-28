#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides a script for automating git operations.

The script performs various git operations such as staging, committing, and pushing
files. It also integrates with pre-commit hooks and generates commit messages using
OpenAI's API.

Typical usage example:

    $ python push.py --repo-path /path/to/repo --file-name example.txt

Attributes:
    deleted_files (list): List of deleted files.
    untracked_files (list): List of untracked files.
    modified_files (list): List of modified files.
    staged_files (list): List of staged files.
    committed_not_pushed (list): List of committed but not pushed files.
"""

import os
import sys
import argparse
import logging
import subprocess
from git import Repo
from klingon_tools import LogTools
from klingon_tools.git_tools import (
    git_get_toplevel,
    get_git_user_info,
    git_get_status,
    git_commit_deletes,
    git_unstage_files,
    git_stage_diff,
    git_pre_commit,
    git_commit_file,
    log_git_stats,
    cleanup_lock_file,
)
from klingon_tools.git_push import git_push
from klingon_tools.openai_tools import OpenAITools
from klingon_tools.logger import logger

deleted_files = []
untracked_files = []
modified_files = []
staged_files = []
committed_not_pushed = []


def check_software_requirements() -> None:
    """Checks and installs required software.

    This function checks if the required software, specifically `pre-commit`,
    is installed. If it is not installed, the function installs it using pip.

    Raises:
        subprocess.CalledProcessError: If the installation of `pre-commit` fails.
    """
    try:
        # Check if pre-commit is installed
        # Install pre-commit using pip
        subprocess.run(
            ["pre-commit", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info(message="Checking for software requirements", status="✅")
    except subprocess.CalledProcessError:
        # If pre-commit is not installed, log a warning and install it
        logger.warning(message="pre-commit is not installed.", status="Installing")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pre-commit"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Log the successful installation of pre-commit
        logger.info(message="Installed pre-commit", status="✅")


def workflow_process_file(file_name: str, repo: Repo) -> None:
    """Processes a single file through the workflow.

    This function stages the file, generates a commit message, runs pre-commit hooks,
    commits the file, and pushes the commit if all checks pass.

    Args:
        file_name (str): The name of the file to process.
        repo (Repo): The git repository object.

    Raises:
        SystemExit: If pre-commit hooks fail.
    """
    # Generate a diff for the file
    diff = git_stage_diff(file_name, repo)

    # Generate a commit message using the diff
    diff = repo.git.diff("HEAD")
    openai_tools = OpenAITools()
    commit_message = openai_tools.generate_commit_message(diff)

    # Run pre-commit hooks on the file
    success = git_pre_commit(file_name, repo)

    if success:
        if args.dryrun:
            # Log dry run mode and skip commit and push
            logger.info(
                message="Dry run mode enabled. Skipping commit and push.", status="🚫"
            )
        else:
            # Commit the file
            git_commit_file(file_name, repo, commit_message)
            # Push the commit
            if args.dryrun:
                # Log dry run mode and skip push
                logger.info(message="Dry run mode enabled. Skipping push.", status="🚫")
            else:
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
        # Enable debug mode
        # Log debug mode and git status
        logger.debug(message=f"Debug mode enabled", status="🐞 ")
        git_get_status(repo)
        log_git_stats()


# Initialize logging
log_tools = LogTools()


def startup_tasks() -> None:
    """Runs startup maintenance tasks.

    This function initializes the script by parsing command-line arguments,
    setting up logging, checking software requirements, and retrieving git user
    information. It also changes the working directory to the repository path
    and initializes the git repository.

    Raises:
        SystemExit: If the git repository initialization fails.
    """
    # Parse command-line arguments
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
    parser.add_argument(
        "--dryrun",
        action="store_true",
        help="Run the script without committing or pushing changes",
    )
    # Make args global to access throughout the script
    global args
    args = parser.parse_args()

    # Set logging level for httpx to WARNING
    logging.getLogger("httpx").setLevel(logging.WARNING)

    if args.debug:
        log_tools.set_default_style("pre-commit")
        logger.setLevel(logging.DEBUG)

    # Check and install required software
    check_software_requirements()

    # Retrieve git user information
    user_name, user_email = get_git_user_info()
    logger.info(message="Using git user name:", status=f"{user_name}")
    logger.info(message="Using git user email:", status=f"{user_email}")

    # Make repo_path global to access throughout the script
    global repo_path
    repo_path = args.repo_path
    os.chdir(repo_path)

    # Initialize git repository and get status
    global repo, untracked_files, modified_files
    repo = git_get_toplevel()

    if repo is None:
        # Log error and exit if repository initialization fails
        logger.error("Failed to initialize git repository.")
        sys.exit(1)

    # Get git status
    (
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    ) = git_get_status(repo)
    # Log git statistics
    log_git_stats()
    # Clean up lock file
    cleanup_lock_file(repo_path)


def main() -> None:
    """Main function to run the push script.

    This function initializes the script, processes files based on the provided
    command-line arguments, and performs git operations such as staging, committing,
    and pushing files.

    Raises:
        SystemExit: If any critical operation fails.
    """
    # Run startup tasks to initialize the script
    startup_tasks()

    global repo

    if args.file_name:
        # Process a single file if --file-name is provided
        logger.info("File name mode enabled", status=args.file_name)
        git_unstage_files(repo)
        file = args.file_name
        logger.info(message="Processing single file", status=f"{file}")
        workflow_process_file(file, repo)

    elif args.oneshot:
        # Process only one file if --oneshot is provided
        logger.info("One-shot mode enabled", status="🎯")
        git_unstage_files(repo)
        files_to_process = untracked_files + modified_files

        if not files_to_process:
            logger.info("No untracked or modified files to process.")
        else:
            file = files_to_process[0]
            logger.info(message="Processing first file", status=f"{file}")
            workflow_process_file(file, repo)

    else:
        # Process all untracked and modified files in batch mode
        logger.info("Batch mode enabled", status="📦 ")
        git_unstage_files(repo)
        git_commit_deletes(repo)

        for file in untracked_files + modified_files:
            logger.info(message="Processing file", status=f"{file}")
            workflow_process_file(file, repo)

    if committed_not_pushed and not (
        deleted_files or untracked_files or modified_files or staged_files
    ):
        # Push committed but not pushed files if no other files are present
        logger.info(
            message="Only committed not pushed files found. Running git push.",
            status="🚀",
        )
        if args.dryrun:
            logger.info(message="Dry run mode enabled. Skipping push.", status="🚫")
        else:
            git_push(repo)

    # Log script completion
    logger.info(
        message="All files processed. Script completed successfully.",
        status="🚀 ",
    )
    logger.info(message=80 * "=", status="")


if __name__ == "__main__":
    main()
