# tests/test_pr_summary_generate.py
"""
Tests for the pr-summary-generate command.

This module contains pytest-style unit tests for the pr-summary-generate
command-line tool. It verifies the command's execution and output.
"""

import subprocess

import pytest


@pytest.mark.parametrize("debug", [False, True])
def test_pr_summary_generate(debug: bool, capsys) -> None:
    """
    Test the pr-summary-generate command execution and output.

    This test runs the pr-summary-generate command and checks its output for
    expected content and format.

    Assertions:
    1. Check that the command ran without errors (return code 0).
    2. Verify that the command output is not empty.
    3. Ensure that the output contains expected content such as "pull request",
    "changes", "enhancements", and "updates".
    4. If in debug mode, check for the presence of "RETURN CODE:", "STDOUT:",
    and "STDERR:" in the debug output.

    Args:
        debug (bool): Flag to enable debug output.
        capsys: Pytest fixture to capture system output.

    Raises:
        AssertionError: If any of the assertions fail.
    """
    # Run the pr-summary-generate command
    result = subprocess.run(
        ["pr-summary-generate"],
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
    assert_pr_summary_generate_output(
        result, captured.out if debug else "", debug
    )


def assert_pr_summary_generate_output(
    result: subprocess.CompletedProcess, debug_output: str, debug: bool
) -> None:
    """
    Assert the output of pr-summary-generate command.

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
    expected_content = ["pull request", "changes", "enhancements", "updates"]
    missing_content = [
        word for word in expected_content if word not in result.stdout.lower()
    ]

    if missing_content:
        print(
            "Warning: Output is missing some expected content: "
            f"{', '.join(missing_content)}"
        )
        print("Full output:")
        print(result.stdout)
    else:
        print("All expected content found in the output.")

    # Assert that at least some of the expected content is present
    assert len(missing_content) < len(
        expected_content
    ), "Output is missing too much expected content: "
    f"{', '.join(missing_content)}"

    if debug:
        print(f"Full command output:\n{result.stdout}")
        assert "RETURN CODE:" in debug_output
        assert "STDOUT:" in debug_output
        assert "STDERR:" in debug_output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
