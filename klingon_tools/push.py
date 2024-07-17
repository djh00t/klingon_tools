#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides a script for automating git operations.

The script performs various git operations such as staging, committing, and
pushing files. It also integrates with pre-commit hooks and generates commit
messages using OpenAI's API.

Typical usage example:

    $ python push.py --repo-path /path/to/repo --file-name example.txt

Attributes:
    deleted_files (list): List of deleted files.
    untracked_files (list): List of untracked files.
    modified_files (list): List of modified files.
    staged_files (list): List of staged files.
    committed_not_pushed (list): List of committed but not pushed files.
"""
import argparse
import logging
import os
import subprocess
import sys
import requests
from git import Repo
from klingon_tools import LogTools
from klingon_tools.git_tools import (
    LOOP_MAX_PRE_COMMIT,
    cleanup_lock_file,
    get_git_user_info,
    git_commit_deletes,
    git_commit_file,
    git_get_status,
    git_get_toplevel,
    git_pre_commit,
    git_unstage_files,
    log_git_stats,
    process_pre_commit_config,
    push_changes_if_needed,
    git_stage_diff,
)
from klingon_tools.logger import logger
from klingon_tools.openai_tools import OpenAITools

# Initialize variables
deleted_files = []
untracked_files = []
modified_files = []
staged_files = []
committed_not_pushed = []
# repo = None
# args = None
# success = None
# diff = None


def check_software_requirements(repo_path: str, logger) -> None:
    """
    Check and install required software.

    This function checks if the required software, specifically `pre-commit`,
    is installed. If it is not installed, the function installs it using pip.

    Raises:
        subprocess.CalledProcessError: If the installation of `pre-commit`
        fails.
    """
    logger.info(message="Checking for software requirements", status="🔍")
    # Check if .cache/pre-commit directory exists, if not, create it
    cache_dir = os.path.join(repo_path, ".cache", "pre-commit")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        logger.info(message="Created .cache/pre-commit directory", status="✅")

    # Check if .cache/pre-commit/pre-commit.log exists, if not, create it
    log_file = os.path.join(cache_dir, "pre-commit.log")
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("")
        logger.info(
            message="Created .cache/pre-commit/pre-commit.log", status="✅"
        )

    try:
        # Check if pre-commit is installed
        subprocess.run(
            ["pre-commit", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError:
        # If pre-commit is not installed, log a warning and install it
        logger.warning(
            message="pre-commit is not installed.", status="Installing"
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-U",
                "pre-commit",
                "cfgv",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Log the successful installation of pre-commit
        logger.info(message="Installed pre-commit", status="✅")


def run_push_prep(logger) -> None:
    """
    Check for a "push-prep" target in the Makefile and run it if it exists.

    This function checks if the "push-prep" target exists in the Makefile in
    the root of the repository. If it exists, the function runs the target to
    clean up the local codebase before handling any files.

    Raises:
        subprocess.CalledProcessError: If the make command fails.
    """
    makefile_path = os.path.join(os.getcwd(), "Makefile")
    if os.path.exists(makefile_path):
        with open(makefile_path, "r") as makefile:
            if "push-prep:" in makefile.read():
                logger.info(message="Running 'push-prep'", status="✅")
                subprocess.run(["make", "push-prep"], check=True)
            else:
                logger.info(
                    message="'push-prep' target not found in Makefile",
                    status="ℹ️",
                )
    else:
        logger.info(
            message="Makefile not found in the root of the repository",
            status="ℹ️",
        )


def workflow_process_file(
    file_name: str, modified_files: list, repo: Repo, args, logger, log_tools
) -> None:
    """
    Process a single file through the workflow.

    This function stages the file, generates a commit message, runs pre-commit
    hooks, commits the file, and pushes the commit if all checks pass.

    Args:
        file_name (str): The name of the file to process.
        repo (Repo): The git repository object.

    Raises:
        SystemExit: If pre-commit hooks fail.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Git repository status checker and committer."
    )
    parser.add_argument(
        "--repo-path", type=str, default=".", help="Path to the git repository"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode"
    )
    parser.add_argument(
        "--file-name", type=str, help="File name to stage and commit"
    )
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
    # Get git status and update local variables
    (
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    ) = git_get_status(repo)

    # Process deleted files
    if deleted_files:
        git_commit_deletes(repo, deleted_files)

    diff = git_stage_diff(file_name, repo, modified_files)

    attempt = 0
    success = False
    while attempt < LOOP_MAX_PRE_COMMIT:
        # Run pre-commit hooks on the file
        success, diff = git_pre_commit(file_name, repo, modified_files)

        if success:
            if args.dryrun:
                # Log dry run mode and skip commit and push
                logger.info(
                    message="Dry run mode enabled. Skipping commit and push.",
                    status="🚫",
                )
                break
            else:
                # Load OpenAI tools
                openai_tools = OpenAITools()

                # Generate a commit message using the diff
                commit_message = openai_tools.generate_commit_message(diff)

                # Commit the file
                git_commit_file(file_name, repo, commit_message)
                break
        else:
            attempt += 1
            if attempt == LOOP_MAX_PRE_COMMIT:
                # Log pre-commit hook failure
                logger.error(
                    message="Pre-commit hooks failed. Exiting script.",
                    status="❌",
                )
                # Log git status
                (
                    deleted_files,
                    untracked_files,
                    modified_files,
                    staged_files,
                    committed_not_pushed,
                ) = git_get_status(repo)
                # Log git stats
                log_git_stats(
                    deleted_files,
                    untracked_files,
                    modified_files,
                    staged_files,
                    committed_not_pushed,
                )
                # Exit script
                sys.exit(1)

    # Stage the file and generate a diff of the file being processed
    if args.debug:
        # Enable debug mode
        # Log debug mode and git status
        logger.debug(message="Debug mode enabled", status="🐞 ")
        git_get_status(repo)
        log_git_stats(
            deleted_files,
            untracked_files,
            modified_files,
            staged_files,
            committed_not_pushed,
        )


def startup_tasks(args, logger, log_tools) -> Repo:
    """Run startup maintenance tasks.

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
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode"
    )
    parser.add_argument(
        "--file-name", type=str, help="File name to stage and commit"
    )
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
    # Set logging level for httpx to WARNING
    logging.getLogger("httpx").setLevel(logging.WARNING)

    if args.debug:
        log_tools.set_default_style("pre-commit")
        logger.setLevel(logging.DEBUG)

    repo_path = args.repo_path
    os.chdir(args.repo_path)

    # Clean up any existing lock files
    cleanup_lock_file(repo_path)

    # Check if .pre-commit-config.yaml exists, if not, create it
    pre_commit_config_path = os.path.join(repo_path, ".pre-commit-config.yaml")
    if not os.path.exists(pre_commit_config_path):
        logger.info(
            message=".pre-commit-config.yaml not found. "
            "Creating from template.",
            status="📝",
        )
        template_url = (
            "https://raw.githubusercontent.com/djh00t/klingon_tools/main/"
            "repo_templates/python/.pre-commit-config.yaml"
        )
        response = requests.get(template_url)
        if response.status_code == 200:
            with open(pre_commit_config_path, "w") as file:
                file.write(response.text)
            logger.info(
                message=".pre-commit-config.yaml created successfully.",
                status="✅",
            )
        else:
            logger.error(
                message="Failed to download .pre-commit-config.yaml template.",
                status="❌",
            )

    # Check and run the "push-prep" target if it exists
    run_push_prep(logger)

    # Check and install required software
    check_software_requirements(args.repo_path, logger)

    # Retrieve git user information
    user_name, user_email = get_git_user_info()
    logger.info(message="Using git user name:", status=f"{user_name}")
    logger.info(message="Using git user email:", status=f"{user_email}")

    # Initialize git repository and get status
    repo = git_get_toplevel()

    # Return the initialized repo
    return repo


def main():
    """
    Run the push script.

    This function initializes the script, processes files based on the provided
    command-line arguments, and performs git operations such as staging,
    committing, and pushing files.

    Raises:
        SystemExit: If any critical operation fails.
    """
    global args, repo
    global deleted_files
    global untracked_files
    global modified_files
    global staged_files
    global committed_not_pushed

    # Initialize logging
    log_tools = LogTools()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Git repository status checker and committer."
    )
    parser.add_argument(
        "--repo-path", type=str, default=".", help="Path to the git repository"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode"
    )
    parser.add_argument(
        "--file-name", type=str, help="File name to stage and commit"
    )
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
    args = parser.parse_args()

    # Run startup tasks to initialize the script and get repo
    repo = startup_tasks(args, logger, log_tools)

    if repo is None:
        logger.error("Failed to initialize git repository. Exiting.")
        sys.exit(1)

    # Get git status and update global variables
    (
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    ) = git_get_status(repo)

    # Log git statistics
    log_git_stats(
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    )

    # Process a single file if --file-name is provided
    if args.file_name:
        padding = 80 - len(f"File name mode enabled {args.file_name}")
        logger.info(
            f"File name mode enabled{' ' * padding}", status=args.file_name
        )

        # Unstage all staged files if there are any
        if staged_files:
            git_unstage_files(repo, staged_files)

        # If .pre-commit-config.yaml is modified, stage and commit it first
        process_pre_commit_config(repo, modified_files)

        # Set the file name to process
        file = args.file_name

        # Log processing of single file
        logger.info(message="Processing single file", status=f"{file}")

        # Process the file
        workflow_process_file(
            file, modified_files, repo, args, logger, log_tools
        )

        # Push changes if needed
        push_changes_if_needed(repo, args)

    elif args.oneshot:
        # Process only one file if --oneshot is provided
        logger.info("One-shot mode enabled", status="🎯")

        # Unstage all staged files if there are any
        if staged_files:
            git_unstage_files(repo, staged_files)

        # If .pre-commit-config.yaml is modified, stage and commit it first
        process_pre_commit_config(repo, modified_files)

        # Get untracked and modified files
        files_to_process = untracked_files + modified_files

        # Make sure there is something to do
        if not files_to_process:
            # Log no files to process
            logger.info(
                message="No untracked or modified files to process.",
                status="🚫",
            )
        else:
            # Get the first file to process
            file = files_to_process[0]

            # Log processing of first file
            logger.info(message="Processing first file", status=f"{file}")

            # Process the file
            workflow_process_file(
                file, modified_files, repo, args, logger, log_tools
            )

            # Push changes if needed
            push_changes_if_needed(repo, args)
    else:
        # Batch mode: Process all untracked and modified files
        logger.info("Batch mode enabled", status="📦")

        # Unstage all staged files if there are any
        if staged_files:
            git_unstage_files(repo, staged_files)

        # If .pre-commit-config.yaml is modified, stage and commit it first
        process_pre_commit_config(repo, modified_files)

        # Process all untracked and modified files
        files_to_process = untracked_files + modified_files

        if not files_to_process:
            logger.info(
                message="No untracked or modified files to process.",
                status="🚫",
            )
        else:
            for file in files_to_process:
                logger.info(message="Processing file", status=f"{file}")
                workflow_process_file(
                    file, modified_files, repo, args, logger, log_tools
                )
            # Push changes if needed
            push_changes_if_needed(repo, args)

    # Log script completion
    if not untracked_files and not modified_files and not committed_not_pushed:
        logger.info(
            message="No files processed, nothing to do",
            status="🚫",
        )
    else:
        logger.info(
            message="All files processed successfully",
            status="🚀",
        )
    logger.info("=" * 80, status="")


if __name__ == "__main__":
    main()
