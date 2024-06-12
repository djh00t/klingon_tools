import os
import subprocess
import json
import requests
import argparse
import logging
import git


def get_git_status(repo_path="."):
    # Open the repository
    repo = git.Repo(repo_path)

    # Get the current status of the working directory
    modified_not_staged = [item.a_path for item in repo.index.diff(None)]
    staged_not_committed = [item.a_path for item in repo.index.diff("HEAD")]
    committed_not_pushed = [
        item.a_path for item in repo.head.commit.diff("origin/main")
    ]  # Change 'origin/main' to your remote/branch if different

    return modified_not_staged, staged_not_committed, committed_not_pushed


def get_git_stats():
    """
    Gathers statistics about the git repository.

    Returns:
        dict: A dictionary containing the number of files in different states.
    """
    stats = {
        "modified_not_staged": 0,
        "staged_not_committed": 0,
        "committed_not_pushed": 0,
        "untracked_files": 0,
    }

    # Get the number of changed but not staged files
    modified_not_staged = (
        subprocess.check_output(["git", "ls-files", "--modified", "--exclude-standard"])
        .decode("utf-8")
        .strip()
        .split("\n")
    )

    stats["modified_not_staged"] = len([file for file in modified_not_staged if file])

    # Get the number of changed and staged but not committed files
    staged_not_committed = (
        subprocess.check_output(["git", "diff", "--cached", "--name-only"])
        .decode("utf-8")
        .strip()
        .split("\n")
    )
    stats["staged_not_committed"] = len([file for file in staged_not_committed if file])

    # Count the number of untracked files
    stats["untracked_files"] = len(
        [file for file in changed_files if file.startswith("??")]
    )
    committed_not_pushed = (
        subprocess.check_output(["git", "cherry", "-v"])
        .decode("utf-8")
        .strip()
        .split("\n")
    )
    stats["committed_not_pushed"] = len(
        [commit for commit in committed_not_pushed if commit]
    )

    return stats


def setup_logging(debug):
    """
    Sets up logging configuration.

    Args:
        debug (bool): Flag to enable debug logging.
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def generate_commit_message(staged_diffs):
    logging.debug("Generating commit message for staged diffs.")
    """
    Generates a commit message using the OpenAI API.

    Args:
        staged_diffs (str): The staged changes in the repository.

    Returns:
        str: The generated commit message.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    logging.debug(f"API Key: {'set' if api_key else 'not set'}")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    role_system_content_encoded = "Generate a commit message based solely on the staged diffs provided, ensuring accuracy and relevance to the actual changes. Avoid adding speculative or unnecessary footers, such as references to non-existent issues. You must adhere to the conventional commits standard. The commit message should:\n\n- Clearly specify the type of change (feat, fix, build, etc.).\n- Clearly specify the scope of change.\n- Describe the purpose and actual detail of the change with clarity.\n- Use bullet points for the body when more than one item is discussed.\n- You MUST follow the Conventional Commits standardized format:\n\n    <type>(<scope>): <description>\n    [optional body]\n    [optional footer/breaking changes]\n\n\n    Types include: feat, fix, build, ci, docs, style, refactor, perf, test, chore, etc.\n    Ensure the message is factual, based on the provided diffs, and free from any speculative or unnecessary content."

    role_user_content_encoded = (
        f'Generate a git commit message based on these diffs:\n"{staged_diffs}"'
    )

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": role_system_content_encoded},
            {"role": "user", "content": role_user_content_encoded},
        ],
    }

    logging.debug("Sending request to OpenAI API.")
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        data=json.dumps(data),
    )

    response.raise_for_status()
    commit_message = response.json()["choices"][0]["message"]["content"].strip()
    logging.debug(f"Generated commit message: {commit_message}")
    return commit_message


def handle_changed_files():
    """
    Handles changed files by generating a commit message for staged changes and committing them.
    """
    logging.debug("Fetching staged diffs.")
    staged_diffs = subprocess.check_output(
        ["git", "diff", "--cached", "--name-status"]
    ).decode("utf-8")
    logging.debug(f"Staged diffs: {staged_diffs}")
    if staged_diffs:
        commit_message = generate_commit_message(staged_diffs)
        logging.debug("Committing changes.")
        subprocess.run(["git", "commit", "-m", commit_message])
        logging.debug("Changes committed successfully.")
        print("Changes committed successfully.")
    else:
        print("No changes to commit.")


def check_environment_variables():
    """
    Checks if required environment variables are set.
    """
    logging.debug("Checking environment variables.")
    if not os.environ.get("OPENAI_API_KEY"):
        logging.error("OPENAI_API_KEY environment variable is not set.")
        raise ValueError("OPENAI_API_KEY environment variable is not set")


def main(debug=False):
    """
    The main function that orchestrates the script's flow.
    """
    try:
        setup_logging(debug)
        logging.debug("Starting main function.")
        stats = get_git_stats()
        print(
            "=============================================================================="
        )
        print("LOCAL GIT BRANCH STATE (START)")
        print(
            "=============================================================================="
        )
        print(
            f" CHANGED FILES:                                                            {stats['modified_not_staged']}"
        )
        print(
            f" STAGED FILES:                                                             {stats['staged_not_committed']}"
        )
        print(
            f" COMMITS TO PUSH:                                                          {stats['committed_not_pushed']}"
        )
        print(
            "=============================================================================="
        )

        exit(0)

        check_environment_variables()
        logging.debug("Environment variables checked.")
        handle_changed_files()
        logging.debug("Handled changed files.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    repo_path = "."  # Adjust the path to your repository if needed
    modified_not_staged, staged_not_committed, committed_not_pushed = get_git_status(
        repo_path
    )

    print("Modified but not staged files:")
    print(modified_not_staged)

    print("Staged but not committed files:")
    print(staged_not_committed)

    print("Committed but not pushed files:")
    print(committed_not_pushed)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Commit changes with AI-generated commit messages."
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    args = parser.parse_args()

    main(debug=args.debug)
