import subprocess
from functools import wraps

class LogTools:
    """
    A utility class for running and logging python methods and shell commands in a user-friendly manner.

    This class provides decorators for methods and cli commands that log output
    in a clean and consistent manner with simple error handling.
    """
    @staticmethod
    def method_state(name=None):
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
                command = func(*args, **kwargs)
                display_name = name if name else f"'{command}'"
                padding = 72 - len(f"Running {display_name}... ")
                print(f"Running {display_name}... " + " " * padding, end="")
                try:
                    subprocess.run(command, check=True, shell=True)
                    print("\033[1;32mOK\033[0m")  # Bold Green
                except subprocess.CalledProcessError as e:
                    if e.returncode == 1:  # Assuming '1' is a warning
                        print("\033[1;33mWARNING\033[0m")  # Bold Yellow
                    else:
                        print("\033[1;31mERROR\033[0m")  # Bold Red
                    raise
            return wrapper
        return decorator


    @staticmethod
    def command_state(commands):
        """Run a list of shell commands and log their output.

        Args:
            commands (list of tuples): Each tuple contains (command, name).

        Example Usage:

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
            try:
                subprocess.run(command, check=True, shell=True)
                print("\033[1;32mOK\033[0m")  # Bold Green
            except subprocess.CalledProcessError as e:
                if e.returncode == 1:  # Assuming '1' is a warning
                    print("\033[1;33mWARNING\033[0m")  # Bold Yellow
                else:
                    print("\033[1;31mERROR\033[0m")  # Bold Red
                raise
