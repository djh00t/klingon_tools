#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Provides a script for automating git operations.

This module performs various git operations such as staging, committing, and
pushing files. It also integrates with pre-commit hooks and generates commit
messages using LiteLLM.

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
import glob
import logging
import os
import re
import subprocess
import sys
from typing import Any, List, Optional, Tuple

import requests
from git import Repo

from klingon_tools.git_commit_validate import validate_commit_message
from klingon_tools.git_tools import (cleanup_lock_file, git_commit_deletes,
                                     git_commit_file, git_get_status,
                                     git_get_toplevel, log_git_stats,
                                     push_changes_if_needed)
from klingon_tools.git_user_info import get_git_user_info
from klingon_tools.litellm_model_cache import get_supported_models
from klingon_tools.litellm_tools import LiteLLMTools
from klingon_tools.log_msg import klog_hr, log_message
from klingon_tools.log_tools import LogTools
from klingon_tools.pre_commit import git_pre_commit, set_debug_mode

# Initialize variables
deleted_files: List[str] = []
untracked_files: List[str] = []
modified_files: List[str] = []
staged_files: List[str] = []
committed_not_pushed: List[str] = []

# Suppress logs for common HTTP libraries
# logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.getLogger("requests").setLevel(logging.WARNING)
# logging.getLogger("litellm").setLevel(logging.WARNING)

# Configure logging with a simpler format
logging.basicConfig(
    level=logging.WARNING,
    format='%(message)s'
)


def is_valid_semver(version: str) -> bool:
    """
    Validate if a given version string follows semver guidelines, including
    pre-release versions.

    Args:
        version (str): The version string to validate.

    Returns:
        bool: True if the version is valid, False otherwise.
    """
    pattern = (
        r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
        r'(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*'
        r')(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
        r'(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    )
    match = re.match(pattern, version)
    is_valid = bool(match)
    print(f"Validating version: {version}")
    print(f"Is valid: {is_valid}")
    if match:
        print(f"Matched groups: {match.groups()}")
    else:
        print("No match found")
    return is_valid


def find_git_root(start_path: str) -> Optional[str]:
    """Find the root of the git repository.

    Iterates up the directory structure to find the git root. Returns an
    absolute path and prompts to initialize a git repository if not found.

    Args:
        start_path: The starting path to begin the search.

    Returns:
        The path to the root of the git repository, or None if not found.
    """
    current_path = start_path
    while current_path != os.path.dirname(current_path):
        if os.path.isdir(os.path.join(current_path, ".git")):
            return os.path.abspath(current_path)
        current_path = os.path.dirname(current_path)
    return None


def check_software_requirements(repo_path: str, log_message: Any) -> None:
    """Check and install required software.

    This function checks for the presence of pre-commit and installs it if not
    found.

    Args:
        repo_path: The path to the git repository.
        log_message: The logging function to use for output.

    Raises:
        SystemExit: If pre-commit installation fails.
    """
    log_message.info("Checking for software requirements", status="🔍")

    try:
        subprocess.run(
            ["pre-commit", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError:
        log_message.info("pre-commit is not installed", status="Installing")
        try:
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
            log_message.info("Installed pre-commit", status="✅")
        except subprocess.CalledProcessError as e:
            log_message.error(f"Failed to install pre-commit: {e}", status="❌")
            sys.exit(1)


def ensure_pre_commit_config(repo_path: str, log_message: Any) -> None:
    """Ensure .pre-commit-config.yaml exists, create if not.

    This function checks for the presence of .pre-commit-config.yaml and
    creates it from a template if it doesn't exist.

    Args:
        repo_path: The path to the git repository.
        log_message: The logging function to use for output.

    Raises:
        SystemExit: If downloading or writing the config file fails.
    """
    config_path = os.path.join(repo_path, ".pre-commit-config.yaml")
    if not os.path.exists(config_path):
        log_message.info(
            ".pre-commit-config.yaml not found. Creating from template",
            status="📝",
        )
        template_url = (
            "https://raw.githubusercontent.com/djh00t/klingon_templates/main/"
            "python/.pre-commit-config.yaml"
        )
        try:
            response = requests.get(template_url)
            response.raise_for_status()
            with open(config_path, "w") as file:
                file.write(response.text)
            log_message.info(
                ".pre-commit-config.yaml created successfully",
                status="✅",
            )
        except requests.RequestException as e:
            log_message.info(
                f"Failed to download .pre-commit-config.yaml template: {e}",
                status="❌",
            )
            sys.exit(1)
        except IOError as e:
            log_message.info(
                f"Failed to write .pre-commit-config.yaml: {e}",
                status="❌",
            )
            sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the script.

    Returns:
        An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Git repository status checker and committer"
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip running unit tests",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Run without using LLM",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("MODEL_PRIMARY", "gpt-4o-mini"),
        help="Specify the model to use [env var: MODEL_PRIMARY]",
    )
    parser.add_argument(
        "--model-secondary",
        type=str,
        default=os.getenv("MODEL_SECONDARY", "claude-3-haiku-20240307"),
        help="Specify the fallback/secondary model to use",
    )
    parser.add_argument(
        "--models-list",
        action="store_true",
        help="List supported models. [env var: KLINGON_MODELS]",
    )
    parser.add_argument(
        "--output-json",
        "--json",
        action="store_true",
        help="Output the models list in JSON format",
        dest="output_json",
    )
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
        help="File name(s) or patterns to stage and commit",
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
    return parser.parse_args()


def expand_file_patterns(patterns: List[str]) -> List[str]:
    """
    Expand file patterns into a list of matching file names.

    Args:
        patterns: List of file names or glob patterns.

    Returns:
        List of matching file names.
    """
    if not patterns:
        return []

    expanded_files = []
    for pattern in patterns:
        expanded_files.extend(glob.glob(pattern))

    return list(set(expanded_files))  # Remove duplicates


def filter_git_files(
        all_files: List[str], filter_files: List[str]) -> List[str]:
    """
    Filter a list of files based on the provided filter list.

    Args:
        all_files: List of all files to filter.
        filter_files: List of files to keep.

    Returns:
        Filtered list of files.
    """
    return [f for f in all_files if f in filter_files]


def run_tests(log_message: Any = None, no_llm: bool = False) -> bool:
    """Run tests using ktest CLI command and log the results.

    Args:
        log_message: The logging function to use for output.
        no_llm: Whether to run tests without using LLM.

    Returns:
        True if tests pass, False otherwise.
    """
    if log_message:
        log_message.info(
            message="Running unit tests",
            status="🔍"
        )

    try:
        command = [sys.executable, "-m", "klingon_tools.ktest"]
        if no_llm:
            command.append("--no-llm")

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        for line in process.stdout:
            print(line, end='')

        return_code = process.wait()
        tests_passed = return_code == 0

        if tests_passed:
            if log_message:
                log_message.info(
                    message="All tests passed or were skipped successfully",
                    status="✅"
                )
        else:
            if log_message:
                log_message.error(
                    message="Some tests failed",
                    status="❌"
                )

        return tests_passed

    except Exception as e:
        import traceback
        if log_message:
            log_message.error(
                message=f"An error occurred while running tests:\n{str(e)}\n\n"
                f"Traceback:\n{traceback.format_exc()}",
                status="❌"
            )
        return False


def process_files(
    files: List[str],
    repo: Repo,
    args: argparse.Namespace,
    log_message: Any,
    litellm_tools: LiteLLMTools,
) -> bool:
    """Process a list of files through the git workflow.

    This function iterates through the provided list of files, processing each
    one using the workflow_process_file function. It handles staging,
    pre-commit hooks, commit message generation, and committing for each file.

    Args:
        files: A list of file paths to process.
        repo: The git repository object.
        args: Command-line arguments.
        log_message: The logging function to use for output.
        litellm_tools: The LiteLLM tools object.

    Returns:
        bool: True if any changes were made, False otherwise.
    """
    changes_made = False

    file_counter = 0

    for file in files:
        file_counter += 1

        if not os.path.exists(file):
            log_message.warning(
                message="File does not exist or has already been committed: "
                f"{file}",
                status="❌",
            )
            continue

        if os.path.isdir(file):
            log_message.warning(
                message=f"Skipping directory: {file}",
                status="SKIPPED 🦘"
            )
            continue

        log_message.debug(
            message=f"Processing file: {file}",
            status="process_files ✅"
        )

        try:
            workflow_process_file(
                file,
                files,
                repo,
                args,
                log_message,
                litellm_tools,
                file_counter,
            )
            changes_made = True
        except Exception as e:
            log_message.error(
                message="Error processing file",
                reason=f"{file}",
                status="❌"
            )
            log_message.error(
                message=f"\n{str(e)}\n\n",
                status="",
                style="none"
            )

    return changes_made or bool(files)


def run_push_prep(log_message: Any) -> None:
    """Check for a "push-prep" target in the Makefile and run it if it exists.

    Args:
        log_message: The logging function to use for output.

    Raises:
        SystemExit: If running the 'push-prep' target fails.
    """
    makefile_path = os.path.join(os.getcwd(), "Makefile")
    if (os.path.exists(makefile_path)):
        with open(makefile_path, "r") as makefile:
            if "push-prep:" in makefile.read():
                log_message.info(
                    message="Running push-prep",
                    status="✅"
                )
                try:
                    subprocess.run(["make", "push-prep"], check=True)
                except subprocess.CalledProcessError:
                    log_message.error(
                        message="Failed to run push-prep",
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
    max_retries: int = 3,  # Added max_retries to prevent infinite loops
) -> None:
    """Process a single file through the git workflow.

    This function stages the file, generates a commit message, runs pre-commit
    hooks, and commits the file if all checks pass.
    It also handles auto-fixed commit messages by re-staging and re-processing.

    Args:
        file_name: The name of the file to process.
        current_modified_files: List of currently modified files.
        current_repo: The git repository object.
        current_args: Command-line arguments.
        log_message: The logging function to use for output.
        litellm_tools: The LiteLLM tools object.
        file_counter: The current file counter.
        max_retries: Maximum number of auto-fix attempts.

    Raises:
        SystemExit: If pre-commit hooks fail.
    """
    log_message.debug(
        "Processing file",
        status="workflow_process_file ✅"
    )

    # Check if the file has already been committed but not pushed
    if file_name in committed_not_pushed:
        log_message.info(
            message=f"File already committed: {file_name}",
            status="SKIPPED 🦘"
        )
        return

    attempt = 0
    while attempt < max_retries:
        attempt += 1
        log_message.info(
            message=f"Staging {file_name} (Attempt {attempt}/{max_retries})",
            status=f"{file_counter}/{len(current_modified_files)}",
        )

        # Stage the file
        current_repo.git.add(file_name)

        # Generate commit message
        commit_message = litellm_tools.generate_commit_message_for_file(
            file_name=file_name, repo=current_repo)

        # Validate the commit message
        is_valid = validate_commit_message(commit_message, log_message)

        if is_valid:
            # Run pre-commit hooks
            success, _ = git_pre_commit(
                file_name, current_repo, current_modified_files)

            # Commit the file if pre-commit hooks pass
            if success:
                if current_args.dryrun:
                    log_message.info(
                        "Dry run mode enabled. Skipping commit and push",
                        status="🚫")
                else:
                    git_commit_file(file_name, current_repo, commit_message)
            else:
                log_message.error(
                    "Pre-commit hooks failed. Exiting script",
                    status="❌"
                )
                sys.exit(1)

            log_message.info(
                f"Finished processing file: {file_name}",
                status="✅"
            )
            if current_args.debug:
                git_get_status(current_repo)
                log_git_stats(*git_get_status(current_repo))
            return  # Exit after successful processing
        else:
            log_message.error("Commit message validation failed.", status="❌")
            return

    # If max retries exceeded
    log_message.error(
        message=f"Maximum auto-fix attempts reached for {file_name}.",
        status="❌"
        )
    return


def expand_and_check_files(file_patterns: List[str]) -> List[str]:
    """Expand file patterns and check if files exist.

    Args:
        file_patterns: List of file patterns to expand.

    Returns:
        List of expanded file names that exist.

    Raises:
        SystemExit: If a file does not exist.
    """
    if not file_patterns:
        return []
    file_name_list = []
    for pattern in file_patterns:
        file_name_list.extend(glob.glob(pattern))
    for file_name in file_name_list:
        if not os.path.exists(file_name):
            log_message.error(f"File does not exist: {file_name}", status="❌")
            sys.exit(1)
    return file_name_list


def filter_files(file_name_list: List[str]) -> None:
    """
    Filters the global file lists based on the given file name list.

    Args:
        file_name_list (List[str]): The list of file names to filter the global
        file lists with.

    Returns:
        None
    """
    global deleted_files, untracked_files, modified_files, staged_files
    global committed_not_pushed
    deleted_files = [f for f in deleted_files if f in file_name_list]
    untracked_files = [f for f in untracked_files if f in file_name_list]
    modified_files = [f for f in modified_files if f in file_name_list]
    staged_files = [f for f in staged_files if f in file_name_list]
    committed_not_pushed = [
        f for f in committed_not_pushed if f in file_name_list]


def check_for_tests(args):
    """
    Checks for the presence of test files in the repository. This function
    determines if there are any test files in the 'tests' directory of the
    given repository path. It logs appropriate messages based on the presence
    or absence of the 'tests' directory and test files.
    Args:
        args: An object containing the repository path attribute `repo_path`.
    Returns:
        bool: True if test files are found, False otherwise.
    """
    repo_path = find_git_root(args.repo_path)
    tests_dir = os.path.join(repo_path, 'tests')

    if not os.path.isdir(tests_dir):
        log_message.info(
            message=f"{tests_dir} does not exist"
            "Write some tests for this code!",
            status="SKIPPED 🦘"
        )
        return False  # Skip running tests

    # Look for pytest tests in the tests directory
    test_patterns = ['test_*.py', '*_test.py']
    test_files = []
    for pattern in test_patterns:
        test_files.extend(glob.glob(os.path.join(
            tests_dir, '**', pattern), recursive=True))

    if not test_files:
        log_message.info(
            message=f"{tests_dir} exists but there are no tests. Write some"
            "tests for this code!",
            status="SKIPPED 🦘"
        )
        return False  # Skip running tests
    else:
        log_message.debug("Found tests", status="✅")
        return True


def run_tests_and_confirm(log_message: Any, no_llm: bool) -> bool:
    """Run tests and confirm continuation if tests fail.

    Args:
        log_message: The logging function to use for output.
        no_llm: Whether to run tests without using LLM.

    Returns:
        True if tests pass or user confirms to continue, False otherwise.
    """
    log_message.debug("Running tests before processing files", status="🔍")
    tests_passed = run_tests(log_message, no_llm)
    if not tests_passed:
        log_message.error(
            "Tests failed. Do you want to continue anyway? (y/n)", status="👾")
        user_input = input().strip().lower()
        if user_input != 'y':
            log_message.error("Exiting due to failing tests", status="❌")
            return False
        log_message.warning("Continuing despite test failures", status="👾")
    return True


def process_changes(repo, args, litellm):
    """
    Process changes in the repository.

    This function handles untracked, modified, and deleted files.
    It specially processes .pre-commit-config.yaml files directly.
    """
    global untracked_files, modified_files, deleted_files

    # Check for .pre-commit-config.yaml and process it directly
    pre_commit_config = '.pre-commit-config.yaml'
    pre_commit_files = []

    # Check if pre-commit config is in untracked or modified files
    if (pre_commit_config in untracked_files):
        pre_commit_files.append(pre_commit_config)
        # Remove from untracked so it's not processed twice
        untracked_files = [f for f in untracked_files if f != pre_commit_config]
    elif (pre_commit_config in modified_files):
        pre_commit_files.append(pre_commit_config)
        # Remove from modified so it's not processed twice
        modified_files = [f for f in modified_files if f != pre_commit_config]

    # Process .pre-commit-config.yaml directly if found
    for idx, file in enumerate(pre_commit_files):
        workflow_process_file(
            file, pre_commit_files, repo, args, log_message, litellm, idx
        )

    # Create a proper list instead of using the __add__ method directly
    combined_files = list(untracked_files) + list(modified_files)

    # Handle deleted files first
    if deleted_files:
        git_commit_deletes(repo, deleted_files)

    # Process modified and untracked files
    if combined_files:
        return process_files(combined_files, repo, args, log_message, litellm)

    return True or bool(pre_commit_files)  # Return True if any files were processed


def startup_tasks(args: argparse.Namespace) -> Tuple[Repo, str, str]:
    """Run startup maintenance tasks.

    This function initializes the script by setting up logging, checking
    software requirements, and retrieving git user information.

    Args:
        args: Command-line arguments.

    Returns:
        The initialized git repository object, user name, and user email.

    Raises:
        SystemExit: If the git repository initialization fails.
    """
    repo_path = find_git_root(args.repo_path)
    while repo_path is None:
        user_input = input(
            "No git repository found. Do you want to initialize a new "
            "repository in the current directory? (y/n): "
        ).strip().lower()
        if user_input == "y":
            repo_path = os.getcwd()
            subprocess.run(["git", "init"], cwd=repo_path, check=True)
            log_message.info(
                f"Initialized new git repository at {repo_path}",
                status="✅",
            )
        elif user_input == "n":
            log_message.error("No git repository found. Exiting", status="❌")
            sys.exit(1)
        else:
            log_message.warning(
                "Invalid input. Please enter 'y' or 'n'", status="👾"
            )
    os.chdir(repo_path)

    # Cleanup any leftover lock files
    cleanup_lock_file(repo_path)

    # Ensure pre-commit configuration exists
    ensure_pre_commit_config(repo_path, log_message)

    # Run push-prep target in Makefile if it exists
    run_push_prep(log_message)

    # Check for software requirements
    check_software_requirements(repo_path, log_message)

    # Get git user information
    user_name, user_email = get_git_user_info()
    log_message.info(f"Using git user name: {user_name}", status="✅")
    log_message.info(f"Using git user email: {user_email}", status="✅")

    # Initialize top level git repository
    repo = git_get_toplevel()
    if repo is None:
        log_message.error(
            "Failed to initialize git repository. Exiting",
            status="❌",
        )
        sys.exit(1)

    return repo, user_name, user_email


def main() -> int:
    """Run the push script.

    This function initializes the script, processes files based on the
    provided command-line arguments, and performs git operations such as
    staging, committing, and pushing files.

    Returns:
        0 for successful execution, 1 for failed initialization.
    """
    global args, repo, deleted_files, untracked_files, modified_files
    global staged_files, committed_not_pushed

    # Parse command-line arguments
    args = parse_arguments()

    # Set log level to DEBUG if debug mode is enabled
    log_tools = LogTools(debug=args.debug)
    log_tools.set_log_level("DEBUG" if args.debug else "INFO")

    # Log debug mode status
    if args.debug:
        log_message.info("Debug mode enabled", status="🐞")

    # List supported models and exit
    if args.models_list:
        models = get_supported_models()
        model_names_only = sorted(models.keys())
        if args.output_json:
            import json
            print(json.dumps(model_names_only, indent=4))
        else:
            log_message.info(model_names_only, status="", style=None)
        return 0

    # Set debug mode for downstream usage
    set_debug_mode(args.debug)

    # Initialize LiteLLM tools
    litellm_tools = LiteLLMTools(
        debug=args.debug,
        model_primary=args.model,
        model_secondary=args.model_secondary,
        log_http_requests=args.debug  # Only log HTTP requests in debug mode
    )

    # Expand and check file patterns
    file_name_list = expand_and_check_files(args.file_name)

    # Run startup tasks
    repo, user_name, user_email = startup_tasks(args)

    # Error if there is no repository
    if repo is None:
        log_message.error(
            "Failed to initialize git repository. Exiting",
            status="❌")
        return 1

    # Get the current status of the repository
    (
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    ) = git_get_status(repo)

    # Filter files based on the provided file name list
    if args.file_name:
        filtered_file_list = expand_file_patterns(args.file_name)
        deleted_files = filter_git_files(deleted_files, filtered_file_list)
        untracked_files = filter_git_files(untracked_files, filtered_file_list)
        modified_files = filter_git_files(modified_files, filtered_file_list)
        staged_files = filter_git_files(staged_files, filtered_file_list)
        committed_not_pushed = filter_git_files(
            committed_not_pushed, filtered_file_list)

    if not any(
        [
            deleted_files,
            untracked_files,
            modified_files,
            staged_files,
            committed_not_pushed
        ]
    ):
        log_message.info("No files to process, nothing to do", status="🚫")
        return 0

    # Log the current status of the repository
    log_git_stats(
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed
    )

    if staged_files:
        log_message.info("Unstaging files", status="🚫")
        repo.git.reset()
        (
            deleted_files,
            untracked_files,
            modified_files,
            staged_files,
            committed_not_pushed,
        ) = git_get_status(repo)
        log_git_stats(
            deleted_files,
            untracked_files,
            modified_files,
            staged_files,
            committed_not_pushed
        )
        if not modified_files:
            log_message.info(
                "No more files to process. Exiting script",
                status="🚪",
            )
            return 0

    if file_name_list:
        filter_files(file_name_list)

    # Run tests and confirm continuation
    if not args.no_tests:
        # Check to make sure tests/ directory exists and it contains pytest
        # tests using check_for_tests
        if check_for_tests(args):
            # If check_for_tests returns True then run run_tests_and_confirm
            # otherwise just skip it.
            if not run_tests_and_confirm(log_message, args.no_llm):
                return 1
        else:
            # Skip running tests as check_for_tests returned False
            pass

    changes_made = process_changes(repo, args, litellm_tools)

    if changes_made:
        push_changes_if_needed(repo, args)
    else:
        log_message.info("No changes to push", status="ℹ️")

    log_message.info("All files processed successfully", status="🚀")
    klog_hr.info()

    return 0


if __name__ == "__main__":
    sys.exit(main())
