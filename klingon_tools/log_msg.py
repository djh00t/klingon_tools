"""
logger.py

This module initializes the logging tools for the application using the
LogTools class from the klingon_tools package. It sets up the default logging
style and provides a logger instance for logging messages.

Attributes:
    log_tools (LogTools): An instance of the LogTools class for managing
    logging.
    log_message (LogTools.LogMessage): A logger instance for logging messages.
"""

from klingon_tools import LogTools

# Initialize LogTools passing the debug value
args = None  # Define args variable with a default value
log_tools = LogTools(debug=False)
log_message = log_tools.log_message
set_log_level = log_tools.set_log_level
set_default_style = log_tools.set_default_style

# Set default logging style
set_default_style("pre-commit")
