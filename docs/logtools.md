# LogTools Documentation

## Overview

The `LogTools` class provides a flexible and user-friendly logging system for Python applications. It offers methods for logging messages, decorating methods, and running shell commands with consistent and visually appealing output.

## Class: LogTools

### Initialization

```python
from klingon_tools.logtools import LogTools

log_tools = LogTools(debug=False)
```

- `debug` (bool, optional): Flag to enable debug mode. Defaults to False.

### Attributes

- `DEBUG` (bool): Flag indicating if debug mode is enabled.
- `default_style` (str): The default style for log messages.
- `log_message` (LogTools.LogMessage): Instance for logging messages.
- `logger` (logging.Logger): Standard Python logger instance.

### Methods

#### set_log_level(level)

Sets the logging level for the logger.

- `level` (str): The logging level to set (e.g., 'DEBUG', 'INFO').

#### set_default_style(style)

Sets the default style for log messages.

- `style` (str): The style to use for log messages. Valid styles are: 'default', 'pre-commit', 'basic'.

#### method_state(message=None, style="default", status="OK", reason=None)

Decorator to log the state of a method with a given style, status, and reason.

- `message` (str, optional): The message to log.
- `style` (str, optional): The style of the log output. Defaults to "default".
- `status` (str, optional): The status message to log on the far right. Defaults to "OK".
- `reason` (str, optional): The reason for the status message. Defaults to None.

#### command_state(commands, style="default", status="Passed", reason=None)

Runs a list of shell commands and logs their output.

- `commands` (list of tuples): Each tuple contains (command, name).
- `style` (str, optional): The style of the log output. Defaults to "default".
- `status` (str, optional): The status message to log. Defaults to "Passed".
- `reason` (str, optional): The reason for the status message. Defaults to None.

### Inner Class: LogMessage

#### Methods

- `debug(msg=None, *args, **kwargs)`
- `info(msg=None, *args, **kwargs)`
- `warning(msg=None, *args, **kwargs)`
- `error(msg=None, *args, **kwargs)`
- `critical(msg=None, *args, **kwargs)`
- `exception(msg=None, *args, exc_info=True, **kwargs)`

These methods log messages with different severity levels.

## Styles

The `LogTools` class supports three built-in styles for logging messages:

1. **default**: Simple text formatting with right-aligned status and spaces.
2. **basic**: Simple style without ellipses and right-aligned status with spaces.
3. **pre-commit**: Mimics the output format of pre-commit hooks.

### Examples

#### Default Style

```python
log_tools.log_message.info("Installing package")
```

Output:
```
Running Installing package...                                                OK
```

#### Basic Style

```python
log_tools.set_default_style("basic")
log_tools.log_message.warning("Low disk space", status="Warning")
```

Output:
```
Running Low disk space                                                 Warning
```

#### Pre-commit Style

```python
log_tools.set_default_style("pre-commit")
log_tools.log_message.error("Installation failed", status="Failed")
```

Output:
```
Running Installation failed..........................................Failed
```

## Advanced Usage

### Custom Templates

You can set a custom template for log messages using the `set_template` class method:

```python
LogTools.set_template("Priority: {priority} - Message: {message} - Status: {status}")

log_tools = LogTools()
log_tools.log_message.info("Custom template message")
```

Output:
```
Priority: INFO - Message: Custom template message - Status: OK
```

### Debug Mode

Enable debug mode to get additional information:

```python
log_tools = LogTools(debug=True)
```

In debug mode, additional information such as command output and error messages will be printed to the console.

## Integration with klingon_tools/logger.py

The `klingon_tools/logger.py` file initializes an instance of `LogTools` for use throughout the application:

```python
from klingon_tools import LogTools

# Initialize logging
log_tools = LogTools()
logger = log_tools.log_message
```

This allows you to import and use the logger in other parts of your application:

```python
from klingon_tools.logger import logger

logger.info("Application started")
logger.warning("Low memory", status="Warning")
logger.error("Critical error occurred", status="Failed")
```

By using this centralized logger, you ensure consistent logging across your entire application.
