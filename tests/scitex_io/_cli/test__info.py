"""Tests for scitex_io._cli._info: show-info and deprecated info."""

import json

import pytest
from click.testing import CliRunner

from scitex_io._cli._info import info_deprecated, show_info


@pytest.fixture
def runner():
    return CliRunner()


class TestShowInfo:
    def test_default(self, runner):
        res = runner.invoke(show_info, [])
        assert res.exit_code == 0, res.output
        assert "Format Registry" in res.output
        assert "Save:" in res.output
        assert "Load:" in res.output

    def test_help(self, runner):
        res = runner.invoke(show_info, ["--help"])
        assert res.exit_code == 0
        assert "Usage:" in res.output
        assert "registered I/O formats" in res.output

    def test_verbose_v(self, runner):
        res = runner.invoke(show_info, ["-v"])
        assert res.exit_code == 0
        # -v prints built-in formats list
        assert "Built-in:" in res.output

    def test_verbose_vv(self, runner):
        res = runner.invoke(show_info, ["-vv"])
        assert res.exit_code == 0
        assert "Built-in:" in res.output

    def test_json(self, runner):
        res = runner.invoke(show_info, ["--json"])
        assert res.exit_code == 0
        payload = json.loads(res.output)
        assert "save" in payload and "load" in payload
        assert "builtin" in payload["save"]
        assert isinstance(payload["save"]["builtin"], list)


class TestInfoDeprecated:
    def test_exit_2_with_message(self, runner):
        res = runner.invoke(info_deprecated, [])
        assert res.exit_code == 2
        assert "show-info" in res.output

    def test_ignores_unknown_options(self, runner):
        res = runner.invoke(info_deprecated, ["--bogus", "arg"])
        assert res.exit_code == 2
