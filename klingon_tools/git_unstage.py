from git import Repo
from klingon_tools.log_msg import log_message
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
    log_message.info(message="Un-staging staged files", status="🔄")
    log_message.debug(message="Staged files", status=f"{staged_files}")

    # Iterate over each staged file and un-stage it
    for file in staged_files:
        try:
            repo.git.reset("--", file)
            log_message.info(message="Un-staging file", status=f"{file}")
        except git_exc.GitCommandError as e:
            log_message.error(
                message="Error un-staging file", status=f"{file}"
            )
            log_message.exception(message=f"{e}")
