# pre_commit_parser.py
"""
Pre-Commit Parser Module
========================

This module provides functionalities to parse and handle pre-commit hook logs
within a Git repository. It facilitates the execution of pre-commit hooks,
parses their output, and manages the staging and committing of changes based on
the hook results.

Usage Example:
--------------
```python
from git import Repo
from pre_commit_parser import git_pre_commit, set_debug_mode

# Initialize repository
repo = Repo('/path/to/repo')

# Enable debug mode for detailed logging
set_debug_mode(True)

# List of modified files to process
modified_files = ['file1.py', 'file2.py']

# Run pre-commit hooks on each modified file
for file in modified_files.copy():
    success, diff = git_pre_commit(file, repo, modified_files)
    if success:
        print(f"Pre-commit hooks passed for {file}")
    else:
        print(f"Pre-commit hooks failed for {file}")
```
"""

import os
import pprint
import subprocess
import sys
from typing import Tuple, Dict, Optional, List, Iterator
import re
from git import Repo

from klingon_tools.log_msg import log_message, klog_hr
from klingon_tools.git_stage import git_stage_diff
from klingon_tools.litellm_tools import LiteLLMTools
from klingon_tools.utils import klingon_title_case
from klingon_tools.log_tools import LogTools

# Maximum number of pre-commit attempts
LOOP_MAX_PRE_COMMIT = 10

# Global variable to control debug mode
debug_mode = False

# Mapping of statuses to their corresponding icons and templates
STATUS_TEMPLATE_MAP = {
    "Passed": {"status_icon": "✅", "template": "Template 1"},
    "Skipped": {"status_icon": "SKIPPED 🦘", "template": "Template 2"},
    "Failed": {"status_icon": "❌", "template": "Template 3"},
    "Unknown": {"status_icon": "❌", "template": "Template 4"},
}


def set_debug_mode(debug: bool) -> None:
    """
    Set the global debug mode.

    Args:
        debug (bool): If True, enables debug mode; otherwise, disables it.

    Usage Example:
    --------------
    `set_debug_mode(True)`
    """
    global debug_mode
    debug_mode = debug


def pretty_format_dict(data: dict) -> str:
    """Format a dictionary into a pretty-printed string.

    Args:
        data (dict): The dictionary to format.

    Returns:
        str: A pretty-printed string representation of the dictionary.

    Usage Example:
    --------------
    ```python
    formatted = pretty_format_dict({'key': 'value'})
    print(formatted)
    ```
    """
    # Use pprint to format the dictionary with indentation and sorting
    formatted_dict = pprint.pformat(
        data, indent=4, width=120, compact=False, sort_dicts=True
    )

    # Move the opening bracket to its own line
    formatted_dict = formatted_dict.replace("{", "{\n ")

    # Move the closing bracket to its own line
    formatted_dict = formatted_dict[:-1] + "\n}"

    # Return the formatted dictionary string
    return formatted_dict


def get_status_info(status: str) -> Dict[str, str]:
    """Retrieve the status icon and template for a given status.

    Args:
        status (str): The status string (e.g., "Passed", "Failed").

    Returns:
        Dict[str, str]: A dictionary containing the status icon and template.
                        Defaults to "Unknown" if status is not recognized.

    Usage Example:
    --------------
    ```python
    info = get_status_info("Passed")
    print(info['status_icon'])  # Outputs: ✅
    ```
    """
    return STATUS_TEMPLATE_MAP.get(status, STATUS_TEMPLATE_MAP["Unknown"])


def update_parsed_data(
    data: Dict,
    updates: Optional[Dict] = None,
    status_key: Optional[str] = None
) -> Dict:
    """
    Update the parsed data dictionary with additional updates and substitute
    status values if applicable.

    Args:
        data (Dict): The original parsed data dictionary.
        updates (Optional[Dict]): Additional key-value pairs to update the data
        with.
        status_key (Optional[str]): The key in the data dictionary that holds
        the status value.

    Returns:
        Dict: The updated data dictionary.

    Usage Example:
    --------------
    ```python
    data = {'status': 'Passed'}
    updated_data = update_parsed_data(data, {'template': 'Template 1'},
    'status')
    ```
    """
    if updates:
        data.update(updates)

    if status_key and status_key in data:
        status_info = get_status_info(data[status_key])
        data.update(status_info)

    return data


def parse_pre_commit_log(
    log_lines: Iterator[str], padding: Optional[str] = None
) -> Dict:
    """
    Parse the pre-commit log lines and extract relevant information.

    Args:
        log_lines (Iterator[str]): An iterator over the log lines from
        pre-commit hooks.
        padding (Optional[str]): The padding string used in the log messages.

    Returns:
        Dict: A dictionary containing parsed information such as message,
        status, template, and exceptions.

    Usage Example:
    --------------
    ```python
    with open('pre_commit.log') as f:
        log_data = parse_pre_commit_log(iter(f.readlines()))
    ```
    """
    parsed_data = {}
    try:
        log_line = next(log_lines).strip()
    except StopIteration:
        log_line = ""

    if not log_line:
        return {}

    # Store the raw log message
    parsed_data["raw_message"] = log_line

    # Determine padding if not provided
    if not padding:
        padding_match = re.search(r"[^a-zA-Z0-9\s]{3,}", log_line)
        padding = padding_match.group(0) if padding_match else "."

    parsed_data["padding"] = padding

    # Define regex patterns for known templates
    match_patterns = [
        # Template 1: Passed
        (
            r"^(?P<message>.+?)(?P<padding>\.+)(?P<status>Passed)$",
            "Template 1",
        ),
        # Template 2: Skipped
        (
            r"^(?P<message>.+?)(?P<padding>\.+)"
            r"\((?P<reason>.+)\)(?P<status>Skipped)$",
            "Template 2",
        ),
        # Template 3: Failed
        (
            rf"^(?P<message>.+){re.escape(padding)}{{3,}}(?P<status>Failed)$",
            "Template 3",
        ),
    ]

    # Attempt to match the log line with known templates
    for pattern, template in match_patterns:
        match = re.match(pattern, log_line)
        if match:
            parsed_data.update(match.groupdict())
            parsed_data = update_parsed_data(
                parsed_data,
                {
                    "template": template
                },
                "status"
            )
            parsed_data["message_title_case"] = klingon_title_case(
                parsed_data["message"])
            parsed_data["reason"] = parsed_data.get("reason", None)

            # If the status is Failed, parse exceptions
            if parsed_data["status"] == "Failed":
                parsed_data["exceptions"] = parse_exceptions(log_lines)

            log_parsed_data(parsed_data)
            return parsed_data

    # Handle unknown or other templates (Template 4)
    parsed_data = {
        "template": "Template 4",
        "raw_message": log_line,
        "message": (
            log_line.split(padding)[0] if padding in log_line else log_line
        ),
        "reason": None,
        "padding": padding,
        "status": "Unknown",
    }
    parsed_data = update_parsed_data(parsed_data, status_key="status")
    parsed_data["message_title_case"] = klingon_title_case(
        parsed_data["message"])

    log_parsed_data(parsed_data)
    return parsed_data


def parse_exceptions(log_lines: Iterator[str]) -> List[Dict]:
    """Parse exception details from the log lines.

    Args:
        log_lines (Iterator[str]): An iterator over the log lines from
        pre-commit hooks.

    Returns:
        List[Dict]: A list of dictionaries, each containing details of an
        exception.

    Usage Example:
    --------------
    `exceptions = parse_exceptions(iter(log_file_lines))`
    """
    exceptions = []
    exception_data = {}
    exception_messages = []

    for line in log_lines:
        line = line.strip()
        if not line:
            continue  # Ignore blank lines

        # Detect the start of a new exception
        if line.startswith("- hook id:"):
            if exception_data:
                # Save the previous exception data
                exception_data["exception_messages"] = (
                    exception_messages.copy()
                )
                exceptions.append(exception_data.copy())
                exception_data.clear()
                exception_messages.clear()

            exception_data["hook_id"] = line.split(": ", 1)[1]
        elif line.startswith("- exit code:"):
            try:
                exception_data["exit_code"] = int(line.split(": ", 1)[1])
            except ValueError:
                exception_data["exit_code"] = None
        else:
            exception_messages.append(line)
            # Check if the hook modified any files
            if "files were modified by this hook" in line:
                exception_data["files_modified"] = extract_modified_files(
                    exception_messages)

    # Append the last exception if exists
    if exception_data:
        exception_data["exception_messages"] = exception_messages
        exceptions.append(exception_data)

    return exceptions


def extract_modified_files(exception_messages: List[str]) -> List[str]:
    """Extract modified file names from exception messages.

    Args:
        exception_messages (List[str]): A list of exception message strings.

    Returns:
        List[str]: A list of modified file names extracted from the messages.

    Usage Example:
    --------------
    `files = extract_modified_files(['Fixing file1.py', 'Fixing file2.py'])`
    """
    files_modified = []
    for msg in exception_messages:
        match = re.match(r"Fixing (.+)", msg)
        if match:
            files_modified.append(match.group(1))
    return files_modified


def log_parsed_data(parsed_data: Dict) -> None:
    """Log the parsed data according to the status.

    Args:
        parsed_data (Dict): The dictionary containing parsed log information.

    Usage Example:
    --------------
    `log_parsed_data({'message': 'Test', 'status': 'Passed'})`
    """
    if debug_mode:
        # Debugging: Print a horizontal rule and the pretty-formatted parsed
        # data
        log_message.debug(
            f"{pretty_format_dict(parsed_data)}",
            status="",
            style="none",
        )

    # Construct the message line without duplicating the status icon
    message_line = f"{parsed_data['message_title_case']}{parsed_data['padding']}"
    log_message.info(message_line, status=parsed_data.get(
        "status_icon", ""), style="pre-commit")

    # Additional logging for exceptions if the status is Failed
    if parsed_data["status"] == "Failed" and "exceptions" in parsed_data:
        for exception in parsed_data["exceptions"]:
            pre_commit_exception_log_message(exception)
            for line in exception.get("exception_messages", []):
                log_message.error(line.strip(), status="", style="none")


def pre_commit_exception_log_message(exception_data: Dict) -> None:
    """Log pre-commit exception messages.

    Args:
        exception_data (Dict): A dictionary containing exception details.

    Usage Example:
    --------------
    ```python
    pre_commit_exception_log_message({
        'hook_id': 'flake8',
        'exit_code': 1,
        'exception_messages': ['Error: Line too long']
    })
    ```
    """
    log_tools = LogTools(debug=debug_mode)
    log_tools.pre_commit_exception_log_message(exception_data)


def process_pre_commit_config(repo: Repo, modified_files: List[str]) -> None:
    """Process and commit changes to the .pre-commit-config.yaml file.

    If the .pre-commit-config.yaml file is modified, this function stages and
    commits the changes with a generated commit message. If no more files are
    left to process after this, the script exits.

    Args:
        repo (Repo): The Git repository object.
        modified_files (List[str]): A list of modified file paths.

    Usage Example:
    --------------
    `process_pre_commit_config(repo, ['.pre-commit-config.yaml',
    'other_file.py'])`
    """
    if ".pre-commit-config.yaml" in modified_files:
        log_message.info(".pre-commit-config.yaml modified", status="Staging")
        # Stage the .pre-commit-config.yaml file
        repo.git.add(".pre-commit-config.yaml")

        log_message.info(".pre-commit-config.yaml staged", status="Committing")
        # Initialize LiteLLMTools to generate commit message
        litellm_tools = LiteLLMTools()
        commit_message = litellm_tools.create_commit_message(
            ".pre-commit-config.yaml", repo)
        # Commit the staged changes
        repo.index.commit(commit_message)

        log_message.info(".pre-commit-config.yaml committed", status="✅")
        # Remove the processed file from the list
        modified_files.remove(".pre-commit-config.yaml")

        if not modified_files:
            log_message.info(
                "No more files to process. Exiting script.", status="🚪🏃‍♂️")
            sys.exit(0)


def git_pre_commit(
    file_name: str, repo: Repo, modified_files: List[str]
) -> Tuple[bool, str]:
    """Run pre-commit hooks on a file and handle the results.

    Executes the pre-commit hooks for the specified file, parses the output,
    handles any modifications made by the hooks, and commits changes if
    necessary. Retries the hooks up to a maximum number of attempts if files
    are modified by the hooks.

    Args:
        file_name (str): The name of the file to run pre-commit hooks on.
        repo (Repo): The Git repository object.
        modified_files (List[str]): A list of modified file paths.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success, and
        a string representing the diff.

    Usage Example:
    --------------
    ```python
    success, diff = git_pre_commit('file1.py', repo, ['file1.py', 'file2.py'])
    if success:
        print("Pre-commit hooks passed.")
    else:
        print("Pre-commit hooks failed.")
    ```
    """
    # Get the diff for the file and stage changes
    diff = git_stage_diff(file_name, repo, modified_files)
    attempt = 0

    # Log the start of pre-commit hooks
    klog_hr.info(char="-")
    log_message.info("Starting pre-commit hooks for", status=file_name)

    while attempt < LOOP_MAX_PRE_COMMIT:
        attempt += 1
        log_message.info(
            message="Running pre-commit attempt",
            status=f"{attempt}/{LOOP_MAX_PRE_COMMIT}"
        )

        # Set up environment variables for subprocess
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        # Execute the pre-commit hook for the specific file
        process = subprocess.Popen(
            ["pre-commit", "run", "--files", file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        stdout, stderr = process.communicate()
        stdout_lines = iter(stdout.splitlines())

        # Process each line of the pre-commit log output
        for line in stdout_lines:
            log_data = parse_pre_commit_log(iter([line]))
            if log_data and log_data.get("status") == "Failed":
                # Log the exception message
                pre_commit_exception_log_message(log_data)
                # Capture and log all remaining lines
                remaining_lines = list(stdout_lines)
                for remaining_line in remaining_lines:
                    log_message.error(remaining_line.strip(),
                                      status="", style="none")
                # Exit with error
                log_message.error(
                    "Pre-commit hooks failed without modifying files. Exiting",
                    status="❌",
                    style="pre-commit"
                )
                sys.exit(1)

        # If no exceptions, pre-commit hooks passed successfully
        log_message.info("Pre-commit completed", status="✅")
        return True, diff

    # If maximum attempts reached without success
    return False, diff
