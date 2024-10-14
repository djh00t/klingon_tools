# klingon_tools/git_push_helper.py
# pylint: disable=broad-exception-caught
"""Helper module for Git push operations."""

from git import GitCommandError, Repo
from klingon_tools.log_msg import log_message


def git_push(repo: Repo) -> None:
    """Push changes to the remote repository.

    This function synchronizes the local repository with the remote before
    pushing changes. It performs the following steps:
    1. Fetches latest changes from the remote.
    2. Stashes any unstaged changes.
    3. Rebases the current branch on top of the remote branch.
    4. Pushes the changes.
    5. Attempts to reapply any stashed changes.

    Args:
        repo: The Git repository object.

    Raises:
        GitCommandError: If any Git command fails.
    """
    try:
        repo.remotes.origin.fetch()
        current_branch = repo.active_branch.name
        stash_needed = repo.is_dirty(untracked_files=True)

        if stash_needed:
            repo.git.stash(
                "save",
                "--include-untracked",
                "Auto stash before rebase"
            )

        repo.git.rebase(f"origin/{current_branch}")

        if stash_needed:
            try:
                repo.git.stash("pop")
            except GitCommandError:
                log_message.error(
                    "Failed to apply stashed changes",
                    status="❌",
                    reason="stash pop",
                )
                # Note: Manual conflict resolution may be required here

        repo.remotes.origin.push()
        log_message.info("Pushed changes to remote repository", status="✅")
    except GitCommandError as e:
        log_message.error(
            "Failed to push changes to remote repository",
            status="❌",
            reason=f"push: {str(e)}",
        )
    except (ConnectionError, TimeoutError) as e:
        log_message.error(
            "Network error occurred during push",
            status="❌",
            reason=str(e),
        )
    except Exception as e:
        log_message.error(
            "An unexpected error occurred",
            status="❌",
            reason=str(e),
        )
