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
    def __init__(self, debug=False):
        """
        Initialize LogTools with an optional debug flag.

        Args:
            debug (bool): Flag to enable debug mode. Defaults to False.
        """
        self.DEBUG = debug

    def log_message(self, message, category="INFO"):
        """Log a message with a given category."""
        if category == "INFO":
            print(f"{LogTools.BOLD_GREEN}{message}{LogTools.RESET}")
        elif category == "WARNING":
            print(f"{LogTools.BOLD_YELLOW}{message}{LogTools.RESET}")
        elif category == "ERROR":
            print(f"{LogTools.BOLD_RED}{message}{LogTools.RESET}")

    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_RED = "\033[1;31m"
    RESET = "\033[0m"

    def method_state(self, name=None):
        """Decorator to run and log shell commands.

        Args:
            name (str, optional): A custom name for the command. Defaults to None.

        Example Usage:

        ```python
        from klingon_tools.logtools import LogTools

        @LogTools.method_state(name="Install numpy")
        def install_numpy():
            return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

        install_numpy()
        ```

        Expected output:

        ```plaintext
        Running Install numpy...                                               OK
        ```
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                display_name = name if name else func.__name__
                padding = 72 - len(f"Running {display_name}... ")
                print(f"Running {display_name}... " + " " * padding, end="")

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
                        print(f"\rRunning {display_name}... " + " " * padding + f"{LogTools.BOLD_GREEN}OK{LogTools.RESET}")
                        if self.DEBUG and stdout:
                            print(f"{LogTools.BOLD_GREEN}INFO DEBUG:\n{LogTools.RESET}{stdout}")
                    elif result == 1:  # Assuming '1' is a warning
                        print(f"\rRunning {display_name}... " + " " * padding + f"{LogTools.BOLD_YELLOW}WARNING{LogTools.RESET}")
                        if self.DEBUG and stdout:
                            self.log_message(f"WARNING DEBUG:\n{stdout}", "WARNING")
                    else:
                        print(f"\rRunning {display_name}... " + " " * padding + f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}")
                        if self.DEBUG and stderr:
                            self.log_message(f"ERROR DEBUG:\n{stderr}", "ERROR")
                except Exception as e:
                    print(f"\rRunning {display_name}... " + " " * padding + f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}")
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

    def command_state(self, commands):
        """Run a list of shell commands and log their output.

        Args:
            commands (list of tuples): Each tuple contains (command, name).

        ```python
        from klingon_tools.logtools import LogTools
        commands = [
            ("PIP_ROOT_USER_ACTION=ignore pip install -q numpy", "Install numpy"),
            ("echo 'Hello, World!'", "Print Hello World")
        ]
        LogTools.command_state(commands)
        ```

        Expected output:

        ```plaintext
        Running Install numpy...                                               OK
        Running Print Hello World...                                           OK
        ```
        """
        for command, name in commands:
            display_name = name if name else f"'{command}'"
            padding = 72 - len(f"Running {display_name}... ")
            print(f"Running {display_name}... " + " " * padding, end="")

            # Capture stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            try:
                result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
                stdout = result.stdout
                stderr = result.stderr

                if result.returncode == 0:
                    print(f"\rRunning {display_name}... " + " " * padding + f"{LogTools.BOLD_GREEN}OK{LogTools.RESET}")
                    if self.DEBUG and stdout:
                        self.log_message(f"INFO DEBUG:\n{stdout}", "INFO")
                elif result.returncode == 1:  # Assuming '1' is a warning
                    print(f"\rRunning {display_name}... " + " " * padding + f"{LogTools.BOLD_YELLOW}WARNING{LogTools.RESET}")
                    if self.DEBUG and stdout:
                        self.log_message(f"WARNING DEBUG:\n{stdout}", "WARNING")
                else:
                    print(f"\rRunning {display_name}... " + " " * padding + f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}")
                    if self.DEBUG and stderr:
                        self.log_message(f"ERROR DEBUG:\n{stderr}", "ERROR")
            except subprocess.CalledProcessError as e:
                print(f"\rRunning {display_name}... " + " " * padding + f"{LogTools.BOLD_RED}ERROR{LogTools.RESET}")
                stderr = sys.stderr.getvalue()
                if self.DEBUG and stderr:
                    self.log_message(f"ERROR DEBUG:\n{stderr}", "ERROR")
                raise e
            finally:
                # Restore stdout and stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
