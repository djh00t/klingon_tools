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
    - ktest: Runs pytest and displays the results.

Example:
    To generate a pull request title:
        gh_pr_gen_title()

    To generate a pull request summary:
        gh_pr_gen_summary()

    To generate a pull request context:
        gh_pr_gen_context()

    To generate a pull request body:
        gh_pr_gen_body()

    To run tests:
        ktest()
"""

from klingon_tools.git_log_helper import get_commit_log
from klingon_tools.log_msg import log_message, set_default_style, set_log_level
from klingon_tools.litellm_tools import LiteLLMTools
import pytest
import os


def ktest(loglevel="INFO"):
    """
    Run pytest and display the results with the specified log level.

    This function runs the tests using pytest and ensures that the logging
    output is displayed.

    Args:
        loglevel (str): The logging level to use. Can be one of:
                        'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
                        Defaults to 'INFO'.

    Entrypoint:
        ktest
    """
    # Set the default logging style
    set_default_style("pre-commit")

    # Set the logging level based on the passed argument
    set_log_level(loglevel.upper())

    # List to capture test results
    results = []

    class TestLogPlugin:
        def pytest_runtest_logreport(self, report):
            if report.when == "call":
                test_name = report.nodeid
                if report.passed:
                    log_message.info(message=f"{test_name}", status="✅")
                    results.append((test_name, "passed"))
                elif report.failed:
                    # Check if the test is optional and log as warning
                    if "optional" in report.keywords:
                        log_message.warning(
                            message=f"{test_name} (optional)", status="⚠️"
                        )
                        results.append((test_name, "optional-failed"))
                    else:
                        log_message.error(message=f"{test_name}", status="❌")
                        results.append((test_name, "failed"))
                    # Print debug info after the log messages
                    log_message.debug(message=f"Debug info for {test_name}")
                    print(report.longrepr)
                elif report.skipped:
                    log_message.info(message=f"{test_name}", status="⏭️")
                    results.append((test_name, "skipped"))

    # Redirect stdout to suppress pytest output (to prevent double logging)
    with open(os.devnull, "w") as devnull:
        original_stdout = os.dup(1)
        os.dup2(devnull.fileno(), 1)

        try:
            # Run pytest with the custom plugin
            pytest.main(["tests", "--tb=short"], plugins=[TestLogPlugin()])
        finally:
            # Restore stdout
            os.dup2(original_stdout, 1)

    # Return the results in the expected format
    return [
        {"name": test_name, "outcome": outcome}
        for test_name, outcome in results
    ]


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
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    litellm_tools = LiteLLMTools()
    pr_title = litellm_tools.generate_pull_request_title(diff)

    print(pr_title)  # Print the title
    return pr_title  # Return the title


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
    # log_message.info("Generating PR summary using LiteLLMTools...")
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    litellm_tools = LiteLLMTools()
    pr_summary = litellm_tools.generate_pull_request_summary(
        diff, dryrun=False
    )

    print(pr_summary)
    return pr_summary


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
    # log_message.info("Generating PR context using LiteLLMTools...")
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    litellm_tools = LiteLLMTools()
    pr_context = litellm_tools.generate_pull_request_context(
        diff, dryrun=False
    )

    print(pr_context)
    return pr_context


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
    # log_message.info("Generating PR body using LiteLLMTools...")
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    litellm_tools = LiteLLMTools()
    pr_body = litellm_tools.generate_pull_request_body(diff)

    print(pr_body)
    return pr_body
