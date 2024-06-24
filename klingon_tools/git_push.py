import git
from git import GitCommandError
from klingon_tools.logger import logger
from klingon_tools.git_validate_commit import validate_commit_messages


def git_push(repo: git.Repo) -> None:
    """Pushes changes to the remote repository."""
    try:
        # Validate commit messages
        if not validate_commit_messages(repo):
            logger.error(
                message="Commit message validation failed. Aborting push.", status="❌"
            )
            return

        # Fetch the latest changes from the remote repository
        repo.remotes.origin.fetch()

        # Get the current branch name
        current_branch = repo.active_branch.name

        # Check for unstaged changes and stash them if any
        stash_needed = repo.is_dirty(untracked_files=True)
        if stash_needed:
            repo.git.stash("save", "--include-untracked", "Auto stash before rebase")

        # Rebase the current branch on top of the remote branch
        repo.git.rebase(f"origin/{current_branch}")

        # Push the changes to the remote repository
        repo.remotes.origin.push()

        # Apply the stashed changes back if they were stashed
        if stash_needed:
            try:
                repo.git.stash("pop")
            except GitCommandError as e:
                logger.error(
                    message="Failed to apply stashed changes",
                    status="❌",
                    reason=str(e),
                )
                # If there are conflicts, you can handle them here or manually resolve them

        logger.info(message="Pushed changes to remote repository", status="✅")
    except GitCommandError as e:
        logger.error(
            message="Failed to push changes to remote repository",
            status="❌",
            reason=str(e),
        )
    except Exception as e:
        logger.error(
            message="An unexpected error occurred",
            status="❌",
            reason=str(e),
        )
