"""
This module provides tools for generating commit messages, pull request titles,
and release bodies using OpenAI's API.

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
import subprocess
import textwrap

import openai
from openai import OpenAI
from git import Repo

from klingon_tools.git_user_info import get_git_user_info
from klingon_tools.logger import logger
from klingon_tools.git_unstage import git_unstage_files
from klingon_tools.git_log_helper import get_commit_log


class OpenAITools:
    """
    A class that provides tools for generating content using OpenAI's API.

    This class initializes the OpenAI client, stores AI templates, and provides
    methods for generating various types of content such as commit messages,
    pull request titles, and release bodies.
    """

    def __init__(self, debug=False):
        """
        Initialize the OpenAITools instance.

        This method sets up the OpenAI API client and defines the templates
        used for content generation.

        Raises:
            ValueError: If the OpenAI API key is not set in the environment.
        """
        self.debug = debug
        # Initialize OpenAI API client
        if self.debug:
            openai.logging = "debug"
        else:
            openai.logging = "info"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key is missing. Please set the OPENAI_API_KEY "
                "environment variable."
            )
        self.client = OpenAI(api_key=api_key)

        # AI Templates
        self.templates = {
            "commit_message_system": """
            Generate a commit message based solely on the staged diffs
            provided, ensuring accuracy and relevance to the actual changes.
            Avoid speculative or unnecessary footers, such as references to
            non-existent issues.

            Follow the Conventional Commits standard using the following
            format: ``` <type>(scope): <description>

            ```
            Consider the following options when selecting commit types:
            • build: updates to build system & external dependencies
            • chore: changes that don't modify src or test files
            • ci: changes to CI configuration files and scripts
            • docs: updates to documentation & comments
            • feat: add new feature or function to the codebase
            • fix: correct bugs and other errors in code
            • perf: improve performance without changing existing functionality
            • refactor: code changes that neither fix bugs nor add features
            • revert: Reverts a previous commit
            • style: changes that do not affect the meaning of the code
            (white-space, formatting, missing semi-colons, etc) but improve
            readability, consistency, or maintainability
            • test: add, update, correct unit tests
            • other:  Changes that don't fit into the above categories

            Scope: Select the most specific of application name, file name,
            class name, method/function name, or feature name for the commit
            scope. If in doubt, use the name of the file being modified.

            Breaking Changes: Include a `BREAKING CHANGE:` footer or append !
            after type/scope for commits that introduce breaking changes.

            Footers: Breaking change is the only footer permitted. Do not add
            "Co-authored-by" or other footers unless explicitly requested.
            """,
            "commit_message_user": """
            Generate a git commit message based on these diffs: \"{diff}\"
            """,
            "pull_request_title": """
            Look at the conventional commit messages provided and generate a
            pull request title that clearly summarizes the changes included in
            them.

            Keep the summary high level extremely terse and you MUST limit it
            to no more than 72 characters.

            Do not include a type prefix, contributor, commit type or scope in
            the title. \"{diff}\"
            """,
            "pull_request_summary": """
            Look at the conventional commit messages provided and generate a
            concise pull request summary. Keep the summary specific and to the
            point, avoiding unnecessary details.

            Aim to use no more than 2 paragraphs of summary.

            The reader is busy and must be able to read and understand the
            content quickly & without fuss.

            Content should be returned as markdown without headings or font
            styling, bullet points and plain paragraph text are ok. \"{diff}\"
            """,
            "pull_request_context": """
            Look at the conventional commit messages provided and generate a
            concise context statement for the changes in the pull request that
            clearly explains why the changes have been made.

            Use bullet points to list the reasons for the changes, but use as
            few as possible to keep the context concise.

            Content should be returned as markdown without headings or font
            styling, bullet points and plain paragraph text are ok. \"{diff}\"
            """,
            "pull_request_body": """
            Look at the conventional commit messages provided and generate a
            pull request body using the following markdown as a template:
<!-- START OF TEMPLATE --> ## Description <!-- A brief description of the
changes introduced by this PR -->

## Motivation and Context <!-- Why is this change required? What problem does
it solve? -->

## Issue Link <!-- (optional) --> <!-- Link to any related related issues
(optional) -->

## Types of Changes <!-- What types of changes does your code introduce? Put an
`x` in all the boxes that apply and add indented bullet point descriptions for
each change of that type under it --> - [ ] `feat`: ✨ A new feature
    - Change 1
    - Change 2
- [ ] `fix`: 🐛 A bug fix
    - Change 1
    - Change 2
- [ ] `docs`: 📚 Documentation only changes
    - Change 1
    - Change 2
- [ ] `style`: 💄 Changes that do not affect the meaning of the code
  (white-space, formatting, missing semi-colons, etc)
    - Change 1
    - Change 2
- [ ] `refactor`: ♻️ A code change that neither fixes a bug nor adds a feature
    - Change 1
    - Change 2
- [ ] `perf`: 🚀 A code change that improves performance
    - Change 1
    - Change 2
- [ ] `test`: 🚨 Adding missing or correcting existing tests
    - Change 1
    - Change 2
- [ ] `build`: 🛠️ Changes that affect the build system or external
  dependencies (example scopes: gulp, broccoli, npm)
    - Change 1
    - Change 2
- [ ] `ci`: ⚙️ Changes to our CI configuration files and scripts (example
  scopes: Travis, Circle, BrowserStack, SauceLabs)
    - Change 1
    - Change 2
- [ ] `chore`: 🔧 Other changes that don't modify src or test files
    - Change 1
    - Change 2
- [ ] `revert`: ⏪ Reverts a previous commit
    - Change 1
    - Change 2
<!-- END OF TEMPLATE -->
            \"{diff}\"
            """,
            "release_body": """
            Generate a release body based on the changes included in this
            release: \"{diff}\"
            """,
            # Add more templates as needed for changelogs, documentation, etc.
        }

    def generate_content(self, template_key: str, diff: str) -> str:
        """
        Generates content based on a specific template using the OpenAI API.

        Args:
            template_key (str): The key for the template to use.
            diff (str): The diff to include in the generated content.

        Returns:
            str: The generated content.

        Raises:
            ValueError: If the template_key is not found in the templates
            dictionary.
            openai.APIConnectionError: If there's an error connecting to the
            OpenAI API.
        """
        template = self.templates.get(template_key)
        if not template:
            raise ValueError(f"Template '{template_key}' not found.")

        max_diff_length = 10000  # Adjust this value as needed
        truncated_diff = diff[:max_diff_length]

        role_user_content = template.format(diff=truncated_diff)

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self.templates["commit_message_system"],
                    },
                    {"role": "user", "content": role_user_content},
                ],
                model="gpt-4o-mini",
            )
        except openai.APIConnectionError as e:
            logger.error(f"Failed to connect to OpenAI API: {e}")
            raise

        generated_content = response.choices[0].message.content.strip()
        return generated_content.replace("```", "").strip()

    def format_message(self, message: str) -> str:
        """
        Formats a message with line wrapping and adds an appropriate emoticon
        prefix.

        Args:
            message (str): The message to format.

        Returns:
            str: The formatted message.

        Raises:
            ValueError: If the commit message format is incorrect.
        """
        commit_message = "\n".join(
            line if len(line) <= 78 else "\n".join(textwrap.wrap(line, 78))
            for line in message.split("\n")
        )

        try:
            parts = commit_message.split(":")
            if len(parts) < 2:
                raise ValueError(
                    "Commit message format is incorrect. Expected format: "
                    "type(scope): description"
                )

            commit_type_scope = parts[0]

            if "(" in commit_type_scope and ")" in commit_type_scope:
                commit_type, commit_scope = commit_type_scope.split("(")
                commit_scope = commit_scope.rstrip(")")
            else:
                raise ValueError(
                    "Commit message must include a scope in the format "
                    "type(scope): description"
                )

            emoticon_prefix = {
                "build": "🛠️",
                "chore": "🔧",
                "ci": "⚙️",
                "docs": "📚",
                "feat": "✨",
                "fix": "🐛",
                "perf": "🚀",
                "refactor": "♻️",
                "revert": "⏪",
                "style": "💄",
                "test": "🚨",
                "other": "⚠️",
            }.get(commit_type, "")
        except ValueError as e:
            logger.error(f"Commit message format error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

        formatted_message = (
            f"{emoticon_prefix} {commit_type}({commit_scope}): "
            f"{commit_message.split(':', 1)[1].strip()}"
        )

        return formatted_message

    def format_pr_title(self, title: str) -> str:
        """
        Formats a pull request title.

        This function ensures the title is a single line and does not exceed 72
        characters.

        Args:
            title (str): The title to format.

        Returns:
            str: The formatted title.
        """
        formatted_title = " ".join(title.split())
        if len(formatted_title) > 72:
            formatted_title = formatted_title[:72] + "..."
        return formatted_title

    def signoff_message(self, message: str) -> str:
        """
        Appends a sign-off to the message with the user's name and email.

        Args:
            message (str): The message to append the sign-off to.

        Returns:
            str: The message with the appended sign-off.
        """
        user_name, user_email = get_git_user_info()
        signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
        return f"{message}{signoff}"

    def generate_commit_message(self, diff: str, dryrun: bool = False) -> str:
        """
        Generates a commit message based on the provided diff.

        This function handles both regular changes and file deletions.

        Args:
            diff (str): The diff to include in the generated commit message.
            dryrun (bool): If True, unstages all files after generating the
            message.

        Returns:
            str: The formatted commit message.

        Raises:
            ValueError: If the commit message format is incorrect.
            subprocess.CalledProcessError: If a Git command fails.
        """
        deleted_files = subprocess.run(
            ["git", "ls-files", "--deleted"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()

        if deleted_files:
            for file in deleted_files:
                try:
                    file_diff = subprocess.run(
                        ["git", "diff", file],
                        capture_output=True,
                        text=True,
                        check=True,
                    ).stdout
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to get diff for {file}: {e}")
                    continue

                generated_message = self.generate_content(
                    "commit_message_user", file_diff
                )

                try:
                    formatted_message = self.format_message(generated_message)
                    formatted_message = self.signoff_message(formatted_message)
                except ValueError as e:
                    logger.error(f"Error formatting commit message: {e}")
                    if "must include a scope" in str(e):
                        commit_type, commit_description = (
                            generated_message.split(":", 1)
                        )
                        commit_scope = "specific-scope"
                        generated_message = f"{commit_type}({commit_scope}): \
                            {commit_description.strip()}"
                        formatted_message = self.format_message(
                            generated_message
                        )
                        formatted_message = self.signoff_message(
                            formatted_message
                        )
                        logger.error(
                            "Scope was missing. Please provide a more "
                            "specific scope."
                        )

                logger.info(
                    message="=" * 80,
                    status="",
                )
                logger.info(
                    f"Generated commit message for {file}:\n\n"
                    f"{formatted_message}\n"
                )
                logger.info(
                    message="=" * 80,
                    status="",
                )

                subprocess.run(
                    ["git", "commit", "-m", formatted_message, file],
                    check=True,
                )

        try:
            generated_message = self.generate_content(
                "commit_message_user", diff
            )
            formatted_message = self.format_message(generated_message)
            formatted_message = self.signoff_message(formatted_message)

            logger.info(
                message="=" * 80,
                status="",
            )
            logger.info(
                message=f"Generated commit message:\n\n{formatted_message}\n",
                status="",
            )
            logger.info(
                message="=" * 80,
                status="",
            )

            return formatted_message

        except ValueError as e:
            logger.error(f"Error formatting commit message: {e}")
            if "must include a scope" in str(e):
                commit_type, commit_description = generated_message.split(
                    ":", 1
                )
                commit_scope = "specific-scope"  # Placeholder
                generated_message = f"{commit_type}({commit_scope}): \
                    {commit_description.strip()}"
                formatted_message = self.format_message(generated_message)
                formatted_message = self.signoff_message(formatted_message)
                logger.error(
                    "Scope was missing. Please provide a more specific scope."
                )

                logger.info(
                    message="=" * 80,
                    status="",
                )
                logger.info(
                    message=f"Generated commit message:\n\n"
                    f"{formatted_message}\n",
                    status="",
                )
                logger.info(
                    message="=" * 80,
                    status="",
                )

                return formatted_message

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def generate_pull_request_title(self, diff: str) -> str:
        """
        Generates a pull request title from the provided diff.

        Args:
            diff (str): The diff to include in the generated pull request
            title.

        Returns:
            str: The formatted pull request title.
        """
        generated_title = self.generate_content("pull_request_title", diff)
        formatted_title = self.format_pr_title(generated_title)
        return formatted_title

    def generate_pull_request_summary(
        self, diff: str, dryrun: bool = False
    ) -> str:
        """
        Generates a pull request summary from the git log differences between
        current branch and origin/release..HEAD.

        Args:
            diff (str): The diff to include in the generated pull request
            summary.
            dryrun (bool): If True, unstages all files after generating the
            summary.

        Returns:
            str: The formatted pull request summary.
        """
        try:
            commits = get_commit_log("origin/release").stdout
            generated_summary = self.generate_content(
                "pull_request_summary", commits
            )

            return generated_summary
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting commit log: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating PR summary: {e}")
            raise

    def generate_pull_request_context(
        self, diff: str, dryrun: bool = False
    ) -> str:
        """
        Generates a pull request context from the git log differences between
        current branch and origin/release..HEAD.

        Args:
            diff (str): The diff to include in the generated pull request
            context.
            dryrun (bool): If True, unstages all files after generating the
            context.

        Returns:
            str: The formatted pull request context.
        """
        try:
            commits = get_commit_log("origin/release").stdout
            generated_context = self.generate_content(
                "pull_request_context", commits
            )

            return generated_context
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting commit log: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating PR context: {e}")
            raise

    def generate_pull_request_body(self, diff: str) -> str:
        """
        Generates a pull request body from the provided diff.

        Args:
            diff (str): The diff to include in the generated pull request body.

        Returns:
            str: The formatted pull request body.
        """
        generated_body = self.generate_content("pull_request_body", diff)
        return generated_body

    def generate_release_body(
        self, repo: Repo, diff: str, dryrun: bool = False
    ) -> str:
        """
        Generates a release body based on the provided diff.

        Args:
            diff (str): The diff to include in the generated release body.
            dryrun (bool): If True, unstages all files after generating the
            body.

        Returns:
            str: The formatted release body.
        """
        generated_body = self.generate_content("release_body", diff)
        formatted_body = self.format_message(generated_body)

        if dryrun:
            git_unstage_files(
                repo, repo.git.diff("--cached", "--name-only").splitlines()
            )

        logger.info(
            message="=" * 80,
            status="",
        )
        logger.info(
            message=f"Generated release body:\n\n{formatted_body}\n",
            status="",
        )
        logger.info(
            message="=" * 80,
            status="",
        )

        return formatted_body
