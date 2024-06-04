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

The `LogTools` class provides a static method `command_state` to run shell commands and log their output.

#### Methods

##### `command_state(name=None)`

A decorator to run and log shell commands.

###### Args:
- `name` (str, optional): A custom name for the command. Defaults to `None`.

###### Example Usage

```python
from klingon_tools import LogTools

@LogTools.command_state(name="Install numpy")
def install_numpy():
    return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

install_numpy()
```

##### `run_command(command, name=None)`

Runs a shell command and logs its output.

###### Args:
- `command` (str): The shell command to run.
- `name` (str, optional): A custom name for the command. Defaults to `None`.

###### Example Usage

```python
from klingon_tools import LogTools

LogTools.run_command("PIP_ROOT_USER_ACTION=ignore pip install -q numpy", name="Install numpy")
```

###### Expected Output

```plaintext
Running Install numpy...                                               OK
```

## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
