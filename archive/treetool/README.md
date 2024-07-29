# tt - Treetool

A tool for saving and generating project file and directory structures. It was
designed to provide a rapid way of generating directory and file structures for
new projects.

It can take a CSV file as input to create a directory structure or save a CSV
file representing the file and directory structure from an existing project. It
also has a raw mode that accepts piped input from `tree -F`.

## Features

- Create a directory structure from a CSV file.
- Save a CSV file representing the file and directory structure of a project.
- Accept raw input from `tree -F` and generate a CSV file from it.

## Usage

```bash
tt [OPTIONS]
```

Options:

- `-c, --create FILE`: Create directory and file structure using a CSV file as input.
- `-s, --save FILE`: Save the directory and file structure to the CSV file provided.
- `-i, --install`: Install tt into /usr/local/bin/ and test if it's in the path.
- `--raw`: Process raw input from 'tree -F' and create a CSV file. (Must be
  used with -o/--output)
- `-v, --version`: Print the version number and exit.

## Installation

`tt` can be installed and upgraded using the `-i` or `--install` command-line argument.

## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
