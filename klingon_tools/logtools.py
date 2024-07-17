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
        DEBUG (bool): Flag to enable debug mode. BOLD_GREEN (str): ANSI escape
        code for bold green text. BOLD_YELLOW (str): ANSI escape code for bold
        yellow text. BOLD_RED (str): ANSI escape code for bold red text. RESET
        (str): ANSI escape code to reset text formatting. logger
        (logging.Logger): Logger instance for logging messages. template (str):
        Template for log messages.
    """

    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_RED = "\033[1;31m"
    RESET = "\033[0m"
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO, format="%(message)s"
    )  # Default logging level without prefix

    template = None

    @classmethod
    def set_template(cls, template):
        """Sets the template for log messages.

        Args:
            template (str): The template to use for log messages.
        """
        # Set the class-level template for log messages
        cls.template = template

    VALID_STYLES = ["default", "pre-commit", "basic"]

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

    def __init__(self, debug=False):
        """Initializes LogTools with an optional debug flag.

        Args:
            debug (bool): Flag to enable debug mode. Defaults to False.
        """
        # Initialize the logger and set the debug flag
        self.DEBUG = debug
        self.log_message = LogTools.LogMessage(__name__, self)
        self.logger = logging.getLogger(__name__)
        if self.DEBUG:
            self.configure_logging()

    def configure_logging(self):
        """Configures the logging level to DEBUG."""
        logging.basicConfig(level=logging.DEBUG)
        self.logger.setLevel(logging.DEBUG)
        self.log_message.setLevel(logging.DEBUG)

    class LogMessage:
        """Handles logging messages with a given severity, style, status, and
        reason.

        This class provides methods to log messages with different severity
        levels (info, warning, error, etc.) and supports custom templates for
        log messages.

        Args:
            name (str): The name of the logger.
        """

        # Initialize the logger with the given name
        def __init__(self, name, parent):
            self.logger = logging.getLogger(name)
            self.parent = parent

        def _log(
            self,
            level,
            msg=None,
            style=None,
            status="OK",
            reason=None,
            *args,
            **kwargs,
        ):
            if style is None:
                style = (
                    self.parent.default_style
                    if hasattr(self.parent, "default_style")
                    else "default"
                )
            if style not in self.parent.VALID_STYLES:
                raise ValueError(
                    f"Invalid style '{style}'. Valid styles are: "
                    f"{', '.join(self.parent.VALID_STYLES)}"
                )
            if "message" in kwargs:
                msg = kwargs.pop("message")
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
                    for char in "🐛✨🔧⚙️🚀✅🛑🚫‼️❗️❌🚨⚠️⚠️↩️↪️🎯🔁🔄⏭️😀😁😂🤣"
                    "😃😄😅😆😉😊😋😎😍😘😗😙😚🙂🤗🤔🤐"
                    "😐😑😶😏😣😥😮🤐😯😪😫😴😌😛😜😝🤤"
                    "😒😓😔😕🙃🤑😲☹🙁😖😞😟😤😢😭😦😧"
                    "😨😩🤯😬😰😱😳🤪😵😡😠🤬😷🤒🤕🤢"
                    "🤮🤧😇🤠🤡🤥🤫🤭🧐🤓😈👿👹👺💀👻"
                    "👽👾🤖💩😺😸😹😻😼😽🙀😿😾📦🔍📖🥳"
                )
                else 0
            )
            if style == "pre-commit":
                padding = 80 - len(f"{msg} {status}") - emoji_adjustment
                msg = f"{msg}{'.' * padding}{status}"
            elif style == "basic":
                padding = 80 - len(f"{msg} {status}") - emoji_adjustment
                msg = f"{msg}{' ' * padding}{status}"
            elif style == "default" and status == "":
                padding = 76 - len(f"{msg} {status}") - emoji_adjustment
                msg = f"{msg}{' ' * padding}{status}"
            elif style == "default":
                padding = 76 - len(f"{msg} {status}") - emoji_adjustment
                msg = f"{msg}... {' ' * padding}{status}"

            else:
                padding = 76 - len(f"{msg} {status}") - emoji_adjustment
                msg = f"{msg}... {' ' * padding}{status}"
            self.logger.log(level, msg, *args, **kwargs)

        def debug(self, msg=None, *args, **kwargs):
            self._log(logging.DEBUG, msg, *args, **kwargs)

        def info(self, msg=None, *args, **kwargs):
            self._log(logging.INFO, msg, *args, **kwargs)

        def warning(self, msg=None, *args, **kwargs):
            self._log(logging.WARNING, msg, *args, **kwargs)

        def error(self, msg=None, *args, **kwargs):
            self._log(logging.ERROR, msg, *args, **kwargs)

        def critical(self, msg=None, *args, **kwargs):
            self._log(logging.CRITICAL, msg, *args, **kwargs)

        def exception(self, msg=None, *args, exc_info=True, **kwargs):
            self._log(logging.ERROR, msg, exc_info=exc_info, *args, **kwargs)

        def log(self, level, msg, *args, **kwargs):
            self._log(level, msg, *args, **kwargs)

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
                # Handle exceptions and log errors
                # Capture stdout and stderr to handle method output
                if style == "pre-commit":
                    display_message = self._format_pre_commit(
                        display_message, status, reason
                    )
                    print(display_message, end="")
                else:
                    print(
                        f"Running {display_message}... " + " " * padding,
                        end="",
                    )

                # Capture stdout and stderr to handle method output
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = io.StringIO()
                sys.stderr = io.StringIO()

                try:
                    result = func(*args, **kwargs)
                    stdout = sys.stdout.getvalue()
                    stderr = sys.stderr.getvalue()

                    # Check the result and log accordingly
                    if result is None or result:
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
                        if style == "pre-commit":
                            print(f"{color}{status}{LogTools.RESET}")
                        elif style == "basic":
                            padding = 77 - len(
                                f"Running {display_message} {status}"
                            )
                            print(
                                f"\rRunning {display_message}"
                                f"{' ' * padding}{color}{status}"
                                f"{LogTools.RESET}"
                            )
                        if self.DEBUG and stdout:
                            print(
                                f"{LogTools.BOLD_GREEN}INFO "
                                f"DEBUG:\n{LogTools.RESET}{stdout}"
                            )
                    elif result == 1:  # Assuming '1' is a warning
                        # Log a warning message
                        if style == "pre-commit":
                            print(
                                f"{LogTools.BOLD_YELLOW}{status}"
                                f"{LogTools.RESET}"
                            )
                        else:
                            print(
                                f"\rRunning {display_message}... "
                                f"{' ' * padding}"
                                f"{LogTools.BOLD_YELLOW}WARNING"
                                f"{LogTools.RESET}"
                            )
                        if self.DEBUG and stdout:
                            self.log_message.warning(
                                f"WARNING DEBUG:\n{stdout}"
                            )
                    else:
                        if style == "pre-commit":
                            print(
                                f"{LogTools.BOLD_RED}{status}{LogTools.RESET}"
                            )
                        else:
                            print(
                                f"\rRunning {display_message}... "
                                + " " * padding
                                + f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}"
                            )
                        if self.DEBUG and stderr:
                            self.log_message.error(f"ERROR DEBUG:\n{stderr}")
                except Exception as e:
                    # Handle exceptions and log errors
                    if style == "pre-commit":
                        print(f"{LogTools.BOLD_RED}{status}{LogTools.RESET}")
                    elif style == "basic":
                        padding = 77 - len(
                            f"Running {display_message} {status}"
                        )
                        print(
                            f"\rRunning {display_message}"
                            f"{' ' * padding}{LogTools.BOLD_RED}ERROR"
                            f"{LogTools.RESET}"
                        )
                    stderr = sys.stderr.getvalue()
                    if self.DEBUG and stderr:
                        self.log_message.info(f"ERROR DEBUG:\n{stdout}")
                    raise e
                finally:
                    # Restore stdout and stderr to their original state
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

            return wrapper

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
                print(display_name, end="")
            elif style == "basic":
                padding = 77 - len(f"Running {display_name} {status}")
                print(f"Running {display_name}{' ' * padding}{status}")

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
                stderr = result.stderr

                # Check the return code and log accordingly
                if result.returncode == 0:
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
                    if style == "pre-commit":
                        print(f"{color}{status}{LogTools.RESET}")
                    else:
                        print(
                            f"\rRunning {display_name}... "
                            + " " * padding
                            + f"{color}{status}{LogTools.RESET}"
                        )
                    if self.DEBUG and stdout:
                        self.log_message.info(f"INFO DEBUG:\n{stdout}")
                elif result.returncode == 1:  # Assuming '1' is a warning
                    # Log a warning message
                    if style == "pre-commit":
                        print(
                            f"{LogTools.BOLD_YELLOW}{status}{LogTools.RESET}"
                        )
                    else:
                        print(
                            f"\rRunning {display_name}... "
                            + " " * padding
                            + f"{LogTools.BOLD_YELLOW}WARNING{LogTools.RESET}"
                        )
                    if self.DEBUG and stdout:
                        self.log_message.warning(f"WARNING DEBUG:\n{stdout}")
                else:
                    if style == "pre-commit":
                        print(f"{LogTools.BOLD_RED}{status}{LogTools.RESET}")
                    elif style == "basic":
                        padding = 77 - len(f"Running {display_name} {status}")
                        print(
                            f"\rRunning {display_name}"
                            f"{' ' * padding}{LogTools.BOLD_RED}ERROR"
                            f"{LogTools.RESET}"
                        )
                    if self.DEBUG and stderr:
                        self.log_message.info(f"ERROR DEBUG:\n{stdout}")
            except subprocess.CalledProcessError as e:
                if style == "pre-commit":
                    print(f"{LogTools.BOLD_RED}{status}{LogTools.RESET}")
                else:
                    print(
                        f"\rRunning {display_name}... "
                        + " " * padding
                        + f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}"
                    )
                stderr = sys.stderr.getvalue()
                if self.DEBUG and stderr:
                    self.log_message.info(f"ERROR DEBUG:\n{stdout}")
                raise e
            finally:
                # Restore stdout and stderr to their original state
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
