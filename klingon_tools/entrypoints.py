"""Entrypoints for generating GitHub pull request components using OpenAI tools.

This module provides functions to generate various components of a GitHub pull request
such as the title, summary, context, and body using OpenAI's API. The functions fetch
the commit log from a specified branch, generate the required component, and print it.

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

import logging
import subprocess
from klingon_tools.logger import log_tools
from klingon_tools.git_log_helper import get_commit_log
from klingon_tools.openai_tools import OpenAITools

# Configure logging to include process name
log_tools.configure_logging()

# Suppress logging from the httpx library
logging.getLogger("httpx").setLevel(logging.WARNING)


def gh_pr_gen_title():
    """Generate and print a GitHub pull request title using OpenAI tools.

    This function fetches the commit log from the 'origin/release' branch,
    generates a pull request title using OpenAI's API, and prints the title.

    Entrypoint:
        pr-title-generate

    Example:
        gh_pr_gen_title()
    """
    # logger.info("Generating PR title using OpenAITools...")
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    openai_tools = OpenAITools()
    pr_title = openai_tools.generate_pull_request_title(diff)
    print(pr_title)


def gh_pr_gen_summary():
    """Generate and print a GitHub pull request summary using OpenAI tools.

    This function fetches the commit log from the 'origin/release' branch,
    generates a pull request summary using OpenAI's API, and prints the summary.

    Entrypoint:
        pr-summary-generate

    Example:
        gh_pr_gen_summary()
    """
    # logger.info("Generating PR summary using OpenAITools...")
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    openai_tools = OpenAITools()
    pr_summary = openai_tools.generate_pull_request_summary(diff, dryrun=False)
    print(pr_summary)


def gh_pr_gen_context():
    """Generate and print GitHub pull request context using OpenAI tools.

    This function fetches the commit log from the 'origin/release' branch,
    generates the pull request context using OpenAI's API, and prints the context.

    Entrypoint:
        pr-context-generate

    Example:
        gh_pr_gen_context()
    """
    # logger.info("Generating PR context using OpenAITools...")
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    openai_tools = OpenAITools()
    pr_context = openai_tools.generate_pull_request_context(diff, dryrun=False)
    print(pr_context)


def gh_pr_gen_body():
    """NOTE: This method & Entrypoint have been deprecated.
    Generate and print a GitHub pull request body using OpenAI tools.

    This function fetches the commit log from the 'origin/release' branch,
    generates a pull request body using OpenAI's API, and prints the body.

    Entrypoint:
        pr-body-generate

    Example:
        gh_pr_gen_body()
    """
    # logger.info("Generating PR body using OpenAITools...")
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    openai_tools = OpenAITools()
    pr_body = openai_tools.generate_pull_request_body(diff)
    print(pr_body)


