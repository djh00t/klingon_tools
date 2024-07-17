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

## klingon_tools

`klingon_tools` is a Python package that provides a set of utilities designed to automate and simplify various tasks, making them more efficient and less error-prone. This package includes tools for logging, git operations, OpenAI integration, and more.

### Features

- **Logging Tools**: Provides decorators for methods and CLI commands to log output in a clean and consistent manner with simple error handling.
- **Git Tools**: Functions to interact with a Git repository, including staging, committing, pushing changes, and running pre-commit hooks.
- **OpenAI Tools**: Tools for generating commit messages, pull request titles, and release bodies using OpenAI's API.
- **GitHub Actions Update**: Utility to check and update GitHub Actions versions in workflows.

### Installation

To install `klingon_tools`, use pip:

```sh
pip install klingon_tools
```

### Usage

#### Logging Tools

The `logtools` module provides utilities for running and logging shell commands in a user-friendly manner. It includes the `LogTools` class, which offers decorators for methods and CLI commands to log output in a clean and consistent manner with simple error handling.

**Example Usage of `logtools`**

```python
from klingon_tools import LogTools

log_tools = LogTools(debug=True)

@log_tools.method_state(name="Install numpy")
def install_numpy():
    return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

install_numpy()
```

**Expected output:**

```plaintext
Running Install numpy...                                               OK
```

#### Git Tools

The `git_tools` module provides functions to interact with a Git repository, including staging, committing, pushing changes, and running pre-commit hooks. It also includes functions to retrieve the status of the repository and handle deleted files.

**Example Usage of `git_tools`**

```python
from klingon_tools.git_tools import git_get_toplevel, git_commit_file

repo = git_get_toplevel()
if repo:
    git_commit_file('example.txt', repo)
```

#### OpenAI Tools

The `openai_tools` module provides tools for generating commit messages, pull request titles, and release bodies using OpenAI's API.

**Example Usage of `openai_tools`**

```python
from klingon_tools.openai_tools import OpenAITools

openai_tools = OpenAITools()
diff = "diff content here"
commit_message = openai_tools.generate_commit_message(diff)
print(commit_message)
```

#### GitHub Actions Update

The `gh_actions_update` module provides functionality to check and update GitHub Actions versions in YAML workflow files within a repository.

**Example Usage of `gh-actions-update`**

```sh
python -m klingon_tools.gh_actions_update
```

To update all outdated actions to the latest version, use the `--update` flag:

```sh
python -m klingon_tools.gh_actions_update --update
```

### Entry Points

The package provides several entry points for command-line usage:

- `push`: Automates git operations such as staging, committing, and pushing files.
- `gh-actions-update`: Checks and updates GitHub Actions versions in workflows.
- `pr-title-generate`: Generates a pull request title using OpenAI's API.
- `pr-summary-generate`: Generates a pull request summary using OpenAI's API.
- `pr-context-generate`: Generates a pull request context using OpenAI's API.
- `pr-body-generate`: Generates a pull request body using OpenAI's API.

### Example Usage of `push`

The `push` entry point automates git operations such as staging, committing, and pushing files. It also integrates with pre-commit hooks and generates commit messages using OpenAI's API.

**Usage**

```sh
python -m klingon_tools.push --repo-path /path/to/repo --file-name example.txt
```

### Example Usage of `gh-actions-update`

The `gh-actions-update` entry point finds all GitHub Actions in the current repository, checks the version they are using, and retrieves the most recent version of each action. It returns a table containing "Action Name", "Current Version", and "Latest Version" columns.

**Usage**

```sh
python -m klingon_tools.gh_actions_update
```

To update all outdated actions to the latest version, use the `--update` flag:

```sh
python -m klingon_tools.gh_actions_update --update
```

To update actions in a specific file (bash wildcards accepted), use the `--file` flag:

```sh
python -m klingon_tools.gh_actions_update --update --file {filename}
```

To update all instances of a specific action, use the `--action` flag:

```sh
python -m klingon_tools.gh_actions_update --update --action {action name}
```

To update all instances of a specific action in a specific file, use both `--file` and `--action` flags:

```sh
python -m klingon_tools.gh_actions_update --update --file {filename} --action {action name}
```

### Example Output

```plaintext
Action Name          Current Version    Latest Version
-------------------  -----------------  ---------------
actions/checkout     v2                 v3
actions/setup-python v1                 v2

Note: Use '--update' to update all outdated actions to the latest version.
Use '--update --file {filename}' to update a specific file (bash wildcards accepted).
Use '--action {action name}' to update all instances of a specific action.
Use '--action' and '--file' together to update all instances of a specific action in a specific file.
```

### Conventional Commits

We require all commit messages to follow the Conventional Commits standard. Below are the types we use and their explanations:

| Type      | Emoticon | Description                                      |
|-----------|----------|--------------------------------------------------|
| feat      | ✨        | add new user authentication feature              |
| fix       | 🐛        | resolve issue with user login                    |
| docs      | 📚        | update README with new setup instructions        |
| style     | 💄        | improve button styling                           |
| refactor  | ♻️        | reorganize project structure                     |
| perf      | 🚀        | optimize database queries for faster response    |
| test      | 🚨        | add unit tests for login component               |
| build     | 🛠️        | update dependencies                              |
| ci        | ⚙️        | add GitHub Actions workflow                      |
| chore     | 🔧        | clean up old files                               |
| revert    | ⏪        | undo previous commit that caused issues          |

### Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

### License

[MIT](https://choosealicense.com/licenses/mit/)

## Usage

Each utility has its own specific usage instructions, which can be found in the comments of the utility's script. In general, utilities can be run from the command line and accept various command-line arguments.

### Example Usage of `gh-actions-update`

The `gh-actions-update` entrypoint finds all GitHub Actions in the current repository, checks the version they are using, and retrieves the most recent version of each action. It returns a table containing "Action Name", "Current Version", and "Latest Version" columns.

#### Usage

To use the `gh-actions-update` entrypoint, run the following command:

```sh
python -m klingon_tools.gh_actions_update
```

To update all outdated actions to the latest version, use the `--update` flag:

```sh
python -m klingon_tools.gh_actions_update --update
```

To update actions in a specific file (bash wildcards accepted), use the `--file` flag:

```sh
python -m klingon_tools.gh_actions_update --update --file {filename}
```

To update all instances of a specific action, use the `--action` flag:

```sh
python -m klingon_tools.gh_actions_update --update --action {action name}
```

To update all instances of a specific action in a specific file, use both `--file` and `--action` flags:

```sh
python -m klingon_tools.gh_actions_update --update --file {filename} --action {action name}
```

#### Example Output

```plaintext
Action Name          Current Version    Latest Version
-------------------  -----------------  ---------------
actions/checkout     v2                 v3
actions/setup-python v1                 v2

Note: Use '--update' to update all outdated actions to the latest version.
Use '--update --file {filename}' to update a specific file (bash wildcards accepted).
Use '--action {action name}' to update all instances of a specific action.
Use '--action' and '--file' together to update all instances of a specific action in a specific file.
```

### Example Usage of `logtools`

The `logtools` utility provides decorators for methods and CLI commands that log output in a clean and consistent manner with simple error handling.

#### Method State Example

```python
from klingon_tools import LogTools

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

#### Command State Example

```python
from klingon_tools import LogTools

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

## Conventional Commits

We require all commit messages to follow the Conventional Commits standard. Below are the types we use and their explanations:

| Type      | Emoticon | Description                                      |
|-----------|----------|--------------------------------------------------|
| feat      | ✨        | add new user authentication feature              |
| fix       | 🐛        | resolve issue with user login                    |
| docs      | 📚        | update README with new setup instructions        |
| style     | 💄        | improve button styling                           |
| refactor  | ♻️        | reorganize project structure                     |
| perf      | 🚀        | optimize database queries for faster response    |
| test      | 🚨        | add unit tests for login component               |
| build     | 🛠️        | update dependencies                              |
| ci        | ⚙️        | add GitHub Actions workflow                      |
| chore     | 🔧        | clean up old files                               |
| revert    | ⏪        | undo previous commit that caused issues          |

## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
