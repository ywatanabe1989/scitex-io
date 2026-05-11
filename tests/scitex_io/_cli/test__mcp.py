"""Tests for scitex_io._cli._mcp: mcp group + start/doctor/install/list-tools."""

import json

import pytest
from click.testing import CliRunner

from scitex_io._cli._mcp import (
    doctor,
    install,
    installation_deprecated,
    list_tools,
    mcp,
    show_installation_deprecated,
    start_server,
)


@pytest.fixture
def runner():
    return CliRunner()


class TestMcpGroup:
    def test_no_subcommand_prints_help(self, runner):
        res = runner.invoke(mcp, [])
        assert res.exit_code == 0
        assert "Usage:" in res.output

    def test_help(self, runner):
        res = runner.invoke(mcp, ["--help"])
        assert res.exit_code == 0
        assert "MCP" in res.output

    def test_help_recursive(self, runner):
        res = runner.invoke(mcp, ["--help-recursive"])
        assert res.exit_code == 0
        # contains subcommand headers
        out = res.output
        assert "mcp" in out
        assert "start" in out
        assert "doctor" in out


class TestStartServer:
    def test_help(self, runner):
        res = runner.invoke(start_server, ["--help"])
        assert res.exit_code == 0
        assert "host" in res.output.lower()
        assert "port" in res.output.lower()

    def test_dry_run(self, runner):
        res = runner.invoke(start_server, ["--dry-run"])
        assert res.exit_code == 0
        assert "DRY RUN" in res.output
        assert "127.0.0.1" in res.output
        assert "8100" in res.output

    def test_dry_run_custom_host_port(self, runner):
        res = runner.invoke(
            start_server, ["--dry-run", "--host", "0.0.0.0", "--port", "9100"]
        )
        assert res.exit_code == 0
        assert "0.0.0.0" in res.output
        assert "9100" in res.output


class TestDoctor:
    def test_runs(self, runner):
        res = runner.invoke(doctor, [])
        # Exit code can be 0 even if fastmcp missing — checks just report
        assert res.exit_code == 0
        assert "MCP Doctor" in res.output
        assert "scitex-io" in res.output

    def test_help(self, runner):
        res = runner.invoke(doctor, ["--help"])
        assert res.exit_code == 0


class TestInstall:
    def test_default_pretty(self, runner):
        res = runner.invoke(install, [])
        assert res.exit_code == 0
        assert "MCP Installation" in res.output
        assert "pip install scitex-io[mcp]" in res.output
        assert "scitex-io mcp start" in res.output
        assert "scitex-io mcp doctor" in res.output

    def test_json(self, runner):
        res = runner.invoke(install, ["--json"])
        assert res.exit_code == 0
        payload = json.loads(res.output)
        assert payload["install_command"] == "pip install scitex-io[mcp]"
        assert "mcpServers" in payload["config"]
        assert "scitex-io" in payload["config"]["mcpServers"]

    def test_dry_run_and_yes_flags_accepted(self, runner):
        res = runner.invoke(install, ["--dry-run", "-y"])
        assert res.exit_code == 0

    def test_help(self, runner):
        res = runner.invoke(install, ["--help"])
        assert res.exit_code == 0


class TestInstallationDeprecated:
    def test_emits_error(self, runner):
        res = runner.invoke(installation_deprecated, [])
        assert res.exit_code == 2
        assert "mcp install" in res.output

    def test_show_installation_deprecated(self, runner):
        res = runner.invoke(show_installation_deprecated, [])
        assert res.exit_code == 2
        assert "mcp install" in res.output


class TestListTools:
    def test_help(self, runner):
        res = runner.invoke(list_tools, ["--help"])
        assert res.exit_code == 0

    def _maybe_skip_if_mcp_missing(self, res):
        # If fastmcp missing, ClickException is raised; surface gracefully
        if res.exit_code != 0 and "MCP not available" in res.output:
            pytest.skip("MCP runtime not installed in this env")

    def test_default(self, runner):
        res = runner.invoke(list_tools, [])
        self._maybe_skip_if_mcp_missing(res)
        assert res.exit_code == 0, res.output
        # Either "No MCP tools" or "MCP Tools (N)" banner
        assert "MCP Tools" in res.output or "No MCP tools" in res.output

    def test_verbose_v(self, runner):
        res = runner.invoke(list_tools, ["-v"])
        self._maybe_skip_if_mcp_missing(res)
        assert res.exit_code == 0

    def test_verbose_vv(self, runner):
        res = runner.invoke(list_tools, ["-vv"])
        self._maybe_skip_if_mcp_missing(res)
        assert res.exit_code == 0

    def test_json(self, runner):
        res = runner.invoke(list_tools, ["--json"])
        self._maybe_skip_if_mcp_missing(res)
        assert res.exit_code == 0
        payload = json.loads(res.output)
        assert "total" in payload
        assert "tools" in payload
        assert isinstance(payload["tools"], list)
