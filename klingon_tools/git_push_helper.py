from git import GitCommandError, Repo
from klingon_tools.logger import logger


def git_push(repo: Repo) -> None:
    """Pushes changes to the remote repository.

    This function performs several steps to ensure that the local repository is
    in sync with the remote repository before pushing changes. It stashes any
    unstaged changes, rebases the current branch on top of the remote branch,
    and then pushes the changes. If there were any stashed changes, it attempts
    to apply them back.

    Args:
        repo (Repo): The Git repository object.

    Raises:
        GitCommandError: If any git command fails.
    """
    try:
        # Fetch the latest changes from the remote repository
        repo.remotes.origin.fetch()

        # Get the current branch name
        current_branch = repo.active_branch.name

        # Check for unstaged changes and stash them if any
        stash_needed = repo.is_dirty(untracked_files=True)
        if stash_needed:
            repo.git.stash(
                "save", "--include-untracked", "Auto stash before rebase"
            )

        # Rebase the current branch on top of the remote branch
        repo.git.rebase(f"origin/{current_branch}")

        # Apply the stashed changes back if they were stashed
        if stash_needed:
            try:
                repo.git.stash("pop")
            except GitCommandError as e:
                logger.error(
                    "Failed to apply stashed changes",
                    status="❌",
                    reason=str(e),
                )
                # If there are conflicts, you can handle them here or manually
                # resolve them

        # Push the changes to the remote repository
        repo.remotes.origin.push()

        logger.info("Pushed changes to remote repository", status="✅")
    except GitCommandError as e:
        logger.error(
            "Failed to push changes to remote repository",
            status="❌",
            reason=str(e),
        )
    except Exception as e:
        logger.error(
            "An unexpected error occurred", status="❌", reason=str(e)
        )
