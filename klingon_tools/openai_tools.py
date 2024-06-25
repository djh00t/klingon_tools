import os
import textwrap
from openai import OpenAI
from klingon_tools.git_user_info import get_git_user_info
from klingon_tools.logger import logger

# Initialize OpenAI API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# AI Templates
templates = {
    "commit_message_system": """
    Generate a commit message based solely on the staged diffs provided, ensuring accuracy and relevance to the actual changes.
    Avoid speculative or unnecessary footers, such as references to non-existent issues. Follow the Conventional Commits standard
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


def format_message(message: str) -> str:
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

    commit_type = commit_message.split(":")[0].split("(")[0]
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

    signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
    if "(" not in commit_message.split(":")[0]:
        commit_message = commit_message.replace(commit_type, f"{commit_type}(scope)")

    formatted_message = f"{emoticon_prefix} {commit_message}{signoff}"

    return formatted_message


def generate_commit_message(diff: str) -> str:
    """Generate a commit message."""
    generated_message = generate_content("commit_message_user", diff)
    formatted_message = format_message(generated_message)

    logger.info(message=80 * "-", status="")
    logger.info(
        message=f"Generated commit message:\n\n{formatted_message}\n", status=""
    )
    logger.info(message=80 * "-", status="")

    return formatted_message


def generate_pull_request_title(diff: str) -> str:
    """Generate a pull request title."""
    generated_title = generate_content("pull_request_title", diff)
    formatted_title = format_message(generated_title)

    logger.info(message=80 * "-", status="")
    logger.info(
        message=f"Generated pull request title:\n\n{formatted_title}\n", status=""
    )
    logger.info(message=80 * "-", status="")

    return formatted_title


def generate_release_body(diff: str) -> str:
    """Generate a release body."""
    generated_body = generate_content("release_body", diff)
    formatted_body = format_message(generated_body)

    logger.info(message=80 * "-", status="")
    logger.info(message=f"Generated release body:\n\n{formatted_body}\n", status="")
    logger.info(message=80 * "-", status="")

    return formatted_body
