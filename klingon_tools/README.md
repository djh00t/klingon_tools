# klingon_tools

The `klingon_tools` Python library provides utilities for running and logging shell commands in a user-friendly manner. This library is designed to simplify the process of executing shell commands and capturing their output, making it easier to automate tasks and handle errors.

## Features

- **LogTools**: A utility for running and logging shell commands and their exit codes in a user-friendly manner.
  - **styles**: Customize the appearance of log output using simple to configure and manage styles.
  - **log_message**: Logs a message with a given severity.
  - **method_state**: Logs the state of a method with a given style, status, and reason.
  - **command_state**: Logs the state of a shell command with a given style, status, and reason.
- **push**: A utility for handling git push operations with additional checks and logging.
- **gh-actions-update**: A utility for updating GitHub Actions workflows to the latest versions.

## Installation

To install the `klingon_tools` library, you can use pip:

```sh
pip install klingon_tools
```

## Class - LogTools

The `LogTools` class provides methods for logging messages, decorating methods, and running shell commands:

- `log_message` - logs a message with a given severity using a specific status name and color. for INFO, yellow for WARNING, and red for ERROR.
- `method_state` - a decorator that logs the state of a method with a given style, status, and reason.
- `command_state` - run shell commands and log their output consistently.

### Styles

The `LogTools` class supports two built-in styles for logging messages. The following styles are available:

- **default**: The default style with simple text formatting and right-aligned status with spaces.
- **basic**: A simple style without ellipses and right-aligned status with spaces.
- **pre-commit**: A style that mimics the output format of pre-commit hooks.

**default**

```plaintext
Running Install numpy...                                                 Passed
Running Install with warning...                            (out of disk)Warning
Running Install with error...                                     (failed)Error
```

**basic**

```plaintext
Running Install numpy                                                        OK
Running Install with warning & reason                      (out of disk)Warning
Running Install with error & reason                               (failed)Error
```

**pre-commit**

<pre>
Running Install numpy........................................................<span style="color: green;">OK</span>
Running Install with warning...............................(out of disk)<span style="color: yellow;">Warning</span>
Running Install with error........................................(failed)<span style="color: red;">Error</span>
</pre>

### Method - `log_message`

Drop-in replacement for the classic python logging library. Is focussed on user experience and simplicity rather than system logging.

The `log_message` class provides methods for logging messages with different severities, each of which have their own default color and status labels:

| Severity | Color  | Status | Description |
|----------------|--------|-------------|---------------|
| INFO           | <span style="color: green;">Green</span>  | OK | Informational message |
| WARNING        | <span style="color: yellow;">Yellow</span> | WARNING | Warning message |
| ERROR          | <span style="color: red;">Red</span>    | ERROR | Error message |
| DEBUG          | <span style="color: cyan;">Cyan</span>   | DEBUG | Debugging message |
| CRITICAL       | <span style="color: red; font-weight: bold;">Red (Bold)</span> | CRITICAL | Critical message |
| EXCEPTION      | <span style="color: orange;">Orange</span> | EXCEPTION | Exception message |

#### Args:
- `message` (str): The message to log. Can be provided as a positional or keyword argument.
- `severity` (str, optional): The severity of the message. Defaults to "INFO" but generally not used if log_message is called with the appropriate priority method i.e. `LogTools.log_message.info("message")`
- `style` (str, optional): The style of the log output. Defaults to "default".
- `status` (str, optional): The status message to log on the far right. Defaults to "OK".
- `reason` (str, optional): The reason for the status message, displayed in round brackets just to left of `status`. Defaults to None.

#### Example Usage

```python
from klingon_tools.logtools import LogTools

log_tools = LogTools()
logger = log_tools.log_message

logger.info("Installing catapult")
logger.warning("Low disk space")
logger.error("Installation failed")
```

#### Expected Output

<pre>
Running Installing catapult...                                               <span style="color: green;">OK</span>
Running Low disk space...                                                    <span style="color: yellow;">WARNING</span>
Running Installation failed...                                               <span style="color: red;">ERROR</span>
</pre>

### Method - `method_state(self, message=None, style="default", status="OK", reason=None)`

`method_state` is a decorator that logs the state of a method with a given style, status, and reason. This is useful for providing user friendly logging where system style logging is too much or likely to cause confusion for the reader.

#### Args:
- `message` (str): The message to log. Can be provided as a positional or keyword argument.
- `style` (str, optional): The style of the log output. Defaults to "default".
- `status` (str, optional): The status message to log on the far right. Defaults to "OK".
- `reason` (str, optional): The reason for the status message, displayed in round brackets just to left of `status`. Defaults to None.

#### Example with Styles

**Default Style**

```python
from klingon_tools.logtools import LogTools

log_tools = LogTools(debug=True)

@log_tools.method_state(message="Install numpy", style="default", status="OK")
def install_numpy():
    return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

install_numpy()
```

**Expected output**

<pre>
Running Install numpy...                                                     <span style="color: green;">OK</span>
</pre>

**Basic Style**

```python
from klingon_tools.logtools import LogTools

log_tools = LogTools(debug=True)

@log_tools.method_state(message="Install numpy", style="basic", status="OK")
def install_numpy():
    return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

install_numpy()
```

**Expected output**

<pre>
Running Install numpy OK
</pre>

**Pre-commit Style**

```python
from klingon_tools.logtools import LogTools

log_tools = LogTools(debug=True)

@log_tools.method_state(message="Install numpy", style="pre-commit", status="Passed")
def install_numpy():
    return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

install_numpy()
```

**Expected Output**

<pre>
Running Install numpy.................................................<span style="color: green;">Passed</span>
</pre>

### Method - `command_state(self, commands, style="default", status="Passed", reason=None)`

`command_state` runs a list of shell commands and logs their output. This is useful for providing user-friendly logging for shell commands.

#### Args:
- `commands` (list of tuples): Each tuple contains (command, name).
- `style` (str, optional): The style of the log output. Defaults to "default".
- `status` (str, optional): The status message to log on the far right. Defaults to "Passed".
- `reason` (str, optional): The reason for the status message, displayed in round brackets just to the left of `status`. Defaults to None.

#### Example with Styles

**Default Style**

```python
from klingon_tools.logtools import LogTools

log_tools = LogTools(debug=True)

commands = [
    ("PIP_ROOT_USER_ACTION=ignore pip install -q numpy", "Install numpy"),
    ("echo 'Hello, World!'", "Print Hello World")
]

log_tools.command_state(commands, style="default", status="Passed")
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

@log_tools.method_state(message="Install numpy", style="pre-commit", status="Passed")
def install_numpy():
    return "PIP_ROOT_USER_ACTION=ignore pip install -q numpy"

install_numpy()

```

**Expected Output**

<pre>

Running Install numpy.................................................<span style="color: green;">Passed</span>

</pre>

### Method - `command_state(self, commands, style="default", status="Passed", reason=None)`

`command_state` runs a list of shell commands and logs their output. This is useful for providing user-friendly logging for shell commands.

#### Args:
  - `commands` (list of tuples): Each tuple contains (command, name).
  - `style` (str, optional): The style of the log output. Defaults to "default".
  - `status` (str, optional): The status message to log on the far right. Defaults to "Passed".
  - `reason` (str, optional): The reason for the status message, displayed in round brackets just to the left of `status`. Defaults to None.

#### Example with Styles

**Default Style**

```python

from klingon_tools.logtools import LogTools

log_tools = LogTools(debug=True)

commands = [
    ("PIP_ROOT_USER_ACTION=ignore pip install -q numpy", "Install numpy"),
    ("echo 'Hello, World!'", "Print Hello World")
]

log_tools.command_state(commands, style="default", status="Passed")

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

log_tools.command_state(commands, style="pre-commit", status="OK")

```

**Expected Output**

<pre>

Running Install numpy.................................................<span style="color: green;">OK</span>
Running Print Hello World.............................................<span style="color: green;">OK</span>

</pre>

## Advanced Usage - Custom Templates

The `LogTools` class allows you to set a custom template for log messages. This can be useful if you want to standardize the format of your log messages across different parts of your application.

### Setting a Custom Template

To set a custom template, use the `set_template` class method. The template should be a string with placeholders for `message`, `style`, and `status`.

#### Example

```python

from klingon_tools.logtools import LogTools

# Set a custom template
LogTools.set_template("Priority: {priority} - Message: {message} - Status: {status}")

# Use log_message with the template
logger = LogTools.log_message
logger.info("Installing catapult")
logger.warning("Low disk space")
logger.error("Installation failed")

```

**Expected Output**

<pre>

Severity: INFO - Message: Installing catapult - Status: OK
Severity: WARNING - Message: Low disk space - Status: WARNING
Severity: ERROR - Message: Installation failed - Status: ERROR

</pre>

## Debug Mode

To enable debug mode, set the `DEBUG` flag to `True`:

```python

log_tools = LogTools(debug=True)

```

In debug mode, additional information such as command output and error messages will be printed to the console.

## Command - push

The `push` command provides automated conventional commit message generation
using the OpenAI API, pre-commit hooks and other tools that make rapid
iterative development structured, consistent and easy to manage.

Once klingon_tools is installed, the `push` command can be used to run
pre-commit, commit and push changes to a remote repository in a single command.

`push` iterates over every changed file, generating a dedicated commit message
per file that has been changed.

### Conventional Commits
This code base follows the Conventional Commits specification to standardize
commit messages. The Conventional Commits specification is a convention for
writing commit messages that helps in understanding the history of changes,
automating the release process, and generating changelogs.

The `push` command uses the OpenAI API to generate conventional commit messages
based on the changes that have been made to the code since the last commit. The
`push` implementation of Conventional Commits specification is slightly
different to the official spec in that the `push` command makes the scope
and description mandatory for all commit messages.

### Requires:
- `OPENAI_API_KEY` environment variable containing the OpenAI API key.

### Args:
- `-h`, `--help`: Show help message and exit.
- `--debug`: Enable debug mode.
- `--dryrun`: Run the push operation in dry-run mode - don't commit or push
  changes.
- `--file-name` (str, optional): The name of the file to process. Defaults to all files that
  aren't already committed. Any committed but not pushed files will aloo be
  pushed.
- `--oneshot`: Run the push operation once and exit.
- `--repo-path` (str, optional): The path to the repository to push. Defaults to the repository
  that the current directory resides in.

### Example Usage

```bash
push
```

### Expected Output


```bash
(klingon_tools) root@OREGON:~/klingon_tools# push
Checking for software requirements...                                        ✅
Using git user name:...                                            David Hooton
Using git user email:...                                       david@hooton.org
--------------------------------------------------------------------------------
Deleted files...                                                              0
Untracked files...                                                            0
Modified files...                                                             1
Staged files...                                                               0
Committed not pushed files...                                                 0
--------------------------------------------------------------------------------
Batch mode enabled...                                                        📦
Un-staging all staged files...                                               🔄
Processing file...                                      klingon_tools/README.md
Staging file...                                                              ✅
Diff generated...                                                            ✅
--------------------------------------------------------------------------------
Generated commit message:

✨ feat(klingon_tools): Update README.md with additional utilities and
descriptions

- Updated descriptions and formatting for LogTools features.
- Added new utilities like push and gh-actions-update with descriptions.
- Included installation instructions and class/method details for better
understanding of LogTools.
- Expanded on the usage examples of `log_message`, `method_state`, and
`command_state`.
- Documented the new `push` command with its arguments and example usage for a
structured development process.
- Provided information on contributing to the project and welcoming new ideas.

Signed-off-by: David Hooton <david@hooton.org>

--------------------------------------------------------------------------------
check for merge conflicts................................................Passed
fix end of files.........................................................Passed
mixed line ending........................................................Passed
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
check yaml...........................................(no files to check)Skipped
black................................................(no files to check)Skipped
--------------------------------------------------------------------------------
Pre-commit completed...                                                      ✅
--------------------------------------------------------------------------------
Generated commit message:

✨ feat(klingon_tools/README.md): Add push command for automated conventional
commit message generation, pre-commit hooks, and tools

Added a new `push` command to provide automated conventional commit message
generation, pre-commit hooks, and other tools for structured and consistent
iterative development management.

Signed-off-by: David Hooton <david@hooton.org>

--------------------------------------------------------------------------------
File committed...                                                            ✅
Pushed changes to remote repository...                                       ✅
All files processed. Script completed successfully....                       🚀
================================================================================

```



## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
