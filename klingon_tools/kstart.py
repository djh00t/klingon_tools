import os
import sys
import subprocess
import configparser
from datetime import datetime


def check_git_config():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~/.gitconfig"))

    if "user" not in config:
        config["user"] = {}

    if "name" not in config["user"]:
        name = input("Enter your Git username: ")
        subprocess.run(["git", "config", "--global", "user.name", name])

    if "email" not in config["user"]:
        email = input("Enter your Git email: ")
        subprocess.run(["git", "config", "--global", "user.email", email])


def load_branch_metadata():
    config = configparser.ConfigParser()
    if os.path.exists(".branch-metadata"):
        config.read(".branch-metadata")
    return config


def save_branch_metadata(config):
    with open(".branch-metadata", "w") as configfile:
        config.write(configfile)


def prompt_with_default(prompt, default):
    return input(f"{prompt} [{default}]: ") or default


def main():
    check_git_config()

    config = load_branch_metadata()

    if "Branch" not in config:
        config["Branch"] = {}

    # GitHub username
    config["Branch"]["GITHUB_USERNAME"] = prompt_with_default(
        "Enter your GitHub username",
        config["Branch"].get("GITHUB_USERNAME", ""),
    )

    # Issue type
    print("Select issue type:")
    print("a) Bug")
    print("b) Documentation")
    print("c) Feature")
    default_issue_type = config["Branch"].get("ISSUE_TYPE", "feature")
    default_choice = (
        "c"
        if default_issue_type == "feature"
        else ("a" if default_issue_type == "bug" else "b")
    )
    issue_type_choice = prompt_with_default(
        "Enter your choice (a/b/c)", default_choice
    ).lower()
    if issue_type_choice == "a":
        issue_type = "bug"
    elif issue_type_choice == "b":
        issue_type = "documentation"
    elif issue_type_choice == "c":
        issue_type = "feature"
    else:
        print(f"Invalid choice. Using default: '{default_issue_type}'.")
        issue_type = default_issue_type

    # Store issue_type in config
    config["Branch"]["ISSUE_TYPE"] = issue_type

    # Feature branch title
    config["Branch"]["FEATURE_BRANCH_TITLE"] = prompt_with_default(
        "Enter title for feature branch and PR",
        config["Branch"].get("FEATURE_BRANCH_TITLE", ""),
    )

    # Linked issues
    config["Branch"]["ISSUES_LINKED_TO_BRANCH"] = prompt_with_default(
        "Enter GitHub issues to link (comma-separated)",
        config["Branch"].get("ISSUES_LINKED_TO_BRANCH", ""),
    )

    # Set branch status to 'new'
    config["Branch"]["BRANCH_STATUS"] = "new"

    # Update timestamp
    config["Branch"]["LAST_UPDATED_TIMESTAMP"] = datetime.now().strftime(
        "%Y%m%d"
    )

    # Save metadata
    save_branch_metadata(config)

    # Create and push feature branch
    issue_number = config["Branch"]["ISSUES_LINKED_TO_BRANCH"].split(",")[0]
    branch_name = (
        f"dev-{issue_type}-{issue_number}-"
        f"{config['Branch']['GITHUB_USERNAME']}-"
        f"{config['Branch']['LAST_UPDATED_TIMESTAMP']}"
    )

    try:
        # Check if the branch already exists
        result = subprocess.run(
            ["git", "rev-parse", "--verify", branch_name],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"Branch {branch_name} already exists. Switching to it.")
            subprocess.run(["git", "checkout", branch_name], check=True)
        else:
            # Create new branch
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            print(f"Created new branch: {branch_name}")

        # Push the branch (will update if it already exists)
        subprocess.run(
            ["git", "push", "-u", "origin", branch_name], check=True
        )
        print(f"Pushed branch: {branch_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error handling branch: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# This allows us to test the entrypoint
__main__ = main

if __name__ == "__main__":
    main()
