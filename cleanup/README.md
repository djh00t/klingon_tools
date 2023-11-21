# Cleanup Script

This script is used to cleanup commit messages in a Git repository. It uses the `git filter-branch` command to rewrite the history of the repository, replacing a specified string in commit messages with another string (or deleting it).

## Usage

The script accepts two command-line arguments:

- `-s` or `--string`: The string to be replaced in commit messages.
- `-b` or `--branch`: The branch where you want to start rewriting history. If not provided, the script will use the current branch.

Example:

```bash
./cleanup -s "old string" -b main
```

This will replace all occurrences of "old string" in commit messages on the `main` branch with an empty string (i.e., delete it).

**WARNING:** This script rewrites the history of the Git repository. Use with caution.
