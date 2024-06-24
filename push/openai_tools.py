import os
import textwrap
from openai import OpenAI
from push.logger import logger

# Initialize OpenAI API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# AI Templates
push_role_system_content = """
Generate a commit message based solely on the staged diffs provided, ensuring accuracy and relevance to the actual changes.
Avoid speculative or unnecessary footers, such as references to non-existent issues. Follow the Conventional Commits standard.
"""

push_role_user_content_template = """
Generate a git commit message based on these diffs:
\"{diff}\"
"""


def generate_commit_message(diff: str) -> str:
    """Generates a commit message using OpenAI API based on the provided diff."""
    role_user_content = push_role_user_content_template.format(diff=diff)

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": push_role_system_content},
            {"role": "user", "content": role_user_content},
        ],
        model="gpt-3.5-turbo",
    )

    commit_message = response.choices[0].message.content.strip()
    commit_message = "\n".join(
        [
            (
                " " + line
                if len(line) <= 78
                else "\n".join(
                    " " + wrapped_line for wrapped_line in textwrap.wrap(line, 78)
                )
            )
            for line in commit_message.split("\n")
        ]
    )

    logger.info(message=80 * "-", status="")
    logger.info(message=f"Generated commit message:\n\n{commit_message}\n", status="")
    logger.info(message=80 * "-", status="")

    return commit_message