# tests/test_pr_context_generate.py
"""
Tests for the pr-context-generate command.

This module contains pytest-style unit tests for the pr-context-generate
command-line tool. It verifies the command's execution and output.
"""

import subprocess
import pytest


# Using the fixtures defined in conftest.py


@pytest.mark.parametrize("debug", [False, True])
def test_pr_context_generate(no_llm, debug: bool, capsys) -> None:
    """
    Test the pr-context-generate command execution and output.

    This test runs the pr-context-generate command and checks its output.

    Assertions:
    1. Check that the command ran without errors (return code 0).
    2. Verify that the command output is not empty.
    3. If in debug mode, check for the presence of "RETURN CODE:", "STDOUT:",
    and "STDERR:" in the debug output.

    Args:
        debug (bool): Flag to enable debug output.
        capsys: Pytest fixture to capture system output.

    Raises:
        AssertionError: If any of the assertions fail.

    Assertions:
        1. Checks if the command runs without errors (return code 0).
        2. Verifies that the command output is not empty.
        3. If in debug mode, checks for the presence of debug information in
           the output.
    """
    # Skip the test if LLM tests are disabled (default behavior)
    if no_llm:
        pytest.skip("Skipping LLM tests (use --run-llm to enable)")

    # Run the pr-context-generate command
    result = subprocess.run(
        ["pr-context-generate"],
        capture_output=True,
        text=True,
        check=False,
    )

    # Debugging output
    if debug:
        print("=" * 80)
        print(f"RETURN CODE: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        print("=" * 80)

    # Capture the printed output for assertion
    captured = capsys.readouterr()

    # Assertions
    assert_pr_context_generate_output(no_llm, result,
                                      captured.out if debug else "", debug)


def assert_pr_context_generate_output(
    no_llm: bool,
    result: subprocess.CompletedProcess,
    debug_output: str,
    debug: bool
) -> None:
    """
    Assert the output of pr-context-generate command.

    Args:
        result (subprocess.CompletedProcess): The result of the command
        execution.
        debug_output (str): Captured debug output, if any.
        debug (bool): Flag indicating whether debug mode is active.

    Raises:
        AssertionError: If any of the assertions fail.

    Assertions:
        1. Checks if the command return code is 0 (successful execution).
        2. Verifies that the command output is not empty.
        3. If in debug mode:
           - Prints the full command output.
           - Checks for the presence of "RETURN CODE:", "STDOUT:", and
           "STDERR:" in the debug output.
    """
    # Skip the test if LLM tests are disabled (default behavior)
    if no_llm:
        pytest.skip("Skipping LLM tests (use --run-llm to enable)")

    # Check that the command ran without errors
    assert result.returncode == 0, \
        f"Command failed with return code {result.returncode}"

    # Check that there is some output
    assert result.stdout.strip(), "Command output is empty"

    if debug:
        print(f"Full command output:\n{result.stdout}")
        assert "RETURN CODE:" in debug_output
        assert "STDOUT:" in debug_output
        assert "STDERR:" in debug_output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
