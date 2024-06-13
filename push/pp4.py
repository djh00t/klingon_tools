#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pp4.py

import logging
import git
from git.exc import InvalidGitRepositoryError, NoSuchPathError
import subprocess
import sys
import argparse
from openai import OpenAI
import os
import atexit
import signal
import textwrap
from klingon_tools import LogTools

# Initialize the logger
log_tools = LogTools()
logger = log_tools.log_message

# Set the global log message style
log_tools.set_default_style("pre-commit")

# Initialize the OpenAI API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration & Variables
LOOP_MAX_PRE_COMMIT = 5
deleted_files = []
untracked_files = []
staged_files = []
committed_not_pushed = []

# AI System Prompt Template
role_system_content = """
Generate a commit message based solely on the staged diffs provided, ensuring accuracy and relevance to the actual changes.
Avoid adding speculative or unnecessary footers, such as references to non-existent issues. You must adhere to the conventional commits standard. The commit message should:
- Clearly specify the type of change (feat, fix, build, etc.).
- Clearly specify the scope of change.
- Describe the purpose and actual detail of the change with clarity.
- Use bullet points for the body when more than one item is discussed.
- You MUST follow the Conventional Commits standardized format:

<type>(<scope>): <description>
[optional body]
[optional footer/breaking changes]

Types include: feat, fix, build, ci, docs, style, refactor, perf, test, chore, etc.
Scope (Optional but strongly preferred): The scope of the change eg. button, navbar, config.yaml etc.
Ensure the message is factual, based on the provided diff(s), and free from any speculative or unnecessary content.
"""

# AI Assistant Prompt Template
role_user_content_template = """
Generate a git commit message based on these diffs (git --no-pager diff --patch-with-stat):
\"{diff}\"
"""


def git_get_toplevel():
    try:
        # Initialize the repository object, searching parent directories
        repo = git.Repo(".", search_parent_directories=True)
        # Get the top-level directory
        toplevel_dir = repo.git.rev_parse("--show-toplevel")
        return toplevel_dir
    except (InvalidGitRepositoryError, NoSuchPathError) as e:
        # Handle cases where the directory is not a Git repository or the path is invalid
        logger.error(f"Error: {e}")
        return None


def git_get_status(repo):
    global deleted_files, untracked_files, modified_files, staged_files, committed_not_pushed

    # Get the current status of the working directory
    untracked_files = repo.untracked_files
    modified_files = [
        item.a_path for item in repo.index.diff(None) if item.change_type == "M"
    ]
    staged_files = [item.a_path for item in repo.index.diff("HEAD")]
    committed_not_pushed = [
        item.a_path for item in repo.head.commit.diff("origin/main")
    ]
    deleted_files = [
        item.a_path for item in repo.index.diff(None) if item.change_type == "D"
    ]


def git_commit_deletes(repo):
    # Check if there are any deleted files to commit
    if deleted_files:
        # Combine deleted files and staged deleted files
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

        # Log the deleted files
        logger.info(f"There are {len(all_deleted_files)} deleted files.")
        logger.debug(f"Deleted files: {all_deleted_files}")

        for file in all_deleted_files:
            # Stage the deleted file
            repo.index.remove([file], working_tree=True)

        # Commit the change
        commit_message = "Committing deleted files"
        repo.index.commit(commit_message)

        # Print the number of files committed
        logger.info(
            f"Committed {len(all_deleted_files)} deleted files with message: '{commit_message}'."
        )


# Loop through all staged_files files and de-stage them
def git_unstage_files(repo):
    # Loop through all files in staged_files & de-stage them
    for file in staged_files:
        try:
            repo.git.reset(file)
            logger.info(
                message="Un-staging file:",
                status=f"{file}",
            )
        except git.exc.GitCommandError as e:
            logger.error(
                message="Error un-staging file:",
                status=f"{file}",
            )
            logger.exception(
                message=f"{e}",
            )


# Stage the file, get the diff, and return a commit message
def git_stage_diff(file_name, repo):
    # Stage the file, even if it already staged
    repo.index.add([file_name])

    # Get the list of staged files
    staged_files = repo.git.diff("--cached", "--name-only").splitlines()

    # Print the filenames of all staged files
    logger.info(
        message="Staged files:",
        status=f"{staged_files}",
    )

    # If staging the file worked and it is in the list of staged files, log success, otherwise log error
    if file_name in staged_files:
        logger.info(
            message="Staging file",
            status="✅",
        )
    else:
        logger.error(
            message="Failed to stage file",
            status="❌",
        )
        sys.exit(1)

    # Get the diff
    diff = repo.git.diff("HEAD", file_name)

    # If diff was successful, log success, otherwise log error
    if diff:
        logger.info(
            message="Diff generated",
            status="✅",
        )
    else:
        logger.error(
            message="Failed to generate diff",
            status="❌",
        )

    # Submit the diff to generate_commit_message
    commit_message = generate_commit_message(diff)

    # Create the LLM request
    role_user_content = role_user_content_template.format(diff=diff)

    # Send the LLM request
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": role_system_content},
            {"role": "user", "content": role_user_content},
        ],
        model="gpt-3.5-turbo",
    )

    # Get the commit message from the response
    commit_message = response.choices[0].message.content.strip()

    # Wrap the commit message so it doesn't exceed 72 characters
    commit_message = "\n".join(
        [
            line if len(line) <= 72 else "\n".join(textwrap.wrap(line, 72))
            for line in commit_message.split("\n")
        ]
    )

    # Log the generated commit message
    logger.info(message=80 * "-", status="")
    logger.info(message=f"Generated commit message:\n\n{commit_message}\n", status="")
    logger.info(message=80 * "-", status="")

    # Return the commit message
    return commit_message


# Run pre-commit hooks on the file
def git_pre_commit(file_name, commit_message, repo):
    # Reset the attempt counter
    attempt = 0

    # Loop through the pre-commit hooks until they pass or fail after LOOP_MAX_PRE_COMMIT attempts
    while attempt < LOOP_MAX_PRE_COMMIT:

        # Run the pre-commit hooks
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
            sys.stdout.write(line)  # Print to screen
            stdout.append(line)  # Capture output

        for line in process.stderr:
            sys.stderr.write(line)  # Print to screen
            stderr.append(line)  # Capture output

        process.wait()
        result = subprocess.CompletedProcess(
            process.args, process.returncode, "".join(stdout), "".join(stderr)
        )

        if "files were modified by this hook" in result.stdout:
            logger.info(
                message="File modified by pre-commit:",
                status=f"⚠️",
            )
            logger.info(
                message="Re-staging for pre-commit:",
                status=f"{file_name}",
            )
            logger.info(message=80 * "-", status="")
            repo.index.add([file_name])
            attempt += 1
            if attempt == LOOP_MAX_PRE_COMMIT:
                logger.error(
                    f"Pre-commit hooks failed for {file_name} after {LOOP_MAX_PRE_COMMIT} attempts. Exiting script."
                )
                sys.exit(1)
        elif result.returncode == 0:
            # Pre-commit hooks passed
            logger.info(message=80 * "-", status="")
            logger.info(
                message="Pre-commit completed",
                status="✅",
            )

            # Commit the file
            git_commit_file(file_name, commit_message, repo)
            break  # Break out of the loop once the file is committed


def git_commit_file(file_name, commit_message, repo):
    # Stage the file
    repo.index.add([file_name])

    # Commit the file
    try:
        repo.index.commit(commit_message)
        # If the commit was successful, log the commit message
        logger.info(
            message="File committed",
            status="✅",
        )
    except Exception as e:
        # Log an error if the commit fails
        logger.error(message="Failed to commit file", status="❌", reason=str(e))


def log_git_stats():
    logger.info(message=80 * "-", status="")
    logger.info(
        message="Deleted files:",
        status=f"{len(deleted_files)}",
    )
    logger.info(
        message="Untracked files:",
        status=f"{len(untracked_files)}",
    )
    logger.info(
        message="Modified files:",
        status=f"{len(modified_files)}",
    )
    logger.info(
        message="Staged files:",
        status=f"{len(staged_files)}",
    )
    logger.info(
        message="Committed not pushed files:",
        status=f"{len(committed_not_pushed)}",
    )
    logger.info(message=80 * "-", status="")


def generate_commit_message(diff):
    role_user_content = role_user_content_template.format(diff=diff)

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": role_system_content},
            {"role": "user", "content": role_user_content},
        ],
        model="gpt-3.5-turbo",
    )

    commit_message = response.choices[0].message.content.strip()
    return commit_message


# Define the cleanup function to remove the .lock file
def cleanup_lock_file():
    lock_file_path = os.path.join(repo_path, ".git", "index.lock")
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)
        logger.info("Cleaned up .lock file.")


parser = argparse.ArgumentParser(
    description="Git repository status checker and deleter committer."
)
parser.add_argument(
    "--repo-path",
    type=str,
    default=".",
    help="Path to the git repository (manual override)",
)
parser.add_argument(
    "--debug", default=False, action="store_true", help="Enable debug mode"
)
parser.add_argument("--file-name", type=str, help="File name to stage and diff")
parser.add_argument(
    "--oneshot",
    action="store_true",
    help="Process and commit only one file then exit",
)

# Parse script arguments
args = parser.parse_args()

# Suppress httpx INFO messages
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

# Check if pre-commit is installed. If not, install it.
try:
    subprocess.run(
        ["pre-commit", "--version"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    logger.info(message=80 * "=", status="")
    logger.info("pre-commit is already installed.")

except subprocess.CalledProcessError:
    logger.info("pre-commit is not installed. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pre-commit"], check=True)
    subprocess.run(["pre-commit", "install"], check=True)
    logger.info("pre-commit has been installed and hooks are set up.")

# Define DEBUG variable
DEBUG = args.debug

# Enable debug mode if required
if DEBUG:
    logger.info("Debug mode is enabled.")
    # logging.basicConfig(level=logging.DEBUG)

# Discover the current git repository path. If no git repository is found
# exit the script with an error message and instructions on how to:
#   a) create a new local git repository and push it to a remote repository
#   b) clone an existing remote repository to the current directory
#   c) take an existing remote repository and make the current directory
#   its local repository including all history, adding any local files to
#   the repository.
global repo_path
if args.repo_path == ".":  # Default path
    # Get the top-level directory of the git repository
    repo_path = git_get_toplevel()
    if repo_path:
        logger.info(f"Git top-level directory: {repo_path}")
    else:
        logger.error(
            "No git repository found. Please create a new local git repository and push it to a remote repository, clone an existing remote repository to the current directory, or take an existing remote repository and make the current directory its local repository including all history, adding any local files to the repository."
        )
        sys.exit(1)
else:
    repo_path = args.repo_path

# Initialize the repository
repo = git.Repo(repo_path)

# Register the cleanup function to be called on script exit
atexit.register(cleanup_lock_file)


# Set up signal handling to call the cleanup function on termination signals
def handle_signal(signum, frame):
    cleanup_lock_file()
    sys.exit(1)


signal.signal(signal.SIGINT, handle_signal)  # Handle Ctrl + C
signal.signal(signal.SIGTERM, handle_signal)  # Handle termination signals

# STEP 1: Discover current repository state
git_get_status(repo)

# STEP 2: Log the current repository state
log_git_stats()

# STEP 3: Commit any deleted files immediately
git_commit_deletes(repo)

# STEP 4: De-stage any staged but not committed files so they can be
# handled in the same manner as untracked files
git_unstage_files(repo)

# STEP 5: Discover current repository state again
git_get_status(repo)

# STEP 6: Ensure that there are no remaining deleted_files, if there are
# log an error and exit the script
if deleted_files:
    logger.error(
        "There are still deleted files that need to be committed.\nDeleted files: {deleted_files}"
    )
    sys.exit(1)

# STEP 7: Ensure that there are no remaining staged_files files, if
# there are log an error and exit the script
if staged_files:
    logger.error(
        "There are still staged files that need to be committed.\nStaged files: {staged_files}"
    )
    sys.exit(1)

# STEP 8: Process untracked & modified files
if untracked_files:
    logger.info(f"There are {len(untracked_files)} untracked files to process.")
    logger.info(f"There are {len(modified_files)} modified files to process.")

# STEP 8: Process files based on the --file-name argument
if args.file_name:
    # Process only the specified file
    file = args.file_name
    logger.info(
        message="Processing single file:",
        status=f"{file}",
    )
    commit_message = git_stage_diff(file, repo)
    logger.info(message="Running pre-commit on:", status=f"{file}")
    # logger.info(message=80 * "-", status="")
    git_pre_commit(file, commit_message, repo)
else:
    # Process untracked & modified files
    if untracked_files:
        logger.info(f"There are {len(untracked_files)} untracked files to process.")
    if modified_files:
        logger.info(f"There are {len(modified_files)} modified files to process.")

    # Loop through untracked_files and modified and process them
    for file in untracked_files + modified_files:
        # STEP 8.1.1: Stage file, get the diff and return a commit message
        logger.info(message=80 * "-", status="")
        logger.info(
            message="Processing file:",
            status=f"{file}",
        )
        commit_message = git_stage_diff(file, repo)

        # STEP 8.1.2: Run pre-commit over the file, re-staging and retrying until it fixes
        # any issues and passes or fails after LOOP_MAX_PRE_COMMIT attempts
        logger.info(message="Running pre-commit on:", status=f"{file}")
        logger.info(message=80 * "-", status="")
        git_pre_commit(file, commit_message, repo)

        # STEP 8.1.3: Exit if args.oneshot is set otherwise continue processing
        # untracked files
        if args.oneshot:
            logger.info("Oneshot mode enabled. Exiting script.")
            logger.info(message=80 * "=", status="")
            break

# Say bye bye
logger.info(message="All files processed. Exiting script.", status="😀")
logger.info(message=80 * "=", status="")
