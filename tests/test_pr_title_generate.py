# tests/test_pr_title_generate.py
"""
Tests for the pr-title-generate command.

This module contains pytest-style unit tests for the pr-title-generate
command-line tool. It verifies the command's execution and output.
"""

import subprocess
import pytest


@pytest.fixture
def no_llm(pytestconfig):
    """
    Fixture to access the --no-llm flag.
    """
    return pytestconfig.getoption("--no-llm")


@pytest.mark.parametrize("debug", [False, True])
def test_pr_title_generate(no_llm, debug: bool, capsys) -> None:
    """
    Test the pr-title-generate command execution and output.

    This test runs the pr-title-generate command and checks its output for
    expected format and length.

    Assertions:
    1. Check that the command ran without errors (return code 0).
    2. Verify that there is a line of text output in stdout.
    3. Ensure that the title length is 75 characters or less.
    4. Check that the generated title is not empty or only whitespace.
    5. Verify that the title starts with an uppercase letter.
    6. Ensure that the title ends with an ellipsis or does not end with a
    period.
    7. If in debug mode, check for the presence of "RETURN CODE:", "STDOUT:",
    and "STDERR:" in the debug output.

    Args:
        debug (bool): Flag to enable debug output.
        capsys: Pytest fixture to capture system output.

    Raises:
        AssertionError: If any of the assertions fail.
    """
    # Skip the test if the --no-llm flag is set
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag")

    # Run the pr-title-generate command
    result = subprocess.run(
        ["pr-title-generate"],
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
    assert_pr_title_generate_output(no_llm, result,
                                    captured.out if debug else "", debug)


def assert_pr_title_generate_output(
    no_llm: bool,
    result: subprocess.CompletedProcess,
    debug_output: str,
    debug: bool
) -> None:
    """
    Assert the output of pr-title-generate command.

    Args:
        result (subprocess.CompletedProcess): The result of the command
        execution.
        debug_output (str): Captured debug output, if any.
        debug (bool): Flag indicating whether debug mode is active.

    Raises:
        AssertionError: If any of the assertions fail.
    """
    # Skip the test if the --no-llm flag is set
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag")

    # Check that the command ran without errors
    assert result.returncode == 0, \
        f"Command failed with return code {result.returncode}"

    output_lines = result.stdout.splitlines()

    print(f"output_lines: {output_lines}")

    # Check that there is a line of text output in stdout
    assert len(output_lines) > 0, "No output was generated"

    # Remove quotation marks from the title
    title = output_lines[0].strip().strip('"')

    # Check that its length is 72 characters or less in stdout (including
    # possible ellipsis)
    assert len(title) <= 75, f"Title exceeds 75 characters: {len(title)} chars"

    # Additional checks
    assert title.strip(), "Generated title is empty or only whitespace"
    assert title[0].isupper(), "Title should start with an uppercase letter"
    assert title.endswith("...") or not title.endswith(
        "."
    ), "Title should end with an ellipsis or not end with a period"

    if debug:
        print(f"Generated title: {title}")
        assert "RETURN CODE:" in debug_output
        assert "STDOUT:" in debug_output
        assert "STDERR:" in debug_output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
