"""Entrypoints for generating GitHub pull request components using OpenAI
tools.

This module provides functions to generate various components of a GitHub pull
request such as the title, summary, context, and body using OpenAI's API. The
functions fetch the commit log from a specified branch, generate the required
component, and print it.

Entrypoints:
    - pr-title-generate: Generates a GitHub pull request title.
    - pr-summary-generate: Generates a GitHub pull request summary.
    - pr-context-generate: Generates GitHub pull request context.
    - pr-body-generate: Generates a GitHub pull request body.

Example:
    To generate a pull request title:
        gh_pr_gen_title()

    To generate a pull request summary:
        gh_pr_gen_summary()

    To generate a pull request context:
        gh_pr_gen_context()

    To generate a pull request body:
        gh_pr_gen_body()

"""

import warnings
from klingon_tools.git_log_helper import get_commit_log
from klingon_tools.litellm_tools import LiteLLMTools
import traceback


# Filter out specific warnings
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="pydantic"
)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="imghdr")
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="importlib_resources"
)


def gh_pr_gen_title():
    """Generate and print a GitHub pull request title using OpenAI tools.

    This function fetches the commit log from the 'origin/release' branch,
    generates a pull request title using OpenAI's API, prints the title,
    and returns it.

    Entrypoint:
        pr-title-generate

    Example:
        pr_title = gh_pr_gen_title()
    """
    try:
        commit_result = get_commit_log("origin/release")
        diff = commit_result.stdout
        litellm_tools = LiteLLMTools()
        pr_title = litellm_tools.generate_pull_request_title(diff)
        print(pr_title)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1, None


def gh_pr_gen_summary():
    """Generate and print a GitHub pull request summary using OpenAI tools.

    This function fetches the commit log from the 'origin/release' branch,
    generates a pull request summary using OpenAI's API, and prints the
    summary.

    Entrypoint:
        pr-summary-generate

    Example:
        gh_pr_gen_summary()
    """
    try:
        # log_message.info("Generating PR summary using LiteLLMTools...")
        commit_result = get_commit_log("origin/release")
        diff = commit_result.stdout
        litellm_tools = LiteLLMTools()
        pr_summary = litellm_tools.generate_pull_request_summary(
            diff, dryrun=False
        )
        print(pr_summary)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1, None


def gh_pr_gen_context():
    """Generate and print GitHub pull request context using OpenAI tools.

    This function fetches the commit log from the 'origin/release' branch,
    generates the pull request context using OpenAI's API, and prints the
    context.

    Entrypoint:
        pr-context-generate

    Example:
        gh_pr_gen_context()
    """
    try:
        # log_message.info("Generating PR context using LiteLLMTools...")
        commit_result = get_commit_log("origin/release")
        diff = commit_result.stdout
        litellm_tools = LiteLLMTools()
        pr_context = litellm_tools.generate_pull_request_context(
            diff, dryrun=False
        )
        print(pr_context)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1, None
