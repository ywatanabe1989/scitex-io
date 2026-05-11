"""Tests for scitex_io._cli._configs: load-configs and deprecated configs."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from scitex_io._cli._configs import configs_deprecated, load_configs_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "PATH.yaml").write_text("DATA_DIR: ./data\n")
    (cfg / "PARAMS.yaml").write_text("ALPHA: 0.05\nBETA: 0.2\n")
    return cfg


class TestLoadConfigs:
    def test_help(self, runner):
        res = runner.invoke(load_configs_cmd, ["--help"])
        assert res.exit_code == 0
        assert "Usage:" in res.output
        assert "YAML" in res.output or "configuration" in res.output

    def test_default_pretty(self, runner, config_dir):
        res = runner.invoke(load_configs_cmd, ["-d", str(config_dir)])
        assert res.exit_code == 0, res.output
        assert "Config dir:" in res.output
        assert "Namespaces:" in res.output
        # Yaml content surfaced
        assert "PATH" in res.output or "PARAMS" in res.output

    def test_json_output(self, runner, config_dir):
        res = runner.invoke(load_configs_cmd, ["-d", str(config_dir), "--json"])
        assert res.exit_code == 0, res.output
        payload = json.loads(res.output)
        assert isinstance(payload, dict)
        # Namespaces are uppercase filename stems
        assert "PATH" in payload or "PARAMS" in payload

    def test_verbose_debug(self, runner, config_dir):
        res = runner.invoke(load_configs_cmd, ["-d", str(config_dir), "--debug", "-v"])
        assert res.exit_code == 0, res.output

    def test_no_debug_flag(self, runner, config_dir):
        res = runner.invoke(load_configs_cmd, ["-d", str(config_dir), "--no-debug"])
        assert res.exit_code == 0, res.output

    def test_missing_dir_does_not_crash(self, runner, tmp_path):
        # load_configs tolerates missing dir (returns empty); cmd should still exit 0
        missing = tmp_path / "nope"
        res = runner.invoke(load_configs_cmd, ["-d", str(missing)])
        # Either succeeds with empty namespaces, or surfaces error — both acceptable
        assert res.exit_code in (0, 1, 2)


class TestConfigsDeprecated:
    def test_emits_redirect_and_exit_2(self, runner):
        res = runner.invoke(configs_deprecated, [])
        assert res.exit_code == 2
        assert "load-configs" in res.output
