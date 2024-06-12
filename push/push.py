#!/usr/bin/env python3
import os
import subprocess
import sys
import json
import time
import shutil


# Define color variables
class Colors:
    RED = "\033[0;31m"
    BOLD_RED = "\033[1;31m"
    GREEN = "\033[0;32m"
    GREEN_BOLD = "\033[1;32m"
    YELLOW = "\033[1;33m"
    BOLD_YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    BOLD_BLUE = "\033[1;34m"
    ORANGE = "\033[0;33m"
    BOLD_ORANGE = "\033[1;33m"
    NC = "\033[0m"  # No Color
    WHITE_BOLD = "\033[1;37m"
    PRE_COMMIT_OK = "\033[42m\033[34m"  # Green background with blue text
    PRE_COMMIT_ERROR = "\033[41m\033[97m"  # Red background with white text
    PRE_COMMIT_WARN = "\033[43m\033[30m"  # Yellow background with black text
    PRE_COMMIT_INFO = "\033[46m\033[30m"  # Cyan background with black text


# Define width for output
WIDTH = 80

# Set argument
MESSAGE = " ".join(sys.argv[1:])

# Get root directory of git repo
ROOT_DIR = (
    subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()
)

TEMPLATE_FILE = os.path.join(ROOT_DIR, "scripts", ".pushrc_template")
PUSH_CONFIG_FILE = os.path.join(ROOT_DIR, ".pushrc")

if not os.path.exists(PUSH_CONFIG_FILE):
    shutil.copy(TEMPLATE_FILE, PUSH_CONFIG_FILE)


# Check if required environment variables are set
def check_environment_variables():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print(f"{Colors.RED}OPENAI_API_KEY environment variable is not set{Colors.NC}")
        sys.exit(1)


# Generate a commit message using the OpenAI API
def generate_commit_message():
    commit_message = ""
    attempt = 1
    max_attempts = 5

    while not commit_message and attempt < max_attempts:
        if attempt > 1:
            print(f"Waiting {2 ** (attempt - 1)} seconds before retrying...")
            time.sleep(2 ** (attempt - 1))
        attempt += 1

        staged_diffs = subprocess.run(
            ["git", "--no-pager", "diff", "--staged", "--patch-with-stat"],
            capture_output=True,
            text=True,
        ).stdout.strip()

        if not staged_diffs:
            print(f"No staged changes to generate commit message for.")
            return None

        role_system_content = "Generate a commit message based solely on the staged diffs provided, ensuring accuracy and relevance to the actual changes. Avoid adding speculative or unnecessary footers, such as references to non-existent issues. You must adhere to the conventional commits standard. The commit message should:\n\n- Clearly specify the type of change (feat, fix, build, etc.).\n- Clearly specify the scope of change.\n- Describe the purpose and actual detail of the change with clarity.\n- Use bullet points for the body when more than one item is discussed.\n- You MUST follow the Conventional Commits standardized format:\n\n    <type>(<scope>): <description>\n    [optional body]\n    [optional footer/breaking changes]\n\n\n    Types include: feat, fix, build, ci, docs, style, refactor, perf, test, chore, etc.\n    Ensure the message is factual, based on the provided diffs, and free from any speculative or unnecessary content."

        role_user_content = (
            f'Generate a git commit message based on these diffs:\n"{staged_diffs}"'
        )

        response = subprocess.run(
            [
                "curl",
                "-s",
                "-X",
                "POST",
                "https://api.openai.com/v1/chat/completions",
                "-H",
                "Content-Type: application/json",
                "-H",
                f"Authorization: Bearer {os.getenv('OPENAI_API_KEY')}",
                "-d",
                json.dumps(
                    {
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": role_system_content},
                            {"role": "user", "content": role_user_content},
                        ],
                    }
                ),
            ],
            capture_output=True,
            text=True,
        )

        if response.returncode != 0:
            print(
                f"Failed to generate commit message. Attempt {attempt} of {max_attempts}."
            )
            continue

        commit_message = (
            json.loads(response.stdout)
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        if not commit_message:
            print(
                f"Failed to generate commit message. Attempt {attempt} of {max_attempts}."
            )

    if not commit_message:
        print(
            f"{Colors.RED}Failed to generate commit message after {max_attempts} attempts. Please check your internet connection and try again.{Colors.NC}"
        )
        sys.exit(1)

    return commit_message.strip() if commit_message else None


# Main function
def main():
    check_environment_variables()

    commit_message = generate_commit_message()
    print(f"Generated commit message:\n\n{commit_message}")

    if commit_message:
        print("\nPushing changes...")
        subprocess.run(["git", "commit", "-m", commit_message])
        subprocess.run(["git", "push"])
    else:
        print(
            f"{Colors.RED}No commit message generated. Exiting without committing.{Colors.NC}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
