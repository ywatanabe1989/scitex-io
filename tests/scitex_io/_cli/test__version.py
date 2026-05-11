"""Tests for scitex_io._cli._version (deprecated `version` subcommand)."""

import pytest
from click.testing import CliRunner

from scitex_io._cli._main import main
from scitex_io._cli._version import version as version_cmd


@pytest.fixture
def runner():
    return CliRunner()


class TestVersionDeprecated:
    def test_invokes_to_exit_2_with_message(self, runner):
        res = runner.invoke(version_cmd, [])
        assert res.exit_code == 2
        assert "--version" in res.output

    def test_through_main_alias(self, runner):
        res = runner.invoke(main, ["version"])
        assert res.exit_code == 2
        assert "--version" in res.output

    def test_ignores_unknown_options(self, runner):
        # context_settings ignore_unknown_options=True
        res = runner.invoke(version_cmd, ["--bogus"])
        assert res.exit_code == 2
