"""Tests for scitex_io._cli._main: root group, deprecations, recursive help."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from scitex_io._cli._main import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestMainHelp:
    def test_help_flag_short(self, runner):
        res = runner.invoke(main, ["-h"])
        assert res.exit_code == 0
        assert "Usage:" in res.output
        assert "scitex-io" in res.output

    def test_help_flag_long(self, runner):
        res = runner.invoke(main, ["--help"])
        assert res.exit_code == 0
        # categorized section headers — at least one category must appear
        assert any(
            cat in res.output for cat in ("Core I/O", "Integration", "Utility", "Other")
        )

    def test_no_subcommand_prints_help(self, runner):
        res = runner.invoke(main, [])
        assert res.exit_code == 0
        assert "Usage:" in res.output

    def test_version_long(self, runner):
        res = runner.invoke(main, ["--version"])
        assert res.exit_code == 0
        # importlib version prefix appears
        assert "main" in res.output or "version" in res.output.lower()

    def test_version_short(self, runner):
        res = runner.invoke(main, ["-V"])
        assert res.exit_code == 0

    def test_help_recursive(self, runner):
        res = runner.invoke(main, ["--help-recursive"])
        assert res.exit_code == 0
        # Should iterate visible subcommands
        assert "scitex-io" in res.output
        assert "show-info" in res.output or "load-configs" in res.output

    def test_json_flag_propagates(self, runner):
        # --json on root just sets ctx.obj["as_json"], should not crash with no subcommand
        res = runner.invoke(main, ["--json"])
        assert res.exit_code == 0


class TestMainCategorization:
    def test_help_includes_known_commands(self, runner):
        res = runner.invoke(main, ["--help"])
        out = res.output
        for cmd in ("show-info", "load-configs", "list-python-apis", "mcp"):
            assert cmd in out, f"{cmd} missing from --help"

    def test_unknown_command_errors(self, runner):
        res = runner.invoke(main, ["this-command-does-not-exist"])
        assert res.exit_code != 0
        # Click prints "No such command"
        assert "No such command" in res.output or "Error" in res.output


class TestDeprecatedShellCompletion:
    def test_shell_completion_deprecated_emits_error(self, runner):
        res = runner.invoke(main, ["shell-completion"])
        assert res.exit_code == 2
        assert "install-shell-completion" in res.output or "split into" in res.output
