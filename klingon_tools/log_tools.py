"""
Utilities for running and logging shell commands in a user-friendly manner.

This module provides the LogTools class, which offers decorators for methods
and CLI commands to log output in a clean and consistent manner with simple
error handling.

Classes:
    LogTools: A utility class for running and logging Python methods and shell
              commands.
    LogTools.LogMessage: Handles logging messages with a given severity,
                         style, status, and reason.

Functions:
    method_state: Decorator to log the state of a method.
    command_state: Runs a list of shell commands and logs their output.
    _format_pre_commit: Formats the message in pre-commit style.
"""

import io
import logging
import subprocess
import sys
from functools import wraps
from typing import Optional, Callable, List, Tuple


class LogTools:
    """
    A utility class for running and logging Python methods and shell commands.

    This class provides decorators for methods and CLI commands that log output
    in a clean and consistent manner with simple error handling.

    Attributes:
        DEBUG: Flag to enable debug mode.
        logger: Logger instance for logging messages.
        template: Template for log messages.
        default_style: Default style for log messages.
        log_message: Instance of LogMessage for handling logs.
    """

    VALID_STYLES = ["default", "pre-commit", "basic", "none"]

    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_RED = "\033[1;31m"
    RESET = "\033[0m"
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    template = None

    def __init__(self, debug: bool) -> None:
        """
        Initializes LogTools with an optional debug flag.

        Args:
            debug: Flag to enable debug mode.
        """
        # Initialize the logger and set the debug flag
        self.debug = debug
        self.default_style = "default"  # Set a default style
        self.log_message = LogTools.LogMessage(__name__, self)
        self.logger = logging.getLogger(__name__)
        self.set_log_level("DEBUG" if self.debug else "INFO")

    def set_default_style(self, style: str) -> None:
        """
        Sets the default style for log messages.

        Args:
            style: The style to use for log messages.

        Raises:
            ValueError: If the provided style is not valid.
        """
        if style not in self.VALID_STYLES:
            raise ValueError(
                f"Invalid style '{style}'. Valid styles are: "
                f"{', '.join(self.VALID_STYLES)}"
            )
        self.default_style = style
        self.log_message.default_style = style

    def set_log_level(self, level: str) -> None:
        """
        Sets the logging level for the logger.

        Args:
            level: The logging level to set (e.g., 'DEBUG', 'INFO').

        Raises:
            ValueError: If the provided level is not valid.
        """
        # If level is not INFO print a message saying the level being set.
        # Also make sure that the level is in uppercase and a valid level
        level = level.upper()
        if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(
                f"Invalid log level '{level}'. Valid levels are: "
                "'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'"
            )
        if level != "INFO":
            print(f"Setting log level to {level}")

        self.logger.setLevel(level)
        self.log_message.set_log_level(level)

    @classmethod
    def set_template(cls, template: str) -> None:
        """
        Sets the template for log messages.

        Args:
            template: The template to use for log messages.
        """
        # Set the class-level template for log messages
        cls.template = template

    def configure_logging(self) -> None:
        """
        Configures the logging settings for the application.

        This method sets up the logging level and format for the application's
        logs.
        """
        # Set the logging level to DEBUG
        # This allows all log messages to be captured
        # and displayed in the logs
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    class LogMessage:
        """
        Handles logging messages with a given severity, style, status, and
        reason.

        This class provides methods to log messages with different severity
        levels (debug, info, warning, error, critical) and supports custom
        templates for log messages.

        Args:
            name: The name of the logger.
            parent: The parent LogTools instance.

        Attributes:
            logger: The logger instance.
            parent: The parent LogTools instance.
            default_style: The default style for log messages.
        """

        def __init__(self, name, parent):
            self.logger = logging.getLogger(name)
            self.parent = parent
            self.default_style = "default"

        def _log(self, level, *args, **kwargs):
            """
            Logs a message with a given level, style, status, and reason.

            Args:
                level (int): The severity level of the log message.
                *args: Variable length argument list for the log message.
                **kwargs: Arbitrary keyword arguments for style, status,
                reason,
                          etc.
            """
            msg = kwargs.get("message") or (args[0] if args else None)
            style = kwargs.get("style", self.default_style)
            status = kwargs.get("status", "OK")
            reason = kwargs.get("reason")

            if style is None:
                self.logger.log(level, msg)
                return

            if style not in self.parent.VALID_STYLES:
                raise ValueError(
                    f"Invalid style '{style}'. Valid styles are: "
                    f"{', '.join(self.parent.VALID_STYLES)}"
                )

            msg = self._prepare_message(msg, reason, status, style)
            final_msg = self._format_message(msg, status, style)
            self.logger.log(level, final_msg)

        def _prepare_message(self, msg, reason, status, style):
            """
            Prepares the message by applying the template, reason, and status.

            Args:
                msg (str): The log message.
                reason (str): The reason for the status.
                status (str): The status message.
                style (str): The style of the message.

            Returns:
                str: The prepared message.
            """
            if reason:
                msg = f"{msg} ({reason})"
            if self.parent.template:
                msg = self.parent.template.format(
                    message=msg, style=style, status=status
                )
            return msg

        def _format_message(self, msg, status, style):
            """
            Formats the message based on the style and status.

            Args:
                msg (str): The log message.
                status (str): The status message.
                style (str): The style of the message.

            Returns:
                str: The formatted message.
            """
            total_length = 79
            status_length = len(status) + self._get_emoji_adjustment(status)
            max_msg_length = total_length - status_length - 1

            if style == "none":
                return msg

            if style == "pre-commit":
                return self._format_pre_commit(msg, status, max_msg_length)
            if style == "basic":
                return self._format_basic(msg, status, max_msg_length)
            # default style
            return self._format_default(msg, status, max_msg_length)

        def _get_emoji_adjustment(self, status):
            """
            Calculates the emoji adjustment based on the given status.

            Parameters:
            - status (str): The status for which the emoji adjustment is
            calculated.

            Returns:
            - int: The calculated emoji adjustment.
            """
            emoji_chars = (
                "🐛✨🔧⚙️🚀✅🛑🚫‼️❗️❌🚨⚠️⚠️↩️↪️🎯🔁🔄⏭️"
                "😀😁😂🤣😃😄😅😆😉😊😋😎😍😘😗😙😚🙂"
                "🤗🤔🤐😐😑😶😏😣😥😮🤐😯😪😫😴😌😛😜"
                "😝🤤😒😓😔😕🙃🤑😲☹🙁😖😞😟😤😢😭"
                "😦😧😨😩🤯😬😰😱😳🤪😵😡😠🤬😷🤒🤕"
                "🤢🤮🤧😇🤠🤡🤥🤫🤭🧐🤓😈👿👹👺💀"
                "👻👽👾🤖💩😺😸😹😻😼😽🙀😿😾📦🔍📖🥳"
            )
            adjustment = 1 if any(
                char in status for char in emoji_chars
            ) else 0
            adjustment += -1 if any(char in status for char in "ℹ️") else 0
            if status == "SKIPPED":
                adjustment += -11
                status = f"{LogTools.BOLD_YELLOW}{status}{LogTools.RESET}"
            return adjustment

        def _format_pre_commit(self, msg, status, max_msg_length):
            """
            Formats the message in pre-commit style.

            Args:
                msg (str): The log message.
                status (str): The status message.
                max_msg_length (int): The maximum allowed length of the
                message.

            Returns:
                str: The formatted message.
            """
            if len(msg) > max_msg_length:
                msg = msg[: max_msg_length - 3] + "..."
            padding = max_msg_length - len(msg)
            return f"{msg}{'.' * padding} {status}"

        def _format_basic(self, msg, status, max_msg_length):
            """
            Formats the message in basic style.

            Args:
                msg (str): The log message.
                status (str): The status message.
                max_msg_length (int): The maximum allowed length of the
                message.

            Returns:
                str: The formatted message.
            """
            if len(msg) > max_msg_length:
                msg = msg[: max_msg_length - 3] + "..."
            padding = max_msg_length - len(msg)
            return f"{msg}{' ' * padding} {status}"

        def _format_default(self, msg, status, max_msg_length):
            """
            Formats the message in default style.

            Args:
                msg (str): The log message.
                status (str): The status message.
                max_msg_length (int): The maximum allowed length of the
                message.

            Returns:
                str: The formatted message.
            """
            if status:
                max_msg_length -= 4  # Account for "... "
            if len(msg) > max_msg_length:
                msg = msg[: max_msg_length - 3] + "..."
            padding = max_msg_length - len(msg)
            if status:
                return f"{msg}... {' ' * padding} {status}"
            return f"{msg}{' ' * padding} {status}"

        def debug(self, *args, **kwargs):
            """Log a debug message."""
            self._log(logging.DEBUG, *args, **kwargs)

        def info(self, *args, **kwargs):
            """Log an info message."""
            self._log(logging.INFO, *args, **kwargs)

        def warning(self, *args, **kwargs):
            """Log a warning message."""
            self._log(logging.WARNING, *args, **kwargs)

        def error(self, *args, **kwargs):
            """Log an error message."""
            self._log(logging.ERROR, *args, **kwargs)

        def critical(self, *args, **kwargs):
            """Log a critical message."""
            self._log(logging.CRITICAL, *args, **kwargs)

        def exception(self, *args, exc_info=True, **kwargs):
            """Log an exception with traceback."""
            kwargs["exc_info"] = exc_info
            self._log(logging.ERROR, *args, **kwargs)
            if exc_info:
                import traceback  # pylint: disable=C0415

                tb = traceback.format_exc()
                self._log(logging.ERROR, tb, style="none")

        def log(self, level, *args, **kwargs):
            """
            Logs a message with a specific log level.

            Args:
                level (int): The log level to use.
                *args: Variable length argument list for the log message.
                **kwargs: Arbitrary keyword arguments for the log message.
            """
            self._log(level, *args, **kwargs)

        def set_log_level(self, level):
            """
            Sets the logging level for the logger.

            Args:
                level (str): The logging level to set.
            """
            self.logger.setLevel(level)

        def get_effective_level(self):
            """
            Gets the effective logging level of the logger.

            Returns:
                int: The effective logging level.
            """
            return self.logger.getEffectiveLevel()

        def is_enabled_for(self, level):
            """
            Checks if the logger is enabled for the given logging level.

            Args:
                level (int): The logging level to check.

            Returns:
                bool: True if the logger is enabled for the level, False
                      otherwise.
            """
            return self.logger.isEnabledFor(level)

        def add_handler(self, hdlr):
            """
            Adds the specified handler to the logger.

            Args:
                hdlr (logging.Handler): The handler to add.
            """
            self.logger.addHandler(hdlr)

        def remove_handler(self, hdlr):
            """
            Removes the specified handler from the logger.

            Args:
                hdlr (logging.Handler): The handler to remove.
            """
            self.logger.removeHandler(hdlr)

        def has_handlers(self):
            """
            Checks if the logger has any handlers configured.

            Returns:
                bool: True if the logger has handlers, False otherwise.
            """
            return self.logger.hasHandlers()

        def call_handlers(self, record):
            """
            Passes the log record to all handlers for the logger.

            Args:
                record (logging.LogRecord): The log record to handle.
            """
            self.logger.callHandlers(record)

        def handle(self, record):
            """
            Handles the log record by passing it to all handlers.

            Args:
                record (logging.LogRecord): The log record to handle.
            """
            self.logger.handle(record)

        def make_record(self, *args, **kwargs):
            """
            Creates a log record with the given arguments.

            Args:
                *args: Variable length argument list for creating the log
                       record.
                **kwargs: Arbitrary keyword arguments for creating the log
                          record.

            Returns:
                logging.LogRecord: The created log record.
            """
            return self.logger.makeRecord(*args, **kwargs)

        def find_caller(self, *args, **kwargs):
            """
            Finds the caller's source file and line number.

            Args:
                *args: Variable length argument list for finding the caller.
                **kwargs: Arbitrary keyword arguments for finding the caller.

            Returns:
                tuple: The source file name and line number of the caller.
            """
            return self.logger.findCaller(*args, **kwargs)

        def get_child(self, suffix):
            """
            Creates a child logger with the given suffix.

            Args:
                suffix (str): The suffix for the child logger.

            Returns:
                logging.Logger: The created child logger.
            """
            return self.logger.getChild(suffix)

        def __repr__(self):
            return repr(self.logger)

        def method_state(
            self,
            message: Optional[str] = None,
            style: str = "default",
            status: str = "OK",
            reason: Optional[str] = None,
        ) -> Callable:
            """
            Decorator to log the state of a method with given style and status.

            This decorator is useful for providing user-friendly logging where
            system-style logging might be too verbose or confusing for the
            reader.

            Args:
                message: The message to log. If not provided, the function name
                        will be used.
                style: The style of the log output. Defaults to "default".
                status: The status to log. Defaults to "OK".
                reason: The reason for the status, displayed in parentheses
                        before the status.

            Returns:
                The decorated function with logging.

            Example:
                @log_tools.method_state(
                    message="Install numpy",
                    style="pre-commit"
                )
                def install_numpy():
                    return "pip install -q numpy"

                install_numpy()

                # Output:
                # Running Install numpy.................................Passed
            """

            # Define the decorator function
            def decorator(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    display_message = message if message else func.__name__
                    padding = 72 - len(f"Running {display_message}... ")
                    if style == "pre-commit":
                        display_message = self._format_pre_commit(
                            display_message, status, reason
                        )
                        print(display_message, end="", flush=True)
                    else:
                        print(
                            f"Running {display_message}... " + " " * padding,
                            end="",
                            flush=True,
                        )

                    # Capture stdout and stderr to handle method output
                    old_stdout = sys.stdout
                    old_stderr = sys.stderr
                    sys.stdout = io.StringIO()
                    sys.stderr = io.StringIO()

                    try:
                        result = func(*args, **kwargs)
                        stdout = sys.stdout.getvalue()

                        # Determine the color based on the status
                        color = (
                            LogTools.BOLD_GREEN
                            if status == "OK"
                            else (
                                LogTools.BOLD_YELLOW
                                if status == "WARNING"
                                else LogTools.BOLD_RED
                            )
                        )

                        return result, stdout, color, display_message
                    # pylint: disable=broad-except
                    except Exception as e:
                        # Here's the change: use self.parent.log_message
                        # instead of self.log_message
                        self.parent.log_message.error(
                            message=f"An unexpected error occurred: {str(e)}"
                        )
                        return (
                            None,
                            "",
                            f"ERROR: {str(e)}",
                            LogTools.BOLD_RED,
                            display_message,
                        )
                    finally:
                        # Restore stdout and stderr to their original state
                        sys.stdout = old_stdout
                        sys.stderr = old_stderr

                def print_status(stdout, color, display_message):
                    """
                    Prints the status of the method after it has been executed.

                    Args:
                        stdout: The captured standard output.
                        color: The color to display the status.
                        display_message: The message to display.
                    """
                    if style == "pre-commit":
                        print(f"{color}{status}{LogTools.RESET}", flush=True)
                    elif style == "basic":
                        padding = 77 - len(
                            f"Running {display_message} {status}"
                            )
                        print(
                            f"\rRunning {display_message}"
                            f"{' ' * padding}{color}{status}"
                            f"{LogTools.RESET}",
                            flush=True,
                        )
                    else:  # default style
                        print(f"{color}{status}{LogTools.RESET}", flush=True)

                    if self.parent.debug and stdout:
                        print(
                            f"{LogTools.BOLD_GREEN}INFO "
                            f"DEBUG:\n{LogTools.RESET}{stdout}",
                            flush=True,
                        )

                def execute(*args, **kwargs):
                    result, stdout, color, display_message = \
                        wrapper(*args, **kwargs)
                    print_status(stdout, color, display_message)
                    return result

                return execute

            return decorator

    def command_state(
        self,
        commands: List[Tuple[str, str]],
        style: str = "default",
        status: str = "Passed",
        reason: Optional[str] = None,
    ) -> None:
        """
        Runs a list of shell commands and logs their output.

        This method is useful for providing user-friendly logging for shell
        commands.

        Args:
            commands: List of tuples, each containing (command, name).
            style: The style of the log output. Defaults to "default".
            status: The status message to log. Defaults to "Passed".
            reason: The reason for the status, displayed in parentheses before
                    the status.

        Raises:
            subprocess.CalledProcessError: If a command fails to execute.

        Example:
            commands = [
                ("pip install -q numpy", "Install numpy"),
                ("echo 'Hello, World!'", "Print greeting")
            ]
            log_tools.command_state(commands, style="pre-commit")

            # Output:
            # Running Install numpy.................................Passed
            # Running Print greeting................................Passed
        """
        # Iterate over the list of commands and log their output
        for command, name in commands:
            display_name = name if name else f"'{command}'"
            padding = 72 - len(f"Running {display_name}... ")
            if style == "pre-commit":
                display_name = self._format_pre_commit(
                    display_name, status, reason
                )
                print(display_name, end="", flush=True)
            elif style == "basic":
                padding = 77 - len(f"Running {display_name} {status}")
                print(
                    f"Running {display_name}{' ' * padding}{status}",
                    flush=True,
                )
            else:  # default style
                print(
                    f"Running {display_name}... " + " " * padding,
                    end="",
                    flush=True,
                )

            # Capture stdout and stderr to handle command output
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            try:
                result = subprocess.run(
                    command,
                    check=True,
                    shell=True,
                    capture_output=True,
                    text=True,
                )
                stdout = result.stdout

                # Determine the color based on the status
                color = (
                    LogTools.BOLD_GREEN
                    if status == "Passed"
                    else (
                        LogTools.BOLD_YELLOW
                        if status == "WARNING"
                        else LogTools.BOLD_RED
                    )
                )

                # Restore stdout and stderr to their original state
                sys.stdout = old_stdout
                sys.stderr = old_stderr

                # Print the status
                if style == "pre-commit":
                    print(f"{color}{status}{LogTools.RESET}", flush=True)
                elif style == "basic":
                    # This case is already handled above
                    pass
                else:  # default style
                    print(f"{color}{status}{LogTools.RESET}", flush=True)

                if self.debug and stdout:
                    self.log_message.info(f"INFO DEBUG:\n{stdout}")
            except subprocess.CalledProcessError as e:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                print(f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}", flush=True)
                if self.debug:
                    self.log_message.error(f"ERROR DEBUG:\n{e.stderr}")
                raise e
            finally:
                # Ensure stdout and stderr are restored
                sys.stdout = old_stdout
                sys.stderr = old_stderr

    @staticmethod
    def _format_pre_commit(message, status, reason=None):
        """
        Formats the message in pre-commit style.

        Args:
            message (str): The message to format.
            status (str): The status to append to the message.
            reason (str, optional): The reason for the status. Defaults to
            None.

        Returns:
            str: The formatted message.
        """
        # Define the maximum length for the message
        max_length = 60
        padding_char = "."
        status_length = len(status) + 2 if reason else len(status)
        message_lines = []

        while len(message) > max_length:
            split_index = message.rfind(" ", 0, max_length)
            if split_index == -1:
                split_index = max_length
            message_lines.append(message[:split_index])
            message = message[split_index:].strip()

        if message:
            message_lines.append(message)

        formatted_message = ""
        for i, line in enumerate(message_lines):
            if i == len(message_lines) - 1:
                padding = max_length - len(line) - status_length
                formatted_message += line + padding_char * padding
                if reason:
                    formatted_message += f"({reason})"
                formatted_message += status
            else:
                formatted_message += line + "\n"

        return formatted_message
