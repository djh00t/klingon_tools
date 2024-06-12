import logging
import git
from git.exc import InvalidGitRepositoryError, NoSuchPathError
import subprocess
import sys
import argparse
from openai import OpenAI
import os
import pre_commit
from pre_commit import commands as pccmds
from pre_commit import store as pcstore

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration
LOOP_MAX_PRE_COMMIT = 5

deleted_files = []
untracked_files = []
staged_not_committed = []
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
        print(f"Error: {e}")
        return None


def git_get_status(repo):
    global deleted_files, untracked_files, staged_not_committed, committed_not_pushed

    # Get the current status of the working directory
    untracked_files = repo.untracked_files
    staged_not_committed = [item.a_path for item in repo.index.diff("HEAD")]
    committed_not_pushed = [
        item.a_path for item in repo.head.commit.diff("origin/main")
    ]
    deleted_files = [
        item.a_path for item in repo.index.diff(None, R=True) if item.deleted_file
    ]


def git_commit_deletes(repo):
    # Check if there are any deleted files to commit
    if deleted_files:
        # Log the deleted files
        logger.info(f" There are {len(deleted_files)} deleted files.")
        logger.debug(f"Deleted files: {deleted_files}")

        for file in deleted_files:
            # Stage the deleted file
            repo.index.remove(file)

            # Commit the change
            commit_message = "Committing deleted file"
            git_commit_file(file, commit_message)

        # Print the number of files committed
        logger.info(
            f"Committed {len(deleted_files)} deleted files with message: '{commit_message}'."
        )
    else:
        logger.info("No deleted files to commit.")


# Loop through all staged_not_committed files and de-stage them
def git_de_stage_files(repo):
    # Loop through all files in staged_not_committed & de-stage them
    for file in staged_not_committed:
        repo.index.remove([file], force=True)


# Stage the file, get the diff, and return a commit message
def git_stage_diff(file_name, repo):
    # Stage the file
    repo.index.add([file_name])

    # Get the diff
    diff = repo.git.diff("HEAD", file_name)

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

    # Log the generated commit message
    logger.info(f"Generated commit message:\n{commit_message}")

    # Return the commit message
    return commit_message


def git_pre_commit(file_name, commit_message, repo):
    # Reset the attempt counter
    attempt = 0

    logger.debug(f"Running pre-commit hooks on file: {file_name}")
    logger.debug(f"Commit message: {commit_message}")

    # Loop through the pre-commit hooks until they pass or fail after LOOP_MAX_PRE_COMMIT attempts
    while attempt < LOOP_MAX_PRE_COMMIT:

        # Run the pre-commit hooks on the file
        # store = pcstore.Store(repo.git_dir)
        # pcargs = argparse.Namespace(config=repo.git_dir + "/.pre-commit-config.yaml", all_files=False, files=[file_name], hook_stage='manual', verbose=False, show_diff_on_failure=False, color='auto')

        process = subprocess.Popen(
            ["pre-commit", "run", "--files", file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = [], []

        for line in process.stdout:
            print(line, end="")  # Print to screen
            stdout.append(line)  # Capture output

        for line in process.stderr:
            print(line, end="")  # Print to screen
            stderr.append(line)  # Capture output

        process.wait()
        result = subprocess.CompletedProcess(
            process.args, process.returncode, "".join(stdout), "".join(stderr)
        )

        logger.debug(f"Pre-commit hooks result for {file_name}: {result.returncode}")
        logger.debug(f"Pre-commit hooks result: {result}")

        if "files were modified by this hook" in result.stdout:
            print(
                f"Files were modified by pre-commit hooks for {file_name}. Re-staging and retrying commit."
            )
            repo.index.add([file_name])
            attempt += 1
            if attempt == LOOP_MAX_PRE_COMMIT:
                print(
                    f"Pre-commit hooks failed for {file_name} after {LOOP_MAX_PRE_COMMIT} attempts. Exiting script."
                )
                sys.exit(1)
        elif result.returncode == 0:
            # Pre-commit hooks passed
            logger.info(f"Pre-commit hooks passed for {file_name}.")

            # Commit the file
            logger.info(f"Committing file: {file_name}")
            git_commit_file(file_name, commit_message, repo)


def git_commit_file(file_name, commit_message, repo):
    # Stage the file
    repo.index.add([file_name])

    # Commit the file
    repo.index.commit(commit_message)

    print(f"Committed file(s): {file_name}")


def log_git_stats():
    logger.info(79 * "=")
    logger.info(
        f"Deleted files:                                                  {len(deleted_files)}"
    )
    logger.info(
        f"Untracked files:                                                {len(untracked_files)}"
    )
    logger.info(
        f"Staged files:                                                   {len(staged_not_committed)}"
    )
    logger.info(
        f"Committed not pushed files:                                     {len(committed_not_pushed)}"
    )
    logger.info(79 * "=")


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


if __name__ == "__main__":
    # Check if pre-commit is installed. If not, install it.
    try:
        subprocess.run(
            ["pre-commit", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("pre-commit is already installed.")
    except subprocess.CalledProcessError:
        print("pre-commit is not installed. Installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pre-commit"], check=True
        )
        subprocess.run(["pre-commit", "install"], check=True)
        print("pre-commit has been installed and hooks are set up.")

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

    # Setup logger and debug mode
    logger = logging.getLogger()

    # Define DEBUG variable
    DEBUG = args.debug

    # Enable debug mode if required
    if DEBUG:
        print("Debug mode is enabled.")
        logging.basicConfig(level=logging.DEBUG)

    # Discover the current git repository path. If no git repository is found
    # exit the script with an error message and instructions on how to:
    #   a) create a new local git repository and push it to a remote repository
    #   b) clone an existing remote repository to the current directory
    #   c) take an existing remote repository and make the current directory
    #   its local repository including all history, adding any local files to
    #   the repository.
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

    # Initialize the repository
    repo = git.Repo(repo_path)

    # STEP 1: Discover current repository state
    git_get_status(repo)

    # STEP 2: Log the current repository state
    log_git_stats()

    # STEP 3: Commit any deleted files immediately
    git_commit_deletes(repo)

    # STEP 4: De-stage any staged but not committed files so they can be
    # handled in the same manner as untracked files
    git_de_stage_files(repo)

    # STEP 5: Discover current repository state again
    git_get_status(repo)

    # STEP 6: Ensure that there are no remaining deleted_files, if there are
    # log an error and exit the script
    if deleted_files:
        logger.error(
            "There are still deleted files that need to be committed.\nDeleted files: {deleted_files}"
        )
        sys.exit(1)

    # STEP 7: Ensure that there are no remaining staged_not_committed files, if
    # there are log an error and exit the script
    if staged_not_committed:
        logger.error(
            "There are still staged files that need to be committed.\nStaged files: {staged_not_committed}"
        )
        sys.exit(1)

    # STEP 8: Process untracked files
    if untracked_files:
        logger.info(f"There are {len(untracked_files)} untracked files to process.")

    # STEP 8.1: Loop through untracked_files and process them
    for file in untracked_files:
        # STEP 8.1.1: Stage file, get the diff and return a commit message
        logger.debug(f"Processing untracked file: {file}")
        commit_message = git_stage_diff(file, repo)

        # STEP 8.1.2: Run pre-commit over the file, re-staging and retrying until it fixes
        # any issues and passes or fails after LOOP_MAX_PRE_COMMIT attempts
        logger.debug(f"Running pre-commit hooks on file: {file}")
        git_pre_commit(file, commit_message, repo)

        # STEP 8.1.3: Exit if args.oneshot is set otherwise continue processing
        # untracked files
        if args.oneshot:
            logger.info("Oneshot mode enabled. Exiting script.")
            break
