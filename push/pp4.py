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

# Initialize the OpenAI API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration & Variables
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
    global deleted_files, untracked_files, modified_files, staged_not_committed, committed_not_pushed

    # Get the current status of the working directory
    untracked_files = repo.untracked_files
    modified_files = [
        item.a_path for item in repo.index.diff(None) if item.change_type == "M"
    ]
    staged_not_committed = [item.a_path for item in repo.index.diff("HEAD")]
    committed_not_pushed = [
        item.a_path for item in repo.head.commit.diff("origin/main")
    ]
    deleted_files = [
        item.a_path for item in repo.index.diff(None) if item.change_type == "D"
    ]


def git_commit_deletes(repo):
    # Check if there are any deleted files to commit
    if deleted_files or staged_not_committed:
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
        logger.info(f" There are {len(all_deleted_files)} deleted files.")
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
    else:
        logger.info("No deleted files to commit.")


# Loop through all staged_not_committed files and de-stage them
def git_de_stage_files(repo):
    # Loop through all files in staged_not_committed & de-stage them
    for file in staged_not_committed:
        try:
            if file in repo.index.entries:
                repo.index.remove([file], force=True)
            else:
                logger.warning(f"File {file} not found in index, skipping de-stage.")
        except git.exc.GitCommandError as e:
            logger.error(f"Error de-staging file {file}: {e}")


# Stage the file, get the diff, and return a commit message
def git_stage_diff(file_name, repo):
    # Stage the file
    logger.info(f"Staging file: {file_name}")
    repo.index.add([file_name])

    # Get the diff
    logger.info(f"Getting diff for file: {file_name}")
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
    logger.info(f"Generated commit message:\n\n{commit_message}\n")

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
            break  # Break out of the loop once the file is committed


def git_commit_file(file_name, commit_message, repo):
    # Stage the file
    repo.index.add([file_name])

    # Commit the file
    repo.index.commit(commit_message)

    # If the commit was successful, log the commit message
    logger.info(f"Committed file: {file_name} OK")


def log_git_stats():
    logger.info(79 * "=")
    logger.info(
        f"Deleted files:                                                  {len(deleted_files)}"
    )
    logger.info(
        f"Untracked files:                                                {len(untracked_files)}"
    )
    logger.info(
        f"Modified files:                                                 {len(modified_files)}"
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


# Define the cleanup function to remove the .lock file
def cleanup_lock_file():
    lock_file_path = os.path.join(repo_path, ".git", "index.lock")
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)
        logger.info("Cleaned up .lock file.")


# Register the cleanup function to be called on script exit
atexit.register(cleanup_lock_file)


# Set up signal handling to call the cleanup function on termination signals
def handle_signal(signum, frame):
    cleanup_lock_file()
    sys.exit(1)


signal.signal(signal.SIGINT, handle_signal)  # Handle Ctrl + C
signal.signal(signal.SIGTERM, handle_signal)  # Handle termination signals

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

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Check if pre-commit is installed. If not, install it.
try:
    subprocess.run(
        ["pre-commit", "--version"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
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

# STEP 8: Process untracked & modified files
if untracked_files:
    logger.info(f"There are {len(untracked_files)} untracked files to process.")
    logger.info(f"There are {len(modified_files)} modified files to process.")

# STEP 8.1: Loop through untracked_files and modified and process them
for file in untracked_files + modified_files:
    # STEP 8.1.1: Stage file, get the diff and return a commit message
    logger.info(f"Processing file: {file}")
    commit_message = git_stage_diff(file, repo)

    # STEP 8.1.2: Run pre-commit over the file, re-staging and retrying until it fixes
    # any issues and passes or fails after LOOP_MAX_PRE_COMMIT attempts
    logger.info(f"Running pre-commit hooks on file: {file}")
    git_pre_commit(file, commit_message, repo)

    # STEP 8.1.3: Exit if args.oneshot is set otherwise continue processing
    # untracked files
    if args.oneshot:
        logger.info("Oneshot mode enabled. Exiting script.")
        break
