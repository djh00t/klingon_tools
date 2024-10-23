"""Initializes logging tools for the application.

This module sets up the logging tools using the LogTools class from the
klingon_tools package. It initializes the logger, sets the default logging
style, and provides functions for logging and configuration.

Attributes:
    log_tools (LogTools): An instance of the LogTools class for managing
        logging.
    log_message (LogTools.LogMessage): A logger instance for logging messages.
    set_log_level (function): Function to set the log level.
    set_default_style (function): Function to set the default logging style.
"""

import logging
from klingon_tools import LogTools

# Initialize logging tools
log_tools = LogTools(debug=False)

# Expose log_message
log_message = log_tools.log_message

# Expose klog_hr
klog_hr = log_tools.klog_hr

# Expose set_log_level
set_log_level = log_tools.set_log_level

# Expose set_default_style
set_default_style = log_tools.set_default_style

# Set default logging style
set_default_style("pre-commit")

# Add log level attributes to LogTools
LogTools.DEBUG = logging.DEBUG
LogTools.INFO = logging.INFO
LogTools.WARNING = logging.WARNING
LogTools.ERROR = logging.ERROR
LogTools.CRITICAL = logging.CRITICAL
