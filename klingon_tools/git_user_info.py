import subprocess
import sys
from typing import Tuple
from klingon_tools.logger import logger


def get_git_user_info() -> Tuple[str, str]:
    """Retrieves the user's name and email from git configuration."""

    def get_config_value(command: str) -> str:
        try:
            return subprocess.check_output(command.split()).decode().strip()
        except subprocess.CalledProcessError:
            return ""

    user_name = get_config_value("git config --get user.name") or get_config_value(
        "git config --global --get user.name"
    )
    user_email = get_config_value("git config --get user.email") or get_config_value(
        "git config --global --get user.email"
    )

    if (
        not user_name
        or user_name == "Your Name"
        or not user_email
        or user_email == "your.email@example.com"
    ):
        logger.error(
            "Git user name and email are not set or are set to default values."
        )
        logger.info(
            "Please set your git user name and email using the following commands:"
        )
        logger.info("  git config --global user.name 'Your Name'")
        logger.info("  git config --global user.email 'your.email@example.com'")
        sys.exit(1)

    return user_name, user_email
