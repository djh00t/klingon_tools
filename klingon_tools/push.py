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
4. Run unit tests
5. Process files based on the mode:
   a. Single file mode: Process only the specified file
   b. One-shot mode: Process only the first untracked or modified file
   c. Batch mode: Process all untracked and modified files
6. For each processed file:
   a. Stage the file
   b. Run pre-commit hooks
   c. Generate commit message (if not in dry-run mode)
   d. Commit the file (if not in dry-run mode)
7. Push changes (if not in dry-run mode)

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

Best ollama models to use for git commit messages:
  - gpt-4o - excellent (paid)
  - gpt-4o-mini - very good (paid)
  - chatgpt-4o-latest - very good (paid)
  - deepseek-coder-v2 - very good
  - codestral-latest - very good (paid)
  - mistral-small-latest - Good content
  - mistral-nemo - good content, weird formatting
  - phi3:mini - Overly verbose
  - llama2:latest - Good content but returns it with extra content around the
    answer
  - llama3.1:latest - Good content but returns it with extra content around the
    answer.
  - codeqwen:latest - Doesn't appear to know what conventional commits format
    is.
  - codellama:latest - Doesn't understand what a breaking change is.
"""
import argparse
import os
import subprocess
import sys
import requests
import datetime
from git import Repo
from typing import Any, List, Tuple, Optional
from klingon_tools.git_tools import (
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
)

from klingon_tools.log_msg import log_message, set_log_level
from klingon_tools.litellm_tools import LiteLLMTools
from klingon_tools.git_unstage import git_unstage_files
from klingon_tools.entrypoints import ktest

# Initialize variables
deleted_files = []
untracked_files = []
modified_files = []
staged_files = []
committed_not_pushed = []


def find_git_root(start_path: str) -> Optional[str]:
    """
    Find the root of the git repository by iterating up the directory
    structure. Returns an absolute path and prompts to initialize a git
    repository if not found.

    Args:
        start_path (str): The starting path to begin the search.

    Returns:
        Optional[str]: The path to the root of the git repository, or None if
        not found.
    """
    current_path = start_path
    while current_path != os.path.dirname(current_path):
        if os.path.isdir(os.path.join(current_path, ".git")):
            return os.path.abspath(current_path)
        current_path = os.path.dirname(current_path)
    return None


def validate_commit_message(commit_message: str) -> bool:
    """
    Validate the commit message format.

    Args:
        commit_message (str): The commit message to validate.

    Returns:
        bool: True if the commit message is valid, False otherwise.
    """
    # Example validation: Check if the commit message is not empty and has a
    # minimum length
    return bool(commit_message and len(commit_message) > 10)


def check_software_requirements(repo_path: str, log_message: Any) -> None:
    """
    Check and install required software.

    This function checks for the presence of pre-commit and installs it if not
    found.

    Args:
        repo_path (str): The path to the git repository.
        log_message (Any): The logging function to use for output.

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
                    "pytest",
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
            "https://raw.githubusercontent.com/djh00t/klingon_templates/main/"
            "python/.pre-commit-config.yaml"
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
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests",
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
        "--file-name",
        type=str,
        nargs="*",
        help="File name(s) to stage and commit",
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


def run_tests(log_message: Any = None, quiet: bool = False) -> bool:
    """
    Run tests using the ktest function and log the results using LogTools.

    This function runs the tests using the ktest function. If tests fail, it
    logs detailed debug information and returns False.

    Args:
        log_message (Any): The logging function to use for output.
        quiet (bool): Flag to run ktest in quiet mode. Defaults to False.

    Returns:
        bool: True if tests pass, False otherwise.
    """
    if log_message:
        # Log the start of the test execution
        log_message.info("Running tests using ktest", status="🔍")
    try:
        # Execute the ktest function to run the tests
        results = ktest()
        # Return True if all tests passed, False otherwise
        log_message.info(80 * "-", status="", style="none")
        return all(test["outcome"] == "passed" for test in results)
    except Exception as e:
        # Log the error message and return False
        log_message.error("ERROR DEBUG:", status="❌")
        log_message.error(str(e), status="", style="none")
        log_message.info(80 * "-", status="", style="none")
        return False


def process_files(
    files: List[str],
    repo: Repo,
    args: argparse.Namespace,
    log_message: Any,
    litellm_tools: LiteLLMTools,
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

    Note:
        This function relies on the global 'modified_files' list to track
        modifications.

    Raises:
        Any exceptions raised by workflow_process_file are not caught here and
        will propagate.
    """
    global modified_files  # Use the global modified_files list

    file_counter = 0  # Initialize file counter

    for file in files:
        file_counter += 1  # Increment file counter
        # Check if the file exists
        if not os.path.exists(file):
            log_message.warning(
                message="File does not exist or has already been committed: "
                f"{file}",
                status="❌",
            )
            continue
        if os.path.isdir(file):
            log_message.warning(message="Skipping directory", status=f"{file}")
            continue
        log_message.debug(
            message=f"Processing file: {file}", status="process_files ✅"
        )

        try:
            # Check if the file is already committed
            if file in committed_not_pushed:
                log_message.info(
                    message=f"File already committed: {file}", status="⏭️"
                )
                continue

            # Process the file using the workflow_process_file function
            workflow_process_file(
                file,
                modified_files,
                repo,
                args,
                log_message,
                litellm_tools,
                file_counter,
            )
        except Exception as e:
            # Log any errors that occur during processing
            log_message.error(
                f"Error processing file {file}: {str(e)}", status="❌"
            )
            print()
            print(f"{str(e)}")
            print()

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
    makefile_path = os.path.join(os.getcwd(), "Makefile")
    if os.path.exists(makefile_path):
        with open(makefile_path, "r") as makefile:
            if "push-prep:" in makefile.read():
                log_message.info(message="Running push-prep", status="✅")
                try:
                    subprocess.run(["make", "push-prep"], check=True)
                except subprocess.CalledProcessError as e:
                    log_message.error(
                        message=f"Failed to run push-prep: {e}",
                        status="❌",
                    )
                    sys.exit(1)
            else:
                log_message.info(
                    message="push-prep target not found in Makefile",
                    status="ℹ️",
                )
    else:
        log_message.info(
            message="Makefile not found in the root of the repository",
            status="ℹ️",
        )


def workflow_process_file(
    file_name: str,
    current_modified_files: List[str],
    current_repo: Repo,
    current_args: argparse.Namespace,
    log_message: Any,
    litellm_tools: LiteLLMTools,
    file_counter: int,
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

    Raises:
        SystemExit: If pre-commit hooks fail.

    Note:
        This function modifies global variables: modified_files, repo, and
        args.
    """
    global modified_files, repo, args

    log_message.debug(
        message="Processing file",
        status="workflow_process_file ✅",
    )

    # Check if the file is already committed
    if file_name in committed_not_pushed:
        log_message.info(f"File already committed: {file_name}", status="⏭️")
        return

    # Run pre-commit hooks on the file
    success, diff = git_pre_commit(
        file_name, current_repo, current_modified_files
    )

    # Get the root directory of the repository
    repo_root = current_repo.working_dir

    # Save diff only for every 5th file processed
    if file_counter % 5 == 0:
        # Get current date and time in YYYYMMDDHHMMSS format
        now = datetime.datetime.now()
        date_time = now.strftime("%Y%m%d%H%M%S")

        # Log diff to
        # {repo_root}/benchmarking/diff-corpus/YYYYMMDDHHMMSS_git_benchmark.diff
        import textwrap

        with open(
            f"{repo_root}/benchmarking/diff-corpus/"
            f"{date_time}_git_benchmark.diff",
            "w",
        ) as f:
            wrapped_diff = textwrap.fill(
                diff, width=79, subsequent_indent=" " * 12
            )
            f.write(wrapped_diff)

    if success:
        if current_args.dryrun:
            # Log dry run mode and skip commit and push
            log_message.info(
                message="Dry run mode enabled. Skipping commit and push.",
                status="🚫",
            )
            return
        else:
            # Generate commit message and commit the file
            for attempt in range(3):
                try:
                    commit_message = litellm_tools.generate_commit_message(
                        diff
                    )
                    # Assuming validate_commit_message is a function to
                    # validate the commit message format
                    if validate_commit_message(commit_message):
                        git_commit_file(
                            file_name, current_repo, commit_message
                        )
                        break
                    else:
                        log_message.error(
                            f"\n{commit_message}\n", status="", style="none"
                        )
                        diff += "\nCommit message format error"
                        litellm_tools.update_prompt(
                            "Commit message format error"
                        )
                except Exception as e:
                    log_message.error(
                        f"Failed to generate commit message for {file_name}: "
                        f"{e}",
                        status="❌",
                    )
                    return
            else:
                log_message.error(
                    f"Failed to generate valid commit message for {file_name}"
                    "after 3 attempts",
                    status="❌",
                )
                return
    else:
        log_message.error(
            message="Pre-commit hooks failed. Exiting script.",
            status="❌",
        )
        sys.exit(1)

    log_message.info(f"Finished processing file: {file_name}", status="✅")
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


def startup_tasks(args: argparse.Namespace) -> Tuple[Repo, str, str]:
    """
    Run startup maintenance tasks.

    This function initializes the script by setting up logging, checking
    software requirements, and retrieving git user information.

    Args:
        args (argparse.Namespace): Command-line arguments.
        log_message (Any): The logging function to use for output.

    Returns:
        Tuple[Repo, str, str]: The initialized git repository object, user
        name, and user email.

    Raises:
        SystemExit: If the git repository initialization fails.
    """

    # Find the root of the git repository
    repo_path = find_git_root(args.repo_path)
    while repo_path is None:
        user_input = (
            input(
                "No git repository found. Do you want to initialize a new "
                "repository in the current directory? (y/n): "
            )
            .strip()
            .lower()
        )
        if user_input == "y":
            repo_path = os.getcwd()
            subprocess.run(["git", "init"], cwd=repo_path, check=True)
            log_message.info(
                message=f"Initialized new git repository at {repo_path}",
                status="✅",
            )
        elif user_input == "n":
            log_message.error(
                message="No git repository found. Exiting.", status="❌"
            )
            sys.exit(1)
        else:
            log_message.warning(
                message="Invalid input. Please enter 'y' or 'n'.", status="⚠️"
            )
        log_message.warning(
            message="No git repository found. Initializing a new repository.",
            status="⚠️",
        )
        repo_path = args.repo_path
        os.makedirs(repo_path, exist_ok=True)
        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        log_message.info(
            message="Initialized new git repository at", status=f"{repo_path}"
        )
    else:
        log_message.info(
            message="Using repository path", status=f"{repo_path}"
        )
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
    log_message.info(message=f"Using git user name: {user_name}", status="✅")
    log_message.info(
        message=f"Using git user email: {user_email}", status="✅"
    )

    # Initialize the git repository object
    repo = git_get_toplevel()

    # Exit if the git repository initialization fails
    if repo is None:
        log_message.error(
            message="Failed to initialize git repository. Exiting.",
            status="❌",
        )
        sys.exit(1)

    # Return the initialized git repository object, user name, and user email
    return repo, user_name, user_email


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

    # Parse command-line arguments
    args = parse_arguments()

    # Initialize LiteLLMTools
    litellm_tools = LiteLLMTools(
        debug=args.debug,  # Set to True for debug mode
        # model_primary="gpt-4o-mini",
        # model_primary="ollama_chat/deepseek-coder-v2",
        # model_primary="groq/mixtral-8x7b-32768",
        # model_primary="groq/gemma-7b-it",
        model_primary="groq/llama-3.1-70b-versatile",
        # model_secondary="claude-3-haiku-20240307"
        model_secondary="gpt-4o-mini",
    )

    # Set default logging level to INFO
    set_log_level("INFO")

    # Override logging level to DEBUG if debug mode is enabled
    if args.debug:
        set_log_level("DEBUG")

    # Expand wildcards and check if the files specified by --file-name exist
    # before running push-prep
    file_name_list = []
    if args.file_name:
        import glob

        for pattern in args.file_name:
            file_name_list.extend(glob.glob(pattern))
        for file_name in file_name_list:
            if not os.path.exists(file_name):
                log_message.error(
                    message=f"File does not exist: {file_name}", status="❌"
                )
                return 1

    # Run startup tasks to initialize the script and get repo
    repo, user_name, user_email = startup_tasks(args)

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

    # If --file-name is used, filter the lists to only include files in
    # file_name_list
    if file_name_list:
        deleted_files = [f for f in deleted_files if f in file_name_list]
        untracked_files = [f for f in untracked_files if f in file_name_list]
        modified_files = [f for f in modified_files if f in file_name_list]
        staged_files = [f for f in staged_files if f in file_name_list]
        committed_not_pushed = [
            f for f in committed_not_pushed if f in file_name_list
        ]

    # Run tests before processing any files unless --skip-tests is specified
    if not args.skip_tests:
        log_message.info("Running tests before processing files", status="🔍")
        if not run_tests(log_message):
            log_message.error("Exiting due to failing tests", status="❌")
            return 1
    else:
        log_message.info(
            "Skipping tests as per --skip-tests argument", status="🚫"
        )

    # Unstage all staged files if there are any
    if staged_files:
        git_unstage_files(repo, staged_files)

    # If there are deleted files, commit them
    if deleted_files:
        git_commit_deletes(repo, deleted_files)

    # If .pre-commit-config.yaml is modified, stage and commit it first
    process_pre_commit_config(repo, modified_files)

    if args.oneshot:
        # One-shot mode: Process only the first file in files_to_process
        log_message.info("One-shot mode enabled", status="🎯")
        files_to_process = untracked_files + modified_files
        if files_to_process:
            process_files(
                [files_to_process[0]], repo, args, log_message, litellm_tools
            )
        else:
            log_message.info("No files to process.", status="🚫")
    else:
        # Batch mode: Process all untracked and modified files
        log_message.info("Batch mode enabled", status="📦")
        files_to_process = untracked_files + modified_files
        if files_to_process:
            process_files(
                files_to_process, repo, args, log_message, litellm_tools
            )
        else:
            log_message.info("No files to process.", status="🚫")

    # Push changes if needed
    push_changes_if_needed(repo, args)

    # Log script completion
    log_message.info("All files processed successfully", status="🚀")
    log_message.info("=" * 80, status="", style="none")

    return 0


if __name__ == "__main__":
    sys.exit(main())
