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
    """Generate content based on a specific template."""
    template = templates.get(template_key, "")
    if not template:
        raise ValueError(f"Template '{template_key}' not found.")

    role_user_content = template.format(diff=diff)

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": templates["commit_message_system"]},
            {"role": "user", "content": role_user_content},
        ],
        model="gpt-3.5-turbo",
    )

    generated_content = response.choices[0].message.content.strip()
    return generated_content


def format_message(message: str, dryrun: bool = False) -> str:
    """Format message with line wrapping and sign-off."""
    user_name, user_email = get_git_user_info()
    commit_message = "\n".join(
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
        parts = commit_message.split(":")
        if len(parts) < 2:
            logger.error(
                "Commit message format is incorrect. Expected format: type(scope): description"
            )
            raise ValueError(
                "Commit message format is incorrect. Expected format: type(scope): description"
            )

        commit_type_scope = parts[0]
        commit_description = parts[1].strip()

        if "(" in commit_type_scope and ")" in commit_type_scope:
            commit_type, commit_scope = commit_type_scope.split("(")
            commit_scope = commit_scope.rstrip(")")
        else:
            raise ValueError(
                "Commit message must include a scope in the format type(scope): description"
            )

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
        logger.error(f"Commit message format error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

    signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
    formatted_message = f"{emoticon_prefix} {commit_type}({commit_scope}): {commit_message.split(':', 1)[1].strip()}{signoff}"

    if dryrun:
        unstage_files()

    if dryrun:
        unstage_files()
    return formatted_message


def unstage_files():
    """Unstage all staged files."""
    try:
        subprocess.run(["git", "reset", "HEAD"], check=True)
        logger.info("Unstaged all files.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to unstage files: {e}")
        raise


def generate_commit_message(diff: str, dryrun: bool = False) -> str:
    """Generate a commit message."""
    generated_message = generate_content("commit_message_user", diff)
    try:
        formatted_message = format_message(generated_message, dryrun)
    except ValueError as e:
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

    logger.info(message=80 * "-", status="")
    logger.info(
        message=f"Generated commit message:\n\n{formatted_message}\n", status=""
    )
    logger.info(message=80 * "-", status="")

    return formatted_message


def generate_pull_request_title(diff: str, dryrun: bool = False) -> str:
    """Generate a pull request title."""
    generated_title = generate_content("pull_request_title", diff)
    formatted_title = format_message(generated_title, dryrun)

    if dryrun:
        unstage_files()

    logger.info(message=80 * "-", status="")
    logger.info(
        message=f"Generated pull request title:\n\n{formatted_title}\n", status=""
    )
    logger.info(message=80 * "-", status="")

    return formatted_title


def generate_release_body(diff: str, dryrun: bool = False) -> str:
    """Generate a release body."""
    generated_body = generate_content("release_body", diff)
    formatted_body = format_message(generated_body, dryrun)

    if dryrun:
        unstage_files()

    logger.info(message=80 * "-", status="")
    logger.info(message=f"Generated release body:\n\n{formatted_body}\n", status="")
    logger.info(message=80 * "-", status="")

    return formatted_body
