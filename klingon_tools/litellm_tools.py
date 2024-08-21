"""
This module provides tools for generating content using LiteLLM models.

Features:
- Initialize LiteLLM models based on the desired API type.
- Generate commit messages, pull request titles, summaries, contexts, and
bodies.
- Format pull request titles to ensure they meet length requirements.
- Truncate summaries and bodies if they exceed specified word limits.

Arguments:
- model_primary (str): The primary model to use (default: "gpt-4o-mini").
- model_secondary (str): The secondary model to use if the primary is
unavailable (default: "claude-3-haiku-20240307").
- debug (bool): Flag to enable debug mode (default: False).

Outputs:
- Generated content based on the provided templates and diffs.
- Formatted pull request titles, summaries, contexts, and bodies.

Model Options:
- "gpt-4o-mini": Uses OpenAI's GPT-4 model.
- "claude-3-haiku-20240307": Uses Anthropic's Claude model.
- "ollama_chat/": Uses a local Ollama chat model. For instance if I wanted to
use llama3.1 I would enter 'ollama_chat/llama3.1' as either my primary or
secondary models.
- A complete list of available litellm models and their costs are available at:
https://models.litellm.ai/

Initialization:
    tools = LiteLLMTools(debug=True)

Usage:
    diff = "Your diff content here"
    commit_message = tools.generate_content("commit_message_system", diff)
    pr_title = tools.generate_pull_request_title(diff)
    pr_summary = tools.generate_pull_request_summary(diff)
    pr_context = tools.generate_pull_request_context(diff)
    pr_body = tools.generate_pull_request_body(diff)
"""

import os
import subprocess
import textwrap

import litellm
from git import Repo

from klingon_tools.git_user_info import get_git_user_info
from klingon_tools.log_msg import log_message
from klingon_tools.git_unstage import git_unstage_files
from klingon_tools.git_log_helper import get_commit_log


class LiteLLMTools:
    def __init__(
        self,
        debug=False,
        model_primary="gpt-4o-mini",
        model_secondary="claude-3-haiku-20240307",
    ):
        self.debug = debug
        self.model_primary = model_primary
        self.model_secondary = model_secondary
        self.model_fallback = "gpt-4o-mini"  # Default fallback model

        # Set debug logging for litellm
        if self.debug:
            os.environ["LITELLM_LOG"] = "DEBUG"

        # Set up API keys
        openai_api_key = os.getenv("OPENAI_API_KEY")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        if openai_api_key:
            litellm.api_key = openai_api_key
        if anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key

        # Set up model fallback
        self.models = [
            self.model_primary,
            self.model_secondary,
            self.model_fallback,
        ]

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
            Generate a concise pull request title that summarizes the changes
            included in the provided commit messages.

            IMPORTANT RULES:
            1. The title MUST be 72 characters or less. This is a strict
            requirement.
            2. Do not include any type prefix, contributor name, commit type,
            or scope.
            3. Focus on the most significant change or the overall theme of
            the changes.
            4. Use clear and concise language.
            5. If needed, prioritize clarity over completeness.

            Commit messages: \"{diff}\"

            Remember, the title must be 72 characters or less. If your initial
            attempt is too long, try again with an even more concise version.
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

            Use bullet points to list the reasons for the changes, but use as
            few as possible to keep the context concise.

            Content should be returned as markdown without headings or font
            styling, bullet points and plain paragraph text are ok.

            IMPORTANT GUIDELINES:
            1. Explain why these changes were necessary.
            2. Use bullet points to list the main reasons for the changes.
            3. Keep it brief but informative - aim for 3-5 bullet points.
            4. Focus on the business or technical motivations behind the
            changes.
            5. If addressing any issues or bugs, mention them concisely.
            6. Avoid technical implementation details unless crucial for
            understanding the context.

            Commit messages: \"{diff}\"

            Provide a context that helps reviewers understand the motivation
            and importance of these changes.
            """,
            "pull_request_body": """
            Generate a comprehensive pull request body based on the provided
            commit messages. Use the following template structure:

            ## Description
            [Provide a brief description of the changes introduced by this PR]

            ## Motivation and Context
            [Explain why this change is required and what problem it solves]

            ## Types of Changes
            [Mark which types of changes your code introduces. Use 'x' to mark
            the boxes. Add bullet points under each selected type to briefly
            describe the changes.]

            - [ ] `feat`: ✨ A new feature
            - [ ] `fix`: 🐛 A bug fix
            - [ ] `docs`: 📚 Documentation only changes
            - [ ] `style`: 💄 Changes that do not affect the meaning of the code
            - [ ] `refactor`: ♻️ A code change that neither fixes a bug nor
              adds a feature
            - [ ] `perf`: 🚀 A code change that improves performance
            - [ ] `test`: 🚨 Adding missing or correcting existing tests
            - [ ] `build`: 🛠️ Changes that affect the build system or external
              dependencies
            - [ ] `ci`: ⚙️ Changes to our CI configuration files and scripts
            - [ ] `chore`: 🔧 Other changes that don't modify src or test files
            - [ ] `revert`: ⏪ Reverts a previous commit

            Commit messages: \"{diff}\"

            Fill out the template based on the provided commit messages,
            ensuring a comprehensive and informative pull request body.
            """,
        }

    def get_working_model(self):
        for model in self.models:
            try:
                # Test the model with a simple completion
                litellm.completion(
                    model=model, messages=[{"role": "user", "content": "Test"}]
                )
                return model
            except Exception as e:
                log_message.warning(
                    f"Model '{model}' is unavailable: {e}. Trying next model."
                )

        raise ValueError("No working models found.")

    def generate_content(self, template_key: str, diff: str) -> str:
        template = self.templates.get(template_key)
        if not template:
            raise ValueError(f"Template '{template_key}' not found.")

        max_diff_length = 10000  # Adjust this value as needed
        truncated_diff = diff[:max_diff_length]

        role_user_content = template.format(diff=truncated_diff)

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
        except Exception as e:
            log_message.error(f"Failed to generate content: {e}")
            raise

        generated_content = response.choices[0].message.content.strip()
        return generated_content.replace("```", "").strip()

    def format_message(self, message: str) -> str:
        commit_message = "\n".join(
            (
                "\n".join(
                    textwrap.wrap(
                        line,
                        width=79,
                        subsequent_indent=" "
                        * (len(line) - len(line.lstrip())),
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
                "other": "⚠️",
            }.get(commit_type, "")
        except ValueError as e:
            log_message.error(f"Commit message format error: {e}")
            raise
        except Exception as e:
            log_message.error(f"Unexpected error: {e}")
            raise

        formatted_message = (
            f"{emoticon_prefix} {commit_type}({commit_scope}): "
            f"{commit_message.split(':', 1)[1].strip()}"
        )

        return formatted_message

    def format_pr_title(self, title: str) -> str:
        formatted_title = " ".join(title.split())
        if len(formatted_title) > 72:
            formatted_title = formatted_title[:72] + "..."
        return formatted_title

    def signoff_message(self, message: str) -> str:
        user_name, user_email = get_git_user_info()
        signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
        return f"{message}{signoff}"

    def generate_commit_message(self, diff: str, dryrun: bool = False) -> str:
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
                    log_message.error(f"Failed to get diff for {file}: {e}")
                    continue

                generated_message = self.generate_content(
                    "commit_message_user", file_diff
                )

                try:
                    formatted_message = self.format_message(generated_message)
                    formatted_message = self.signoff_message(formatted_message)
                except ValueError as e:
                    log_message.error(f"Error formatting commit message: {e}")
                    if "must include a scope" in str(e):
                        commit_type, commit_description = (
                            generated_message.split(":", 1)
                        )
                        commit_scope = "specific-scope"
                        generated_message = (
                            f"{commit_type}({commit_scope}): ",
                        )
                        f"{commit_description.strip()}"
                        formatted_message = self.format_message(
                            generated_message
                        )
                        formatted_message = self.signoff_message(
                            formatted_message
                        )
                        log_message.error(
                            "Scope was missing. Please provide a more "
                            "specific scope."
                        )

                log_message.info(message="=" * 80, status="", style="none")
                log_message.info(
                    f"Generated commit message for {file}:\n\n"
                    f"{formatted_message}\n"
                )
                log_message.info(message="=" * 80, status="", style="none")

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

            log_message.info(message="=" * 80, status="", style="none")
            wrapped_message = "\n".join(
                (
                    "\n".join(
                        textwrap.wrap(
                            line,
                            width=79,
                            subsequent_indent=" "
                            * (len(line) - len(line.lstrip())),
                        )
                    )
                    if len(line) > 79
                    else line
                )
                for line in formatted_message.split("\n")
            )
            log_message.info(
                message=f"Generated commit message:\n\n{wrapped_message}\n",
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
                generated_message = (f"{commit_type}({commit_scope}): ",)
                "{commit_description.strip()}"
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
                    message="Generated commit message:"
                    f"\n\n{wrapped_message}\n",
                    status="",
                    style="none",
                )
                log_message.info(message="=" * 80, status="", style="none")

                return formatted_message

        except Exception as e:
            log_message.error(f"Unexpected error: {e}")
            raise

    def generate_pull_request_title(self, diff: str) -> str:
        generated_title = self.generate_content("pull_request_title", diff)
        formatted_title = self.format_pr_title(generated_title)
        return formatted_title

    def generate_pull_request_summary(
        self, diff: str, dryrun: bool = False
    ) -> str:
        try:
            commits = get_commit_log("origin/release").stdout
            generated_summary = self.generate_content(
                "pull_request_summary", commits
            )

            return generated_summary
        except subprocess.CalledProcessError as e:
            log_message.error(f"Error getting commit log: {e}")
            raise
        except Exception as e:
            log_message.error(f"Unexpected error generating PR summary: {e}")
            raise

    def generate_pull_request_context(
        self, diff: str, dryrun: bool = False
    ) -> str:
        try:
            commits = get_commit_log("origin/release").stdout
            generated_context = self.generate_content(
                "pull_request_context", commits
            )

            return generated_context
        except subprocess.CalledProcessError as e:
            log_message.error(f"Error getting commit log: {e}")
            raise
        except Exception as e:
            log_message.error(f"Unexpected error generating PR context: {e}")
            raise

    def generate_pull_request_body(self, diff: str) -> str:
        generated_body = self.generate_content("pull_request_body", diff)
        return generated_body

    def generate_release_body(
        self, repo: Repo, diff: str, dryrun: bool = False
    ) -> str:
        generated_body = self.generate_content("release_body", diff)
        formatted_body = self.format_message(generated_body)

        if dryrun:
            git_unstage_files(
                repo, repo.git.diff("--cached", "--name-only").splitlines()
            )

        log_message.info(message="=" * 80, status="", style="none")
        log_message.info(
            message=f"Generated release body:\n\n{formatted_body}\n",
            status="",
        )
        log_message.info(message="=" * 80, status="", style="none")

        return formatted_body


# Initialize tools
tools = LiteLLMTools(debug=True)
