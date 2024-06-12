import subprocess
from functools import wraps
import sys
import io


class LogTools:
    """
    A utility class for running and logging python methods and shell commands in a user-friendly manner.

    This class provides decorators for methods and cli commands that log output
    in a clean and consistent manner with simple error handling.

    Attributes:
        DEBUG (bool): Flag to enable debug mode.
        BOLD_GREEN (str): ANSI escape code for bold green text.
        BOLD_YELLOW (str): ANSI escape code for bold yellow text.
        BOLD_RED (str): ANSI escape code for bold red text.
        RESET (str): ANSI escape code to reset text formatting.

    Methods:
        log_message(message, category="INFO"): Log a message with a given category.
        method_state(name=None): Decorator to run and log shell commands.
        command_state(commands): Run a list of shell commands and log their output.
    """

    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_RED = "\033[1;31m"
    RESET = "\033[0m"

    template = None

    def __init__(self, debug=False):
        """
        Initialize LogTools with an optional debug flag.

        Args:
            debug (bool): Flag to enable debug mode. Defaults to False.
        """
        self.DEBUG = debug

    @classmethod
    def set_template(cls, template):
        """
        Set the template for log messages.

        Args:
            template (str): The template to use for log messages.
        """
        cls.template = template

    @staticmethod
    def log_message(
        message, category="INFO", style="default", status="OK", reason=None
    ):
        """
        Drop-in replacement for the classic python logging library. Is focussed on user
        experience and simplicity rather than system logging.

        The `log_message` method has three static methods:
         - `info`
           - log message in default text color
           - status in `green`
           - default status is `OK`
         - `warning`
           - log message in default text color
           - status in `yellow`
           - default status is `WARNING`
         - `error`
           - log message in default text color
           - status in `red`
           - default status is `ERROR`

        Args:
         - `message` (str): The message to log. Can be provided as a positional or keyword argument.
         - `category` (str, optional): The category of the message. Defaults to "INFO"
           but generally not used if log_message is called with the appropriate
           category method i.e. `LogTools.log_message.info("message")`
         - `style` (str, optional): The style of the log output. Defaults to "default".
         - `status` (str, optional): The status message to log on the far right. Defaults to "OK".
         - `reason` (str, optional): The reason for the status message, displayed in
           round brackets just to left of `status`. Defaults to None.

        Example Usage

        ```python

        from klingon_tools.logtools import LogTools

        logger = LogTools.log_message

        logger.info("Installing catapult")
        logger.warning("Low disk space")
        logger.error("Installation failed")

        ```

        Expected Output

        <pre>

        Running Installing catapult...                                               <span style="color: green;">OK</span>
        Running Low disk space...                                                    <span style="color: yellow;">WARNING</span>
        Running Installation failed...                                               <span style="color: red;">ERROR</span>

        </pre>
        """
        if LogTools.template:
            message = LogTools.template.format(
                message=message, category=category, style=style, status=status
            )

        color = (
            LogTools.BOLD_GREEN
            if category == "INFO"
            else LogTools.BOLD_YELLOW if category == "WARNING" else LogTools.BOLD_RED
        )
        padding = 72 - len(f"Running {message}... ")
        if style == "pre-commit":
            formatted_message = LogTools._format_pre_commit(message, status, reason)
            print(formatted_message, end="")
        else:
            reason_str = f"({reason})" if reason else ""
            print(
                f"Running {message}... "
                + " " * padding
                + f"{reason_str}{color}{status}{LogTools.RESET}"
            )

    @staticmethod
    def info(message, style="default", status="OK", reason=None):
        LogTools.log_message(
            message, category="INFO", style=style, status=status, reason=reason
        )

    @staticmethod
    def warning(message, style="default", status="WARNING", reason=None):
        LogTools.log_message(
            message, category="WARNING", style=style, status=status, reason=reason
        )

    @staticmethod
    def error(message, style="default", status="ERROR", reason=None):
        LogTools.log_message(
            message, category="ERROR", style=style, status=status, reason=reason
        )

    def method_state(self, message=None, style="default", status="OK", reason=None):
        """
        `method_state` is a decorator that logs the state of a method with a given
        style, status, and reason. This is useful for providing user friendly logging
        where system style logging is too much or likely to cause confusion for the
        reader.

        Args:
          - `message` (str): The message to log. Can be provided as a positional or keyword argument.
          - `style` (str, optional): The style of the log output. Defaults to "default".
          - `status` (str, optional): The status message to log on the far right. Defaults to "OK".
          - `reason` (str, optional): The reason for the status message, displayed in
          round brackets just to left of `status`. Defaults to None.

        Example with Styles

        **Default Style**

        ```python

        from klingon_tools.logtools import LogTools

        log_tools = LogTools(debug=True)

        @log_tools.method_state(message="Install numpy", style="default")
        def install_numpy():
            return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

        install_numpy()

        ```

        **Expected output**

        <pre>

        Running Install numpy...                                                     <span style="color: green;">OK</span>

        </pre>

        **Pre-commit Style**

        ```python

        from klingon_tools.logtools import LogTools

        log_tools = LogTools(debug=True)

        @log_tools.method_state(message="Install numpy", style="pre-commit", status="Passed", reason="All tests passed")
        def install_numpy():
            return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

        install_numpy()

        ```

        **Expected Output**

        <pre>

        Running Install numpy.................................................<span style="color: green;">Passed</span>

        </pre>
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                display_message = message if message else func.__name__
                padding = 72 - len(f"Running {display_message}... ")
                if style == "pre-commit":
                    display_message = self._format_pre_commit(
                        display_message, status, reason
                    )
                    print(display_message, end="")
                else:
                    print(f"Running {display_message}... " + " " * padding, end="")

                # Capture stdout and stderr
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = io.StringIO()
                sys.stderr = io.StringIO()

                try:
                    result = func(*args, **kwargs)
                    stdout = sys.stdout.getvalue()
                    stderr = sys.stderr.getvalue()

                    if result is None or result:
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
                        else:
                            print(
                                f"\rRunning {display_message}... "
                                + " " * padding
                                + f"{color}{status}{LogTools.RESET}"
                            )
                        if self.DEBUG and stdout:
                            print(
                                f"{LogTools.BOLD_GREEN}INFO DEBUG:\n{LogTools.RESET}{stdout}"
                            )
                    elif result == 1:  # Assuming '1' is a warning
                        if style == "pre-commit":
                            print(f"{LogTools.BOLD_YELLOW}{status}{LogTools.RESET}")
                        else:
                            print(
                                f"\rRunning {display_message}... "
                                + " " * padding
                                + f"{LogTools.BOLD_YELLOW}WARNING{LogTools.RESET}"
                            )
                        if self.DEBUG and stdout:
                            self.log_message(f"WARNING DEBUG:\n{stdout}", "WARNING")
                    else:
                        if style == "pre-commit":
                            print(f"{LogTools.BOLD_RED}{status}{LogTools.RESET}")
                        else:
                            print(
                                f"\rRunning {display_message}... "
                                + " " * padding
                                + f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}"
                            )
                        if self.DEBUG and stderr:
                            self.log_message(f"ERROR DEBUG:\n{stderr}", "ERROR")
                except Exception as e:
                    if style == "pre-commit":
                        print(f"{LogTools.BOLD_RED}{status}{LogTools.RESET}")
                    else:
                        print(
                            f"\rRunning {display_message}... "
                            + " " * padding
                            + f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}"
                        )
                    stderr = sys.stderr.getvalue()
                    if self.DEBUG and stderr:
                        self.log_message(f"ERROR DEBUG:\n{stderr}", "ERROR")
                    raise e
                finally:
                    # Restore stdout and stderr
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

            return wrapper

        return decorator

    def command_state(self, commands, style="default", status="Passed", reason=None):
        """
        `command_state` runs a list of shell commands and logs their output. This is useful for providing user-friendly logging for shell commands.

        Args:
          - `commands` (list of tuples): Each tuple contains (command, name).
          - `style` (str, optional): The style of the log output. Defaults to "default".
          - `status` (str, optional): The status message to log on the far right. Defaults to "Passed".
          - `reason` (str, optional): The reason for the status message, displayed in round brackets just to the left of `status`. Defaults to None.

        Example with Styles

        **Default Style**

        ```python

        from klingon_tools.logtools import LogTools

        log_tools = LogTools(debug=True)

        commands = [
            ("PIP_ROOT_USER_ACTION=ignore pip install -q numpy", "Install numpy"),
            ("echo 'Hello, World!'", "Print Hello World")
        ]

        log_tools.command_state(commands)

        ```

        **Expected output**

        <pre>

        Running Install numpy...                                                     <span style="color: green;">Passed</span>
        Running Print Hello World...                                                 <span style="color: green;">Passed</span>

        </pre>

        **Pre-commit Style**

        ```python

        from klingon_tools.logtools import LogTools

        log_tools = LogTools(debug=True)

        commands = [
            ("PIP_ROOT_USER_ACTION=ignore pip install -q numpy", "Install numpy"),
            ("echo 'Hello, World!'", "Print Hello World")
        ]

        log_tools.command_state(commands, style="pre-commit", status="Passed", reason="All tests passed")

        ```

        **Expected Output**

        <pre>

        Running Install numpy.................................................<span style="color: green;">Passed</span>
        Running Print Hello World.............................................<span style="color: green;">Passed</span>

        </pre>
        """
        for command, name in commands:
            display_name = name if name else f"'{command}'"
            padding = 72 - len(f"Running {display_name}... ")
            if style == "pre-commit":
                display_name = self._format_pre_commit(display_name, status, reason)
                print(display_name, end="")
            else:
                print(f"Running {display_name}... " + " " * padding, end="")

            # Capture stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            try:
                result = subprocess.run(
                    command, check=True, shell=True, capture_output=True, text=True
                )
                stdout = result.stdout
                stderr = result.stderr

                if result.returncode == 0:
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
                        self.log_message(f"INFO DEBUG:\n{stdout}", "INFO")
                elif result.returncode == 1:  # Assuming '1' is a warning
                    if style == "pre-commit":
                        print(f"{LogTools.BOLD_YELLOW}{status}{LogTools.RESET}")
                    else:
                        print(
                            f"\rRunning {display_name}... "
                            + " " * padding
                            + f"{LogTools.BOLD_YELLOW}WARNING{LogTools.RESET}"
                        )
                    if self.DEBUG and stdout:
                        self.log_message(f"WARNING DEBUG:\n{stdout}", "WARNING")
                else:
                    if style == "pre-commit":
                        print(f"{LogTools.BOLD_RED}{status}{LogTools.RESET}")
                    else:
                        print(
                            f"\rRunning {display_name}... "
                            + " " * padding
                            + f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}"
                        )
                    if self.DEBUG and stderr:
                        self.log_message(f"ERROR DEBUG:\n{stderr}", "ERROR")
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
                    self.log_message(f"ERROR DEBUG:\n{stderr}", "ERROR")
                raise e
            finally:
                # Restore stdout and stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr

    @staticmethod
    def _format_pre_commit(message, status, reason=None):
        """Format the message in pre-commit style."""
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
