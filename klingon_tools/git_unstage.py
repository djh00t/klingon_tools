from git import Repo
from klingon_tools.logger import logger
from git import exc as git_exc


def git_unstage_files(repo: Repo, staged_files: list) -> None:
    """Unstages all staged files in the given repository.

    This function iterates over all staged files in the repository and
    un-stages them. It logs the status of each file as it is un-staged.

    Args:
        repo: An instance of the git.Repo object representing the repository.

    Returns:
        None
    """
    logger.info(message="Un-staging all staged files", status="🔄")
    logger.debug(message="Staged files", status=f"{staged_files}")

    # Iterate over each staged file and un-stage it
    for file in staged_files:
        try:
            repo.git.reset("--", file)
            logger.info(message="Un-staging file", status=f"{file}")
        except git_exc.GitCommandError as e:
            logger.error(message="Error un-staging file", status=f"{file}")
            logger.exception(message=f"{e}")
