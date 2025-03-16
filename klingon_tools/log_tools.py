import io
import logging
import subprocess
import sys
import textwrap
from functools import wraps
from typing import Optional, Callable, List, Tuple


class LogTools:
    """
    A utility class for running and logging Python methods and shell commands.

    This class provides decorators for methods and CLI commands that log output
    in a clean and consistent manner with simple error handling.
    """

    VALID_STYLES = ["default", "pre-commit", "basic", "none"]

    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_RED = "\033[1;31m"
    RESET = "\033[0m"
    logger = logging.getLogger(__name__)
    log_message = None
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Logging suppression configuration
    # Adjust logging for the following libraries to WARNING
    suppress_library_logging_warning = [
        "requests",
        "urllib3",
        "litellm",
        "httpx"
    ]

    # Set the log level for the libraries above to WARNING
    for lib in suppress_library_logging_warning:
        logging.getLogger(lib).setLevel(logging.WARNING)

    # Clear template values
    template = None

    def __init__(self, debug: bool) -> None:
        self.debug = debug
        self.default_style = "default"
        self.current_log_level = None  # Track the current log level
        if LogTools.log_message is None:
            LogTools.log_message = LogTools.LogMessage(__name__, self)
        self.log_message = LogTools.log_message
        self.klog_hr = LogTools.HorizontalRuleLogger(self.log_message)
        self.set_log_level("DEBUG" if self.debug else "INFO")

    def set_default_style(self, style: str) -> None:
        if style not in self.VALID_STYLES:
            raise ValueError(f"Invalid style '{style}'.")
        self.default_style = style
        self.log_message.default_style = style

    def set_log_level(self, level: str) -> None:
        level = level.upper()
        if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level '{level}'.")
        if level != self.current_log_level:
            self.current_log_level = level
            self.log_message.set_log_level(level)

    def get_log_level(self) -> int:
        """Get the current log level."""
        return self.log_message.logger.level

    @classmethod
    def set_template(cls, template: str) -> None:
        """Set the template for log messages."""
        cls.template = template

    class LogMessage:
        """
        Handles logging messages with a given severity, style, status, and
        reason.
        """

        def __init__(self, name, parent):
            self.logger = logging.getLogger(name)
            self.parent = parent
            self.default_style = "default"

        def _log(self, level, *args, **kwargs):
            msg = kwargs.get("message") or (args[0] if args else None)
            style = kwargs.get("style", self.default_style)
            status = kwargs.get("status", "OK")
            reason = kwargs.get("reason")
            width = kwargs.get("width", 0)  # For wrapping and formatting width
            indent = kwargs.get("indent", 0)  # For indenting wrapped lines

            if style not in self.parent.VALID_STYLES:
                raise ValueError(f"Invalid style '{style}'.")

            msg = self._prepare_message(msg, reason, status, style)
            final_msg = self._wrap_message(msg, width, indent)
            formatted_msg = self._format_message(
                final_msg, status, style, width)
            self.logger.log(level, formatted_msg)

            # If exc_info is True, log the exception info
            if kwargs.get('exc_info'):
                import traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tb_str = ''.join(
                    traceback.format_exception(
                        exc_type, exc_value, exc_traceback))
                self.logger.log(level, tb_str)

        def _wrap_message(self, msg, width, indent):
            """
            Wraps the message if a width is provided, with optional indent.
            """
            if width <= 0:
                return msg
            return textwrap.fill(
                msg, width=width, subsequent_indent=" " * indent)

        def _prepare_message(self, msg, reason, status, style):
            if reason:
                msg = f"{msg} ({reason})"
            if self.parent.template:
                msg = self.parent.template.format(
                    message=msg, style=style, status=status)
            return msg.strip()

        def _format_message(
                self,
                msg,
                status,
                style,
                language="Python",
                width=80):
            """
            Formats the message with optional styles and width handling.

            Args:
                msg (str): The message to format.
                status (str): Status of the operation.
                style (str): The style for the message (default, basic,
                pre-commit, none).
                language (str): The programming language (used for comment
                formatting).
                width (int): The total width of the message line.
            """

            # Use the provided width or default to 80 characters
            total_length = width if width > 0 else 80
            status_length = len(status)
            max_msg_length = total_length - status_length - 2

            if style == "none":
                return msg

            if style == "pre-commit":
                return self._format_pre_commit(msg, status, max_msg_length)
            if style == "basic":
                return self._format_basic(msg, status, max_msg_length)
            return self._format_default(msg, status, max_msg_length)

        @staticmethod
        def _format_pre_commit(msg, status, max_msg_length):
            if len(msg) > max_msg_length:
                msg = msg[: max_msg_length - 3] + "..."
            padding = max_msg_length - len(msg)
            return f"{msg}{'.' * padding} {status}"

        @staticmethod
        def _format_basic(msg, status, max_msg_length):
            if len(msg) > max_msg_length:
                msg = msg[: max_msg_length - 3] + "..."
            padding = max_msg_length - len(msg)
            return f"{msg}{' ' * padding} {status}"

        def _format_default(self, msg, status, max_msg_length):
            if len(msg) > max_msg_length:
                msg = msg[: max_msg_length - 3] + "..."
            padding = max_msg_length - len(msg)
            return f"{msg}{' ' * padding} {status}"

        def debug(self, *args, **kwargs):
            self._log(logging.DEBUG, *args, **kwargs)

        def info(self, *args, **kwargs):
            self._log(logging.INFO, *args, **kwargs)

        def warning(self, *args, **kwargs):
            self._log(logging.WARNING, *args, **kwargs)

        def error(self, *args, **kwargs):
            self._log(logging.ERROR, *args, **kwargs)

        def exception(self, *args, **kwargs):
            """Log an exception with ERROR level."""
            kwargs['exc_info'] = True
            self._log(logging.ERROR, *args, **kwargs)

        def critical(self, *args, **kwargs):
            self._log(logging.CRITICAL, *args, **kwargs)

        def get_log_level(self) -> int:
            """Get the current log level for the logger."""
            return self.logger.level

        def set_log_level(self, level: str) -> None:
            """Set the log level for the logger."""
            self.logger.setLevel(level)

    class HorizontalRuleLogger:
        """
        A simple logger for horizontal rules (lines of characters).
        """

        def __init__(self, log_message):
            self.log_message = log_message

        def _log_hr(self, level, char="=", width=80):
            hr_line = char * width
            self.log_message._log(
                level,
                message=hr_line,
                status="",
                style="none"
            )

        def info(self, char="=", width=80):
            self._log_hr(logging.INFO, char, width)

        def debug(self, char="=", width=80):
            self._log_hr(logging.DEBUG, char, width)

        def warning(self, char="=", width=80):
            self._log_hr(logging.WARNING, char, width)

        def error(self, char="=", width=80):
            self._log_hr(logging.ERROR, char, width)

        def critical(self, char="=", width=80):
            self._log_hr(logging.CRITICAL, char, width)

    def pre_commit_exception_log_message(
        self,
        exception_data: dict
    ) -> None:
        """Logs pre-commit exception details in a structured format."""
        # Format hook ID with right-aligned value
        hook_id = exception_data.get('hook_id', '').strip().title()
        self.log_message.error(
            f"- Hook id: {hook_id}", status="", style="none")

        # Format exit code with right-aligned value
        exit_code = str(exception_data.get('exit_code', ''))
        self.log_message.error(
            f"- Exit code: {exit_code}", status="", style="none")

        # Log exception messages
        messages = exception_data.get('exception_messages', [])
        if messages:
            for line in messages:
                if "files were modified by this hook" in line.lower():
                    self.log_message.error(
                        "Files Were Modified by This Hook",
                        status="",
                        style="none"
                    )
                else:
                    self.log_message.error(
                        line.strip(), status="", style="none")

    def method_state(
        self,
        message: Optional[str] = None,
        style: str = "default",
        status: str = "OK",
        reason: Optional[str] = None,
    ) -> Callable:
        """
        Decorator to log the state of a method with a given style and status.
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                display_message = message if message else func.__name__
                padding = 72 - len(f"Running {display_message}... ")
                print(f"Running {display_message}... " +
                      " " * padding, end="", flush=True)

                old_stdout = sys.stdout
                sys.stdout = io.StringIO()

                try:
                    result = func(*args, **kwargs)
                    stdout = sys.stdout.getvalue()
                    color = (LogTools.BOLD_GREEN if status == "OK"
                             else LogTools.BOLD_RED)
                    return result, stdout, color, display_message
                except Exception as e:
                    self.log_message.error(
                        message=f"An unexpected error occurred: {str(e)}")
                    return None, "", LogTools.BOLD_RED, display_message
                finally:
                    sys.stdout = old_stdout

            def execute(*args, **kwargs):
                result, stdout, color, display_message = wrapper(
                    *args, **kwargs)
                print(f"{color}{status}{LogTools.RESET} {status}", flush=True)
                self.log_message.info(
                    message=f"Command '{display_message}' completed with status: {status}"
                )
                if self.debug and stdout:
                    print(
                        f"{LogTools.BOLD_GREEN}"
                        f"INFO DEBUG:\n{LogTools.RESET}{stdout}"
                    )
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
        """
        for command, name in commands:
            display_message = name if name else f"'{command}'"
            padding = 72 - len(f"Running {display_message}... ")
            print(f"Running {display_message}... " +
                  " " * padding, end="", flush=True)

            old_stdout = sys.stdout
            sys.stdout = io.StringIO()

            try:
                result = subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True
                )
                stdout = result.stdout
                color = (LogTools.BOLD_GREEN
                         if status == "Passed"
                         else LogTools.BOLD_RED
                         )
                print(f"{color}{status}{LogTools.RESET} {status}", flush=True)

                if self.debug and stdout:
                    self.log_message.info(f"INFO DEBUG:\n{stdout}")
            except subprocess.CalledProcessError as e:
                sys.stdout = old_stdout
                print(f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}", flush=True)
                if self.debug:
                    self.log_message.error(f"ERROR DEBUG:\n{e.stderr}")
                raise e
            finally:
                sys.stdout = old_stdout

            # Log the completion status
            self.log_message.info(
                message=f"Command '{display_message}' completed with status: {status}"
            )
