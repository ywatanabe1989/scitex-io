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
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


# Dict utilities
class DotDict:
    """A dictionary-like object that allows attribute-like access (for valid identifier keys)
    and standard item access for all keys (including integers, etc.)."""

    def __init__(self, dictionary=None):
        super().__setattr__("_data", {})
        if dictionary is not None:
            if isinstance(dictionary, DotDict):
                dictionary = dictionary._data
            elif not isinstance(dictionary, dict):
                raise TypeError("Input must be a dictionary.")
            for key, value in dictionary.items():
                if isinstance(value, dict) and not isinstance(value, DotDict):
                    value = DotDict(value)
                self[key] = value

    def __getattr__(self, key):
        if key.startswith("_"):
            return super().__getattribute__(key)
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

    def __setattr__(self, key, value):
        if key == "_data" or key.startswith("_"):
            super().__setattr__(key, value)
        else:
            if isinstance(value, dict) and not isinstance(value, DotDict):
                value = DotDict(value)
            self._data[key] = value

    def __delattr__(self, key):
        if key.startswith("_"):
            super().__delattr__(key)
        else:
            try:
                del self._data[key]
            except KeyError:
                raise AttributeError(
                    f"'{type(self).__name__}' object has no attribute '{key}'"
                )

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def to_dict(self, include_private=False):
        """Recursively convert to plain dict."""
        result = {}
        for key, value in self._data.items():
            if not include_private and isinstance(key, str) and key.startswith("_"):
                continue
            if isinstance(value, DotDict):
                value = value.to_dict(include_private=include_private)
            result[key] = value
        return result

    def __str__(self):
        import json as _json

        def default_handler(obj):
            if isinstance(obj, DotDict):
                return obj.to_dict()
            try:
                _json.dumps(obj)
                return obj
            except (TypeError, OverflowError):
                return str(obj)

        try:
            return _json.dumps(self.to_dict(), indent=4, default=default_handler)
        except TypeError as e:
            return f"<DotDict at {hex(id(self))}, keys: {list(self._data.keys())}> Error: {e}"

    def __repr__(self):
        import pprint as _pprint

        return _pprint.pformat(self.to_dict(include_private=False), indent=2, width=80)

    def __len__(self):
        return len(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def update(self, dictionary):
        if isinstance(dictionary, dict):
            iterator = dictionary.items()
        elif hasattr(dictionary, "__iter__"):
            iterator = dictionary
        else:
            raise TypeError(
                "Input must be a dictionary or an iterable of key-value pairs."
            )
        for key, value in iterator:
            self[key] = value

    def setdefault(self, key, default=None):
        if key not in self._data:
            self[key] = default
            return default
        return self._data[key]

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError(f"pop expected at most 2 arguments, got {1 + len(args)}")
        if key not in self._data:
            if args:
                return args[0]
            raise KeyError(key)
        return self._data.pop(key)

    def __contains__(self, key):
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def copy(self):
        return DotDict(self._data.copy())

    def __eq__(self, other):
        if isinstance(other, DotDict):
            return self._data == other._data
        elif isinstance(other, dict):
            return self._data == other
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return len(self._data) > 0


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
