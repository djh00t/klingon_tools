# tests/test_ktest.py
"""Tests for the ktest module."""

import pytest
from unittest.mock import patch, ANY, MagicMock
from klingon_tools.ktest import (
    ktest,
    ktest_entrypoint,
    KTestLogPlugin,
    _setup_output_capture,
    _prepare_pytest_args
)
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
def mock_log_tools():
    """Fixture to create a mock LogTools instance."""
    with patch("klingon_tools.ktest.LogTools") as MockLogTools:
        mock_instance = MockLogTools.return_value
        yield mock_instance


@pytest.mark.timeout(5)
def test_ktest_default(
    mock_pytest_main,
    mock_set_default_style,
    mock_log_tools
):
    """Test the ktest function with default parameters."""
    result = ktest(as_entrypoint=False)

    mock_set_default_style.assert_called_once_with("pre-commit")
    mock_log_tools.set_log_level.assert_called_once_with("INFO")
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


@pytest.mark.timeout(5)
def test_ktest_custom_loglevel(
    mock_pytest_main, mock_set_default_style, mock_log_tools
):
    """Test the ktest function with a custom log level."""
    ktest(loglevel="DEBUG", as_entrypoint=False)

    mock_set_default_style.assert_called_once_with("pre-commit")
    mock_log_tools.set_log_level.assert_called_once_with("DEBUG")
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


@pytest.mark.timeout(5)
def test_ktest_as_entrypoint(
    mock_pytest_main, mock_set_default_style
):
    """Test the ktest function when run as an entrypoint."""
    result = ktest(as_entrypoint=True)

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
@pytest.mark.timeout(5)
def test_ktest_suppress_output(
    mock_stderr,
    mock_stdout,
    mock_pytest_main,
    mock_set_default_style,
    mock_log_tools,
):
    """Test the ktest function with output suppression."""
    ktest(as_entrypoint=False, suppress_output=True)

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


@pytest.mark.timeout(5)
def test_ktest_entrypoint():
    """Test the ktest_entrypoint function."""
    with patch("klingon_tools.ktest.ktest") as mock_ktest, \
            patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
        mock_ktest.return_value = 0
        mock_parse_args.return_value = argparse.Namespace(
            no_llm=False,
            loglevel="INFO",
        )

        ktest_entrypoint([])  # Simulate calling with no arguments

        mock_ktest.assert_called_once_with(
            loglevel="INFO",
            as_entrypoint=True,
            no_llm=False,
        )


@pytest.mark.timeout(5)
def test_ktest_no_llm(mock_pytest_main):
    """Test the ktest function with the no_llm argument set to True."""
    ktest(no_llm=True, as_entrypoint=False)

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


@pytest.mark.timeout(5)
def test_logplugin():
    """Test the LogPlugin class."""
    mock_log_message = MagicMock()
    mock_log_message.logger = MagicMock()
    mock_log_message.logger.getEffectiveLevel.return_value = 10
    results = []
    plugin = KTestLogPlugin(results)

    # Test passed test
    report = MagicMock(when="call", nodeid="test_passed",
                       passed=True, failed=False, skipped=False)
    plugin.pytest_runtest_logreport(report)
    assert results == [("test_passed", "passed")]

    # Test failed test
    report = MagicMock(when="call", nodeid="test_failed", passed=False,
                       failed=True, skipped=False, keywords={})
    plugin.pytest_runtest_logreport(report)
    assert results == [("test_passed", "passed"), ("test_failed", "failed")]

    # Test optional failed test
    report = MagicMock(
        when="call",
        nodeid="test_optional_failed",
        passed=False,
        failed=True,
        skipped=False,
        keywords={"optional": True}
    )
    plugin.pytest_runtest_logreport(report)
    assert results == [
        ("test_passed", "passed"),
        ("test_failed", "failed"),
        ("test_optional_failed", "optional-failed"),
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


@pytest.mark.timeout(5)
def test_setup_output_capture():
    """Test the _setup_output_capture function."""
    captured_output = _setup_output_capture(True, "INFO")
    assert isinstance(captured_output, io.StringIO)

    captured_output = _setup_output_capture(False, "INFO")
    assert captured_output is None

    captured_output = _setup_output_capture(True, "DEBUG")
    assert captured_output is None


@pytest.mark.timeout(5)
def test_prepare_pytest_args():
    """Test the _prepare_pytest_args function."""
    args = _prepare_pytest_args(False)
    assert "--no-llm" not in args

    args = _prepare_pytest_args(True)
    assert "--no-llm" in args
