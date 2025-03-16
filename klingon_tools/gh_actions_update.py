# klingon_tools/gh_actions_update.py
"""
Module for updating GitHub Actions versions in workflows.

This module provides functionality to check and update GitHub Actions versions
in YAML workflow files within a repository. It supports filtering by action,
job, repository, and owner, and can output results in JSON format or update the
workflow files directly.

Usage:
    python gh_actions_update.py --help

"""

import argparse
import json
import logging
import os
import re
from typing import Dict, List, Any

import requests
from git import Repo
from ruamel.yaml import YAML
from tabulate import tabulate
from klingon_tools.log_msg import log_message
from klingon_tools.log_tools import LogTools


def can_display_emojis(no_emojis_flag: bool, args: argparse.Namespace) -> bool:
    """
    Checks if the terminal can display emojis.

    This function checks the LANG environment variable and the --no-emojis flag
    to determine if the terminal can display emojis.

    Args:
        no_emojis_flag (bool): A boolean flag indicating if emojis are
        disabled. args (argparse.Namespace): The parsed command-line arguments.

    Returns:
        bool: A boolean indicating if emojis can be displayed.
    """
    # Check if emojis are disabled by the --no-emojis flag
    if no_emojis_flag:
        if not args.quiet:
            log_message.debug(
                "Emojis are disabled by the --no-emojis flag."
            )
        return False

    # Check the LANG environment variable for UTF-8 support
    lang = os.getenv("LANG", "")
    if "UTF-8" in lang:
        log_message.debug(
            f"Terminal supports emojis based on LANG: {lang} 😎"
        )
        return True

    # Log a warning if emojis may not be supported
    if not args.quiet:
        log_message.warning(
            message=f"Terminal may not support emojis based on LANG: {lang} 😎"
        )

    return False


def get_github_token() -> str:
    """
    Retrieves the GitHub token from the environment variable.

    This function fetches the GitHub token from the environment variable
    'GITHUB_TOKEN'. This token is used for authenticating API requests to
    GitHub.

    Returns:
        str: The GitHub token as a string. If the environment variable is not
        set, it returns None.
    """
    return os.getenv("GITHUB_TOKEN")


def get_latest_version(repo_name: str) -> str:
    """
    Fetches the latest version of a GitHub repository.

    This function makes an API request to GitHub to fetch the latest release
    version of a given repository.

    Args:
        repo_name (str): The name of the repository in the format 'owner/repo'.

    Returns:
        str: The latest version tag of the repository. If the request fails, it
        returns None.
    """
    # Split the repository name into owner and repo
    owner, repo = repo_name.split("/")

    # Construct the URL for the GitHub API request
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    log_message.debug(
        f"Fetching latest version for repo: {repo_name} using URL: {url}"
    )

    # Set up headers for the API request
    headers = {
        "User-Agent": "gh-actions-update-script",
    }

    # Add authorization header if a GitHub token is available
    token = get_github_token()
    if token:
        headers["Authorization"] = f"token {token}"

    # Make the API request to fetch the latest release
    response = requests.get(url, headers=headers, timeout=10)
    log_message.debug(message=f"Response status code: {response.status_code}")

    # Check if the request was successful
    if response.status_code == 200:
        log_message.debug(
            message=f"Latest version for {repo_name}: "
            f"{response.json()['tag_name']}"
        )
        return response.json()["tag_name"]

    # Log an error if the request failed
    log_message.error(
        message=f"Failed to fetch latest version for {repo_name}, "
        f"status code: {response.status_code}"
    )
    return None


def remove_emojis(text: str) -> str:
    """
    Removes emojis from the given text.

    This function uses a regular expression to identify and remove emojis from
    the input text. It covers a wide range of emoji characters including
    emoticons, symbols, pictographs, transport symbols, flags, dingbats, and
    enclosed characters.

    Args:
        text (str): The input text containing emojis.

    Returns:
        str: The text with emojis removed.
    """
    # Define a regular expression pattern to match emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "]+",
        flags=re.UNICODE,
    )

    # Substitute emojis with an empty string
    return emoji_pattern.sub(r"", text)


def build_action_dict(
    file_path: str,
    action_name: str,
    current_version: str,
    action_display: str,
    job_display: str,
) -> dict:
    """
    Builds a dictionary with the required data for each action.

    This function constructs a dictionary containing relevant information about
    a GitHub Action, including its file path, owner, repository, current
    version, display name, and job name. It also processes the action display
    name to remove any emojis.

    Args:
        file_path (str): The path to the YAML file.
        action_name (str): The name of the GitHub Action in the format
        'owner/repo'.
        current_version (str): The current version of the action.
        action_display (str): The display name of the action.
        job_display (str): The display name of the job.

    Returns:
        dict: A dictionary containing the action data.
    """
    # Define a regular expression pattern to match emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "]+",
        flags=re.UNICODE,
    )

    # Search for an emoji in the action display name
    emoji = emoji_pattern.search(action_display)
    emoji = emoji.group(0) if emoji else ""

    # Remove the emoji from the action display name
    name_clean = action_display.replace(emoji, "").strip()

    # Split the action name into owner and repository
    owner, repo = action_name.split("/")

    # Construct and return the action dictionary
    return {
        "file_name": file_path,
        "action_owner": owner,
        "action_repo": repo,
        "action_version_current": current_version,
        "action_name": action_display,
        "action_name_clean": name_clean,
        "job_name": job_display,
        "action_latest_version": None,  # Placeholder for latest version
    }


def find_github_actions(args: argparse.Namespace) -> Dict[str, Dict]:
    """
    Finds all GitHub Actions in the current repository.

    This function searches for all GitHub Actions in the YAML workflow files
    within the current repository and returns a dictionary of action data.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.

    Returns:
        dict: A dictionary containing the action data.
    """
    repo = Repo(".", search_parent_directories=True)
    os.chdir(repo.git.rev_parse("--show-toplevel"))

    actions = {}
    yaml_files = [args.file] if args.file else get_yaml_files()

    log_message.debug(f"YAML files to process: {yaml_files}")
    log_message.debug(f"Arguments received: {args}")

    for file_path in yaml_files:
        process_yaml_file(file_path, actions, args)

    log_message.debug(f"YAML files found: {yaml_files}")
    return actions


def get_yaml_files() -> List[str]:
    """Returns a list of YAML files in the .github/workflows directory."""
    yaml_files = []
    for root, _, files in os.walk(".github/workflows/"):
        for file in files:
            if file.endswith((".yml", ".yaml")):
                file_path = os.path.join(root, file)
                yaml_files.append(file_path)
                log_message.debug(f"Found YAML file: {file_path}")
    return yaml_files


def process_yaml_file(
    file_path: str, actions: Dict[str, Dict], args: argparse.Namespace
):
    """Processes a single YAML file and updates the actions dictionary."""
    yaml = YAML()
    yaml.preserve_quotes = True
    with open(file_path, "r", encoding="utf-8") as f:
        workflow_data = yaml.load(f)
        log_message.debug(f"Processing file: {file_path}")
        log_message.debug(f"Workflow data: {workflow_data}")

        if "jobs" in workflow_data:
            process_jobs(file_path, workflow_data, actions, args)


def process_jobs(
    file_path: str,
    workflow_data: Dict,
    actions: Dict[str, Dict],
    args: argparse.Namespace
) -> None:
    """Processes jobs in a workflow and updates the actions dictionary."""
    for job_name, job in workflow_data["jobs"].items():
        if "steps" in job:
            for step in job["steps"]:
                if "uses" in step:
                    action_context = {
                        'workflow_data': workflow_data,
                        'job_name': job_name,
                        'step': step,
                        'actions': actions
                    }
                    process_action(file_path, action_context, args)


def process_action(
    file_path: str,
    action_context: Dict[str, Any],
    args: argparse.Namespace
) -> None:
    """Processes a single action and updates the actions dictionary if it
    matches the filter criteria."""
    workflow_data = action_context['workflow_data']
    job_name = action_context['job_name']
    step = action_context['step']
    actions = action_context['actions']

    action_name, current_version = step["uses"].split("@")
    action_display = workflow_data.get("name", "Unknown Action")
    job_display = job_name

    action_dict = build_action_dict(
        file_path, action_name, current_version, action_display, job_display
    )

    if action_matches_filter(action_dict, args):
        key = (
            f"{file_path}:{action_dict['action_owner']}:"
            f"{action_dict['action_repo']}:"
            f"{action_display}:{job_name}:{current_version}"
        )
        actions[key] = action_dict


def action_matches_filter(action_dict: Dict, args: argparse.Namespace) -> bool:
    """Checks if an action matches the filter criteria."""
    return (
        (not args.owner or args.owner == action_dict["action_owner"]) and
        (not args.repo or args.repo == action_dict["action_repo"]) and
        (not args.job or args.job == action_dict["job_name"]) and
        (not args.action or args.action in (
            action_dict["action_name"], action_dict["action_name_clean"]))
    )


def update_action_version(
    file_path: str, action_name: str, latest_version: str
) -> bool:
    """Updates the version of a specific GitHub Action in a YAML file.

    This function reads a YAML file, searches for a specific GitHub Action, and
    updates its version to the latest version provided. If the action is found
    and updated, the changes are written back to the file.

    Args:
        file_path (str): The path to the YAML file.
        action_name (str): The name of the GitHub Action in the format
        'owner/repo'.
        latest_version (str): The latest version of the action.

    Returns:
        bool: True if the action was updated, False otherwise.
    """
    log_message.debug(
        message="Updating action %s in file %s to version %s",
        args=(action_name, file_path, latest_version),
    )

    # Read the YAML file content
    yaml = YAML()
    yaml.preserve_quotes = True
    with open(file_path, "r", encoding="utf-8") as file:
        content = yaml.load(file)

    updated = False

    # Search for the action in the jobs section
    for job in content.get("jobs", {}).values():
        for step in job.get("steps", []):
            if "uses" in step and step["uses"].startswith(action_name):
                step["uses"] = f"{action_name}@{latest_version}"
                updated = True

    # Write the updated content back to the file if any updates were made
    if updated:
        log_message.info(
            f"Action {action_name} updated to version "
            f"{latest_version} in file {file_path}"
        )
        with open(file_path, "w", encoding="utf-8") as file:
            yaml.dump(content, file)
    else:
        log_message.warning(
            message="No updates made for action %s in file %s",
            args=(action_name, file_path),
        )

    log_message.debug(
        message="Updated %s to %s in %s",
        args=(action_name, latest_version, file_path),
    )

    return updated


def collect_api_data(actions: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Collects the latest version data for GitHub Actions from the GitHub API.

    This function iterates over a dictionary of GitHub Actions, fetches the
    latest version for each unique repository from the GitHub API, and updates
    the action data with the latest version information.

    Args:
        actions (dict): A dictionary containing the action data. Each key is a
        unique
                        identifier for an action, and each value is a
                        dictionary with details about the action.

    Returns:
        dict: A dictionary with the latest version data for each action.
    """
    # Extract unique repositories from the actions dictionary
    unique_repos = set(
        (action["action_owner"], action["action_repo"])
        for action in actions.values()
    )

    # Iterate over each unique repository
    for owner, repo in unique_repos:
        repo_name = f"{owner}/{repo}"

        # Fetch the latest version of the repository from the GitHub API
        latest_version = get_latest_version(repo_name)

        # Update the action data with the latest version
        for action in actions.values():
            if (
                action["action_owner"] == owner and
                action["action_repo"] == repo
            ):
                action["action_latest_version"] = (
                    latest_version if latest_version else "Unknown"
                )

    return actions


# Configure logging with a simpler format
logging.basicConfig(
    level=logging.WARNING,
    format='%(message)s'
)


def setup_logging(args: argparse.Namespace) -> None:
    """
    Sets up logging based on the provided command-line arguments.

    This function configures the logging level and settings based on the
    command-line arguments provided by the user. It checks for a GitHub token
    and sets the logging level to DEBUG if the --debug flag is set.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
    """
    token = get_github_token()

    # Initialize logging tools
    log_tools = LogTools(debug=args.debug)
    log_tools.set_log_level("DEBUG" if args.debug else "INFO")

    log_message.debug("GitHub Actions Updater is starting.")

    if token:
        log_message.debug("Using GitHub token for authentication.")
    else:
        log_message.warning(
            "No GitHub token found. Requests may be rate-limited."
        )


def present_state_data(
        actions: Dict[str, Dict],
        args: argparse.Namespace) -> None:
    """
    Presents the state data for GitHub Actions.

    This function displays the state data for GitHub Actions in a tabular
    format or as a JSON object based on the provided command-line arguments.

    Args:
        actions (dict): A dictionary containing the action data.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    if args.json:
        print(json.dumps(actions, indent=4))
    else:
        table = build_table(actions, args)
        print(tabulate(table, headers=get_headers()))
        if not args.update and not args.quiet:
            print(
                "\nNote: Use '--update' to update all outdated actions to the"
                "latest version."
            )


def build_table(
    actions: Dict[str, Dict],
    args: argparse.Namespace
) -> List[List[str]]:
    """Builds a table of action data for display."""
    table = []
    for data in actions.values():
        current_version = data["action_version_current"]
        latest_version = data["action_latest_version"]
        status = get_status(current_version, latest_version, args.no_emojis)
        action_name = remove_emojis(data["action_name"]).strip() \
            if args.no_emojis else data["action_name"]
        table.append([
            data["file_name"],
            data["action_owner"],
            data["action_repo"],
            action_name,
            data["job_name"],
            current_version,
            latest_version,
            status,
        ])
    return table


def get_headers() -> List:
    """
    Returns the headers for the action data table.
    """
    return [
        "File",
        "Owner",
        "Repo",
        "Action Name",
        "Job",
        "Current",
        "Latest",
        "Status"
    ]


def get_status(
        current_version: str, latest_version: str, no_emojis: bool) -> str:
    """Determines the status of an action based on its version."""
    if current_version == latest_version:
        return "OK" if no_emojis else "✅"
    return "Upgrade" if no_emojis else "⬆️"


def main() -> None:
    """
    Main function to check and update GitHub Actions versions.

    This function parses command-line arguments, sets up logging, finds GitHub
    Actions in the repository, collects the latest version data, and presents
    or updates the actions based on the provided arguments.
    """
    # Initialize the argument parser
    parser = argparse.ArgumentParser(
        description="Check and update GitHub Actions versions.", add_help=False
    )

    # Add command-line arguments
    parser.add_argument(
        "--action", type=str, help="Update all instances of a specific action."
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging."
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Update actions in a specific file (bash wildcards accepted).",
    )
    parser.add_argument("--job", type=str, help="Filter actions by job name.")
    parser.add_argument(
        "--repo", type=str, help="Filter actions by repository name."
    )
    parser.add_argument(
        "--owner", type=str, help="Filter actions by owner name."
    )
    parser.add_argument(
        "--no-emojis", action="store_true", help="Disable emojis in output."
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress startup log messages."
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update outdated actions to the latest version.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the results as a JSON object.",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )
    args = parser.parse_args()

    # Suppress startup log messages if update flag is set
    if args.update:
        args.quiet = True

    # Set up logging based on the provided arguments
    setup_logging(args)

    # Determine if emojis should be displayed - default to showing emojis
    if not args.quiet:
        # Only disable emojis if explicitly requested with --no-emojis
        # Otherwise, check if the terminal can display them
        if args.no_emojis:
            args.no_emojis = not can_display_emojis(False, args)
        else:
            args.no_emojis = False
    else:
        # In quiet mode, respect the --no-emojis flag
        args.no_emojis = args.no_emojis if args.no_emojis else False

    # Collect file data
    log_message.debug("Collecting file data...")
    actions = find_github_actions(args)
    log_message.debug(f"Actions data:\n{actions}")

    # Collect API data (latest versions)
    log_message.debug("Collecting API data...")
    actions = collect_api_data(actions)
    log_message.debug(f"API data: {actions}")

    # Update file data for filtered files to the latest version
    if args.update:
        for data in actions.values():
            if data["action_version_current"] != data["action_latest_version"]:
                log_message.info(
                    f"Updating action: {data['action_owner']}/{data['action_repo']} "
                    f"from version {data['action_version_current']} to {data['action_latest_version']}",
                    status="⬆️"
                )
                update_action_version(
                    data["file_name"],
                    f"{data['action_owner']}/{data['action_repo']}",
                    data["action_latest_version"],
                )
            else:
                log_message.info(
                    f"No update needed for action: {data['action_owner']}/{data['action_repo']}",
                    status="✅"
                )

        # Collect file data after update
        actions_after = find_github_actions(args)
        actions_after = collect_api_data(actions_after)
        present_state_data(actions_after, args)
    else:
        present_state_data(actions, args)


if __name__ == "__main__":
    main()
