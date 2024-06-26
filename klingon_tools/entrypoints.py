import os
import logging
from klingon_tools.logger import logger, log_tools

# Configure logging to include process name
log_tools.configure_logging()


from klingon_tools.openai_tools import OpenAITools

# Suppress logging from the httpx library
logging.getLogger("httpx").setLevel(logging.WARNING)


def gh_pr_gen_title():
    # logger.info("Generating PR title using OpenAITools...")
    diff = os.popen("git diff origin/main..HEAD").read()
    openai_tools = OpenAITools()
    pr_title = openai_tools.generate_pull_request_title(diff)
    print(pr_title)
