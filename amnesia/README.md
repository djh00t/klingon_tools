# Amnesia

This script is used to cleanup commit messages in a Git repository. It uses the
`git filter-branch` command to rewrite history, replacing a specified string in
commit messages with another string (or deleting it) all of these things being
something you really shouldn't be doing.

**WARNING:** This script rewrites history. Git won't remember the thing
you delete. There is no turning back. Using this script is almost certainly an
extremely bad idea, but if this is your jam go at it.

## Usage

The script accepts the following command-line arguments:

- `-b` or `--branch`: The branch where you want to start rewriting history. If not provided, the script will use the current branch.
- `-i` or `--install`: Install the script to your path. This will copy the
  script to `/usr/local/bin/amnesia` and make it executable. You will need to
  run this as root or with `sudo`.
- `-s` or `--string`: The string to be replaced in commit messages.
- `-v` or `--version`: Print the version number and exit.

Example:

```bash
./amnesia -s "old string" -b main
```

This will replace all occurrences of "old string" in commit messages on the `main` branch with an empty string (i.e., delete it).

## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
