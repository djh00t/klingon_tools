"""Tests for the LogTools class and its methods."""

from io import StringIO
from typing import Tuple

import pytest
from unittest.mock import patch, MagicMock

from klingon_tools.log_tools import LogTools, logging

log_tools = LogTools(debug=True)


class LogCaptureHandler(logging.Handler):
    """A custom logging handler to capture log messages for testing."""

    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        """Capture a log record by appending it to the messages list."""
        formatter = logging.Formatter('%(levelname)s %(message)s')
        self.setFormatter(formatter)

        # Check if there is exception information to include in the log message
        if record.exc_info:
            # Format the exception message and traceback
            formatted_message = self.format(record)
            exception_message = formatter.formatException(record.exc_info)
            # Append both the formatted message and the exception traceback
            self.messages.append(f"{formatted_message}\n{exception_message}")
        else:
            # Only append the formatted message
            self.messages.append(self.format(record))


@pytest.fixture
def log_tools_fixture() -> Tuple[LogTools, LogCaptureHandler]:
    """Create a LogTools instance with a LogCaptureHandler."""
    lt = LogTools(debug=True)
    log_capture_handler = LogCaptureHandler()
    lt.logger.addHandler(log_capture_handler)
    lt.log_message.logger.addHandler(log_capture_handler)
    return lt, log_capture_handler


def test_init():
    """Test the initialization of the LogTools class."""
    lt = LogTools(debug=True)
    assert lt.debug is True
    assert lt.default_style == "default"
    assert isinstance(lt.log_message, LogTools.LogMessage)
    assert lt.logger.level == logging.DEBUG


def test_set_default_style(log_tools_fixture):
    """Test setting the default style for LogTools."""
    lt, _ = log_tools_fixture
    lt.set_default_style("pre-commit")
    assert lt.default_style == "pre-commit"
    assert lt.log_message.default_style == "pre-commit"

    with pytest.raises(ValueError):
        lt.set_default_style("invalid_style")


def test_set_log_level(log_tools_fixture):
    """Test setting the log level for LogTools."""
    lt, _ = log_tools_fixture
    lt.set_log_level("INFO")
    assert lt.logger.level == logging.INFO
    assert lt.log_message.logger.level == logging.INFO

    with pytest.raises(ValueError):
        lt.set_log_level("INVALID_LEVEL")


def test_log_message(log_tools_fixture):
    """Test the basic logging functionality of LogTools."""
    lt, log_capture = log_tools_fixture
    lt.log_message.info("Test message", style="default", status="OK")
    assert any("Test message" in msg for msg in log_capture.messages)
    assert any("OK" in msg for msg in log_capture.messages)


@patch("sys.stdout", new_callable=StringIO)
def test_method_state_decorator(mock_stdout, log_tools_fixture):
    """Test the method_state decorator of LogTools."""
    lt, log_capture = log_tools_fixture

    @lt.method_state(
        message="Test method",
        style="default",
        status="OK"
    )
    def test_method():
        print("Inside test_method")
        return True

    result = test_method()
    stdout_output = mock_stdout.getvalue()
    log_messages = log_capture.messages

    assert "Running Test method" in stdout_output
    assert "OK" in stdout_output or any("OK" in msg for msg in log_messages)
    assert result is True


@patch("sys.stdout", new_callable=StringIO)
@patch("subprocess.run")
def test_command_state(mock_subprocess_run, mock_stdout, log_tools_fixture):
    """Test the command_state method of LogTools."""
    lt, log_capture = log_tools_fixture
    mock_subprocess_run.return_value = MagicMock(
        returncode=0, stdout="Command output", stderr=""
    )
    commands = [("echo 'test'", "Test Command")]

    lt.command_state(commands, style="default", status="Passed")

    stdout_output = mock_stdout.getvalue()
    log_messages = log_capture.messages

    assert "Running Test Command" in stdout_output or any(
        "Running Test Command" in msg for msg in log_messages
    )
    assert "Passed" in stdout_output or any(
        "Passed" in msg for msg in log_messages
    )


def test_format_pre_commit():
    """Test the _format_pre_commit static method of LogTools."""
    # 80 characters minus status length and a space
    max_msg_length = 80 - len(" Passed") - 1
    formatted = LogTools.LogMessage._format_pre_commit(
        "Test message", "Passed", max_msg_length
    )
    assert "Test message" in formatted
    assert "Passed" in formatted
    # Check that the entire formatted string is <= 80 characters
    assert len(formatted) <= 80


def test_log_message_styles(log_tools_fixture):
    """Test different logging styles of LogTools."""
    lt, log_capture = log_tools_fixture
    lt.log_message.info("Test default", style="default")
    lt.log_message.info("Test pre-commit", style="pre-commit")
    lt.log_message.info("Test basic", style="basic")
    lt.log_message.info("Test none", style="none")

    messages = log_capture.messages
    assert any("Test default" in msg for msg in messages)
    assert any("Test pre-commit" in msg for msg in messages)
    assert any("Test basic" in msg for msg in messages)
    assert any("Test none" in msg for msg in messages)


def test_log_message_levels(log_tools_fixture):
    """Test different logging levels of LogTools."""
    lt, log_capture = log_tools_fixture
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


def test_log_message_exception(log_tools_fixture):
    """Test exception logging of LogTools."""
    lt, log_capture = log_tools_fixture
    try:
        raise Exception("Test exception")
    except Exception:
        # exc_info is set to True by default in the exception method
        lt.log_message.exception("Exception occurred")

    messages = log_capture.messages

    # Print the captured messages to verify the content
    print("Captured log messages:", messages)

    # Check for the custom log message
    assert any("Exception occurred" in msg for msg in messages), \
        "Custom exception message not found in logs"

    # Check for the actual exception message in the traceback
    assert any("Test exception" in msg for msg in messages), \
        "The exception message 'Test exception' was not found in the logs"
