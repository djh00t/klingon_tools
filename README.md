# klingon_utils
# Utility Repository

This repository contains a set of utilities that are frequently used. These utilities are designed to automate and simplify various tasks, making them more efficient and less error-prone.

## Contents

Currently, the repository includes the following utilities:

- `treetool (tt)`: A tool for saving and generating project file and directory structures. See [treetool/README.md](treetool/README.md) for more details.
- `gitignore`: A generic .gitignore file. See [gitignore/README.md](gitignore/README.md) for more details.
- `amnesia`: A utility for rewriting commit history in a Git repository. See [amnesia/README.md](amnesia/README.md) for more details.
- `Cxcel`: Render CSV files in both terminal and web interfaces. Real-time updates to the displayed CSV content by monitoring file changes. See [Cxcel/README.md](Cxcel/README.md) for more details.
- `klingon tool (kt)`: Installer/updater for klingon tools CLI. See [kt/README.md](kt/README.md) for more details.

### klingon_tools

A Python library that contains the following utilities:

- `logtools`: A utility for running and logging shell commands and their exit codes in a user-friendly manner.

## Usage

Each utility has its own specific usage instructions, which can be found in the comments of the utility's script. In general, utilities can be run from the command line and accept various command-line arguments.

### Example Usage of `logtools`

The `logtools` utility provides decorators for methods and CLI commands that log output in a clean and consistent manner with simple error handling.

#### Method State Example

```python
from klingon_tools import LogTools

@LogTools.method_state(name="Install numpy")
def install_numpy():
    return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

install_numpy()
```

Expected output:

```plaintext
Running Install numpy...                                               OK
```

#### Command State Example

```python
from klingon_tools import LogTools

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
