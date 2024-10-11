"""Unit tests for the log_msg module."""

import pytest
import logging
from klingon_tools import LogTools
from klingon_tools.log_msg import (
    log_tools,
    log_message,
    set_log_level,
    set_default_style,
)


def test_log_tools_initialization():
    """Test if LogTools is initialized correctly."""
    assert isinstance(log_tools, LogTools)
    # Remove the debug attribute check as it's not part of the LogTools class


def test_log_message():
    """Test if log_message is an instance of LogTools.LogMessage."""
    assert isinstance(log_message, LogTools.LogMessage)


def test_set_log_level():
    """Test if set_log_level is a callable function."""
    assert callable(set_log_level)


def test_set_default_style():
    """Test if set_default_style is a callable function."""
    assert callable(set_default_style)


def test_default_style():
    """Test if the default style is set to 'pre-commit'."""
    assert log_tools.default_style == "pre-commit"


@pytest.mark.parametrize(
    "level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
)
def test_set_log_level_functionality(level):
    """Test if set_log_level function changes the log level correctly."""
    set_log_level(level)
    assert log_tools.logger.level == getattr(logging, level)
    assert log_message.logger.level == getattr(logging, level)


def test_set_default_style_functionality():
    """Test if set_default_style function changes the default style."""
    original_style = log_tools.default_style
    new_style = "basic"  # Use a valid style from VALID_STYLES
    set_default_style(new_style)
    assert log_tools.default_style == new_style
    # Reset to the original style
    set_default_style(original_style)


def test_set_default_style_invalid():
    """Test if set_default_style raises ValueError for invalid style."""
    with pytest.raises(ValueError):
        set_default_style("invalid-style")
