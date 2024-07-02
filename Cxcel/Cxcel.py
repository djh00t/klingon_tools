import argparse
import curses
import signal
import time

import numpy as np
import pandas as pd
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class CSVFileHandler(FileSystemEventHandler):
    """
    A file system event handler that triggers a redraw callback when the specified CSV file is modified.

    Attributes:
        filename (str): The path to the CSV file being monitored.
        redraw_callback (function): The callback function to be called when the file is modified.
        max_col_width (int): The maximum width for any column when rendering the CSV.
    """

    def __init__(self, filename, redraw_callback, max_col_width=20):
        """
        Initialize the CSVFileHandler with the filename, redraw callback, and maximum column width.

        Args:
            filename (str): The path to the CSV file being monitored.
            redraw_callback (function): The callback function to be called when the file is modified.
            max_col_width (int): The maximum width for any column when rendering the CSV.
        """
        self.filename = filename
        self.redraw_callback = redraw_callback
        self.max_col_width = max_col_width

    def on_modified(self, event):
        """
        Event handler for the modified event. Calls the redraw callback if the monitored file is modified.

        Args:
            event (FileSystemEvent): The event object representing the file system event.
        """
        if event.src_path == self.filename:
            self.redraw_callback()


def get_column_widths(df, max_col_width):
    widths = [
        min(max(len(str(value)) for value in df[col].fillna("")), max_col_width)
        for col in df.columns
    ]
    header_widths = [min(len(str(header)), max_col_width) for header in df.columns]
    return [max(w, h) for w, h in zip(widths, header_widths)]


def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Header color
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Regular text


def render_csv(stdscr, filename, max_col_width):
    df = pd.read_csv(filename).fillna("")  # Replace NaN with empty string
    max_y, max_x = stdscr.getmaxyx()
    col_widths = get_column_widths(df, max_col_width)

    init_colors()

    header_str = " | ".join(
        str(df.columns[i]).ljust(col_widths[i]) for i in range(len(df.columns))
    )
    stdscr.attron(curses.color_pair(1))  # Colored header
    stdscr.addstr(0, 0, header_str[:max_x])
    stdscr.attroff(curses.color_pair(1))

    stdscr.addstr(1, 0, "-" * (sum(col_widths) + len(col_widths) * 3))

    for i, row in enumerate(df.itertuples(index=False), start=2):
        if i > max_y:
            break
        line = " | ".join(
            str(getattr(row, col)).ljust(col_widths[j])
            for j, col in enumerate(df.columns)
        )
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(i, 0, line[:max_x])
        stdscr.attroff(curses.color_pair(2))

    stdscr.refresh()


def handle_resize(stdscr, filename, max_col_width):
    def redraw():
        stdscr.clear()
        render_csv(stdscr, filename, max_col_width)

    return redraw


def main(stdscr, filename, max_col_width=20):
    curses.curs_set(0)  # Hide cursor
    redraw = handle_resize(stdscr, filename, max_col_width)
    render_csv(stdscr, filename, max_col_width)

    event_handler = CSVFileHandler(filename, redraw, max_col_width)
    observer = Observer()
    observer.schedule(event_handler, filename, recursive=False)
    observer.start()

    signal.signal(signal.SIGWINCH, lambda sig, frame: redraw())

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render CSV file in terminal")
    parser.add_argument("filename", help="Path to the CSV file")
    args = parser.parse_args()

    curses.wrapper(main, args.filename, max_col_width=20)
