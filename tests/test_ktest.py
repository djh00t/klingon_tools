# tests/test_ktest.py
"""Tests for the ktest module."""

import pytest
from unittest.mock import patch, ANY
import klingon_tools.ktest as ktest
import io


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
        ["tests", "--tb=short", "--import-mode=importlib", "-v"], plugins=[ANY]
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
        ["tests", "--tb=short", "--import-mode=importlib", "-v"], plugins=[ANY]
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
        ["tests", "--tb=short", "--import-mode=importlib", "-v"], plugins=[ANY]
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
        ["tests", "--tb=short", "--import-mode=importlib", "-v"], plugins=[ANY]
    )


def test_ktest_entrypoint():
    """
    Test the ktest_entrypoint function.

    This test verifies that the ktest_entrypoint function correctly calls
    sys.exit with the result of ktest. It checks the following:

    1. sys.exit is called with the result of ktest.
    2. ktest is called with as_entrypoint=True.
    """
    with patch("klingon_tools.ktest.ktest") as mock_ktest, patch(
        "sys.exit"
    ) as mock_exit:
        mock_ktest.return_value = 0
        ktest.ktest_entrypoint()
        mock_ktest.assert_called_once_with(as_entrypoint=True)
        mock_exit.assert_called_once_with(0)
