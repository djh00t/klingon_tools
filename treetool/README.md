# tt - Treetool

`tt` is a utility for mapping and generating directory structures. It was designed to provide a rapid way of generating directory and file structures for new projects. 

## Features

- Generate a directory structure from a CSV file.
- Generate a CSV file representing the file and directory structure from an existing directory.
- Accept raw input from `tree -F` and generate a CSV file from it.

## Usage

```bash
tt [OPTIONS]
```

Options:

- `-i, --input FILE`: Use the provided CSV file as input.
- `-o, --output FILE`: Write the directory and file structure to the provided CSV file.
- `-i, --install`: Install tt into /usr/local/bin/ and test if it's in the path.
- `--raw`: Process raw input from `tree` and create a CSV file.

## Installation

`tt` can be installed into `/usr/local/bin/` using the `-i` or `--install` command-line argument.

## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
