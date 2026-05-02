#!/usr/bin/env python3
"""Tests for the format registry system."""
from scitex_io._registry import (
    register_saver, register_loader, get_saver, get_loader,
    list_formats, unregister_saver, unregister_loader, _normalize_ext,
)

class TestNormalizeExt:
    def test_adds_dot(self):
        assert _normalize_ext("csv") == ".csv"
    def test_keeps_dot(self):
        assert _normalize_ext(".csv") == ".csv"
    def test_lowercase(self):
        assert _normalize_ext(".CSV") == ".csv"

class TestRegistry:
    def test_builtin_formats_loaded(self):
        fmts = list_formats()
        assert len(fmts["save"]["builtin"]) > 20
        assert len(fmts["load"]["builtin"]) > 20

    def test_get_builtin_saver(self):
        assert callable(get_saver(".json"))

    def test_get_builtin_loader(self):
        assert callable(get_loader(".json"))

    def test_unknown_ext_returns_none(self):
        assert get_saver(".unknown_xyz") is None
        assert get_loader(".unknown_xyz") is None

    def test_user_override(self):
        def my_saver(obj, path, **kw): pass
        register_saver(".test_ov", my_saver)
        assert get_saver(".test_ov") is my_saver
        unregister_saver(".test_ov")
        assert get_saver(".test_ov") is None

    def test_decorator_pattern(self):
        @register_saver(".test_deco")
        def save_deco(obj, path, **kw): pass
        assert get_saver(".test_deco") is save_deco
        unregister_saver(".test_deco")

    def test_user_overrides_builtin(self):
        original = get_saver(".json")
        def custom_json(obj, path, **kw): pass
        register_saver(".json", custom_json)
        assert get_saver(".json") is custom_json
        unregister_saver(".json")
        assert get_saver(".json") is original
