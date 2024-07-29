# Cxcel - Terminal and Web CSV Viewer

## Overview

Render CSV files in both terminal and web interfaces. It provides real-time updates to the displayed CSV content by monitoring file changes, making it an excellent tool for viewing and analyzing data streams or frequently updated CSV files.

## Features

- Terminal-based CSV rendering with real-time updates.
- Web interface for viewing CSV files in a browser.
- Automatic adjustment of column widths based on content.
- Color-coded headers for better readability.
- Responsive design to fit different terminal and browser window sizes.

## Installation

To install Cxcel, you need to have Python installed on your system. Cxcel also requires several third-party libraries which can be installed using pip:

```bash
pip install -r requirements.txt
```

## Usage

### Terminal Mode

To run Cxcel in terminal mode, navigate to the Cxcel directory and execute:

```bash
python main.py --file path/to/your/file.csv
```

This will open the CSV file in your terminal window with real-time updates.

### Web Mode

To run Cxcel in web mode, use the `--web` flag:

```bash
python main.py --file path/to/your/file.csv --web
```

This will start a local web server, and you can view the CSV file by navigating to `http://localhost:5000` in your web browser.

## Development

Cxcel is an open-source project, and contributions are welcome. If you find a bug or have a feature request, please open an issue or submit a pull request.

## License

Cxcel is released under the MIT License. See the LICENSE file for more details.
