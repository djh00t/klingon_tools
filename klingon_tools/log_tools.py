import io
import logging
import subprocess
import sys
from functools import wraps
from typing import Optional, Callable, List, Tuple, Dict, Any


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
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    template = None

    def __init__(self, debug: bool) -> None:
        self.debug = debug
        self.default_style = "default"
        self.log_message = LogTools.LogMessage(__name__, self)
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
        if level != "INFO":
            print(f"Setting log level to {level}")

        self.logger.setLevel(level)

    @classmethod
    def set_template(cls, template: str) -> None:
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

            if style not in self.parent.VALID_STYLES:
                raise ValueError(f"Invalid style '{style}'.")

            msg = self._prepare_message(msg, reason, status, style)
            final_msg = self._format_message(msg, status, style)
            self.logger.log(level, final_msg)

        def _prepare_message(self, msg, reason, status, style):
            if reason:
                msg = f"{msg} ({reason})"
            if self.parent.template:
                msg = self.parent.template.format(
                    message=msg, style=style, status=status)
            return msg

        comment_definition: List[Dict[str, Any]] = [
            {
                "start": "#",
                "interim": "NULL",
                "end": "NULL",
                "comment": "Single-line comment",
                "languages": [
                    "Python", "Ruby", "Perl", "Shell scripts (Bash, Zsh)",
                    "PHP", "PowerShell", "R", "Julia", "Tcl", "Makefile",
                    "CMake", "YAML", "Dockerfile", "gitconfig", "Swift", "Nim"
                ]
            },
            {
                "start": "//",
                "interim": "NULL",
                "end": "NULL",
                "comment": "Single-line comment",
                "languages": [
                    "JavaScript", "Java", "C", "C++", "C#", "Go", "Rust",
                    "Swift", "Kotlin", "Scala", "Dart", "TypeScript", "PHP",
                    "Groovy", "Haxe"
                ]
            },
            {
                "start": "/*",
                "interim": "NULL",
                "end": "*/",
                "comment": "Multi-line comment",
                "languages": [
                    "JavaScript", "Java", "C", "C++", "C#", "Go", "Rust",
                    "Swift", "Kotlin", "Scala", "Dart", "TypeScript", "PHP",
                    "CSS", "Less", "Sass", "SQL"
                ]
            },
            {
                "start": "<!--",
                "interim": "NULL",
                "end": "-->",
                "comment": "Comment in markup languages",
                "languages": [
                    "HTML", "XML", "SVG", "Markdown"
                ]
            },
            {
                "start": "--",
                "interim": "NULL",
                "end": "NULL",
                "comment": "Single-line comment",
                "languages": [
                    "SQL", "Haskell", "Lua", "Ada", "AppleScript", "Eiffel",
                    "VHDL"
                ]
            },
            {
                "start": "%",
                "interim": "NULL",
                "end": "NULL",
                "comment": "Single-line comment",
                "languages": [
                    "MATLAB", "Octave", "LaTeX", "Erlang", "Prolog"
                ]
            },
            {
                "start": '"""',
                "interim": "NULL",
                "end": '"""',
                "comment": "Multi-line string/comment",
                "languages": [
                    "Python (docstrings)", "Kotlin (multi-line strings)"
                ]
            },
            {
                "start": "'''",
                "interim": "NULL",
                "end": "'''",
                "comment": "Multi-line string/comment",
                "languages": [
                    "Python (alternative docstrings)",
                    "Ruby (multi-line strings)"
                ]
            },
            {
                "start": "/**",
                "interim": "*",
                "end": "*/",
                "comment": "Documentation comment",
                "languages": [
                    "Java (Javadoc)", "JavaScript (JSDoc)",
                    "C# (XML Documentation)", "Kotlin (KDoc)",
                    "Scala (ScalaDoc)", "Dart", "TypeScript",
                    "PHP (phpDocumentor)"
                ]
            },
            {
                "start": "///",
                "interim": "NULL",
                "end": "NULL",
                "comment": "Single-line documentation comment",
                "languages": [
                    "C#", "Rust", "Dart"
                ]
            },
            {
                "start": "///",
                "interim": "///",
                "end": "///",
                "comment": "Multi-line documentation comment",
                "languages": [
                    "C#", "XML (when used in source code)"
                ]
            },
            {
                "start": "=begin",
                "interim": "NULL",
                "end": "=end",
                "comment": "Multi-line comment",
                "languages": [
                    "Ruby"
                ]
            },
            {
                "start": "=pod",
                "interim": "NULL",
                "end": "=cut",
                "comment": "Multi-line documentation",
                "languages": [
                    "Perl (POD - Plain Old Documentation)"
                ]
            },
            {
                "start": "{-",
                "interim": "NULL",
                "end": "-}",
                "comment": "Multi-line comment",
                "languages": [
                    "Haskell", "Elm"
                ]
            },
            {
                "start": "--[[",
                "interim": "NULL",
                "end": "]]",
                "comment": "Multi-line comment",
                "languages": [
                    "Lua"
                ]
            },
            {
                "start": ";",
                "interim": "NULL",
                "end": "NULL",
                "comment": "Single-line comment",
                "languages": [
                    "Assembly", "Lisp", "Scheme", "Clojure", "AutoHotkey"
                ]
            },
            {
                "start": "'",
                "interim": "NULL",
                "end": "NULL",
                "comment": "Single-line comment",
                "languages": [
                    "Visual Basic", "VBA"
                ]
            },
            {
                "start": "REM",
                "interim": "NULL",
                "end": "NULL",
                "comment": "Single-line comment",
                "languages": [
                    "BASIC", "batch files"
                ]
            },
            {
                "start": "dnl",
                "interim": "NULL",
                "end": "NULL",
                "comment": "Single-line comment",
                "languages": [
                    "M4"
                ]
            },
            {
                "start": "//!",
                "interim": "NULL",
                "end": "NULL",
                "comment": "Single-line documentation comment",
                "languages": [
                    "Rust (for module-level documentation)"
                ]
            },
            {
                "start": "/*!",
                "interim": "NULL",
                "end": "*/",
                "comment": "Multi-line documentation comment",
                "languages": [
                    "C", "C++ (when used with tools like Doxygen)"
                ]
            }
        ]

        def _format_message(self, msg, status, style, language="Python"):
            # Comment style logic removed to prevent unwanted prefixes
            total_length = 78
            status_length = len(status)
            max_msg_length = total_length - status_length - 1

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

        def critical(self, *args, **kwargs):
            self._log(logging.CRITICAL, *args, **kwargs)

        def exception(self, *args, **kwargs):
            self.logger.exception(*args, **kwargs)

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
                    message=f"Command '{display_message}'"
                    f"completed with status: {status}"
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
                message=f"Command '{
                    display_message}' completed with status: {status}"
            )
