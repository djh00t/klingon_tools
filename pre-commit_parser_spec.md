I want you to modiufy the pre-commit parser to use a template system to capture
the pre-commit output.

There are 3 templates used to format the output of the pre-commit parser. Lets
take a look at each of them.

Template 1: Test Passed

In this case the output contains the message "autopep8" left aligned, the
status "Passed" right aligned and the space between them filled with "." as
padding and a width of 80.

```raw_output
autopep8..................................................................Passed
```

```message_template[padding=".", width=80]
{message}{padding}{status}
```

Template 2: Test Skipped with Reason

In this case the output contains the message "check json" left aligned, the
reason "no files to check" inside of () and status "Skipped" right aligned. The
space between the message and the reason is filled with "." as padding and a
width of 80.

```raw_output
check json............................................(no files to check)Skipped
```

```message_template[padding=".", width=80]
{message}{padding}({reason}){status}
```

Template 3: Test Failed with hook_id, exit_code and exception_message.

In this case the output contains the message "flake8" left aligned, the status
"Failed" right aligned and the space between them filled with "." as
padding and a width of 80.

This message also contains additional debug not found in other templates on the
lines that follow the message:
    - The first line contains the hook id "hook id: flake8"
    - The second line contains the exit code "exit code: 1"
    - The third line is empty ""
    - The lines after the third line contain the exception message(s)
    "klingon_tools/pre_commit.py:131:80: E501 line too long (80 > 79
    characters)" and could be many lines long.

```raw_output
flake8...................................................................Failed
- hook id: flake8
- exit code: 1

klingon_tools/pre_commit.py:131:80: E501 line too long (80 > 79 characters)
```

```message_template[padding=".", width=80]
{message}{padding}{status}
- hook id: {exception_hook_id}
- exit code: {exception_exit_code}

{exception_message}
```

Lets also add a fourth "Catch-all" template that will be used if the parser is
unable to exact match any of the other templates.

Once this data is collected we can use the fields captured in the template to
log output via log_message(). The {message}, {status}, {reason} are all direct
mapped to arguments that log_message accepts. The {exception_hook_id},
exception_exit_code and exception_message are specific to error handling and
should be logged using the following template:

```python
def pre_commit_exception_log_message():
    # Log the first line
    log_message(
        message=message,
        status=status
    )

    # Log the hook id
    log_message(
        message=f"hook id: {exception_hook_id}"
    )

    # Log the exit code
    log_message(
        message=f"exit code: {exception_exit_code}"
    )

    # Log the exception message
    for line in exception_message:
        log_message(
            message=line
        )
```
