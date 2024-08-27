"""
klingon_tools.logtools

This module provides utilities for running and logging shell commands in a
user-friendly manner. It includes the LogTools class, which offers decorators
for methods and CLI commands to log output in a clean and consistent manner
with simple error handling.

Classes:
    LogTools: A utility class for running and logging Python methods and shell
    commands. LogTools.LogMessage: Handles logging messages with a given
    severity, style, status, and reason.

Functions:
    method_state: Decorator to log the state of a method with a given style,
    status, and reason. command_state: Runs a list of shell commands and logs
    their output with a given style, status, and reason. _format_pre_commit:
    Formats the message in pre-commit style.
"""

import io
import logging
import subprocess
import sys
from functools import wraps


class LogTools:
    """
    A utility class for running and logging Python methods and shell commands
    in a user-friendly manner.

    This class provides decorators for methods and CLI commands that log output
    in a clean and consistent manner with simple error handling.

    Attributes:
        debug (bool): Flag to enable debug mode.
        logger(logging.Logger): Logger instance for logging messages.
        template (str): Template for log messages.
    """

    VALID_STYLES = ["default", "pre-commit", "basic", "none"]

    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_RED = "\033[1;31m"
    RESET = "\033[0m"
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    template = None

    def __init__(self, debug):
        """Initializes LogTools with an optional debug flag.

        Args:
            debug (bool): Flag to enable debug mode. Defaults to False.
        """
        # Initialize the logger and set the debug flag
        self.DEBUG = debug
        self.default_style = "default"  # Set a default style
        self.log_message = LogTools.LogMessage(__name__, self)
        self.logger = logging.getLogger(__name__)
        self.set_log_level("DEBUG" if self.DEBUG else "INFO")

    def set_default_style(self, style):
        """Sets the default style for log messages.

        Args:
            style (str): The style to use for log messages.

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

    def set_log_level(self, level):
        """Sets the logging level for the logger.

        Args:
            level (str): The logging level to set (e.g., 'DEBUG', 'INFO').
        """
        # If level is not INFO print a message saying the level being set. Also
        # make sure that the level is in uppercase and a valid level
        level = level.upper()
        if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(
                f"Invalid log level '{level}'. Valid levels are: "
                "'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'"
            )
        if level != "INFO":
            print(f"Setting log level to {level}")

        self.logger.setLevel(level)
        self.log_message.setLevel(level)

    @classmethod
    def set_template(cls, template):
        """Sets the template for log messages.

        Args:
            template (str): The template to use for log messages.
        """
        # Set the class-level template for log messages
        cls.template = template

    def configure_logging(self):
        # Placeholder for logging configuration
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    class LogMessage:
        """Handles logging messages with a given severity, style, status, and
        reason.

        This class provides methods to log messages with different severity
        levels (info, warning, error, etc.) and supports custom templates for
        log messages.

        Args:
            name (str): The name of the logger.
        """

        def __init__(self, name, parent):
            self.logger = logging.getLogger(name)
            self.parent = parent
            self.default_style = "default"

        def _log(
            self,
            level,
            *args,
            **kwargs
        ):
            msg = kwargs.get('message') or (args[0] if args else None)
            style = kwargs.get('style', self.default_style)
            status = kwargs.get('status', "OK")
            reason = kwargs.get('reason')

            if style is None:
                # Output plain text without formatting when style is None
                final_msg = msg
                self.logger.log(level, final_msg)
                return

            if style not in self.parent.VALID_STYLES:
                raise ValueError(
                    f"Invalid style '{style}'. Valid styles are: "
                    f"{', '.join(self.parent.VALID_STYLES)}"
                )

            if reason:
                msg = f"{msg} ({reason})"
            if self.parent.template:
                msg = self.parent.template.format(
                    message=msg, style=style, status=status
                )

            emoji_adjustment = (
                1
                if any(
                    char in status
                    for char in "🐛✨🔧⚙️🚀✅🛑🚫‼️❗️❌🚨⚠️⚠️↩️↪️🎯🔁🔄⏭️"
                    "😀😁😂🤣😃😄😅😆😉😊😋😎😍😘😗😙😚🙂"
                    "🤗🤔🤐😐😑😶😏😣😥😮🤐😯😪😫😴😌😛😜"
                    "😝🤤😒😓😔😕🙃🤑😲☹🙁😖😞😟😤😢😭"
                    "😦😧😨😩🤯😬😰😱😳🤪😵😡😠🤬😷🤒🤕"
                    "🤢🤮🤧😇🤠🤡🤥🤫🤭🧐🤓😈👿👹👺💀"
                    "👻👽👾🤖💩😺😸😹😻😼😽🙀😿😾📦🔍📖🥳"
                )
                else 0
            )

            total_length = 79
            status_length = len(status) + emoji_adjustment
            max_msg_length = (
                total_length - status_length - 1
            )  # -1 for space between msg and status

            if style == "pre-commit":
                if len(msg) > max_msg_length:
                    msg = msg[: max_msg_length - 3] + "..."
                padding = max_msg_length - len(msg)
                msg = f"{msg}{'.' * padding} {status}"
            elif style == "basic":
                if len(msg) > max_msg_length:
                    msg = msg[: max_msg_length - 3] + "..."
                padding = max_msg_length - len(msg)
                msg = f"{msg}{' ' * padding} {status}"
            elif style == "default":
                if status:
                    max_msg_length -= 4  # Account for "... "
                if len(msg) > max_msg_length:
                    msg = msg[: max_msg_length - 3] + "..."
                padding = max_msg_length - len(msg)
                if status:
                    msg = f"{msg}... {' ' * padding} {status}"
                else:
                    msg = f"{msg}{' ' * padding} {status}"
            elif style == "none":
                final_msg = msg
                self.logger.log(level, final_msg)
                return

            final_msg = msg.ljust(total_length)
            self.logger.log(level, final_msg)

        def debug(self, *args, **kwargs):
            self._log(logging.DEBUG, *args, **kwargs)

        def info(self, *args, **kwargs):
            self._log(logging.INFO, *args, **kwargs)

        def warning(self, *args, **kwargs):
            self._log(logging.WARNING, *args, **kwargs)

        def error(self, *args, **kwargs):
            self._log(logging.ERROR, *args, **kwargs)

        def critical(self, *args, **kwargs):
            self._log(logging.CRITICAL, *args, **kwargs)

        def exception(self, *args, exc_info=True, **kwargs):
            kwargs['exc_info'] = exc_info
            self._log(logging.ERROR, *args, **kwargs)
            if exc_info:
                import traceback
                tb = traceback.format_exc()
                self._log(logging.ERROR, tb, style="none")

        def log(self, level, *args, **kwargs):
            self._log(level, *args, **kwargs)

        def setLevel(self, level):
            self.logger.setLevel(level)

        def getEffectiveLevel(self):
            return self.logger.getEffectiveLevel()

        def isEnabledFor(self, level):
            return self.logger.isEnabledFor(level)

        def addHandler(self, hdlr):
            self.logger.addHandler(hdlr)

        def removeHandler(self, hdlr):
            self.logger.removeHandler(hdlr)

        def hasHandlers(self):
            return self.logger.hasHandlers()

        def callHandlers(self, record):
            self.logger.callHandlers(record)

        def handle(self, record):
            self.logger.handle(record)

        def makeRecord(self, *args, **kwargs):
            return self.logger.makeRecord(*args, **kwargs)

        def findCaller(self, *args, **kwargs):
            return self.logger.findCaller(*args, **kwargs)

        def getChild(self, suffix):
            return self.logger.getChild(suffix)

        def __repr__(self):
            return repr(self.logger)

    def method_state(
        self, message=None, style="default", status="OK", reason=None
    ):
        """
        Decorator to log the state of a method with a given style, status, and
        reason.

        This is useful for providing user-friendly logging where system-style
        logging is too much or likely to cause confusion for the reader.

        Args:
            message (str): The message to log. Can be provided as a positional
            or keyword argument. style (str, optional): The style of the log
            output. Defaults to "default". status (str, optional): The status
            message to log on the far right. Defaults to "OK". reason (str,
            optional): The reason for the status message, displayed in round
            brackets just to the left of `status`. Defaults to None.

        Returns:
            function: The decorated function with logging.

        Example with Styles:
            **Default Style**
                from klingon_tools.logtools import LogTools

                log_tools = LogTools(debug=True)

                @log_tools.method_state(message="Install numpy",
                style="default") def install_numpy():
                    return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

                install_numpy()

            **Expected output**
                Running Install numpy...
                OK

            **Pre-commit Style**
                from klingon_tools.logtools import LogTools

                log_tools = LogTools(debug=True)

                @log_tools.method_state(message="Install numpy",
                style="pre-commit", status="Passed", reason="All tests passed")
                def install_numpy():
                    return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

                install_numpy()

            **Expected Output**
                Running Install
                numpy.................................................Passed
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
                except Exception as e:
                    return None, "", str(e), LogTools.BOLD_RED, display_message
                finally:
                    # Restore stdout and stderr to their original state
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

            def print_status(result, stdout, color, display_message):
                if style == "pre-commit":
                    print(f"{color}{status}{LogTools.RESET}", flush=True)
                elif style == "basic":
                    padding = 77 - len(f"Running {display_message} {status}")
                    print(
                        f"\rRunning {display_message}"
                        f"{' ' * padding}{color}{status}"
                        f"{LogTools.RESET}",
                        flush=True,
                    )
                else:  # default style
                    print(f"{color}{status}{LogTools.RESET}", flush=True)

                if self.DEBUG and stdout:
                    print(
                        f"{LogTools.BOLD_GREEN}INFO "
                        f"DEBUG:\n{LogTools.RESET}{stdout}",
                        flush=True,
                    )

            def execute(*args, **kwargs):
                result, stdout, color, display_message = wrapper(
                    *args, **kwargs
                )
                print_status(result, stdout, color, display_message)
                return result

            return execute

        return decorator

    def command_state(
        self, commands, style="default", status="Passed", reason=None
    ):
        """
        Runs a list of shell commands and logs their output with a given style,
        status, and reason.

        This is useful for providing user-friendly logging for shell commands.

        Args:
            commands (list of tuples): Each tuple contains (command, name).
            style (str, optional): The style of the log output. Defaults to
            "default". status (str, optional): The status message to log on the
            far right. Defaults to "Passed". reason (str, optional): The reason
            for the status message, displayed in round brackets just to the
            left of `status`. Defaults to None.

        Example with Styles:
            **Default Style**
                from klingon_tools.logtools import LogTools

                log_tools = LogTools(debug=True)

                commands = [
                    ("PIP_ROOT_USER_ACTION=ignore pip install -q numpy",
                    "Install numpy"), ("echo 'Hello, World!'", "Print Hello
                    World")
                ]

                log_tools.command_state(commands)

            **Expected output**
                Running Install numpy...
                Passed Running Print Hello World...
                Passed

            **Pre-commit Style**
                from klingon_tools.logtools import LogTools

                log_tools = LogTools(debug=True)

                commands = [
                    ("PIP_ROOT_USER_ACTION=ignore pip install -q numpy",
                    "Install numpy"), ("echo 'Hello, World!'", "Print Hello
                    World")
                ]

                log_tools.command_state(commands, style="pre-commit",
                status="Passed", reason="All tests passed")

            **Expected Output**
                Running Install
                numpy.................................................Passed
                Running Print Hello
                World.............................................Passed
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

                if self.DEBUG and stdout:
                    self.log_message.info(f"INFO DEBUG:\n{stdout}")
            except subprocess.CalledProcessError as e:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                print(f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}", flush=True)
                if self.DEBUG:
                    self.log_message.error(f"ERROR DEBUG:\n{e.stderr}")
                raise e
            finally:
                # Ensure stdout and stderr are restored
                sys.stdout = old_stdout
                sys.stderr = old_stderr

    @staticmethod
    def _format_pre_commit(message, status, reason=None):
        """Formats the message in pre-commit style.

        Args:
            message (str): The message to format. status (str): The status to
            append to the message. reason (str, optional): The reason for the
            status. Defaults to None.

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
