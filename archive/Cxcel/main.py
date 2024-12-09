# Cxcel/main.py
import argparse
import curses
import time

import pandas as pd
from flask import Flask, jsonify, render_template
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import os

# Initialize Flask app
app = Flask(__name__)
filename = None


class TerminalCSVFileHandler(FileSystemEventHandler):
    """
    A file system event handler for terminal mode that updates the terminal
    display when the CSV file is modified.

    Attributes:
        stdscr (curses window object): The curses window used for rendering the
        CSV content. filename (str): The path to the CSV file being monitored.
    """

    def __init__(self, stdscr, filename):
        """
        Initialize the TerminalCSVFileHandler with the curses window and
        filename.

        Args:
            stdscr (curses window object): The curses window used for rendering
            the CSV content. filename (str): The path to the CSV file being
            monitored.
        """
        self.stdscr = stdscr
        self.filename = filename

    def on_modified(self, event):
        """
        Event handler for the modified event. Clears the screen and re-renders
        the CSV content when the file is modified.

        Args:
            event (FileSystemEvent): The event object representing the file
            system event.
        """
        if event.src_path == self.filename:
            self.stdscr.clear()
            render_csv(self.stdscr, self.filename)
            self.stdscr.refresh()


def get_column_widths(df, max_col_width=20):
    widths = [
        min(
            max(len(str(value)) for value in df[col].fillna("")), max_col_width
        )
        for col in df.columns
    ]
    header_widths = [
        min(len(str(header)), max_col_width) for header in df.columns
    ]
    return [max(w, h) for w, h in zip(widths, header_widths)]


def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Header color
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Regular text


def render_csv(stdscr, file):
    df = pd.read_csv(file).fillna("")
    max_y, max_x = stdscr.getmaxyx()
    col_widths = get_column_widths(df)

    init_colors()

    header_str = " | ".join(
        str(df.columns[i]).ljust(col_widths[i]) for i in range(len(df.columns))
    )
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(0, 0, header_str)
    stdscr.attroff(curses.color_pair(1))

    # Calculate total line length based on column widths
    total_line_length = (
        sum(col_widths) + (len(col_widths) - 1) * 3
    )  # Adjust for separators
    stdscr.addstr(1, 0, "-" * total_line_length)

    for i, row in enumerate(df.itertuples(index=False), start=2):
        if i > max_y:
            break
        line = " | ".join(
            str(row[j]).ljust(col_widths[j]) for j in range(len(row))
        )
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(i, 0, line)
        stdscr.attroff(curses.color_pair(2))

    stdscr.refresh()


def run_in_terminal(stdscr, filename):
    curses.curs_set(0)
    render_csv(stdscr, filename)

    event_handler = TerminalCSVFileHandler(stdscr, filename)
    observer = Observer()
    observer.schedule(event_handler, filename, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def run_terminal_viewer(filename):
    curses.wrapper(run_in_terminal, filename)


class CSVFileHandler(FileSystemEventHandler):
    def __init__(self, update_function):
        self.update_function = update_function

    def on_modified(self, event):
        if event.src_path == filename:
            self.update_function()


def read_csv_to_html(file):
    df = pd.read_csv(file).fillna("")
    return df.to_html(
        index=False,
        border=0,
        classes="table table-striped",
        table_id="csv-data",
    )


@app.route("/")
def index():
    return render_template("index.html", table=read_csv_to_html(filename))


@app.route("/update")
def update():
    return jsonify({"table": read_csv_to_html(filename)})


def run_web_server():
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode, use_reloader=True)


def main():
    global filename

    parser = argparse.ArgumentParser(description="CSV Viewer")
    parser.add_argument("--file", help="Path to the CSV file", required=True)
    parser.add_argument(
        "--web", action="store_true", help="Launch web interface"
    )
    args = parser.parse_args()

    filename = args.file

    if args.web:
        # Web mode
        observer = Observer()
        # Placeholder update function
        event_handler = CSVFileHandler(lambda: None)
        observer.schedule(event_handler, path=filename, recursive=False)
        observer.start()

        debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
        app.run(debug=debug_mode, use_reloader=True)

        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        # Terminal mode
        run_terminal_viewer(filename)  # Pass filename here


if __name__ == "__main__":
    main()
