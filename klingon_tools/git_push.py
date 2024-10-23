"""Module for pushing changes to a remote Git repository.

This module provides functionality to push changes to a remote Git repository
after performing several checks and operations such as handling file deletions
and managing submodules.

Typical usage example:

    import git
    from klingon_tools.git_push import git_push

    repo = git.Repo('/path/to/repo')
    git_push(repo)
"""

import subprocess
import git
from git import GitCommandError
from klingon_tools.log_msg import log_message
from klingon_tools.litellm_tools import LiteLLMTools


def git_push(repo: git.Repo) -> None:
    """Pushes changes to the remote repository.

    This function performs several steps to ensure that the local repository is
    in sync with the remote repository before pushing changes. It handles file
    deletions, generates commit messages for untracked files, and manages
    submodules if present.

    Args:
        repo: The Git repository object.

    Raises:
        GitCommandError: If any git command fails.
        Exception: For any unexpected errors.
    """
    try:
        repo.git.reset()
        _handle_file_deletions(repo)

        litellm_tools = LiteLLMTools()
        _generate_and_commit_messages(repo, litellm_tools)

        if _is_submodule(repo):
            _handle_submodule(repo)
        else:
            push_changes(repo)

    except GitCommandError as e:
        log_message.error("Failed to push changes to remote repository",
                          status="❌", reason=str(e))
    except (ValueError, TypeError, AttributeError) as e:
        log_message.error("An error occurred while processing repository data",
                          status="❌", reason=str(e))


def _handle_file_deletions(repo: git.Repo) -> None:
    """Handles file deletions in the repository."""
    deleted_files = subprocess.run(
        ["git", "ls-files", "--deleted"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()

    for file in deleted_files:
        try:
            repo.index.remove([file], working_tree=True)
            commit_message = f"chore({file}): Cleanup deleted items"
            repo.index.commit(commit_message)
        except GitCommandError as e:
            log_message.error(f"Failed to handle deletion for {file}: {e}")


def _generate_and_commit_messages(repo: git.Repo,
                                  litellm_tools: LiteLLMTools) -> None:
    """Generates and commits messages for untracked files."""
    for file in repo.untracked_files:
        try:
            file_diff = subprocess.run(
                ["git", "diff", file],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            commit_message = litellm_tools.generate_commit_message(file_diff)
            repo.git.add(file)
            repo.index.commit(commit_message)
        except subprocess.CalledProcessError as e:
            log_message.error(
                f"Failed to generate commit message for {file}: {e}")


def _is_submodule(repo: git.Repo) -> bool:
    """Checks if the current repository is a submodule."""
    return ".git" in repo.git.rev_parse("--show-toplevel")


def _handle_submodule(repo: git.Repo) -> None:
    """Handles changes in a submodule and its parent repository."""
    repo.git.add(".")
    repo.index.commit("Update config file in submodule")

    main_repo_path = repo.git.rev_parse("--show-superproject-working-tree")
    main_repo = git.Repo(main_repo_path)

    main_repo.git.add(repo.working_tree_dir)
    main_repo.index.commit(f"Update config file in {repo.working_tree_dir} "
                           "submodule")
    main_repo.remotes.origin.push()


def push_changes(repo: git.Repo) -> None:
    """
    Pushes changes to the remote repository after all commits are made.

    This function ensures that the local repository is in sync with the remote
    repository before pushing changes. It stashes any unstaged changes, rebases
    the current branch on top of the remote branch, and then pushes the
    changes.

    Args:
        repo: The Git repository object.

    Raises:
        GitCommandError: If any git command fails.
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
            except GitCommandError as e:
                log_message.error("Failed to apply stashed changes",
                                  status="❌", reason=str(e))

        repo.remotes.origin.push()
        log_message.info("Pushed changes to remote repository", status="✅")
    except GitCommandError as e:
        log_message.error("Failed to push changes to remote repository",
                          status="❌", reason=str(e))
    except (ValueError, TypeError, AttributeError) as e:
        log_message.error("An error occurred while processing repository data",
                          status="❌", reason=str(e))
    except OSError as e:
        log_message.error("An OS-related error occurred", status="❌",
                          reason=str(e))
