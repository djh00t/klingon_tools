# LogTools Documentation

## Class - LogTools

The `LogTools` class provides methods for logging messages, decorating methods, and running shell commands:

- `log_message` - logs a message with a given severity using a specific status name and color.
- `method_state` - a decorator that logs the state of a method with a given style, status, and reason.
- `command_state` - runs shell commands and logs their output consistently.
- `set_default_style` - sets the default style for log messages.
- `set_log_level` - sets the logging level for the logger.
- `set_template` - sets a custom template for log messages.

### Styles

The `LogTools` class supports four built-in styles for logging messages, plus a plain text option:

- **default**: The default style with simple text formatting and right-aligned status with spaces.
- **basic**: A simple style without ellipses and right-aligned status with spaces.
- **pre-commit**: A style that mimics the output format of pre-commit hooks.
- **none**: A style that outputs the message without any formatting.
- **None**: When `style=None`, outputs the plain text value of the message argument with no formatting, ignoring the status.

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

The `log_message` class is a drop-in replacement for the classic Python logging library. It focuses on user experience and simplicity rather than system logging.

The `log_message` class provides methods for logging messages with different severities:

| Method    | Default Color | Default Status | Description         |
|-----------|---------------|----------------|---------------------|
| debug     | Cyan          | DEBUG          | Debugging message   |
| info      | Green         | OK             | Informational message |
| warning   | Yellow        | WARNING        | Warning message     |
| error     | Red           | ERROR          | Error message       |
| critical  | Bold Red      | CRITICAL       | Critical message    |
| exception | Red           | ERROR          | Exception message   |

#### Args:
- `msg` (str): The message to log. Can be provided as a positional or keyword argument.
- `style` (str, optional): The style of the log output. Defaults to the class's default style.
- `status` (str, optional): The status message to log on the far right. Defaults to the method's default status.
- `reason` (str, optional): The reason for the status message, displayed in round brackets just to the left of `status`. Defaults to None.

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

`method_state` is a decorator that logs the state of a method with a given style, status, and reason. This is useful for providing user-friendly logging where system-style logging is too much or likely to cause confusion for the reader.

#### Args:
- `message` (str): The message to log. If not provided, the function name will be used.
- `style` (str, optional): The style of the log output. Defaults to "default".
- `status` (str, optional): The status message to log on the far right. Defaults to "OK".
- `reason` (str, optional): The reason for the status message, displayed in round brackets just to the left of `status`. Defaults to None.

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

### Method - `set_default_style(self, style)`

Sets the default style for log messages.

#### Args:
- `style` (str): The style to use for log messages. Must be one of the valid styles: "default", "basic", "pre-commit", or "none".

### Method - `set_log_level(self, level)`

Sets the logging level for the logger.

#### Args:
- `level` (str): The logging level to set. Must be one of: "DEBUG", "INFO", "WARNING", "ERROR", or "CRITICAL".

### Method - `set_template(cls, template)`

Sets the template for log messages.

#### Args:
- `template` (str): The template to use for log messages. Should include placeholders for {message}, {style}, and {status}.

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

## Advanced Usage

### Custom Templates

The `LogTools` class allows you to set a custom template for log messages. This can be useful if you want to standardize the format of your log messages across different parts of your application.

To set a custom template, use the `set_template` class method. The template should be a string with placeholders for `message`, `style`, and `status`.

#### Example

```python
from klingon_tools.logtools import LogTools

# Set a custom template
LogTools.set_template("Priority: {priority} - Message: {message} - Status: {status}")

# Initialize LogTools
log_tools = LogTools(debug=True)
logger = log_tools.log_message

# Use log_message with the template
logger.info("Installing catapult")
logger.warning("Low disk space")
logger.error("Installation failed")
```

### Debug Mode

To enable debug mode, initialize `LogTools` with the `debug` parameter set to `True`:

```python
log_tools = LogTools(debug=True)
```

In debug mode, additional information such as command output and error messages will be printed to the console.

### Setting Log Level

You can set the log level using the `set_log_level` method:

```python
log_tools.set_log_level("DEBUG")
```

### Setting Default Style

You can set the default style for all log messages using the `set_default_style` method:

```python
log_tools.set_default_style("pre-commit")
```

This will apply the specified style to all subsequent log messages unless overridden in individual log calls.
