# klingon_tools

The `klingon_tools` Python library provides utilities for running and logging shell commands in a user-friendly manner. This library is designed to simplify the process of executing shell commands and capturing their output, making it easier to automate tasks and handle errors.

## Features

- **LogTools**: A utility for running and logging shell commands and their exit codes in a user-friendly manner.

## Installation

To install the `klingon_tools` library, you can use pip:

```sh
pip install klingon_tools
```

## Usage

### LogTools

The `LogTools` class provides static methods `method_state` and `command_state` to run shell commands and log their output.

#### Methods

##### `method_state(name=None)`

A decorator to run and log shell commands.

###### Args:
- `name` (str, optional): A custom name for the command. Defaults to `None`.

###### Example Usage

```python
from klingon_tools.logtools import LogTools

log_tools = LogTools(debug=True)

@log_tools.method_state(name="Install numpy")
def install_numpy():
    return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

install_numpy()
```

Expected output:

```plaintext
Running Install numpy...                                               OK
```

##### `command_state(commands)`

Runs a list of shell commands and logs their output.

###### Args:
- `command` (str): The shell command to run.
- `name` (str, optional): A custom name for the command. Defaults to `None`.

###### Example Usage

```python
from klingon_tools.logtools import LogTools

commands = [
    ("PIP_ROOT_USER_ACTION=ignore pip install -q numpy", "Install numpy"),
    ("echo 'Hello, World!'", "Print Hello World")
]
log_tools.command_state(commands)
```

Expected output:

```plaintext
Running Install numpy...                                               OK
```

### `log_message(message, category="INFO")`

Logs a message with a given category.

###### Args:
- `message` (str): The message to log.
- `category` (str, optional): The category of the message. Defaults to `"INFO"`.

###### Example Usage

```python
from klingon_tools.logtools import LogTools

LogTools.log_message("This is an info message", "INFO")
LogTools.log_message("This is a warning message", "WARNING")
LogTools.log_message("This is an error message", "ERROR")
```

Expected output:

```plaintext
This is an info message
This is a warning message
This is an error message
```

## Debug Mode

To enable debug mode, set the `DEBUG` flag to `True`:

```python
log_tools = LogTools(debug=True)
```

## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
