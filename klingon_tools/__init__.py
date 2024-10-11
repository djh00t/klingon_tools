"""
Klingon Tools: A collection of utilities for various tasks.

This module provides access to the LogTools class, which offers
logging functionality for the Klingon Tools package.
"""

from .log_tools import LogTools as _LogTools


class LogTools(_LogTools):
    """
    A wrapper class for LogTools with a simplified initialization.

    This class inherits from the base LogTools class and provides
    a streamlined constructor for easier instantiation.
    """

    def __init__(self, debug=False):
        super().__init__(debug)


__version__ = "0.0.0"

__all__ = ["LogTools"]
