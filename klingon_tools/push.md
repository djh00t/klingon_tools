# push

The `push` command provides automated conventional commit message generation using the OpenAI API, pre-commit hooks, and other tools that make rapid iterative development structured, consistent, and easy to manage.

## Features

- **Automated Commit Message Generation**: Generate commit messages based on the changes made using the OpenAI API.
- **Pre-commit Hooks**: Run pre-commit hooks to ensure code quality and consistency.
- **Batch Processing**: Process all untracked and modified files in batch mode.
- **One-shot Mode**: Process and commit only one file and then exit.
- **Dry-run Mode**: Run the script without committing or pushing changes.

## Installation

To install the `push` tool, you can use pip:

```sh
pip install klingon_tools
```

## Usage

To use the `push` command, run it from the root of your repository:

```sh
push [OPTIONS]
```

### Command-Line Arguments

The following command-line arguments are supported:

- `--repo-path <path>`: Path to the git repository (default: current directory).
- `--debug`: Enable debug mode.
- `--file-name <file>`: File name to stage and commit.
- `--oneshot`: Process and commit only one file then exit.
- `--dryrun`: Run the script without committing or pushing changes.
- `-h`, `--help`: Show help message and exit.

### Example Usage

Process all untracked and modified files in batch mode:

```sh
push
```

**Expected Output:**

```plaintext
Checking for software requirements...                                        ✅
Using git user name:...                                            John Doe
Using git user email:...                                       john.doe@example.com
--------------------------------------------------------------------------------
Deleted files...                                                              0
Untracked files...                                                            2
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

✨ feat(klingon_tools): Update README.md with additional utilities and descriptions

- Updated descriptions and formatting for LogTools features.
- Added new utilities like push and gh-actions-update with descriptions.
- Included installation instructions and class/method details for better understanding of LogTools.
- Expanded on the usage examples of `log_message`, `method_state`, and `command_state`.
- Documented the new `push` command with its arguments and example usage for a structured development process.
- Provided information on contributing to the project and welcoming new ideas.

Signed-off-by: John Doe <john.doe@example.com>

--------------------------------------------------------------------------------
Pre-commit completed...                                                      ✅
File committed...                                                            ✅
Pushed changes to remote repository...                                       ✅
All files processed. Script completed successfully....                       🚀
================================================================================
```

Process and commit only one file:

```sh
push --oneshot
```

**Expected Output:**

```plaintext
Checking for software requirements...                                        ✅
Using git user name:...                                            John Doe
Using git user email:...                                       john.doe@example.com
--------------------------------------------------------------------------------
Deleted files...                                                              0
Untracked files...                                                            2
Modified files...                                                             1
Staged files...                                                               0
Committed not pushed files...                                                 0
--------------------------------------------------------------------------------
One-shot mode enabled...                                                     🎯
Un-staging all staged files...                                               🔄
Processing file...                                      klingon_tools/README.md
Staging file...                                                              ✅
Diff generated...                                                            ✅
--------------------------------------------------------------------------------
Generated commit message:

✨ feat(klingon_tools): Update README.md with additional utilities and descriptions

- Updated descriptions and formatting for LogTools features.
- Added new utilities like push and gh-actions-update with descriptions.
- Included installation instructions and class/method details for better understanding of LogTools.
- Expanded on the usage examples of `log_message`, `method_state`, and `command_state`.
- Documented the new `push` command with its arguments and example usage for a structured development process.
- Provided information on contributing to the project and welcoming new ideas.

Signed-off-by: John Doe <john.doe@example.com>

--------------------------------------------------------------------------------
Pre-commit completed...                                                      ✅
File committed...                                                            ✅
Pushed changes to remote repository...                                       ✅
All files processed. Script completed successfully....                       🚀
================================================================================
```

Run the script without committing or pushing changes:

```sh
push --dryrun
```

**Expected Output:**

```plaintext
Checking for software requirements...                                        ✅
Using git user name:...                                            John Doe
Using git user email:...                                       john.doe@example.com
--------------------------------------------------------------------------------
Deleted files...                                                              0
Untracked files...                                                            2
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

✨ feat(klingon_tools): Update README.md with additional utilities and descriptions

- Updated descriptions and formatting for LogTools features.
- Added new utilities like push and gh-actions-update with descriptions.
- Included installation instructions and class/method details for better understanding of LogTools.
- Expanded on the usage examples of `log_message`, `method_state`, and `command_state`.
- Documented the new `push` command with its arguments and example usage for a structured development process.
- Provided information on contributing to the project and welcoming new ideas.

Signed-off-by: John Doe <john.doe@example.com>

--------------------------------------------------------------------------------
Pre-commit completed...                                                      ✅
Dry run mode enabled. Skipping commit and push...                            🚫
All files processed. Script completed successfully....                       🚀
================================================================================
```

### Environmental Requirements

The `push` command requires an OpenAI API key to generate commit messages. Set the `OPENAI_API_KEY` environment variable with your OpenAI API key:

```sh
export OPENAI_API_KEY=your_openai_api_key
```

## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
