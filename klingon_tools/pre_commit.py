import os
import subprocess
import sys
from typing import Tuple
from git import Repo
from klingon_tools.log_msg import log_message
from klingon_tools.git_stage import git_stage_diff
from klingon_tools.litellm_tools import LiteLLMTools

LOOP_MAX_PRE_COMMIT = 10


def process_pre_commit_config(repo: Repo, modified_files: list) -> None:
    """Process the .pre-commit-config.yaml file.

    This function stages and commits the .pre-commit-config.yaml file if it is
    modified.

    Args:
        repo (Repo): The git repository object.
        modified_files (list): List of modified files.
    """
    # If .pre-commit-config.yaml is modified, stage and commit it
    if ".pre-commit-config.yaml" in modified_files:
        log_message.info(
            message=".pre-commit-config.yaml modified",
            status="Staging"
        )
        repo.git.add(".pre-commit-config.yaml")

        log_message.info(
            message=".pre-commit-config.yaml staged",
            status="Committing"
        )
        litellm_tools = LiteLLMTools()
        repo.git.diff("HEAD", ".pre-commit-config.yaml")
        commit_message = litellm_tools.generate_commit_message(
            ".pre-commit-config.yaml", repo
        )
        repo.index.commit(commit_message)

        log_message.info(
            message=".pre-commit-config.yaml committed",
            status="✅"
        )

        # Remove .pre-commit-config.yaml from modified_files
        modified_files.remove(".pre-commit-config.yaml")

        # If modified_files is empty, log no more files to process and exit
        if not modified_files:
            log_message.info(
                message="No more files to process. Exiting script.",
                status="🚪🏃‍♂️",
            )
            sys.exit(0)


def git_pre_commit(
    file_name: str, repo: Repo, modified_files: list
) -> Tuple[bool, str]:
    """Runs pre-commit hooks on a file.

    This function runs pre-commit hooks on the specified file. If the hooks
    modify the file, it re-stages the file and re-runs the hooks up to a
    maximum number of attempts. If the hooks pass without modifying the file,
    it returns True. If the hooks fail after the maximum number of attempts, it
    exits the script.

    Args:
        file_name: The name of the file to run pre-commit hooks on.
        repo: An instance of the git.Repo object representing the repository.
        modified_files: A list of modified files in the repository.

    Returns:
        A tuple containing a boolean indicating if the pre-commit hooks passed,
        and the diff of the file.
    """
    # Stage the file and generate a diff of the file being processed
    diff = git_stage_diff(file_name, repo, modified_files)

    attempt = 0  # Initialize the attempt counter
    log_message.info(80 * "-", status="", style="none")
    log_message.info("Starting pre-commit hooks for", status=f"{file_name}")

    while attempt < LOOP_MAX_PRE_COMMIT:
        # Log start of attempt number
        log_message.info(
            message="Running pre-commit attempt",
            status=f"{attempt + 1}/{LOOP_MAX_PRE_COMMIT}",
        )
        env = os.environ.copy()  # Copy the current environment variables
        # Set PYTHONUNBUFFERED to ensure real-time output
        env["PYTHONUNBUFFERED"] = "1"

        process = subprocess.run(
            ["pre-commit", "run", "--files", file_name],
            capture_output=True,
            text=True,
            env=env,
        )

        # Process the output
        for line in process.stdout.splitlines():
            if line.startswith("Passed"):
                log_message.info(line, status="✅")
            elif line.startswith("Skipped"):
                log_message.info(
                    message=line,
                    status="SKIPPED 🦘"
                    )
            elif line.startswith("Failed"):
                log_message.error(line, status="❌")
            else:
                log_message.debug(line, status="")

        # Process the error output
        for line in process.stderr.splitlines():
            log_message.error(line, status="❌")

        log_message.debug(
            message="Pre-commit hooks completed with return code",
            status=f"{process.returncode}",
        )

        if (
            "files were modified by this hook" in process.stdout
            or "Fixing" in process.stdout
        ):
            # Log that the file was modified by the pre-commit hook
            log_message.info(message=80 * "-", status="", style="none")
            log_message.info(
                f"File {file_name} was modified by pre-commit hooks",
                status="🔁",
            )
            log_message.info(
                message=("File modified by pre-commit, restaging"),
                status="🔁",
            )
            log_message.info(message=80 * "-", status="", style="none")

            # Re-stage the file and generate a new diff
            diff = git_stage_diff(file_name, repo, modified_files)

            # Increment the attempt counter
            attempt += 1  # Increment the attempt counter
            if (
                attempt == LOOP_MAX_PRE_COMMIT
            ):  # Check if maximum attempts reached
                log_message.error(
                    message=f"Pre-commit hooks failed for {file_name} after "
                    f"{LOOP_MAX_PRE_COMMIT} attempts. Exiting script.",
                    status="❌",
                )
                sys.exit(1)  # Exit the script if maximum attempts reached
        if process.returncode == 0:  # Check if pre-commit hooks passed
            log_message.info(
                f"Pre-commit hooks passed for {file_name}",
                status="✅"
            )
            return True, diff  # Return True if hooks passed

        if (
            process.returncode == 1
            and "files were modified by this hook" not in process.stdout
            and "Fixing" not in process.stdout
        ):
            log_message.error(
                message="Pre-commit hooks failed without modifying files. "
                "Exiting push.",
                status="❌",
            )
            log_message.info(80 * "-", status="", style="none")
            sys.exit(1)

    log_message.error(
        f"Pre-commit hooks did not pass for {file_name} after "
        f"{LOOP_MAX_PRE_COMMIT} attempts",
        status="❌",
    )
    return False, diff  # Return False if pre-commit hooks did not pass
