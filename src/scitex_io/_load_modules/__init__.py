#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:05:00 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/__init__.py

"""
Load modules for scitex.io.load functionality.

Each handler is imported with a try/except so that missing optional
dependencies only disable the relevant format rather than crashing the
entire package.
"""

import importlib as __importlib
import inspect as __inspect
import os as __os
import warnings as __warnings

_current_dir = __os.path.dirname(__file__)
_pkg = __name__

for _filename in __os.listdir(_current_dir):
    if not _filename.endswith(".py") or _filename.startswith("__"):
        continue
    _module_name = _filename[:-3]
    try:
        _module = __importlib.import_module(f".{_module_name}", package=_pkg)
    except ImportError as _exc:
        __warnings.warn(
            f"scitex_io: optional dependency missing, skipping load module "
            f"'{_module_name}': {_exc}",
            ImportWarning,
            stacklevel=2,
        )
        continue

    for _name, _obj in __inspect.getmembers(_module):
        if (__inspect.isfunction(_obj) or __inspect.isclass(_obj)) and not _name.startswith("_"):
            globals()[_name] = _obj

# Clean up loop variables
del (
    __os,
    __importlib,
    __inspect,
    __warnings,
    _current_dir,
    _pkg,
    _filename,
    _module_name,
    _module,
    _name,
    _obj,
)

# EOF
