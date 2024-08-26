# tests/test_logtools.py
"""Tests for the LogTools class and its methods.

This module contains unit tests for the LogTools class from the klingon_tools
package. It covers initialization, configuration, and various logging
functionalities.
"""

import logging
from io import StringIO
from typing import Tuple

import pytest
from unittest.mock import patch, MagicMock

from klingon_tools.logtools import LogTools


class LogCaptureHandler(logging.Handler):
    """A custom logging handler to capture log messages for testing."""

    def __init__(self):
        """Initialize the LogCaptureHandler."""
        super().__init__()
        self.messages = []

    def emit(self, record):
        """Capture a log record by appending it to the messages list.

        Args:
            record (logging.LogRecord): The log record to capture.
        """
        self.messages.append(self.format(record))


@pytest.fixture
def log_tools() -> Tuple[LogTools, LogCaptureHandler]:
    """Fixture to create a LogTools instance with a LogCaptureHandler.

    Returns:
        Tuple[LogTools, LogCaptureHandler]: A tuple containing the LogTools
        instance and the LogCaptureHandler.
    """
    lt = LogTools(debug=True)
    log_capture_handler = LogCaptureHandler()
    lt.logger.addHandler(log_capture_handler)
    lt.log_message.logger.addHandler(log_capture_handler)
    return lt, log_capture_handler


def test_init():
    """Test the initialization of the LogTools class."""
    lt = LogTools(debug=True)
    assert lt.DEBUG is True
    assert lt.default_style == "default"
    assert isinstance(lt.log_message, LogTools.LogMessage)
    assert lt.logger.level == logging.DEBUG


def test_set_default_style(log_tools):
    """Test setting the default style for LogTools."""
    lt, _ = log_tools
    lt.set_default_style("pre-commit")
    assert lt.default_style == "pre-commit"
    assert lt.log_message.default_style == "pre-commit"

    with pytest.raises(ValueError):
        lt.set_default_style("invalid_style")


def test_set_log_level(log_tools):
    """Test setting the log level for LogTools."""
    lt, _ = log_tools
    lt.set_log_level("INFO")
    assert lt.logger.level == logging.INFO
    assert lt.log_message.logger.level == logging.INFO

    with pytest.raises(ValueError):
        lt.set_log_level("INVALID_LEVEL")


def test_set_template():
    """Test setting the template for LogTools."""
    template = "{message} - {style} - {status}"
    LogTools.set_template(template)
    assert LogTools.template == template


def test_log_message(log_tools):
    """Test the basic logging functionality of LogTools."""
    lt, log_capture = log_tools
    lt.log_message.info("Test message", style="default", status="OK")
    assert any("Test message" in msg for msg in log_capture.messages)
    assert any("OK" in msg for msg in log_capture.messages)


@patch("sys.stdout", new_callable=StringIO)
def test_method_state_decorator(mock_stdout, log_tools):
    """Test the method_state decorator of LogTools."""
    lt, log_capture = log_tools

    @lt.method_state(message="Test method", style="default", status="OK")
    def test_method():
        print("Inside test_method")
        return True

    print("Before calling test_method")
    result = test_method()
    print("After calling test_method")
    stdout_output = mock_stdout.getvalue()
    log_messages = log_capture.messages

    print("Stdout output:", repr(stdout_output))
    print("Log messages:", log_messages)
    print("Result:", result)

    assert "Running Test method" in stdout_output
    assert "OK" in stdout_output or any("OK" in msg for msg in log_messages)


@patch("sys.stdout", new_callable=StringIO)
@patch("subprocess.run")
def test_command_state(mock_subprocess_run, mock_stdout, log_tools):
    """Test the command_state method of LogTools."""
    lt, log_capture = log_tools
    mock_subprocess_run.return_value = MagicMock(
        returncode=0, stdout="Command output", stderr=""
    )
    commands = [("echo 'test'", "Test Command")]

    print("Before calling command_state")
    lt.command_state(commands, style="default", status="Passed")
    print("After calling command_state")

    stdout_output = mock_stdout.getvalue()
    log_messages = log_capture.messages

    print("Stdout output:", repr(stdout_output))
    print("Log messages:", log_messages)
    print("Mock subprocess_run calls:", mock_subprocess_run.call_args_list)

    assert "Running Test Command" in stdout_output or any(
        "Running Test Command" in msg for msg in log_messages
    )
    assert "Passed" in stdout_output or any(
        "Passed" in msg for msg in log_messages
    )


def test_format_pre_commit():
    """Test the _format_pre_commit static method of LogTools."""
    formatted = LogTools._format_pre_commit(
        "Test message", "Passed", "All good"
    )
    assert "Test message" in formatted
    assert "Passed" in formatted
    assert "All good" in formatted
    assert len(formatted.split("\n")[0]) <= 80  # Check line length


def test_log_message_styles(log_tools):
    """Test different logging styles of LogTools."""
    lt, log_capture = log_tools
    lt.log_message.info("Test default", style="default")
    lt.log_message.info("Test pre-commit", style="pre-commit")
    lt.log_message.info("Test basic", style="basic")
    lt.log_message.info("Test none", style="none")

    messages = log_capture.messages
    assert any("Test default" in msg for msg in messages)
    assert any("Test pre-commit" in msg for msg in messages)
    assert any("Test basic" in msg for msg in messages)
    assert any("Test none" in msg for msg in messages)


def test_log_message_levels(log_tools):
    """Test different logging levels of LogTools."""
    lt, log_capture = log_tools
    lt.log_message.debug("Debug message")
    lt.log_message.info("Info message")
    lt.log_message.warning("Warning message")
    lt.log_message.error("Error message")
    lt.log_message.critical("Critical message")

    messages = log_capture.messages
    assert any("Debug message" in msg for msg in messages)
    assert any("Info message" in msg for msg in messages)
    assert any("Warning message" in msg for msg in messages)
    assert any("Error message" in msg for msg in messages)
    assert any("Critical message" in msg for msg in messages)


def test_log_message_exception(log_tools):
    """Test exception logging of LogTools."""
    lt, log_capture = log_tools
    try:
        raise Exception("Test exception")
    except Exception:
        lt.log_message.exception("Exception occurred")

    messages = log_capture.messages
    assert any("Exception occurred" in msg for msg in messages)
    assert any("Test exception" in msg for msg in messages)


if __name__ == "__main__":
    pytest.main()
