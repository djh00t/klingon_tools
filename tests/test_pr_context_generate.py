# tests/test_pr_context_generate.py
"""
Tests for the pr-context-generate command.

This module contains pytest-style unit tests for the pr-context-generate
command-line tool. It verifies the command's execution and output.
"""

import subprocess

import pytest


@pytest.mark.parametrize("debug", [False, True])
def test_pr_context_generate(debug: bool, capsys) -> None:
    """
    Test the pr-context-generate command execution and output.

    This test runs the pr-context-generate command and checks its output
    for expected content and format.

    Args:
        debug (bool): Flag to enable debug output.
        capsys: Pytest fixture to capture system output.

    Raises:
        AssertionError: If any of the assertions fail.
    """
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
    assert_pr_context_generate_output(
        result, captured.out if debug else "", debug
    )


def assert_pr_context_generate_output(
    result: subprocess.CompletedProcess, debug_output: str, debug: bool
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
    """
    # Check that the command ran without errors
    assert (
        result.returncode == 0
    ), f"Command failed with return code {result.returncode}"

    # Check that there is some output
    assert result.stdout.strip(), "Command output is empty"

    # Check for expected content in the output
    expected_content = ["commit", "changes", "code"]
    missing_content = [
        word for word in expected_content if word not in result.stdout.lower()
    ]

    assert (
        not missing_content
    ), f"Output is missing expected content: {', '.join(missing_content)}"

    if debug:
        print(f"Full command output:\n{result.stdout}")
        assert "RETURN CODE:" in debug_output
        assert "STDOUT:" in debug_output
        assert "STDERR:" in debug_output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
