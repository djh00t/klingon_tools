# Klingon Pre-Commit Hooks - Logging Templates

There are 4 possible statuses for the parser to handle:
    - Passed
    - Skipped
    - Failed
    - Other

The schema returned by the parser will be slightly different depending on the
status. The schema will always contain: 
    - template: The matched template
    - raw_message: The raw original log line
    - message: The parsed message
    - reason: The reason field value if present
    - padding: The padding used in the message
    - status: The status of the message

Following is how I want the parser to handle and log each status. The dict in
these examples is the schema that will be returned by the parser.

## Passed

A success is logged and the pre-commit run will continue

```logging
--------------------------------------------------------------------------------
DEBUG:pre_commit_parser
    {
        "template": "Template 1",
        "raw_message": "check for added large files..............................................Passed",
        "message": "check for added large files",
        "reason": None,
        "padding": ".",
        "status": "Passed",
    }
Check for Added Large Files.................................................. ✅
--------------------------------------------------------------------------------
```

## Skipped

The hook was skipped and pre-commit will continue

```logging
--------------------------------------------------------------------------------
DEBUG:pre_commit_parser
    {
        "template": "Template 2",
        "raw_message": "check python ast.....................................(no files to check)Skipped",
        "message": "check python ast",
        "reason": "no files to check",
        "padding": ".",
        "status": "Skipped",
    }
Check Python AST..................................................... SKIPPED 🦘
--------------------------------------------------------------------------------
```

## Failed

The hook has failed and the pre-commit run will be aborted.

Failed is a special case as it contains more than one line of information to
manage. The first line contains the basic message, padding and status. The
subsequent lines contain the exception data.

How to parse the exception data:
    - There may be multiple exceptions in the `exceptions` list of dictionaries.
    - There may be blank lines in the output which must be ignored.
    - Exceptions all start with the `hook_id`
    - The `exit_code` is on the line directly under the `hook_id`
    - One or more lines of exception message will follow and must be collected
    and saved in the `exceptions.exception_messages` list for the exception it belongs to.
    - Continue to read lines until pre-commit exits or a new exception is provided.

Interpreted Data:
    - If "files were modified by this hook" is present in `exceptions.exception_messages` then:
        - Set `exceptions.files_modified` to an empty list.
        - Add file names from the exception messages to `exceptions.files_modified`.

```logging
--------------------------------------------------------------------------------
DEBUG:pre_commit_parser
    {
        "template": "Template 3",
        "raw_message": "fix end of files.........................................................Failed",
        "message": "fix end of files",
        "reason": None,
        "padding": ".",
        "status": "Failed",
        "exceptions": [
            {
                "hook_id": "end-of-file-fixer",
                "exit_code": 1,
                "exception_messages": [
                    "files were modified by this hook",
                    "Fixing pre-commit_parser_spec.md",
                ],
                "files_modified": [
                    "pre_commit_parser_spec.md"
                ]
            }
        ]
    }
Fix End of Files............................................................. ❌
--------------------------------------------------------------------------------
```

## Other

If the log line doesn't match any of the other templates, the parser will log
the raw messages one line at a time until such time as a template matches the
line or the pre-commit run finishes.

Using the previously provided and returned code, give me a fully integrated
file that uses DRY, pep8, google style guide and that works with the provided
data.

The file we are working on is part of a library and is called by other parts of the code base using git_pre_commit and set_debug_mode like this:
```
    # Run pre-commit hooks
    success, _ = git_pre_commit(
        file_name, current_repo, modified_files)
```
and this:
```
    # Set debug mode for downstream usage
    set_debug_mode(args.debug)
```
