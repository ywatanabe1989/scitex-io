#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for trivial shim modules — `__main__.py` and `_load_cache.py`.

from __future__ import annotations
These exist for back-compat with the umbrella; just verify the
re-exports work and `python -m scitex_io` invokes the CLI cleanly.
"""


import subprocess
import sys


class TestMainEntryPoint:
    def test_python_dash_m_scitex_io_help(self):
        """`python -m scitex_io --help` should exit 0 and print help."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_io", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"exit {result.returncode}; stderr={result.stderr!r}"
        )
        assert "Usage" in result.stdout or "usage" in result.stdout.lower()

    def test_python_dash_m_scitex_io_version(self):
        result = subprocess.run(
            [sys.executable, "-m", "scitex_io", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

