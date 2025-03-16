import subprocess
import warnings

import pytest


@pytest.fixture(autouse=True)
def ignore_warnings():
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="pydantic"
    )
    warnings.filterwarnings(
        "ignore",
        message="Support for class-based `config` is deprecated*",
        category=DeprecationWarning,
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="imghdr"
    )
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="importlib_resources"
    )
    warnings.filterwarnings(
        "ignore",
        message="'imghdr' is deprecated and slated for removal in Python 3.13",
        category=DeprecationWarning,
    )
    warnings.filterwarnings(
        "ignore",
        message="open_text is deprecated. Use files() instead.",
        category=DeprecationWarning,
    )


# Using the fixtures defined in conftest.py


@pytest.mark.parametrize("debug", [False, True])
def test_pr_summary_generate(no_llm, debug: bool, capsys) -> None:
    """
    Test the pr-summary-generate command execution and output.

    This test runs the pr-summary-generate command and checks its output.

    Args:
        no_llm (bool): Flag to skip LLM tests.
        debug (bool): Flag to enable debug output.
        capsys: Pytest fixture to capture system output.

    Raises:
        AssertionError: If any of the assertions fail.
    """
    # Skip the test if LLM tests are disabled (default behavior)
    if no_llm:
        pytest.skip("Skipping LLM tests (use --run-llm to enable)")

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
        no_llm, result, captured.out if debug else "", debug
    )


def assert_pr_summary_generate_output(
        no_llm: bool,
        result: subprocess.CompletedProcess,
        debug_output: str,
        debug: bool,
) -> None:
    """
    Assert the output of pr-summary-generate command.

    Args:
        no_llm (bool): Flag to skip LLM tests.
        result (subprocess.CompletedProcess): The result of the command
        execution.
        debug_output (str): Captured debug output, if any.
        debug (bool): Flag indicating whether debug mode is active.

    Raises:
        AssertionError: If any of the assertions fail.
    """
    # Skip the test if LLM tests are disabled (default behavior)
    if no_llm:
        pytest.skip("Skipping LLM tests (use --run-llm to enable)")

    # Check that the command ran without errors
    assert result.returncode == 0, (
        f"Command failed with return code {result.returncode}")

    # Check that there is some output
    assert result.stdout.strip(), "Command output is empty"

    if debug:
        print(f"Full command output:\n{result.stdout}")  # noqa: E501
        assert "RETURN CODE:" in debug_output
        assert "STDOUT:" in debug_output
        assert "STDERR:" in debug_output

    # Additional check was removed as it used undefined functions and arguments


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
