#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scitex-io CLI - Command-line interface for scitex-io."""

from ._main import main

__all__ = ["main"]


# audit §4 — inject version into root --help
try:
    from importlib.metadata import version as _v
    main.help = (
        f"scitex-io (v{_v('scitex-io')}) — "
        + (main.help or "").lstrip()
    )
except Exception:
    pass
