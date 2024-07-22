import logging
from klingon_tools.logger import log_tools
from klingon_tools.git_log_helper import get_commit_log
from klingon_tools.openai_tools import OpenAITools

# Configure logging to include process name
log_tools.configure_logging()

# Suppress logging from the httpx library
logging.getLogger("httpx").setLevel(logging.WARNING)


def gh_pr_gen_title():
    # logger.info("Generating PR title using OpenAITools...")
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    openai_tools = OpenAITools()
    pr_title = openai_tools.generate_pull_request_title(diff)
    print(pr_title)


def gh_pr_gen_summary():
    # logger.info("Generating PR summary using OpenAITools...")
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    openai_tools = OpenAITools()
    pr_summary = openai_tools.generate_pull_request_summary(diff, dryrun=False)
    print(pr_summary)


def gh_pr_gen_context():
    # logger.info("Generating PR context using OpenAITools...")
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    openai_tools = OpenAITools()
    pr_context = openai_tools.generate_pull_request_context(diff, dryrun=False)
    print(pr_context)


def gh_pr_gen_body():
    # logger.info("Generating PR body using OpenAITools...")
    commit_result = get_commit_log("origin/release")
    diff = commit_result.stdout
    openai_tools = OpenAITools()
    pr_body = openai_tools.generate_pull_request_body(diff)
    print(pr_body)
