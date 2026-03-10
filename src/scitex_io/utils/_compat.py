#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compatibility layer for scitex error classes.

When scitex is installed, uses real error classes.
Otherwise provides lightweight fallbacks.
"""

import os
import warnings

try:
    from scitex.errors import (
        IOError as SciTeXIOError,
        FileFormatError,
        PathNotFoundError,
        check_file_exists,
        check_path,
        warn_data_loss,
    )

    SCITEX_ERRORS_AVAILABLE = True
except ImportError:
    SCITEX_ERRORS_AVAILABLE = False

    class SciTeXIOError(Exception):
        def __init__(self, msg, context=None, suggestion=None):
            super().__init__(msg)

    class FileFormatError(Exception):
        def __init__(self, path, expected_format=None, actual_format=None):
            super().__init__(f"File format error: {path}")

    class PathNotFoundError(FileNotFoundError):
        pass

    def check_file_exists(path):
        if not os.path.exists(path):
            raise FileNotFoundError(path)

    def check_path(path):
        pass

    def warn_data_loss(name, msg):
        warnings.warn(f"Data loss warning for {name}: {msg}")
