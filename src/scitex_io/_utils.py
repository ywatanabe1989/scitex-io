#!/usr/bin/env python3
"""
Inline utilities to avoid external dependencies.
All utilities needed by scitex-io that would otherwise come from scitex.
"""

import os
from pathlib import Path


# String utilities
def clean_path(path_string):
    """Clean and normalize a file system path."""
    return os.path.normpath(str(path_string))


def color_text(text, color):
    """Simple colored text."""
    try:
        from colorama import Fore, Style
        colors = {
            "green": Fore.GREEN,
            "red": Fore.RED,
            "yellow": Fore.YELLOW,
            "blue": Fore.BLUE,
            "magenta": Fore.MAGENTA,
            "cyan": Fore.CYAN,
        }
        return f"{colors.get(color, '')}{text}{Style.RESET_ALL}"
    except ImportError:
        return text


def readable_bytes(size):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


# Dict utilities
class DotDict(dict):
    """Dictionary with dot notation access."""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dictionary=None):
        if dictionary:
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    value = DotDict(value)
                self[key] = value


# Decorator utilities
def preserve_doc(func):
    """Placeholder for preserve_doc decorator."""
    return func


# Path utilities
def split(path):
    """Split path into components."""
    return Path(path).parts


def this_path():
    """Get current file path."""
    import inspect
    frame = inspect.currentframe().f_back
    return frame.f_code.co_filename


def clean(path):
    """Clean path."""
    return str(Path(path).resolve())


def getsize(path):
    """Get file size in bytes."""
    return Path(path).stat().st_size if Path(path).exists() else 0


# String parsing
def parse(string, pattern=None):
    """Simple string parser."""
    if pattern is None:
        return string
    import re
    return re.findall(pattern, string)


# Environment detection
def detect_environment():
    """Detect execution environment."""
    try:
        get_ipython()  # type: ignore
        return "jupyter"
    except NameError:
        return "python"


def get_notebook_info_simple():
    """Get notebook info."""
    return {"path": None, "name": None}
