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


class OpenAITools:
    def __init__(self):
        # Initialize OpenAI API client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # AI Templates
        self.templates = {
            "commit_message_system": """
            Generate a commit message based solely on the staged diffs provided, ensuring accuracy and relevance to the actual changes. Avoid speculative or unnecessary footers, such as references to non-existent issues.

            Follow the Conventional Commits standard using the following format:
            ```
            <type>(scope): <description>

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
            Look at the conventional commit messages provided and generate a
            pull request title that clearly summarizes the changes included in
            them. Keep the summary high level extremely terse and limit it to
            72 characters. You do not need to include the commit type or scope
            in the title.
            \"{diff}\"
            """,
            "release_body": """
            Generate a release body based on the changes included in this release:
            \"{diff}\"
            """,
            # Add more templates as needed for changelogs, documentation, etc.
        }

    def generate_content(self, template_key: str, diff: str) -> str:
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
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.templates["commit_message_system"]},
                {"role": "user", "content": role_user_content},
            ],
            model="gpt-3.5-turbo",
        )

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
            message (str): The message to format.
            dryrun (bool): If True, unstages all files after formatting.

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
                        wrapped_line for wrapped_line in textwrap.wrap(line, 78)
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
                # Remove the closing parenthesis from the scope
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

        # Construct the formatted message
        formatted_message = f"{emoticon_prefix} {commit_type}({commit_scope}): {commit_message.split(':', 1)[1].strip()}"

        return formatted_message

    def format_pr_title(self, title: str) -> str:
        """Formats a pull request title.

        This function formats a given pull request title by ensuring it is a single line
        and does not exceed 72 characters.

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
        """Appends a sign-off to the message with the user's name and email.

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
                    # Log and handle errors related to the commit message format
                    logger.error(f"Error formatting commit message: {e}")

                    # Handle the case where the scope is missing by asking for a specific scope
                    if "must include a scope" in str(e):
                        commit_type, commit_description = generated_message.split(
                            ":", 1
                        )
                        # Here we would ideally use some logic to determine the most specific scope
                        # For now, we will use a placeholder
                        commit_scope = "specific-scope"
                        generated_message = f"{commit_type}({commit_scope}): {commit_description.strip()}"
                        formatted_message = self.format_message(generated_message)
                        formatted_message = self.signoff_message(formatted_message)
                        logger.info(
                            message=f"Scope was missing. Please provide a more specific scope such as application name, file name, class name, method/function name, or feature name.",
                            status="",
                        )

                # Log the generated commit message
                logger.info(message=80 * "-", status="")
                logger.info(
                    message=f"Generated commit message for {file}:\n\n{formatted_message}\n",
                    status="",
                )
                logger.info(message=80 * "-", status="")

                # Commit the deletion with the formatted message
                subprocess.run(
                    ["git", "commit", "-m", formatted_message, file], check=True
                )

        # Generate the commit message content using the OpenAI API
        generated_message = self.generate_content("commit_message_user", diff)

        try:
            # Format the generated commit message
            formatted_message = self.format_message(generated_message)
            formatted_message = self.signoff_message(formatted_message)
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
                formatted_message = self.format_message(generated_message)
                formatted_message = self.signoff_message(formatted_message)
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

    def generate_pull_request_title(self, diff: str, dryrun: bool = False) -> str:
        """Generates a pull request title from the git log differences between
        current branch and origin/main..HEAD.

        This function generates a pull request title based on the provided
        commit messages using the OpenAI API. It formats the generated title
        and handles any errors related to the title format.

        Entrypoint: pr-title-generate

        Args:
            diff (str): The diff to include in the generated pull request title.
            dryrun (bool): If True, unstages all files after generating the title.

        Returns:
            str: The formatted pull request title.

        Raises:
            ValueError: If the pull request title format is incorrect.
        """
        # Check if the origin/main branch exists
        branch_exists = (
            subprocess.run(
                ["git", "rev-parse", "--verify", "origin/main"],
                capture_output=True,
                text=True,
            ).returncode
            == 0
        )

        if branch_exists:
            # Get a log of all changes that this PR is ahead of main by.
            commit_result = subprocess.run(
                ["git", "--no-pager", "log", "origin/main..HEAD", "--pretty=format:%s"],
                capture_output=True,
                text=True,
                check=True,
            )
        else:
            logger.warning("The branch 'origin/main' does not exist.")
            commit_result = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=""
            )

        # Split the result by lines to get individual commit messages
        commits_ahead = commit_result.stdout.splitlines()

        # Save the commits to a single variable
        commits = ""
        for commit in commits_ahead:
            commits += commit + "\n"

        # Generate the pull request title content using the OpenAI API
        generated_title = self.generate_content("pull_request_title", commits)

        # Format the generated pull request title
        formatted_title = self.format_pr_title(generated_title)

        if dryrun:
            # Unstage all files if dryrun is True
            self.unstage_files()

        return formatted_title

    def generate_pull_request_body(self, diff: str, dryrun: bool = False) -> str:
        """Generates a pull request body from the git log differences between
        current branch and origin/main..HEAD.

        This function generates a pull request body based on the provided git
        messages using the OpenAI API. It formats the generated title and
        handles any errors related to the title format.

        Entrypoint: pr-body-generate

        Args:
            diff (str): The diff to include in the generated pull request title.
            dryrun (bool): If True, unstages all files after generating the title.

        Returns:
            str: The formatted pull request title.

        Raises:
            ValueError: If the pull request title format is incorrect.
        """
        # Check if the origin/main branch exists
        branch_exists = (
            subprocess.run(
                ["git", "rev-parse", "--verify", "origin/main"],
                capture_output=True,
                text=True,
            ).returncode
            == 0
        )

        if branch_exists:
            # Get a log of all changes that this PR is ahead of main by.
            commit_result = subprocess.run(
                ["git", "--no-pager", "log", "origin/main..HEAD", "--pretty=format:%s"],
                capture_output=True,
                text=True,
                check=True,
            )
        else:
            logger.warning("The branch 'origin/main' does not exist.")
            commit_result = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=""
            )

        # Split the result by lines to get individual commit messages
        commits_ahead = commit_result.stdout.splitlines()

        # Save the commits to a single variable
        commits = ""
        for commit in commits_ahead:
            commits += commit + "\n"

        # Generate the pull request title content using the OpenAI API
        generated_title = self.generate_content("pull_request_title", commits)

        # Format the generated pull request title
        formatted_title = self.format_pr_title(generated_title)

        if dryrun:
            # Unstage all files if dryrun is True
            self.unstage_files()

        return formatted_title

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
        generated_body = self.generate_content("release_body", diff)

        # Format the generated release body
        formatted_body = self.format_message(generated_body)

        if dryrun:
            # Unstage all files if dryrun is True
            self.unstage_files()

        # Log the generated release body
        logger.info(message=80 * "-", status="")
        logger.info(message=f"Generated release body:\n\n{formatted_body}\n", status="")
        logger.info(message=80 * "-", status="")

        return formatted_body
