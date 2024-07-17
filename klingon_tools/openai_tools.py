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

from klingon_tools.git_user_info import get_git_user_info
from klingon_tools.logger import logger
from klingon_tools.git_log_helper import get_commit_log


class OpenAITools:
    def __init__(self):
        # Initialize OpenAI API client
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

            Consider the following when selecting commit types:
                build: Changes that affect the build system or external
                dependencies chore: Other changes that don't modify src or test
                files ci: Changes to CI configuration files and scripts docs:
                Documentation changes feat: New features fix: Bug fixes perf:
                Code changes that improve performance refactor: Code changes
                that neither fix bugs nor add features revert: Reverts a
                previous commit style: Changes that do not affect the meaning
                of the code (white-space, formatting, missing semi-colons, etc)
                test: Adding missing or correcting existing tests other:
                Changes that don't fit into the above categories

            Scope: Select the most specific of application name, file name,
            class name, method/function name, or feature name for the commit
            scope. If in doubt, use the name of the file being modified.
            Breaking Changes: Include a BREAKING CHANGE: footer or append !
            after type/scope for commits that introduce breaking API changes.
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
        """Generates content based on a specific template.

        This function uses the OpenAI API to generate content based on a given
        template and diff. It formats the template with the provided diff and
        sends a request to the OpenAI API to generate the content.

        Args:
            template_key (str): The key for the template to use. diff (str):
            The diff to include in the generated content.

        Returns:
            str: The generated content.

        Raises:
            ValueError: If the template_key is not found in the templates
            dictionary.
        """
        # Retrieve the template based on the provided key
        template = self.templates.get(template_key, "")
        # Raise an error if the template is not found
        if not template:
            raise ValueError(f"Template '{template_key}' not found.")

        # Truncate the diff if it exceeds a certain length
        max_diff_length = 10000  # Adjust this value as needed
        truncated_diff = (
            diff if len(diff) <= max_diff_length else diff[:max_diff_length]
        )

        # Format the template with the truncated diff
        role_user_content = template.format(diff=truncated_diff)

        # Send a request to the OpenAI API to generate the content
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self.templates["commit_message_system"],
                    },
                    {"role": "user", "content": role_user_content},
                ],
                model="gpt-3.5-turbo",
            )
        except openai.APIConnectionError as e:
            logger.error(f"Failed to connect to OpenAI API: {e}")
            raise

        # Extract the generated content from the API response
        generated_content = response.choices[0].message.content.strip()
        # Remove any backticks from the generated content
        return generated_content.replace("```", "").strip()

    def format_message(self, message: str) -> str:
        """Formats a message with line wrapping.

        This function formats a given message by wrapping lines to a maximum
        length of 78 characters. It also adds an appropriate emoticon prefix
        based on the commit type.

        Args:
            message (str): The message to format. dryrun (bool): If True,
            unstages all files after formatting.

        Returns:
            str: The formatted message.

        Raises:
            ValueError: If the commit message format is incorrect.
        """

        # Wrap lines to a maximum length of 78 characters
        commit_message = "\n".join(
            # Wrap each line individually
            [
                (
                    line
                    if len(line) <= 78
                    else "\n".join(
                        wrapped_line
                        for wrapped_line in textwrap.wrap(line, 78)
                    )
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
                    "Commit message format is incorrect. Expected format: "
                    "type(scope): description"
                )
                raise ValueError(
                    "Commit message format is incorrect. Expected format: "
                    "type(scope): description"
                )

            # Extract the commit type and scope
            commit_type_scope = parts[0]

            # Check if the commit message includes a scope
            if "(" in commit_type_scope and ")" in commit_type_scope:
                # Extract the commit type and scope
                commit_type, commit_scope = commit_type_scope.split("(")
                # Remove the closing parenthesis from the scope
                commit_scope = commit_scope.rstrip(")")
            else:
                raise ValueError(
                    "Commit message must include a scope in the format "
                    "type(scope): description"
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

        # Construct the formatted message
        formatted_message = (
            f"{emoticon_prefix} {commit_type}({commit_scope}):"
            f"{commit_message.split(':', 1)[1].strip()}"
        )

        return formatted_message

    def format_pr_title(self, title: str) -> str:
        """Formats a pull request title.

        This function formats a given pull request title by ensuring it is a
        single line and does not exceed 72 characters.

        Args:
            title (str): The title to format.

        Returns:
            str: The formatted title.
        """
        # Ensure the title is a single line and does not exceed 72 characters
        formatted_title = " ".join(title.split())
        if len(formatted_title) > 72:
            formatted_title = formatted_title[:69] + "..."
        return formatted_title

    def signoff_message(self, message: str) -> str:
        """
        Appends a sign-off to the message with the user's name and email.

        This function appends a sign-off to the given message with the user's
        name and email retrieved from git configuration.

        Args:
            message (str): The message to append the sign-off to.

        Returns:
            str: The message with the appended sign-off.
        """
        # Retrieve the user's name and email from git configuration
        user_name, user_email = get_git_user_info()

        # Append a sign-off with the user's name and email
        signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
        return f"{message}{signoff}"

    def generate_commit_message(self, diff: str, dryrun: bool = False) -> str:
        """Generates a commit message.

        This function generates a commit message based on the provided diff
        using the OpenAI API. It formats the generated message and handles any
        errors related to the commit message format.

        Args:
            diff (str): The diff to include in the generated commit message.
            dryrun (bool): If True, unstages all files after generating the
            message.

        Returns:
            str: The formatted commit message.

        Raises:
            ValueError: If the commit message format is incorrect.
        """
        # Check for deleted files
        deleted_files = subprocess.run(
            ["git", "ls-files", "--deleted"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()

        if deleted_files:
            for file in deleted_files:
                # Generate the commit message content for each deleted file
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
                    # Format the generated commit message
                    formatted_message = self.format_message(generated_message)
                    formatted_message = self.signoff_message(formatted_message)
                except ValueError as e:
                    # Log and handle errors related to the commit message
                    # format
                    logger.error(f"Error formatting commit message: {e}")

                    # Handle the case where the scope is missing by asking for
                    # a specific scope
                    if "must include a scope" in str(e):
                        commit_type, commit_description = (
                            generated_message.split(":", 1)
                        )
                        # Here we would ideally use some logic to determine the
                        # most specific scope For now, we will use a
                        # placeholder
                        commit_scope = "specific-scope"
                        generated_message = (
                            f"{commit_type}({commit_scope}): "
                            f"{commit_description.strip()}"
                        )
                        formatted_message = self.format_message(
                            generated_message
                        )
                        formatted_message = self.signoff_message(
                            formatted_message
                        )
                        logger.info(
                            message="Scope was missing. Please provide a more"
                            "specific scope such as application name, file "
                            "name, class name, method/function name, or "
                            "feature name.",
                            status="",
                        )

                # Log the generated commit message
                logger.info(message=80 * "-", status="")
                logger.info(
                    message="Generated commit message for "
                    f"{file}:\n\n{formatted_message}\n",
                    status="",
                )
                logger.info(message=80 * "-", status="")

                # Commit the deletion with the formatted message
                subprocess.run(
                    ["git", "commit", "-m", formatted_message, file],
                    check=True,
                )

        try:
            # Generate the commit message content using the OpenAI API
            generated_message = self.generate_content(
                "commit_message_user", diff
            )

            # Format the generated commit message
            formatted_message = self.format_message(generated_message)
            formatted_message = self.signoff_message(formatted_message)

            # Log the generated commit message
            logger.info(message=80 * "-", status="")
            logger.info(
                message=f"Generated commit message:\n\n{formatted_message}\n",
                status="",
            )
            logger.info(message=80 * "-", status="")

            return formatted_message

        except ValueError as e:
            # Log and handle errors related to the commit message format
            logger.error(f"Error formatting commit message: {e}")

            # Handle the case where the scope is missing by asking for a
            # specific scope
            if "must include a scope" in str(e):
                commit_type, commit_description = generated_message.split(
                    ":", 1
                )
                # Here we would ideally use some logic to determine the most
                # specific scope For now, we will use a placeholder
                commit_scope = "specific-scope"
                generated_message = f"{commit_type}({commit_scope}): "
                f"{commit_description.strip()}"
                formatted_message = self.format_message(generated_message)
                formatted_message = self.signoff_message(formatted_message)
                logger.info(
                    message="Scope was missing. Please provide a more "
                    "specific scope such as application name, file name, "
                    "class name, method/function name, or feature name.",
                    status="",
                )

                # Log the generated commit message
                logger.info(message=80 * "-", status="")
                logger.info(
                    message="Generated commit message:\n\n"
                    f"{formatted_message}\n",
                    status="",
                )
                logger.info(message=80 * "-", status="")

                return formatted_message

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def generate_pull_request_title(
        self, diff: str, dryrun: bool = False
    ) -> str:
        """
        Generates a pull request title from the git log differences between
        current branch and origin/release..HEAD.

        This function generates a pull request title based on the provided
        commit messages using the OpenAI API. It formats the generated title
        and handles any errors related to the title format.

        Entrypoint: pr-title-generate

        Args:
            diff (str): The diff to include in the generated pull request
            title. dryrun (bool): If True, unstages all files after generating
            the title.

        Returns:
            str: The formatted pull request title.

        Raises:
            ValueError: If the pull request title format is incorrect.
        """

        # Get the commit details including author
        commit_details = subprocess.run(
            [
                "git",
                "--no-pager",
                "log",
                "origin/release..HEAD",
                "--pretty=format:%s by @%an",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()

        # Save the commit details to a single variable
        commits = "\n".join(commit_details)

        # Generate the pull request title content using the OpenAI API
        generated_title = self.generate_content("pull_request_title", commits)

        # Format the generated pull request title
        formatted_title = self.format_pr_title(generated_title)

        if dryrun:
            # Unstage all files if dryrun is True
            self.unstage_files()

        return formatted_title

    def generate_pull_request_summary(
        self, diff: str, dryrun: bool = False
    ) -> str:
        """
        Generates a pull request summary from the git log differences between
        current branch and origin/release..HEAD.

        This function generates a pull request summary based on the provided
        git commit messages using the OpenAI API. It formats the generated
        summary and handles any errors related to the summary format.

        Entrypoint: pr-summary-generate

        Args:
            diff (str): The diff to include in the generated pull request
            summary. dryrun (bool): If True, unstages all files after
            generating the summary.

        Returns:
            str: The formatted pull request summary.

        Raises:
            ValueError: If the pull request summary format is incorrect.
        """
        commits = get_commit_log("origin/release").stdout

        # Generate the pull request summary content using the OpenAI API
        generated_summary = self.generate_content(
            "pull_request_summary", commits
        )

        return generated_summary

    def generate_pull_request_context(
        self, diff: str, dryrun: bool = False
    ) -> str:
        """
        Generates a pull request context from the git log differences between
        current branch and origin/release..HEAD.

        This function generates a pull request context based on the provided
        git commit messages using the OpenAI API. It formats the generated
        context and handles any errors related to the context format.

        Entrypoint: pr-context-generate

        Args:
            diff (str): The diff to include in the generated pull request
            context. dryrun (bool): If True, unstages all files after
            generating the context.

        Returns:
            str: The formatted pull request context.

        Raises:
            ValueError: If the pull request context format is incorrect.
        """
        commits = get_commit_log("origin/release").stdout

        # Generate the pull request context content using the OpenAI API
        generated_context = self.generate_content(
            "pull_request_context", commits
        )

        return generated_context

    def generate_pull_request_body(
        self, diff: str, dryrun: bool = False
    ) -> str:
        """
        Generates a pull request body from the git log differences between
        current branch and origin/release..HEAD.

        This function generates a pull request body based on the provided git
        messages using the OpenAI API. It formats the generated body and
        handles any errors related to the body format.

        Entrypoint: pr-body-generate

        Args:
            diff (str): The diff to include in the generated pull request body.
            dryrun (bool): If True, unstages all files after generating the
            body.

        Returns:
            str: The formatted pull request body.

        Raises:
            ValueError: If the pull request body format is incorrect.
        """
        commit_result = get_commit_log("origin/release")

        # Save the commits to a single variable
        commits = commit_result.stdout

        # Generate the pull request body content using the OpenAI API
        generated_body = self.generate_content("pull_request_body", commits)

        return generated_body

    def unstage_files(self):
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

    def generate_release_body(self, diff: str, dryrun: bool = False) -> str:
        """
        Generates a release body.

        This function generates a release body based on the provided diff using
        the OpenAI API. It formats the generated body and handles any errors
        related to the body format.

        Args:
            diff (str): The diff to include in the generated release body.
            dryrun (bool): If True, unstages all files after generating the
            body.

        Returns:
            str: The formatted release body.

        Raises:
            ValueError: If the release body format is incorrect.
        """
        # Generate the release body content using the OpenAI API
        generated_body = self.generate_content("release_body", diff)

        # Format the generated release body
        formatted_body = self.format_message(generated_body)

        if dryrun:
            # Unstage all files if dryrun is True
            self.unstage_files()

        # Log the generated release body
        logger.info(message=80 * "-", status="")
        logger.info(
            message=f"Generated release body:\n\n{formatted_body}\n", status=""
        )
        logger.info(message=80 * "-", status="")

        return formatted_body
