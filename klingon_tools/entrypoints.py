# klingon_tools/entrypoints.py
"""
Entrypoints for generating GitHub pull request components using OpenAI
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

import argparse
import traceback
import warnings
from klingon_tools.git_log_helper import get_commit_log
from klingon_tools.litellm_tools import LiteLLMTools
from klingon_tools.log_msg import log_message


def log_message_entrypoint():
    """
    Entrypoint for logging messages using the log_message function.

    This function parses command-line arguments and logs a message using the
    specified log level, message, status, reason, and style.

    Entrypoint:
        log-message

    Returns:
        int: 0 for success, 1 for failure
    """
    parser = argparse.ArgumentParser(
        description="Log messages from the command line.")
    parser.add_argument(
        "--level",
        type=str,
        default="INFO",
        help="Log level (INFO, WARNING, ERROR, DEBUG)")
    parser.add_argument(
        "--message",
        type=str,
        required=True,
        help="Log message")
    parser.add_argument("--reason", type=str, default=None, help="Log reason")
    parser.add_argument("--status", type=str, default="OK", help="Log status")
    parser.add_argument(
        "--style",
        type=str,
        default="default",
        help="Log style")
    parser.add_argument(
        "--width",
        type=int,
        default=80,
        help="Text Wrap Width")

    args = parser.parse_args()

    level = args.level.upper()
    message = args.message
    status = args.status
    reason = args.reason
    style = args.style
    width = args.width

    log_func = getattr(log_message, level.lower(), log_message.info)
    log_func(
        message=message,
        status=status,
        reason=reason,
        style=style,
        width=width)
    return 0


# Filter out specific warnings
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="pydantic"
)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="imghdr")
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="importlib_resources"
)


def gh_pr_gen_title():
    """
    Generate and print a GitHub pull request title using OpenAI tools.

    This function fetches the commit log from the 'origin/release' branch,
    generates a pull request title using OpenAI's API, prints the title,
    and returns it.

    Entrypoint:
        pr-title-generate

    Returns:
        int: 0 for success, 1 for failure
    """
    try:
        log_message.info("Generating PR title using LiteLLMTools...")
        commit_result = get_commit_log("origin/release")
        diff = commit_result.stdout
        litellm_tools = LiteLLMTools()
        pr_title = litellm_tools.generate_pull_request_title(diff)
        print(pr_title)
        return 0
    except ImportError as e:
        log_message.error(f"Failed to import required module: {e}")
        return 1
    except ValueError as e:
        log_message.error(f"Invalid value encountered: {e}")
        return 1
    except ConnectionError as e:
        log_message.error(f"Network connection error: {e}")
        return 1
    except Exception as e:  # pylint: disable=broad-except
        log_message.error(f"Unexpected error occurred: {e}")
        log_message.error(
            message=f"Traceback: {traceback.format_exc()}",
            status="",
            style="none",)
        return 1


def gh_pr_gen_summary():
    """
    Generate and print a GitHub pull request summary using OpenAI tools.

    This function fetches the commit log from the 'origin/release' branch,
    generates a pull request summary using OpenAI's API, and prints the
    summary.

    Entrypoint:
        pr-summary-generate

    Returns:
        int: 0 for success, 1 for failure
    """
    try:
        log_message.info("Generating PR summary using LiteLLMTools...")
        litellm_tools = LiteLLMTools()
        pr_summary = litellm_tools.generate_pull_request_summary()
        print(pr_summary)
        return 0
    except ImportError as e:
        log_message.error(f"Failed to import required module: {e}")
        return 1
    except ValueError as e:
        log_message.error(f"Invalid value encountered: {e}")
        return 1
    except ConnectionError as e:
        log_message.error(f"Network connection error: {e}")
        return 1
    except Exception as e:  # pylint: disable=broad-except
        log_message.error(f"Unexpected error occurred: {e}")
        log_message.error(f"Traceback: {traceback.format_exc()}")
        return 1


def gh_pr_gen_context():
    """
    Generate and print GitHub pull request context using LiteLLM.

    This function fetches the commit log from the 'origin/release' branch,
    generates the pull request context using LiteLLM's API, and prints the
    context.

    Entrypoint:
        pr-context-generate

    Returns:
        int: 0 for success, 1 for failure
    """
    try:
        log_message.info("Generating PR context using LiteLLMTools...")
        litellm_tools = LiteLLMTools()
        pr_context = litellm_tools.generate_pull_request_context()
        print(pr_context)
        return 0
    except ImportError as e:
        log_message.error(f"Failed to import required module: {e}")
        return 1
    except ValueError as e:
        log_message.error(f"Invalid value encountered: {e}")
        return 1
    except ConnectionError as e:
        log_message.error(f"Network connection error: {e}")
        return 1
    except Exception as e:  # pylint: disable=broad-except
        log_message.error(f"Unexpected error occurred: {e}")
        log_message.error(f"Traceback: {traceback.format_exc()}")
        return 1
