#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for trivial shim modules — `__main__.py` and `_load_cache.py`.

from __future__ import annotations
These exist for back-compat with the umbrella; just verify the
re-exports work and `python -m scitex_io` invokes the CLI cleanly.
"""


import subprocess
import sys


class TestLoadCacheShim:
    def test_reexports_cache_data(self):
        from scitex_io._load_cache import (
            cache_data,
            get_cached_data,
            load_npy_cached,
        )

        # Each export must be callable.
        for fn in (cache_data, get_cached_data, load_npy_cached):
            assert callable(fn), f"{fn!r} should be callable"

    def test_reexports_match_loading_module(self):
        # The shim should re-export the SAME objects as
        # `scitex_io._loading._load_cache`, not copies.
        from scitex_io import _load_cache as shim
        from scitex_io._loading import _load_cache as canonical

        assert shim.cache_data is canonical.cache_data
        assert shim.get_cached_data is canonical.get_cached_data
        assert shim.load_npy_cached is canonical.load_npy_cached

    def test_all_attribute(self):
        from scitex_io import _load_cache as shim

        assert set(shim.__all__) == {
            "cache_data",
            "get_cached_data",
            "load_npy_cached",
        }


