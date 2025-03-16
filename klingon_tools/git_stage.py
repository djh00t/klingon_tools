from git import Repo
from klingon_tools.log_msg import log_message
import sys


def git_stage_diff(file_name: str, repo: Repo, modified_files: list) -> str:
    """Stages a file, generates a diff, and returns the diff.

    This function checks if any files are already staged, unstages them if
    necessary, stages the specified file in the repository, generates a diff
    for the staged file, and returns the diff as a string. It logs the status
    of the staging and diff generation processes.

    Args:
        file_name: The name of the file to be staged and diffed.
        repo: An instance of the git.Repo object representing the repository.
        modified_files: A list of modified files in the repository.

    Returns:
        A string containing the diff of the staged file.
    """
    log_message.info(message="Preparing to stage file", status=f"{file_name}")

    # Check if any files are already staged
    if repo.git.diff("--cached", "--name-only"):
        log_message.info(
            message="Unstaging previously staged files", status="🔁")
        from klingon_tools.git_unstage import git_unstage_files

        git_unstage_files(repo)

    def stage_file(repo: Repo, file_name: str):
        """Helper function to stage a file."""
        try:
            log_message.debug(
                message="Staging file in repo", status=f"{repo.working_dir}"
            )
            repo.index.add([file_name])
            log_message.debug(message="File staged successfully.", status="✅")
            staged_files = repo.git.diff(
                "--cached", "--name-only").splitlines()
            log_message.debug(message="Staged files", status=f"{staged_files}")

            # Check if the file was successfully staged
            if file_name in staged_files:
                log_message.info(message="Staged file", status="✅")
            else:
                log_message.error(f"Failed to stage file: {file_name}", status="❌")
                sys.exit(1)
        except Exception as e:
            log_message.error(f"Error staging file: {file_name}", status="❌")
            log_message.exception(message=f"{e}")
            sys.exit(1)

    # Stage the file in the main repo
    stage_file(repo, file_name)

    # Recursively stage files in submodules
    for submodule in repo.submodules:
        submodule_repo = submodule.module()
        if submodule_repo.is_dirty(untracked_files=True):
            stage_file(submodule_repo, file_name)

    # Generate the diff for the staged file
    try:
        log_message.debug(f"Generating diff for file: {file_name}")
        diff = repo.git.diff("HEAD", file_name)
        if diff:
            log_message.info(message="Diff generated", status="✅")
        else:
            log_message.error(message="Failed to generate diff", status="❌")
    except Exception as e:
        log_message.error(message="Error generating diff", status="❌")
        log_message.exception(message=f"{e}")

    return diff
