#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides a script for automating git operations.

The script performs various git operations such as staging, committing, and
pushing files. It also integrates with pre-commit hooks and generates commit
messages using OpenAI's API.

Workflow:
1. Parse command-line arguments
2. Run startup tasks (setup logging, check software requirements, etc.)
3. Get git status
4. Process files based on the mode:
   a. Single file mode: Process only the specified file
   b. One-shot mode: Process only the first untracked or modified file
   c. Batch mode: Process all untracked and modified files
5. For each processed file:
   a. Stage the file
   b. Run pre-commit hooks
   c. Generate commit message (if not in dry-run mode)
   d. Commit the file (if not in dry-run mode)
6. Push changes (if not in dry-run mode)

The script has several options:
--repo-path: Specify the path to the git repository (default: current
             directory)
--debug: Enable debug mode for more verbose logging
--file-name: Specify a single file to process
--oneshot: Process only one file and exit
--dryrun: Run the script without making any actual commits or pushes

This script is part of a library with an entrypoint called "push" which points
to this script.

Typical usage example:

    $ push --repo-path /path/to/repo --file-name example.txt

Attributes:
    deleted_files (list): List of deleted files.
    untracked_files (list): List of untracked files.
    modified_files (list): List of modified files.
    staged_files (list): List of staged files.
    committed_not_pushed (list): List of committed but not pushed files.
"""
import argparse
import os
import subprocess
import sys
import requests
from git import Repo
from typing import Any, List, Tuple
from klingon_tools.git_tools import (
    LOOP_MAX_PRE_COMMIT,
    cleanup_lock_file,
    get_git_user_info,
    git_commit_deletes,
    git_commit_file,
    git_get_status,
    git_get_toplevel,
    git_pre_commit,
    log_git_stats,
    process_pre_commit_config,
    push_changes_if_needed,
    git_stage_diff,
)
from klingon_tools.git_unstage import git_unstage_files

# Initialize logging
from klingon_tools.logger import LogTools, log_tools
from klingon_tools.openai_tools import OpenAITools

# Initialize variables
deleted_files = []
untracked_files = []
modified_files = []
staged_files = []
committed_not_pushed = []


def check_software_requirements(repo_path: str, log_message: Any) -> None:
    """
    Check and install required software.

    This function checks for the presence of pre-commit and installs it if not
    found.

    Args:
        repo_path (str): The path to the git repository. log_message (Any): The
        logging function to use for output.

    Raises:
        SystemExit: If pre-commit installation fails.
    """
    # Log the start of the software requirements check
    log_message.info("Checking for software requirements", status="🔍")

    # Try to check if pre-commit is installed
    try:
        # Run the pre-commit --version command to check if pre-commit is
        # installed
        subprocess.run(
            ["pre-commit", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    # If pre-commit is not installed, catch the error
    except subprocess.CalledProcessError:
        log_message.info(
            "pre-commit is not installed.",
            status="Installing",
        )
        # Try to install pre-commit using pip
        try:
            # Run the pip install command to install pre-commit and cfgv
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
            log_message.info("Installed pre-commit", status="✅")
        # If the installation fails, catch the error
        except subprocess.CalledProcessError as e:
            # Log the failure to install pre-commit
            log_message.error(
                f"Failed to install pre-commit: {e}",
                status="❌",
            )
            # Exit the script if pre-commit installation fails
            sys.exit(1)


def ensure_pre_commit_config(repo_path: str, log_message: Any) -> None:
    """
    Ensure .pre-commit-config.yaml exists, create if not.

    This function checks for the presence of .pre-commit-config.yaml and
    creates it from a template if it doesn't exist.

    Args:
        repo_path (str): The path to the git repository.
        log_message (Any): The logging function to use for output.

    Raises:
        SystemExit: If downloading or writing the config file fails.
    """
    # Define the path to the .pre-commit-config.yaml file in the repository
    config_path = os.path.join(repo_path, ".pre-commit-config.yaml")
    # Check if the .pre-commit-config.yaml file exists
    if not os.path.exists(config_path):
        log_message.info(
            ".pre-commit-config.yaml not found. Creating from template.",
            status="📝",
        )
        # Define the URL to the .pre-commit-config.yaml template
        template_url = (
            "https://raw.githubusercontent.com/djh00t/klingon_tools/main/"
            "repo_templates/python/.pre-commit-config.yaml"
        )
        try:
            # Download the .pre-commit-config.yaml template
            response = requests.get(template_url)
            response.raise_for_status()
            # Write the downloaded template to the .pre-commit-config.yaml
            # file
            with open(config_path, "w") as file:
                file.write(response.text)
            log_message.info(
                ".pre-commit-config.yaml created successfully.",
                status="✅",
            )
        # Log an error message if downloading the template fails
        except requests.RequestException as e:
            log_message.info(
                f"Failed to download .pre-commit-config.yaml template: {e}",
                status="❌",
            )
            sys.exit(1)
        # Log an error message if writing the template to the file fails
        except IOError as e:
            log_message.info(
                f"Failed to write .pre-commit-config.yaml: {e}",
                status="❌",
            )
            sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the script.

    This function sets up the argument parser and defines the following
    arguments:
    --repo-path: Path to the git repository (default: current directory)
    --debug: Enable debug mode
    --file-name: File name to stage and commit
    --oneshot: Process and commit only one file then exit
    --dryrun: Run the script without committing or pushing changes

    Returns:
        argparse.Namespace: An object containing the parsed arguments.
    """
    # Initialize the argument parser with a description of the script
    parser = argparse.ArgumentParser(
        description="Git repository status checker and committer."
    )

    # Define command-line arguments
    # Define the --repo-path argument with a default value of the current
    # directory
    # Define the --debug argument to enable debug mode
    # Define the --file-name argument to specify a single file to process
    # Define the --oneshot argument to process only one file and exit
    # Define the --dryrun argument to run the script without committing or
    # pushing changes
    parser.add_argument(
        "--repo-path", type=str, default=".", help="Path to git repository"
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

    # Parse the arguments and return the result
    return parser.parse_args()


def process_files(
    files: List[str],
    repo: Repo,
    args: argparse.Namespace,
    log_message: Any,
    log_tools: Any,
) -> None:
    """
    Process a list of files through the git workflow.

    This function iterates through the provided list of files, processing each
    one using the workflow_process_file function. It handles staging,
    pre-commit hooks, commit message generation, and committing for each file.

    Args:
        files (List[str]): A list of file paths to process.
        repo (Repo): The git repository object.
        args (argparse.Namespace): Command-line arguments.
        log_message (Any): The logging function to use for output.
        log_tools (Any): Additional logging tools.

    Note:
        This function relies on the global 'modified_files' list to track
        modifications.

    Raises:
        Any exceptions raised by workflow_process_file are not caught here and
        will propagate.
    """
    global modified_files  # Use the global modified_files list

    for file in files:
        # Log the current file being processed
        if os.path.isdir(file):
            log_message.warning(message="Skipping directory", status=f"{file}")
            continue
        log_message.info(message="Processing file", status=f"{file}")

        try:
            # Process the file using the workflow_process_file function
            workflow_process_file(
                file, modified_files, repo, args, log_message, log_tools
            )
        except Exception as e:
            # Log any errors that occur during processing
            log_message.error(
                f"Error processing file {file}: {str(e)}", status="❌"
            )

    # After processing all files, update the modified_files list This step is
    # important if any files were committed and are no longer modified
    _, _, modified_files, _, _ = git_get_status(repo)


def run_push_prep(log_message: Any) -> None:
    """
    Check for a "push-prep" target in the Makefile and run it if it exists.

    Args:
        log_message (Any): The logging function to use for output.

    Raises:
        SystemExit: If running the 'push-prep' target fails.
    """
    # Define the path to the Makefile in the current working directory
    makefile_path = os.path.join(os.getcwd(), "Makefile")

    # Check if the Makefile exists
    if os.path.exists(makefile_path):

        # Open the Makefile for reading
        with open(makefile_path, "r") as makefile:

            # Check if the 'push-prep' target is defined in the Makefile
            if "push-prep:" in makefile.read():
                log_message.info("Running 'push-prep'", status="✅")

                # Run the 'push-prep' target using the make command
                try:
                    subprocess.run(["make", "push-prep"], check=True)

                # Log an error message if the 'push-prep' target fails
                except subprocess.CalledProcessError as e:
                    log_message.error(
                        f"Failed to run 'push-prep': {e}",
                        status="❌",
                    )
                    sys.exit(1)

            # Log a message if the 'push-prep' target is not found in the
            # Makefile
            else:
                log_message.info(
                    "'push-prep' target not found in Makefile",
                    status="ℹ️",
                )

    # Log a message if the Makefile is not found in the root of the repository
    else:
        log_message.info(
            "Makefile not found in the root of the repository",
            status="ℹ️",
        )


def startup_tasks(
    args: argparse.Namespace, log_message: Any, log_tools: Any
) -> Tuple[Repo, str, str]:
    """
    Run startup maintenance tasks.

    This function initializes the script by setting up logging, checking
    software requirements, and retrieving git user information.

    Args:
        args (argparse.Namespace): Command-line arguments.
        log_message (Any): The logging function to use for output.
        log_tools (Any): Additional logging tools.

    Returns:
        Tuple[Repo, str, str]: The initialized git repository object, user
        name, and user email.

    Raises:
        SystemExit: If the git repository initialization fails.
    """
    # Set logging style and level if debug mode is enabled
    if args.debug:
        log_tools.set_default_style("pre-commit")
        log_tools.set_log_level("DEBUG")

    # Change the working directory to the repository path
    repo_path = args.repo_path
    os.chdir(repo_path)

    # Clean up any existing lock files in the repository
    cleanup_lock_file(repo_path)
    # Ensure the pre-commit configuration file exists
    ensure_pre_commit_config(repo_path, log_message)
    # Run any pre-push preparation tasks defined in the Makefile
    run_push_prep(log_message)
    # Check and install any required software
    check_software_requirements(repo_path, log_message)

    # Retrieve the git user name and email
    user_name, user_email = get_git_user_info()
    # Log the git user name and email
    log_message.info(message="Using git user name:", status=user_name)
    log_message.info(message="Using git user email:", status=user_email)

    # Initialize the git repository object
    repo = git_get_toplevel()
    # Exit if the git repository initialization fails
    if repo is None:
        log_message.error(
            "Failed to initialize git repository. Exiting.", status="❌"
        )
        sys.exit(1)

    # Return the initialized git repository object, user name, and user email
    return repo, user_name, user_email


def workflow_process_file(
    file_name: str,
    current_modified_files: List[str],
    current_repo: Repo,
    current_args: argparse.Namespace,
    log_message: Any,
    log_tools: Any,
) -> None:
    """
    Process a single file through the git workflow.

    This function stages the file, generates a commit message, runs pre-commit
    hooks, and commits the file if all checks pass.

    Args:
        file_name (str): The name of the file to process.
        current_modified_files (List[str]): List of currently modified files.
        current_repo (Repo): The git repository object.
        current_args (argparse.Namespace): Command-line arguments.
        log_message (Any): The logging function to use for output.
        log_tools (Any): Additional logging tools.

    Raises:
        SystemExit: If pre-commit hooks fail.

    Note:
        This function modifies global variables: modified_files, repo, and
        args.
    """
    global modified_files, repo, args

    # Stage the file and generate a diff of the file being processed
    diff = git_stage_diff(file_name, current_repo, current_modified_files)

    # Attempt pre-commit hooks and commit
    attempt = 0
    success = False
    while attempt < LOOP_MAX_PRE_COMMIT:
        # Run pre-commit hooks on the file
        success, diff = git_pre_commit(
            file_name, current_repo, current_modified_files
        )

        if success:
            if current_args.dryrun:
                # Log dry run mode and skip commit and push
                log_message.info(
                    message="Dry run mode enabled. Skipping commit and push.",
                    status="🚫",
                )
                break
            else:
                # Generate commit message and commit the file
                openai_tools = OpenAITools(debug=args.debug)
                commit_message = openai_tools.generate_commit_message(diff)
                git_commit_file(file_name, current_repo, commit_message)
                break
        else:
            attempt += 1
            if attempt == LOOP_MAX_PRE_COMMIT:
                # Log pre-commit hook failure and exit
                log_message.error(
                    message="Pre-commit hooks failed. Exiting script.",
                    status="❌",
                )
                # Exit script
                sys.exit(1)

    # Debug logging if enabled
    if current_args.debug:
        # Enable debug mode
        # Log debug mode and git status
        log_message.info(message="Debug mode enabled", status="🐞")
        git_get_status(current_repo)
        log_git_stats(*git_get_status(current_repo))

    # Update global variables
    modified_files, repo, args = (
        current_modified_files,
        current_repo,
        current_args,
    )


def main():
    """
    Run the push script.

    This function initializes the script, processes files based on the
    provided command-line arguments, and performs git operations such as
    staging, committing, and pushing files.

    Note:
        This function uses and modifies global variables for tracking file
        status.

    Returns:
        int: 0 for successful execution, 1 for failed initialization.
    """
    global args, repo, deleted_files, untracked_files, modified_files
    global staged_files, committed_not_pushed

    # Initialize logger
    logger = LogTools()
    log_message = logger.log_message

    # Parse command-line arguments
    args = parse_arguments()

    # Run startup tasks to initialize the script and get repo
    repo, user_name, user_email = startup_tasks(args, log_message, log_tools)

    if repo is None:
        log_message.error(
            "Failed to initialize git repository. Exiting.", status="❌"
        )
        return 1

    # Get git status and update global variables
    (
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    ) = git_get_status(repo)

    # Check if there are any files to process initially
    if not (
        deleted_files
        or untracked_files
        or modified_files
        or staged_files
        or committed_not_pushed
    ):
        log_message.info("No files processed, nothing to do", status="🚫")
        return 0
    log_git_stats(
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    )

    # Unstage all staged files if there are any
    if staged_files:
        git_unstage_files(repo, staged_files)

    # If there are deleted files, commit them
    if deleted_files:
        git_commit_deletes(repo, deleted_files)

    # If .pre-commit-config.yaml is modified, stage and commit it first
    process_pre_commit_config(repo, modified_files)

    if args.file_name:
        # Single file mode
        log_message.info("File name mode enabled", status=args.file_name)
        process_files([args.file_name], repo, args, log_message, log_tools)
    elif args.oneshot:
        # One-shot mode: Process only the first file in files_to_process
        log_message.info("One-shot mode enabled", status="🎯")
        files_to_process = untracked_files + modified_files
        if files_to_process:
            process_files(
                [files_to_process[0]], repo, args, log_message, log_tools
            )
        else:
            log_message.info("No files to process.", status="🚫")
    else:
        # Batch mode: Process all untracked and modified files
        log_message.info("Batch mode enabled", status="📦")
        files_to_process = untracked_files + modified_files
        if files_to_process:
            process_files(files_to_process, repo, args, log_message, log_tools)
        else:
            log_message.info("No files to process.", status="🚫")

    # Push changes if needed
    push_changes_if_needed(repo, args)

    # Log script completion
    log_message.info("All files processed successfully", status="🚀")
    log_message.info("=" * 80, status="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
