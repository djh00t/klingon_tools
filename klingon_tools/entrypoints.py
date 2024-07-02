import logging
import subprocess

from klingon_tools.logger import log_tools, logger
from klingon_tools.openai_tools import OpenAITools

# Configure logging to include process name
log_tools.configure_logging()

# Suppress logging from the httpx library
logging.getLogger("httpx").setLevel(logging.WARNING)


def gh_pr_gen_title():
    logger.info("Generating PR title using OpenAITools...")
    diff = subprocess.run(
        ["git", "diff", "origin/main..HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    openai_tools = OpenAITools()
    pr_title = openai_tools.generate_pull_request_title(diff)
    print(pr_title)


def gh_pr_gen_summary():
    logger.info("Generating PR summary using OpenAITools...")
    diff = subprocess.run(
        ["git", "diff", "origin/main..HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    openai_tools = OpenAITools()
    pr_summary = openai_tools.generate_pull_request_summary(diff)
    print(pr_summary)


def gh_pr_gen_context():
    logger.info("Generating PR context using OpenAITools...")
    diff = subprocess.run(
        ["git", "diff", "origin/main..HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    openai_tools = OpenAITools()
    pr_context = openai_tools.generate_pull_request_context(diff)
    print(pr_context)


def gh_pr_gen_body():
    logger.info("Generating PR body using OpenAITools...")
    diff = subprocess.run(
        ["git", "diff", "origin/main..HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    openai_tools = OpenAITools()
    pr_body = openai_tools.generate_pull_request_body(diff)
    print(pr_body)
