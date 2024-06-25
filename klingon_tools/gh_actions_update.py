import argparse
import fnmatch
import logging
import os
import re

import requests
import yaml
from git import Repo
from tabulate import tabulate

logger = logging.getLogger(__name__)


def can_display_emojis(no_emojis_flag: bool, args: argparse.Namespace) -> bool:
    """Check if the terminal can display emojis based on the LANG environment variable and the --no-emojis flag."""
    if no_emojis_flag:
        if not args.quiet:
            logger.debug("Emojis are disabled by the --no-emojis flag.")
        return False
    lang = os.getenv("LANG", "")
    if "UTF-8" in lang:
        logger.debug(f"Terminal supports emojis based on LANG: {lang} 😎")
        return True

    if not args.quiet:
        logger.warning(f"Terminal may not support emojis based on LANG: {lang}")

    return False


def get_github_token():
    """Retrieve the GitHub token from the environment variable."""
    return os.getenv("GITHUB_TOKEN")


def get_latest_version(repo_name: str) -> str:
    """Fetches the latest version of a GitHub repository.

    Args:
        repo_name: The name of the repository in the format 'owner/repo'.

    Returns:
        The latest version tag of the repository.
    """
    owner_repo = repo_name.split("/")
    owner, repo = owner_repo
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    logger.debug(f"Fetching latest version for repo: {repo_name} using URL: {url}")

    headers = {
        "User-Agent": "gh-actions-update-script",
    }
    token = get_github_token()
    if token:
        headers["Authorization"] = f"token {token}"

    response = requests.get(url, headers=headers)
    logger.debug(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        logger.debug(f"Latest version for {repo_name}: {response.json()['tag_name']}")
        return response.json()["tag_name"]
    logger.error(
        f"Failed to fetch latest version for {repo_name}, status code: {response.status_code}"
    )
    return None


def remove_emojis(text: str) -> str:
    """Remove emojis and any spaces between the emoji and the next character from the text."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)


def build_action_dict(
    file_path: str,
    action_name: str,
    current_version: str,
    action_display: str,
    job_display: str,
) -> dict:
    """Builds a dictionary with the required data for each action."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "]+",
        flags=re.UNICODE,
    )
    emoji = emoji_pattern.search(action_display)
    emoji = emoji.group(0) if emoji else ""
    name_clean = action_display.replace(emoji, "").strip()

    owner, repo = action_name.split("/")

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


def find_github_actions(args: argparse.Namespace) -> dict:
    """Find all GitHub Actions in the current repository."""
    repo = Repo(".", search_parent_directories=True)
    os.chdir(repo.git.rev_parse("--show-toplevel"))
    actions = {}
    yaml_files = []
    if args.file:
        yaml_files = [args.file]
    else:
        for root, _, files in os.walk(".github/workflows/"):
            for file in files:
                if file.endswith(".yml") or file.endswith(".yaml"):
                    file_path = os.path.join(root, file)
                    yaml_files.append(file_path)
                    logger.debug(f"Found YAML file: {file_path}")

    logger.debug(f"YAML files to process: {yaml_files}")
    logger.debug(f"Arguments received: {args}")
    for file_path in yaml_files:
        with open(file_path, "r") as f:
            workflow_data = yaml.safe_load(f)
            logger.debug(f"Processing file: {file_path}")
            logger.debug(f"Workflow data: {workflow_data}")
            if "jobs" in workflow_data:
                logger.debug(f"Found jobs in {file_path}")
                for job_name, job in workflow_data["jobs"].items():
                    if "steps" in job:
                        for step in job["steps"]:
                            if "uses" in step:
                                logger.debug(
                                    f"Found action: {step['uses']} in job: {job_name}"
                                )
                                action_name, current_version = step["uses"].split("@")
                                logger.debug(f"Step data: {step}")
                                logger.debug(
                                    f"Action name: {action_name}, Current version: {current_version}"
                                )
                                action_display = workflow_data.get(
                                    "name", "Unknown Action"
                                )
                                job_display = job_name
                                emoji_pattern = re.compile(
                                    "["
                                    "\U0001F600-\U0001F64F"  # emoticons
                                    "\U0001F300-\U0001F5FF"  # symbols & pictographs
                                    "\U0001F680-\U0001F6FF"  # transport & map symbols
                                    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                    "\U00002702-\U000027B0"  # Dingbats
                                    "\U000024C2-\U0001F251"  # Enclosed characters
                                    "]+",
                                    flags=re.UNICODE,
                                )
                                emoji = emoji_pattern.search(action_display)
                                emoji = emoji.group(0) if emoji else ""
                                name_clean = action_display.replace(emoji, "").strip()
                                action_dict = build_action_dict(
                                    file_path,
                                    action_name,
                                    current_version,
                                    action_display,
                                    job_display,
                                )
                                if (
                                    (
                                        not args.owner
                                        or args.owner == action_name.split("/")[0]
                                    )
                                    and (
                                        not args.repo
                                        or args.repo == action_name.split("/")[1]
                                    )
                                    and (not args.job or args.job == job_name)
                                    and (
                                        not args.action
                                        or args.action == action_display
                                        or args.action == name_clean
                                    )
                                ):
                                    key = f"{file_path}:{action_dict['action_owner']}:{action_dict['action_repo']}:{action_display}:{job_name}:{current_version}"
                                    actions[key] = action_dict

    logger.debug(f"YAML files found: {yaml_files}")
    return actions


def update_action_version(
    file_path: str, action_name: str, latest_version: str
) -> None:
    """Update the version of a specific GitHub Action in a file."""
    logger.debug(
        f"Updating action {action_name} in file {file_path} to version {latest_version}"
    )
    full_path = file_path

    with open(full_path, "r") as f:
        content = yaml.safe_load(f)

    updated = False
    logger.debug(f"Searching for action {action_name} in jobs")

    for job_name, job in content.get("jobs", {}).items():
        for step in job.get("steps", []):
            if "uses" in step and step["uses"].startswith(action_name):
                logger.debug(f"Found action {action_name} in job {job_name}")
                step["uses"] = f"{action_name}@{latest_version}"
                updated = True

    if updated:
        logger.info(
            f"Action {action_name} updated to version {latest_version} in file {file_path}"
        )
        with open(full_path, "w") as f:
            yaml.dump(content, f, default_flow_style=False)
    else:
        logger.warning(f"No updates made for action {action_name} in file {file_path}")

    logger.debug(f"Updated {action_name} to {latest_version} in {file_path}")


def collect_api_data(actions: dict) -> dict:
    """Collect the latest version data for GitHub Actions from the API."""
    unique_repos = set(
        (action["action_owner"], action["action_repo"]) for action in actions.values()
    )
    api_data = {}
    for owner, repo in unique_repos:
        repo_name = f"{owner}/{repo}"
        latest_version = get_latest_version(repo_name)
        for key, action in actions.items():
            if action["action_owner"] == owner and action["action_repo"] == repo:
                action["action_latest_version"] = (
                    latest_version if latest_version else "Unknown"
                )
    return actions


def setup_logging(args: argparse.Namespace) -> None:
    """Sets up logging based on the provided arguments.

    Args:
        args: The parsed command-line arguments.
    """
    token = get_github_token()

    logger.debug("GitHub Actions Updater is starting.")

    # Check if a GitHub token is available
    if token:
        logger.debug("Using GitHub token for authentication.")
    else:
        logger.warning("No GitHub token found. Requests may be rate-limited.")

    # Set up logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled.")
    else:
        logging.basicConfig(level=logging.INFO)
        logger.setLevel(logging.INFO)


def present_state_data(actions: dict, args: argparse.Namespace) -> None:
    """Present the state data for GitHub Actions."""
    table = []
    headers = [
        "File",
        "Owner",
        "Repo",
        "Action Name",
        "Job",
        "Current",
        "Latest",
        "Status",
    ]

    for key, data in actions.items():
        current_version = data["action_version_current"]
        latest_version = data["action_latest_version"]
        if current_version == latest_version or current_version.startswith(
            latest_version.split(".")[0]
        ):
            status = "✅" if not args.no_emojis else "OK"
        else:
            status = "⬆️" if not args.no_emojis else "Upgrade"

        if args.no_emojis:
            data["action_name"] = remove_emojis(data["action_name"]).strip()

        table.append(
            [
                data["file_name"],
                data["action_owner"],
                data["action_repo"],
                data["action_name"],
                data["job_name"],
                current_version,
                latest_version,
                status,
            ]
        )

    if args.json:
        import json

        print(json.dumps(actions, indent=4))
    else:
        print(tabulate(table, headers=headers))
        if not args.update and not args.quiet:
            print(
                "\nNote: Use '--update' to update all outdated actions to the latest version."
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check and update GitHub Actions versions.", add_help=False
    )
    parser.add_argument(
        "--action", type=str, help="Update all instances of a specific action."
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    parser.add_argument(
        "--file",
        type=str,
        help="Update actions in a specific file (bash wildcards accepted).",
    )
    parser.add_argument("--job", type=str, help="Filter actions by job name.")
    parser.add_argument("--repo", type=str, help="Filter actions by repository name.")
    parser.add_argument("--owner", type=str, help="Filter actions by owner name.")
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
        "--json", action="store_true", help="Output the results as a JSON object."
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )
    args = parser.parse_args()

    if args.update:
        args.quiet = True

    setup_logging(args)

    if not args.quiet:
        args.no_emojis = not can_display_emojis(args.no_emojis, args)
    else:
        args.no_emojis = args.no_emojis

    # Collect file data
    actions = find_github_actions(args)
    logger.debug(f"Actions data:\n{actions}")

    # Collect API data (Latest)
    actions = collect_api_data(actions)
    logger.debug(f"API data: {actions}")

    if not args.update:
        # Present data
        present_state_data(actions, args)

    else:
        # Update file data for filtered files to Latest version
        for key, data in actions.items():
            logger.debug(f"Checking action: {key}")
            logger.debug(f"Current Version: {data['action_version_current']}")
            logger.debug(f"Latest Version: {data['action_latest_version']}")
            logger.debug(f"Data: {data}")

            # Update action if needed
            if data["action_version_current"] != data["action_latest_version"]:
                logger.info(
                    f"Updating action:  {data['action_owner']}/{data['action_repo']} from version {data['action_version_current']} to {data['action_latest_version']}"
                )
                update_action_version(
                    data["file_name"],
                    f"{data['action_owner']}/{data['action_repo']}",
                    data["action_latest_version"],
                )  # Ensure 'file', 'action_name' are correctly set
            else:
                logger.info(
                    f"No update needed for action: {data['action_owner']}/{data['action_repo']}"
                )

        # Collect file data after update
        actions_after = find_github_actions(args)
        logger.debug(f"Actions after update: {actions_after}")

        # Collect API data again for updated file data
        actions_after = collect_api_data(actions_after)
        logger.debug(f"API data after update: {actions_after}")

        # Present updated data
        present_state_data(actions_after, args)


if __name__ == "__main__":
    main()
