"""
logger.py

This module initializes the logging tools for the application using the
LogTools class from the klingon_tools package. It sets up the default logging
style and provides a logger instance for logging messages.

Attributes:
    log_tools (LogTools): An instance of the LogTools class for managing
    logging. logger (LogTools.LogMessage): A logger instance for logging
    messages.
"""

from klingon_tools import LogTools

# Initialize logging
log_tools = LogTools()
logger = log_tools.log_message

# Debug print
print(f"Logger initialized with default style: {log_tools.default_style}")
