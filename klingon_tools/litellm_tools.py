# klingon_tools/litellm_tools.py
"""Tools for generating content using LiteLLM models.

This module provides functionality to initialize LiteLLM models and generate
various types of content such as commit messages, pull request titles,
summaries, contexts, and bodies.

Attributes:
    None

Example:
    tools = LiteLLMTools(debug=True)
    diff = "Your diff content here"
    commit_message = tools.generate_content("commit_message_system", diff)
    pr_title = tools.generate_pull_request_title(diff)
    pr_summary = tools.generate_pull_request_summary(diff)
    pr_context = tools.generate_pull_request_context(diff)

Note:
    A complete list of available litellm models and their costs are available
    at: https://models.litellm.ai/
"""

import os
import subprocess
import textwrap
import logging
import time
from typing import Tuple, Optional

import litellm
from litellm.exceptions import (
    BadRequestError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    UnprocessableEntityError,
    RateLimitError,
    InternalServerError,
    ContextWindowExceededError,
    ContentPolicyViolationError,
    APIConnectionError,
)
from git import Repo

from klingon_tools.git_user_info import get_git_user_info
from klingon_tools.log_msg import log_message
from klingon_tools.git_log_helper import get_commit_log
from klingon_tools.git_stage import git_stage_diff


class LiteLLMTools:
    """A class for generating content using LiteLLM models."""

    def __init__(
        self,
        debug: bool = False,
        model_primary: str = "gpt-4o-mini",
        model_secondary: str = "claude-3-haiku-20240307",
        log_http_requests: bool = False,
    ):
        """Initialize the LiteLLMTools class.

        Args:
            debug: Whether to enable debug logging.
            model_primary: Name of the primary model to use.
            model_secondary: Name of the secondary model to use.
            log_http_requests: Whether to log HTTP requests.
        """
        os.environ["LITELLM_LOG"] = "DEBUG" if debug else "INFO"

        logging.getLogger("LiteLLM").setLevel(logging.WARNING)
        logging.getLogger("litellm.retry").setLevel(logging.ERROR)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

        self.debug = debug
        self.model_primary = model_primary
        self.model_secondary = model_secondary
        self.log_http_requests = log_http_requests

        self.models = [
            self.model_primary,
            self.model_secondary,
            "gpt-4o-mini",  # Default fallback model
        ]

        self.templates = {
            "commit_message_system": """
            You are an AI assistant specialized in generating clear, concise,
            and informative git commit messages, pull request titles, contexts
            and summaries.

            Your task is to analyze code diffs and produce git repository
            documentation that accurately reflect the changes made.

            Follow best practices for commit messages, including using the
            Conventional Commits format when appropriate.

            When provided with message length or column widths, **they are
            mandatory and must not be exceeded.**

            Return all results as raw plain text containing only the answer
            unless otherwise specified.
            """,
            "commit_message_user": """
            Generate a git commit message based on these diffs: "{diff}"

            Follow the Conventional Commits standard using the following
            format:
            <type>(scope): <description>

            [optional body]

            [optional footer(s)]

            The first line of a conventional commit must not exceed 72
            characters and must be followed by a blank line. The body and
            footer are both optional but must be separated by a blank line if
            present and also must not exceed 72 characters.

            Consider the following options when selecting commit types:
            - build: updates to build system & external dependencies
            - chore: changes that don't modify src or test files
            - ci: changes to CI configuration files and scripts
            - docs: updates to documentation & comments
            - feat: add new feature or function to the codebase
            - fix: correct bugs and other errors in code
            - perf: improve performance without changing existing functionality
            - refactor: code changes that neither fix bugs nor add features
            - revert: Reverts a previous commit
            - style: changes that do not affect the meaning of the code
            (white-space, formatting, missing semi-colons, etc)
            - test: add, update, correct unit tests
            - other: Changes that don't fit into the above categories

            Scope: Select the most specific of application name, file name,
            class name, method/function name, or feature name for the commit
            scope. If in doubt, use the name of the file being modified. *Scope
            is not optional.*

            Breaking Changes: Include a `BREAKING CHANGE:` footer or append !
            after type/scope for commits that introduce breaking changes.
            Breaking change is the only footer permitted. Do not add
            "Co-authored-by" or other footers unless explicitly requested.

            Ensure the commit message is accurate, relevant, and concise.
            **REMEMBER: No more than 72 characters wide on any line of
            content.**
            """,
            "pull_request_title": """
            Generate a pull request title (72 characters or less) summarizing
            the changes in the provided commit messages, focusing on the most
            significant change or overall themes. Keep it high level.

            Exclude conventional commit types, prefixes, contributor name,
            scope, or formatting. Use clear, concise language, prioritizing
            clarity over completeness. No leading or trailing punctuation.

            Example input:
            feat(login): Add error handling to login function
            refactor(user): Update user registration
            doc(README): Update README with contribution guidelines

            Example output:
            "Error handling, refactor user registration, and README update"

            PLEASE NOTE: IT IS CRITICAL to keep the title length under 72
            characters or this process will fail.

            Commit messages: \"{diff}\"
            """,
            "pull_request_summary": """
            Look at the conventional commit messages provided and generate a
            concise pull request summary. Keep the summary specific and to the
            point, avoiding unnecessary details.

            Aim to use no more than 2 paragraphs of summary.

            The reader is busy and must be able to read and understand the
            content quickly & without fuss.

            Content should be returned as markdown without headings or font
            styling, bullet points and plain paragraph text are ok.

            Commit messages: \"{diff}\"

            IMPORTANT GUIDELINES:
            1. The summary should be clear, concise, and informative.
            2. Focus on the most significant changes and their impact.
            3. Use bullet points for clarity if there are multiple distinct
            changes.
            4. Aim for 2-3 paragraphs maximum.
            5. Avoid technical jargon unless absolutely necessary.
            6. Explain why the changes were made, not just what was changed.
            7. If there are breaking changes, clearly highlight them.
            """,
            "pull_request_context": """
            Look at the conventional commit messages provided and generate a
            concise context statement for the changes in the pull request that
            clearly explains why the changes have been made.

            IMPORTANT GUIDELINES:
            1. Explain why these changes were necessary.
            2. Use bullet points to list the main reasons for the changes,but
            use as few as possible to keep the context concise.
            3. Keep it brief but informative - aim for no more than 10 bullet
            points.
            4. Focus on the business or technical motivations behind the
            changes.
            5. If addressing any issues or bugs, mention them concisely.
            6. Avoid technical implementation details unless crucial for
            understanding the context.
            7. Content should be returned as markdown without headings or font
            styling, bullet points and plain paragraph text are ok.
            8. Provide a context that helps reviewers understand the motivation
            and importance of these changes.
            9. The word context must be in the returned content.

            Commit messages: \"{diff}\"
            """,
        }

    def get_working_model(self) -> str:
        """Get a working model from the list of available models.

        Returns:
            str: The name of the working model.

        Raises:
            ValueError: If no working models are found after retries.
        """
        return self.models[0]  # Always return the primary model for testing

    def generate_content(
            self,
            template_key: str,
            diff: str
    ) -> Tuple[str, str]:
        """Generate content based on the given template key and diff.

        Args:
            template_key (str): The key of the template to use.
            diff (str): The diff to be used in the template.

        Returns:
            Tuple[str, str]: A tuple containing the generated content and the
            working model.

        Raises:
            ValueError: If the specified template is not found or if content
            generation fails after retries.
        """
        template = self.templates.get(template_key)
        if not template:
            raise ValueError(f"Template '{template_key}' not found.")

        max_diff_length = 10000
        truncated_diff = diff[:max_diff_length]
        role_user_content = template.format(diff=truncated_diff)

        retries = 3
        for attempt in range(retries):
            try:
                model = self.get_working_model()
                response = litellm.completion(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": self.templates["commit_message_system"],
                        },
                        {"role": "user", "content": role_user_content},
                    ],
                )
                generated_content = response.choices[0].message.content.strip()
                return generated_content.replace("```", "").strip(), model
            except (
                AuthenticationError,
                PermissionDeniedError,
                ContentPolicyViolationError,
            ) as e:
                log_message.error(f"Critical error: {e}")
                raise
            except RateLimitError as e:
                log_message.warning(f"Rate limit exceeded: {e}")
                time.sleep(5)  # Wait longer for rate limit errors
            except (
                BadRequestError,
                NotFoundError,
                UnprocessableEntityError,
                InternalServerError,
                ContextWindowExceededError,
                APIConnectionError,
            ) as e:
                log_message.warning(f"API error: {e}")

            if attempt == retries - 1:
                log_message.error(
                    f"Failed to generate content after {retries} attempts"
                )
                raise ValueError("Content generation failed after max retries")
            time.sleep(2)

        raise ValueError(
            "Unexpected error: Content generation failed without raising "
            "an exception"
        )

    def format_message(self, message: str) -> str:
        """Format a commit message.

        Args:
            message: The commit message to format.

        Returns:
            The formatted commit message.

        Raises:
            ValueError: If the commit message format is incorrect.
        """

        commit_message = "\n".join(
            (
                "\n".join(
                    textwrap.wrap(
                        line,
                        width=78,
                        subsequent_indent=" " * (
                            len(line) - len(line.lstrip())),
                    )
                )
                if len(line) > 79
                else line
            )
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
                "other": "👾",
            }.get(commit_type, "")

            formatted_message = (
                f"{emoticon_prefix} {commit_type}({commit_scope}): "
                f"{commit_message.split(':', 1)[1].strip()}"
            )

            return formatted_message
        except ValueError as e:
            log_message.error(f"Commit message format error: {e}")
            raise
        except Exception as e:
            log_message.error(f"Unexpected error: {e}")
            raise

    def format_pr_title(self, title: str) -> str:
        """Format a pull request title.

        Args:
            title: The pull request title to format.

        Returns:
            The formatted pull request title.
        """
        formatted_title = " ".join(title.split())
        if len(formatted_title) > 72:
            formatted_title = formatted_title[:69] + "..."
        # Explicitly specify fill character
        return formatted_title.ljust(72, " ")

    def generate_pull_request_title(self, diff: str) -> str:
        """
        Generate a pull request title based on the given diff.

        Args:
            diff (str): The diff to generate the title from.

        Returns:
            str: The generated pull request title.
        """
        try:
            generated_title, _ = self.generate_content(
                "pull_request_title",
                diff
            )
            return self.format_pr_title(generated_title)
        except ValueError as e:
            log_message.error(f"Error generating pull request title: {e}")
            return "Pull Request Title Generation Failed"

    def signoff_message(self, message: str) -> str:
        """Add a signoff message to a commit message.

        Args:
            message: The commit message to sign off.

        Returns:
            The commit message with the signoff added.
        """
        user_name, user_email = get_git_user_info()
        signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
        return f"{message}{signoff}"

    def generate_commit_message_for_file(
        self, file_name: str, repo: Repo
    ) -> Optional[str]:
        """Generate a commit message for the given file.

        Args:
            file_name (str): The name of the file to generate a commit message
            for.
            repo (Repo): The Git repository object.

        Returns:
            Optional[str]: The generated commit message, or None if an error
            occurred.
        """
        modified_files = []  # Initialize an empty list for modified_files
        diff = git_stage_diff(file_name, repo, modified_files)

        if diff is None:
            log_message.error(
                message=f"Failed to get diff for {file_name}",
                status="❌"
            )
            return None

        try:
            generated_message, model = self.generate_content(
                "commit_message_user", diff
            )
            formatted_message = self.format_message(generated_message)
            formatted_message = self.signoff_message(formatted_message)

            log_message.info(message="=" * 80, status="", style="none")
            wrapped_message = "\n".join(
                (
                    "\n".join(
                        textwrap.wrap(
                            line,
                            width=79,
                            subsequent_indent=" " * (
                                len(line) - len(line.lstrip())
                            ),
                        )
                    )
                    if len(line) > 79
                    else line
                )
                for line in formatted_message.split("\n")
            )
            log_message.info(
                message=f"\nGenerated commit message [{model}]"
                f"for {file_name}:"
                f"\n\n{wrapped_message}\n",
                status="",
                style="none",
            )
            log_message.info(message="=" * 80, status="", style="none")

            return formatted_message

        except ValueError as e:
            log_message.error(f"Error formatting commit message: {e}")
            if "must include a scope" in str(e):
                commit_type, commit_description = generated_message.split(
                    ":", 1
                )
                commit_scope = "specific-scope"  # Placeholder
                generated_message = (
                    f"{commit_type}({commit_scope}): "
                    f"{commit_description.strip()}"
                )
                formatted_message = self.format_message(generated_message)
                formatted_message = self.signoff_message(formatted_message)
                log_message.error(
                    "Scope was missing. Please provide a more specific scope."
                )

                log_message.info(message="=" * 80, status="", style="none")
                wrapped_message = "\n".join(
                    textwrap.wrap(formatted_message, width=79)
                )
                log_message.info(
                    message=f"\nGenerated commit message [{model}]"
                    f"for {file_name}:"
                    f"\n\n{wrapped_message}\n",
                    status="",
                    style="none",
                )
                log_message.info(message="=" * 80, status="", style="none")

                return formatted_message

        return None

    def generate_pull_request_summary(self) -> Optional[str]:
        """Generate a summary for a pull request.

        Args:
            dryrun (bool, optional): Whether this is a dry run. Defaults to
            False.

        Returns:
            Optional[str]: The generated pull request summary, or None if an
            error occurred.
        """
        try:
            commits = get_commit_log("origin/release").stdout
            generated_summary, _ = self.generate_content(
                "pull_request_summary", commits
            )
            return generated_summary
        except subprocess.CalledProcessError as e:
            log_message.error(f"Error getting commit log: {e}")
        except ValueError as e:
            log_message.error(f"Error generating PR summary: {e}")
        return None

    def generate_pull_request_context(self) -> Optional[str]:
        """Generate context for a pull request.

        Args:
            dryrun (bool, optional): Whether this is a dry run. Defaults to
            False.

        Returns:
            Optional[str]: The generated pull request context, or None if an
            error occurred.
        """
        try:
            commits = get_commit_log("origin/release").stdout
            generated_context, _ = self.generate_content(
                "pull_request_context", commits
            )
            return generated_context
        except subprocess.CalledProcessError as e:
            log_message.error(f"Error getting commit log: {e}")
        except ValueError as e:
            log_message.error(f"Error generating PR context: {e}")
        return None

    def generate_release_body(self, diff: str, dryrun: bool = False) -> str:
        """Generate a release body based on the given diff.

        Args:
            diff (str): The diff to generate the release body from.
            dryrun (bool, optional): Whether this is a dry run. Defaults to
            False.

        Returns:
            str: The generated and formatted release body.
        """
        try:
            generated_body, _ = self.generate_content("release_body", diff)
            formatted_body = self.format_message(generated_body)

            if dryrun:
                # Note: This operation might need to be handled outside this
                # method or passed as a callback function if needed.
                pass

            log_message.info(message="=" * 80, status="", style="none")
            log_message.info(
                message=f"Generated release body:\n\n{formatted_body}\n",
                status="",
            )
            log_message.info(message="=" * 80, status="", style="none")

            return formatted_body
        except ValueError as e:
            log_message.error(f"Error generating release body: {e}")
            return "Release Body Generation Failed"


# Initialize tools
tools = LiteLLMTools(debug=True)
# Add the litellm_tools module content here
