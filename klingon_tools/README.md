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

@LogTools.method_state(name="Install numpy")
def install_numpy():
    return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

install_numpy()
```

Expected output:

```plaintext
Running Install numpy...                                               OK
```

##### `command_state(command, name=None)`

Runs a shell command and logs its output.

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
LogTools.command_state(commands)
```

Expected output:

```plaintext
Running Install numpy...                                               OK
```

## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
