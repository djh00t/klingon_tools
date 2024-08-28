# tests/test_ktest.py
"""Tests for the ktest module."""

import pytest
from unittest.mock import patch, ANY
import klingon_tools.ktest as ktest
import io
import argparse


@pytest.fixture
def mock_pytest_main():
    """Fixture to mock pytest.main."""
    with patch("pytest.main") as mock:
        mock.return_value = 0
        yield mock


@pytest.fixture
def mock_set_default_style():
    """Fixture to mock set_default_style."""
    with patch("klingon_tools.ktest.set_default_style") as mock:
        yield mock


@pytest.fixture
def mock_set_log_level():
    """Fixture to mock set_log_level."""
    with patch("klingon_tools.ktest.set_log_level") as mock:
        yield mock


def test_ktest_default(
        mock_pytest_main,
        mock_set_default_style,
        mock_set_log_level
        ):
    """
    Test the ktest function with default parameters.

    This test verifies that the ktest function behaves correctly when called
    with default parameters. It checks the following:

    1. The default style is set to "pre-commit".
    2. The default log level is set to "INFO".
    3. pytest.main is called with the correct arguments.
    4. The function returns a list when not run as an entrypoint.

    Args:
        mock_pytest_main: Mocked pytest.main function.
        mock_set_default_style: Mocked set_default_style function.
        mock_set_log_level: Mocked set_log_level function.
    """
    result = ktest.ktest(as_entrypoint=False)

    mock_set_default_style.assert_called_once_with("pre-commit")
    mock_set_log_level.assert_called_once_with("INFO")
    mock_pytest_main.assert_called_once_with(
        [
            "tests",
            "--tb=short",
            "--import-mode=importlib",
            "-v",
            "-q",
            "--disable-warnings"
        ],
        plugins=[ANY]
    )
    assert isinstance(result, list)


def test_ktest_custom_loglevel(
    mock_pytest_main, mock_set_default_style, mock_set_log_level
):
    """
    Test the ktest function with a custom log level.

    This test verifies that the ktest function behaves correctly when called
    with a custom log level. It checks the following:

    1. The default style is still set to "pre-commit".
    2. The log level is set to the custom value "DEBUG".
    3. pytest.main is called with the correct arguments.

    Args:
        mock_pytest_main: Mocked pytest.main function.
        mock_set_default_style: Mocked set_default_style function.
        mock_set_log_level: Mocked set_log_level function.
    """
    ktest.ktest(loglevel="DEBUG", as_entrypoint=False)

    mock_set_default_style.assert_called_once_with("pre-commit")
    mock_set_log_level.assert_called_once_with("DEBUG")
    mock_pytest_main.assert_called_once_with(
        [
            "tests",
            "--tb=short",
            "--import-mode=importlib",
            "-v",
            "-q",
            "--disable-warnings"
        ],
        plugins=[ANY]
    )


def test_ktest_as_entrypoint(
    mock_pytest_main, mock_set_default_style, mock_set_log_level
):
    """
    Test the ktest function when run as an entrypoint.

    This test verifies that the ktest function behaves correctly when run
    as an entrypoint. It checks the following:

    1. The function returns an integer (exit code).
    2. pytest.main is called with the correct arguments.

    Args:
        mock_pytest_main: Mocked pytest.main function.
        mock_set_default_style: Mocked set_default_style function.
        mock_set_log_level: Mocked set_log_level function.
    """
    result = ktest.ktest(as_entrypoint=True)

    assert isinstance(result, int)
    mock_pytest_main.assert_called_once_with(
        [
            "tests",
            "--tb=short",
            "--import-mode=importlib",
            "-v",
            "-q",
            "--disable-warnings"
        ],
        plugins=[ANY]
    )


@patch("sys.stdout", new_callable=io.StringIO)
@patch("sys.stderr", new_callable=io.StringIO)
def test_ktest_suppress_output(
    mock_stderr,
    mock_stdout,
    mock_pytest_main,
    mock_set_default_style,
    mock_set_log_level,
):
    """
    Test the ktest function with output suppression.

    This test verifies that the ktest function correctly suppresses output
    when the suppress_output parameter is True. It checks the following:

    1. The function captures and suppresses stdout and stderr.
    2. pytest.main is called with the correct arguments.

    Args:
        mock_stderr: Mocked sys.stderr.
        mock_stdout: Mocked sys.stdout.
        mock_pytest_main: Mocked pytest.main function.
        mock_set_default_style: Mocked set_default_style function.
        mock_set_log_level: Mocked set_log_level function.
    """
    ktest.ktest(as_entrypoint=False, suppress_output=True)

    assert mock_stdout.getvalue() == ""
    assert mock_stderr.getvalue() == ""
    mock_pytest_main.assert_called_once_with(
        [
            "tests",
            "--tb=short",
            "--import-mode=importlib",
            "-v",
            "-q",
            "--disable-warnings"
        ],
        plugins=[ANY]
    )


def test_ktest_entrypoint():
    """
    Test the ktest_entrypoint function.

    This test verifies that the ktest_entrypoint function correctly calls
    sys.exit with the result of ktest. It checks the following:

    1. sys.exit is called with the result of ktest.
    2. ktest is called with as_entrypoint=True and the appropriate default
       args.
    """
    with patch("klingon_tools.ktest.ktest") as mock_ktest, patch(
        "sys.exit"
    ) as mock_exit, patch(
        "argparse.ArgumentParser.parse_args"
    ) as mock_parse_args:
        mock_ktest.return_value = 0
        mock_parse_args.return_value = argparse.Namespace(
            no_llm=False, loglevel="INFO")

        ktest.ktest_entrypoint([])  # Simulate calling with no arguments

        mock_ktest.assert_called_once_with(
            loglevel="INFO", as_entrypoint=True, no_llm=False
        )

        mock_exit.assert_called_once_with(0)


def test_ktest_no_llm(mock_pytest_main):
    """
    Test the ktest function with the no_llm argument set to True.

    This test verifies that the --no-llm argument is correctly passed to
    pytest.

    Args:
        mock_pytest_main: Mocked pytest.main function.
    """
    ktest.ktest(no_llm=True, as_entrypoint=False)

    mock_pytest_main.assert_called_once_with(
        [
            "tests",
            "--tb=short",
            "--import-mode=importlib",
            "-v",
            "-q",
            "--disable-warnings",
            "--no-llm"
        ],
        plugins=[ANY]
    )
