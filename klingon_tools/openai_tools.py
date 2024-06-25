"""
This module provides tools for generating commit messages, pull request titles, and release bodies using OpenAI's API.

Functions:
    generate_content(template_key: str, diff: str) -> str:
        Generates content based on a specific template.
    format_message(message: str, dryrun: bool = False) -> str:
        Formats a message with line wrapping and sign-off.
    unstage_files():
        Unstages all staged files.
    generate_commit_message(diff: str, dryrun: bool = False) -> str:
        Generates a commit message.
    generate_pull_request_title(diff: str, dryrun: bool = False) -> str:
        Generates a pull request title.
    generate_release_body(diff: str, dryrun: bool = False) -> str:
        Generates a release body.
"""

import os
import textwrap
from openai import OpenAI
import subprocess
from klingon_tools.git_user_info import get_git_user_info
from klingon_tools.logger import logger

# Initialize OpenAI API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# AI Templates
templates = {
    "commit_message_system": """
    Generate a commit message based solely on the staged diffs provided, ensuring accuracy and relevance to the actual changes. Avoid speculative or unnecessary footers, such as references to non-existent issues.

    Follow the Conventional Commits standard using the following format:
    ```
    <type>(scope): <description>

    [body]

    [optional footer(s)]
    ```
    Ensure the following:

    Type and Scope: Select the most specific of application name, file name, class name, method/function name, or feature name for the commit scope. If in doubt, use the name of the file being modified.
    Types: Use fix: for patches that fix bugs, feat: for introducing new features, and other recognized types as per conventions (build:, chore:, ci:, docs:, style:, refactor:, perf:, test:, etc.).
    Breaking Changes: Include a BREAKING CHANGE: footer or append ! after type/scope for commits that introduce breaking API changes.
    Footers: Use a convention similar to git trailer format for additional footers.
    Ensure the commit message generation handles diverse scenarios effectively and prompts for necessary inputs when ambiguities arise.
    Do not add "Co-authored-by" or other footers unless explicitly required.
    """,
    "commit_message_user": """
    Generate a git commit message based on these diffs:
    \"{diff}\"
    """,
    "pull_request_title": """
    Generate a pull request title based on the changes made:
    \"{diff}\"
    """,
    "release_body": """
    Generate a release body based on the changes included in this release:
    \"{diff}\"
    """,
    # Add more templates as needed for changelogs, documentation, etc.
}


def generate_content(template_key: str, diff: str) -> str:
    """Generates content based on a specific template.

    This function uses the OpenAI API to generate content based on a given
    template and diff. It formats the template with the provided diff and
    sends a request to the OpenAI API to generate the content.

    Args:
        template_key (str): The key for the template to use.
        diff (str): The diff to include in the generated content.

    Returns:
        str: The generated content.

    Raises:
        ValueError: If the template_key is not found in the templates dictionary.
    """
    # Retrieve the template based on the provided key
    template = templates.get(template_key, "")
    # Raise an error if the template is not found
    if not template:
        raise ValueError(f"Template '{template_key}' not found.")

    # Format the template with the provided diff
    role_user_content = template.format(diff=diff)

    # Send a request to the OpenAI API to generate the content
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": templates["commit_message_system"]},
            {"role": "user", "content": role_user_content},
        ],
        model="gpt-3.5-turbo",
    )

    # Extract the generated content from the API response
    generated_content = response.choices[0].message.content.strip()
    return generated_content


def format_message(message: str, dryrun: bool = False) -> str:
    """Formats a message with line wrapping and sign-off.

    This function formats a given message by wrapping lines to a maximum
    length of 78 characters and appending a sign-off with the user's name
    and email. It also adds an appropriate emoticon prefix based on the
    commit type.

    Args:
        message (str): The message to format.
        dryrun (bool): If True, unstages all files after formatting.

    Returns:
        str: The formatted message.

    Raises:
        ValueError: If the commit message format is incorrect.
    """
    # Retrieve the user's name and email from git configuration
    user_name, user_email = get_git_user_info()

    # Wrap lines to a maximum length of 78 characters
    commit_message = "\n".join(
        # Wrap each line individually
        [
            (
                line
                if len(line) <= 78
                else "\n".join(wrapped_line for wrapped_line in textwrap.wrap(line, 78))
            )
            for line in message.split("\n")
        ]
    )

    try:
        # Split the commit message into type/scope and description
        parts = commit_message.split(":")
        if len(parts) < 2:
            # Raise an error if the commit message format is incorrect
            logger.error(
                "Commit message format is incorrect. Expected format: type(scope): description"
            )
            raise ValueError(
                "Commit message format is incorrect. Expected format: type(scope): description"
            )

        commit_type_scope = parts[0]
        commit_description = parts[1].strip()

        if "(" in commit_type_scope and ")" in commit_type_scope:
            # Extract the commit type and scope
            commit_type, commit_scope = commit_type_scope.split("(")
            commit_scope = commit_scope.rstrip(")")
        else:
            raise ValueError(
                "Commit message must include a scope in the format type(scope): description"
            )

        # Add an appropriate emoticon prefix based on the commit type
        emoticon_prefix = {
            "feat": "✨",
            "fix": "🐛",
            "docs": "📚",
            "style": "💄",
            "refactor": "♻️",
            "perf": "🚀",
            "test": "🚨",
            "build": "🛠️",
            "ci": "⚙️",
            "chore": "🔧",
            "revert": "⏪",
        }.get(commit_type, "")
    except ValueError as e:
        # Log and raise an error if the commit message format is incorrect
        logger.error(f"Commit message format error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

    # Append a sign-off with the user's name and email
    signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
    # Construct the formatted message
    formatted_message = f"{emoticon_prefix} {commit_type}({commit_scope}): {commit_message.split(':', 1)[1].strip()}{signoff}"

    if dryrun:
        # Unstage all files if dryrun is True
        unstage_files()

    return formatted_message
    return formatted_message


def unstage_files():
    """Unstages all staged files.

    This function runs the `git reset HEAD` command to unstage all files
    that have been staged for commit. It logs the success or failure of
    the operation.

    Raises:
        subprocess.CalledProcessError: If the git command fails.
    """
    try:
        # Run the git reset command to unstage all files
        subprocess.run(["git", "reset", "HEAD"], check=True)
        # Log success message
        logger.info("Unstaged all files.")
    except subprocess.CalledProcessError as e:
        # Log and raise an error if the git command fails
        logger.error(f"Failed to unstage files: {e}")
        raise
        raise


def generate_commit_message(diff: str, dryrun: bool = False) -> str:
    """Generates a commit message.

    This function generates a commit message based on the provided diff
    using the OpenAI API. It formats the generated message and handles
    any errors related to the commit message format.

    Args:
        diff (str): The diff to include in the generated commit message.
        dryrun (bool): If True, unstages all files after generating the message.

    Returns:
        str: The formatted commit message.

    Raises:
        ValueError: If the commit message format is incorrect.
    """
    # Generate the commit message content using the OpenAI API
    generated_message = generate_content("commit_message_user", diff)

    try:
        # Format the generated commit message
        formatted_message = format_message(generated_message, dryrun)
    except ValueError as e:
        # Log and handle errors related to the commit message format
        logger.error(f"Error formatting commit message: {e}")

        # Handle the case where the scope is missing by asking for a specific scope
        if "must include a scope" in str(e):
            commit_type, commit_description = generated_message.split(":", 1)
            # Here we would ideally use some logic to determine the most specific scope
            # For now, we will use a placeholder
            commit_scope = "specific-scope"
            generated_message = (
                f"{commit_type}({commit_scope}): {commit_description.strip()}"
            )
            formatted_message = format_message(generated_message, dryrun)
            logger.info(
                message=f"Scope was missing. Please provide a more specific scope such as application name, file name, class name, method/function name, or feature name.",
                status="",
            )

    # Log the generated commit message
    logger.info(message=80 * "-", status="")
    logger.info(
        message=f"Generated commit message:\n\n{formatted_message}\n", status=""
    )
    logger.info(message=80 * "-", status="")

    return formatted_message


def generate_pull_request_title(diff: str, dryrun: bool = False) -> str:
    """Generates a pull request title.

    This function generates a pull request title based on the provided diff
    using the OpenAI API. It formats the generated title and handles any
    errors related to the title format.

    Args:
        diff (str): The diff to include in the generated pull request title.
        dryrun (bool): If True, unstages all files after generating the title.

    Returns:
        str: The formatted pull request title.

    Raises:
        ValueError: If the pull request title format is incorrect.
    """
    # Generate the pull request title content using the OpenAI API
    generated_title = generate_content("pull_request_title", diff)

    # Format the generated pull request title
    formatted_title = format_message(generated_title, dryrun)

    if dryrun:
        # Unstage all files if dryrun is True
        unstage_files()

    # Log the generated pull request title
    logger.info(message=80 * "-", status="")
    logger.info(
        message=f"Generated pull request title:\n\n{formatted_title}\n", status=""
    )
    logger.info(message=80 * "-", status="")

    return formatted_title


def generate_release_body(diff: str, dryrun: bool = False) -> str:
    """Generates a release body.

    This function generates a release body based on the provided diff
    using the OpenAI API. It formats the generated body and handles any
    errors related to the body format.

    Args:
        diff (str): The diff to include in the generated release body.
        dryrun (bool): If True, unstages all files after generating the body.

    Returns:
        str: The formatted release body.

    Raises:
        ValueError: If the release body format is incorrect.
    """
    # Generate the release body content using the OpenAI API
    generated_body = generate_content("release_body", diff)

    # Format the generated release body
    formatted_body = format_message(generated_body, dryrun)

    if dryrun:
        # Unstage all files if dryrun is True
        unstage_files()

    # Log the generated release body
    logger.info(message=80 * "-", status="")
    logger.info(message=f"Generated release body:\n\n{formatted_body}\n", status="")
    logger.info(message=80 * "-", status="")

    return formatted_body
