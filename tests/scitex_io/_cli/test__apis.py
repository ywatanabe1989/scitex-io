"""Tests for scitex_io._cli._apis: list-python-apis."""

import json

import pytest
from click.testing import CliRunner

from scitex_io._cli._apis import (
    _format_signature,
    _get_apis,
    list_python_apis,
)


@pytest.fixture
def runner():
    return CliRunner()


class TestFormatSignature:
    def test_function_with_annotated_default(self):
        def f(x: int = 1, y: str = "a"):
            pass

        out = _format_signature(f)
        assert "x" in out and "y" in out
        assert "int" in out
        assert "str" in out

    def test_function_no_annotations(self):
        def f(a, b=2):
            pass

        out = _format_signature(f)
        assert "a" in out and "b" in out

    def test_function_default_is_truncated(self):
        def f(x="abcdefghijklmnopqrstuvwxyz1234567890"):
            pass

        out = _format_signature(f)
        assert "..." in out

    def test_unsignable_returns_empty(self):
        # builtins like len → may raise; ensure no exception
        out = _format_signature(len)
        assert isinstance(out, str)


class TestGetApis:
    def test_returns_list_of_tuples(self):
        import scitex_io

        results = _get_apis(scitex_io, "scitex_io", max_depth=1)
        assert isinstance(results, list)
        # Each entry: (kind, name, sig, doc)
        for entry in results:
            assert len(entry) == 4
            assert entry[0] in ("F", "C", "M", "V")

    def test_recursion_visit_guard(self):
        import scitex_io

        visited = set()
        a = _get_apis(scitex_io, "scitex_io", max_depth=2, _visited=visited)
        # second call short-circuits when same module is in visited
        b = _get_apis(scitex_io, "scitex_io", max_depth=2, _visited=visited)
        assert b == []
        assert isinstance(a, list)


class TestListPythonApis:
    def test_help(self, runner):
        res = runner.invoke(list_python_apis, ["--help"])
        assert res.exit_code == 0
        assert "Usage:" in res.output

    def test_default(self, runner):
        res = runner.invoke(list_python_apis, [])
        assert res.exit_code == 0, res.output
        assert res.output.strip()  # non-empty

    def test_verbose_v(self, runner):
        res = runner.invoke(list_python_apis, ["-v"])
        assert res.exit_code == 0

    def test_verbose_vv(self, runner):
        res = runner.invoke(list_python_apis, ["-vv"])
        assert res.exit_code == 0

    def test_verbose_vvv(self, runner):
        res = runner.invoke(list_python_apis, ["-vvv"])
        assert res.exit_code == 0

    def test_json(self, runner):
        res = runner.invoke(list_python_apis, ["--json"])
        assert res.exit_code == 0, res.output
        payload = json.loads(res.output)
        assert payload["module"] == "scitex_io"
        assert isinstance(payload["apis"], list)
