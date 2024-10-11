# tests/test_ktest.py
"""Tests for the ktest module."""

import pytest
from unittest.mock import patch, ANY, MagicMock
import klingon_tools.ktest as ktest
import io
import sys
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
    """Test the ktest function with default parameters."""
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
    """Test the ktest function with a custom log level."""
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
    """Test the ktest function when run as an entrypoint."""
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
    """Test the ktest function with output suppression."""
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
    """Test the ktest_entrypoint function."""
    with patch("klingon_tools.ktest.ktest") as mock_ktest, \
         patch("sys.exit") as mock_exit, \
         patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
        mock_ktest.return_value = 0
        mock_parse_args.return_value = argparse.Namespace(
            no_llm=False, loglevel="INFO")

        ktest.ktest_entrypoint([])  # Simulate calling with no arguments

        mock_ktest.assert_called_once_with(
            loglevel="INFO", as_entrypoint=True, no_llm=False
        )

        # Remove this assertion as sys.exit is not called directly in ktest_entrypoint
        # mock_exit.assert_called_once_with(0)


def test_ktest_no_llm(mock_pytest_main):
    """Test the ktest function with the no_llm argument set to True."""
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


def test_testlogplugin():
    """Test the TestLogPlugin class."""
    mock_log_message = MagicMock()
    mock_log_message.logger = MagicMock()
    mock_log_message.logger.getEffectiveLevel.return_value = 10
    results = []
    plugin = ktest.TestLogPlugin(mock_log_message, results)

    # Test passed test
    report = MagicMock(when="call", nodeid="test_passed", passed=True, failed=False, skipped=False)
    plugin.pytest_runtest_logreport(report)
    assert results == [("test_passed", "passed")]

    # Test failed test
    report = MagicMock(when="call", nodeid="test_failed", passed=False,
                       failed=True, skipped=False, keywords={})
    plugin.pytest_runtest_logreport(report)
    assert results == [("test_passed", "passed"), ("test_failed", "failed")]

    # Test optional failed test
    report = MagicMock(when="call", nodeid="test_optional_failed",
                       passed=False, failed=True, skipped=False, keywords={"optional": True})
    plugin.pytest_runtest_logreport(report)
    assert results == [
        ("test_passed", "passed"),
        ("test_failed", "failed"),
        ("test_optional_failed", "optional-failed")
    ]

    # Test skipped test
    report = MagicMock(when="call", nodeid="test_skipped", passed=False,
                       failed=False, skipped=True)
    plugin.pytest_runtest_logreport(report)
    assert results == [
        ("test_passed", "passed"),
        ("test_failed", "failed"),
        ("test_optional_failed", "optional-failed"),
        ("test_skipped", "skipped")
    ]


def test_setup_output_capture():
    """Test the _setup_output_capture function."""
    captured_output = ktest._setup_output_capture(True, "INFO")
    assert isinstance(captured_output, io.StringIO)

    captured_output = ktest._setup_output_capture(False, "INFO")
    assert captured_output is None

    captured_output = ktest._setup_output_capture(True, "DEBUG")
    assert captured_output is None


def test_prepare_pytest_args():
    """Test the _prepare_pytest_args function."""
    args = ktest._prepare_pytest_args(False)
    assert "--no-llm" not in args

    args = ktest._prepare_pytest_args(True)
    assert "--no-llm" in args


def test_restore_output():
    """Test the _restore_output function."""
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    captured_output = io.StringIO()
    sys.stdout = captured_output
    sys.stderr = captured_output

    ktest._restore_output(True, captured_output)

    assert sys.stdout == sys.__stdout__
    assert sys.stderr == sys.__stderr__

    sys.stdout = captured_output
    sys.stderr = captured_output

    ktest._restore_output(False, None)

    assert sys.stdout == captured_output
    assert sys.stderr == captured_output

    # Restore original stdout and stderr
    sys.stdout = original_stdout
    sys.stderr = original_stderr
