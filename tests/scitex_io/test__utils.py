#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_io._utils.

from __future__ import annotations
Every public helper + the DotDict class. Real fixtures only — no mocks
around the system layer beyond `monkeypatch` for env vars / sys.argv.
"""


import os
import sys
from pathlib import Path

import pytest

from scitex_io._utils import (
    DotDict,
    clean,
    clean_path,
    color_text,
    detect_environment,
    get_notebook_info_simple,
    getsize,
    parse,
    preserve_doc,
    readable_bytes,
    split,
    this_path,
)


class TestStringHelpers:
    def test_clean_path_normalises(self):
        assert clean_path("/a/b/../c") == os.path.normpath("/a/b/../c")
        assert clean_path("./x/./y") == os.path.normpath("./x/./y")

    def test_clean_path_pathlike(self):
        assert clean_path(Path("/a") / "b") == os.path.normpath("/a/b")

    def test_color_text_known(self):
        # With colorama installed (it's a transitive dep), expect ANSI
        # escape codes around the text. Without colorama, fall through.
        out = color_text("hi", "green")
        assert "hi" in out

    def test_color_text_unknown_color(self):
        out = color_text("hi", "lavender")
        assert "hi" in out


class TestReadableBytes:
    @pytest.mark.parametrize(
        "size,expected_unit",
        [
            (5, "B"),
            (1500, "KB"),
            (5 * 1024 * 1024, "MB"),
            (3 * 1024**3, "GB"),
            (2 * 1024**4, "TB"),
            (5 * 1024**5, "PB"),
        ],
    )
    def test_units(self, size, expected_unit):
        out = readable_bytes(size)
        assert out.endswith(expected_unit)


class TestDotDictBasics:
    def test_empty_construct(self):
        d = DotDict()
        assert len(d) == 0
        assert bool(d) is False

    def test_from_dict(self):
        d = DotDict({"a": 1, "b": "x"})
        assert d.a == 1
        assert d.b == "x"
        assert bool(d) is True

    def test_from_dotdict(self):
        a = DotDict({"x": 1})
        b = DotDict(a)
        assert b.x == 1

    def test_invalid_input_type(self):
        with pytest.raises(TypeError):
            DotDict([1, 2, 3])

    def test_nested_dict_wraps(self):
        d = DotDict({"top": {"inner": 1}})
        assert isinstance(d.top, DotDict)
        assert d.top.inner == 1

    def test_attr_access_missing_raises(self):
        d = DotDict({"a": 1})
        with pytest.raises(AttributeError):
            _ = d.nonexistent

    def test_attr_set_and_del(self):
        d = DotDict()
        d.x = 5
        assert d.x == 5
        del d.x
        with pytest.raises(AttributeError):
            del d.x  # already gone

    def test_item_access(self):
        d = DotDict({"a": 1, 42: "answer"})
        assert d["a"] == 1
        assert d[42] == "answer"
        d["new"] = 7
        assert d.new == 7
        del d["a"]
        assert "a" not in d

    def test_item_set_wraps_dict(self):
        d = DotDict()
        d["sub"] = {"k": 1}
        assert isinstance(d["sub"], DotDict)
        assert d["sub"].k == 1


class TestDotDictMappingMethods:
    def test_get(self):
        d = DotDict({"a": 1})
        assert d.get("a") == 1
        assert d.get("missing", "default") == "default"

    def test_keys_values_items(self):
        d = DotDict({"a": 1, "b": 2})
        assert set(d.keys()) == {"a", "b"}
        assert set(d.values()) == {1, 2}
        assert set(d.items()) == {("a", 1), ("b", 2)}

    def test_update_with_dict(self):
        d = DotDict({"a": 1})
        d.update({"b": 2, "a": 99})
        assert d.a == 99
        assert d.b == 2

    def test_update_with_iterable(self):
        d = DotDict()
        d.update([("a", 1), ("b", 2)])
        assert d.a == 1 and d.b == 2

    def test_update_bad_input(self):
        d = DotDict()
        with pytest.raises(TypeError):
            d.update(123)

    def test_setdefault(self):
        d = DotDict({"a": 1})
        assert d.setdefault("a", 99) == 1
        assert d.a == 1
        assert d.setdefault("b", 7) == 7
        assert d.b == 7

    def test_pop(self):
        d = DotDict({"a": 1})
        assert d.pop("a") == 1
        assert "a" not in d
        assert d.pop("missing", "default") == "default"
        with pytest.raises(KeyError):
            d.pop("missing")
        with pytest.raises(TypeError):
            d.pop("a", "b", "c")

    def test_contains_iter(self):
        d = DotDict({"a": 1, "b": 2})
        assert "a" in d
        assert list(iter(d)) == ["a", "b"]


class TestDotDictReprAndEq:
    def test_eq_with_dotdict(self):
        assert DotDict({"a": 1}) == DotDict({"a": 1})
        assert DotDict({"a": 1}) != DotDict({"a": 2})

    def test_eq_with_plain_dict(self):
        assert DotDict({"a": 1}) == {"a": 1}
        assert DotDict({"a": 1}) != {"a": 2}

    def test_eq_other_type_returns_false(self):
        assert (DotDict({"a": 1}) == 42) is False

    def test_to_dict_recursive(self):
        d = DotDict({"a": 1, "b": {"c": 2}})
        plain = d.to_dict()
        assert plain == {"a": 1, "b": {"c": 2}}
        assert not isinstance(plain["b"], DotDict)

    def test_to_dict_skips_private_keys(self):
        d = DotDict({"_secret": 1, "open": 2})
        plain = d.to_dict()
        assert "_secret" not in plain
        assert plain["open"] == 2
        plain_all = d.to_dict(include_private=True)
        assert "_secret" in plain_all

    def test_str_is_json(self):
        d = DotDict({"a": 1})
        s = str(d)
        assert '"a": 1' in s

    def test_str_handles_unserialisable(self):
        # Custom non-JSON-serialisable object falls through default_handler
        class Weird:
            def __repr__(self):
                return "<weird>"

        d = DotDict({"x": Weird()})
        s = str(d)
        assert "weird" in s.lower()

    def test_repr_pprint(self):
        d = DotDict({"a": 1})
        assert "'a': 1" in repr(d)

    def test_copy(self):
        d = DotDict({"a": 1})
        c = d.copy()
        assert c == d
        c["a"] = 99
        assert d.a == 1


class TestPathHelpers:
    def test_preserve_doc_returns_func(self):
        def f():
            "doc"
            return 1

        g = preserve_doc(f)
        assert g() == 1
        assert g.__doc__ == "doc"

    def test_split(self):
        parts = split("/a/b/c")
        assert "a" in parts and "b" in parts and "c" in parts

    def test_this_path(self):
        p = this_path()
        # The function returns the *caller's* file (this test file).
        assert "test__utils.py" in p

    def test_clean(self, tmp_path):
        p = tmp_path / "sub" / ".."
        c = clean(str(p))
        # Resolved → tmp_path absolute
        assert Path(c) == tmp_path.resolve()

    def test_getsize_existing(self, tmp_path):
        p = tmp_path / "f.txt"
        p.write_bytes(b"hello world")
        assert getsize(str(p)) == len("hello world")

    def test_getsize_missing(self, tmp_path):
        assert getsize(str(tmp_path / "nope.txt")) == 0


class TestParse:
    def test_no_pattern_returns_string(self):
        assert parse("hello") == "hello"

    def test_matching_path(self):
        result = parse(
            "sub_001/ses_pre/data.vhdr",
            "sub_{id}/ses_{session}/data.vhdr",
        )
        assert result == {"id": 1, "session": "pre"}

    def test_non_matching_returns_empty_dict(self):
        result = parse("nope", "sub_{id}/data.vhdr")
        assert result == {}

    def test_wildcard(self):
        result = parse("/foo/bar/sub_42/extra.txt", "*/sub_{id}/extra.txt")
        assert result == {"id": 42}

    def test_non_numeric_id_stays_string(self):
        assert parse("sub_abc/x.txt", "sub_{id}/x.txt") == {"id": "abc"}

    def test_negative_int(self):
        assert parse("sub_-7/x.txt", "sub_{id}/x.txt") == {"id": -7}


class TestEnvironmentDetect:
    def test_python_env(self):
        # In a plain pytest run, no IPython kernel → detect_environment
        # should return "python".
        assert detect_environment() == "python"

    def test_notebook_path_explicit_env_var(self, tmp_path, monkeypatch):
        nb = tmp_path / "demo.ipynb"
        nb.write_text("{}")
        monkeypatch.setenv("SCITEX_NOTEBOOK_PATH", str(nb))
        name, dir_ = get_notebook_info_simple()
        assert name == "demo.ipynb"
        assert dir_ == str(tmp_path)

    def test_notebook_path_argv_fallback(self, tmp_path, monkeypatch):
        nb = tmp_path / "via_argv.ipynb"
        nb.write_text("{}")
        monkeypatch.delenv("SCITEX_NOTEBOOK_PATH", raising=False)
        monkeypatch.setattr(sys, "argv", ["jupyter", str(nb)])
        name, dir_ = get_notebook_info_simple()
        assert name == "via_argv.ipynb"
        assert dir_ == str(tmp_path)

    def test_notebook_path_none_when_no_signal(self, monkeypatch):
        monkeypatch.delenv("SCITEX_NOTEBOOK_PATH", raising=False)
        monkeypatch.setattr(sys, "argv", ["pytest"])
        # No IPython kernel running → both layers fail → (None, None).
        assert get_notebook_info_simple() == (None, None)

    def test_notebook_path_env_var_missing_file(self, tmp_path, monkeypatch):
        # Env var points at a non-existent path → fall through.
        monkeypatch.setenv("SCITEX_NOTEBOOK_PATH", str(tmp_path / "missing.ipynb"))
        monkeypatch.setattr(sys, "argv", ["pytest"])
        assert get_notebook_info_simple() == (None, None)
