"""Tests for scitex_io._cli._skills: skills list/get/install."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from scitex_io._cli._skills import (
    _list_skill_files,
    _skills_root,
    skills_group,
)


@pytest.fixture
def runner():
    return CliRunner()


class TestHelpers:
    def test_skills_root_exists(self):
        root = _skills_root()
        assert isinstance(root, Path)
        # Should exist for this package
        assert root.is_dir(), f"missing bundled skills at {root}"

    def test_list_skill_files_nonempty(self):
        files = _list_skill_files(_skills_root())
        assert files, "expected at least one bundled skill .md"
        # Excludes SKILL.md
        assert all(p.name != "SKILL.md" for p in files)

    def test_list_skill_files_missing_dir(self, tmp_path):
        assert _list_skill_files(tmp_path / "does-not-exist") == []


class TestSkillsGroup:
    def test_no_subcommand_prints_help(self, runner):
        res = runner.invoke(skills_group, [])
        assert res.exit_code == 0
        assert "Usage:" in res.output

    def test_help(self, runner):
        res = runner.invoke(skills_group, ["--help"])
        assert res.exit_code == 0
        assert "skills" in res.output.lower()


class TestSkillsList:
    def test_default(self, runner):
        res = runner.invoke(skills_group, ["list"])
        assert res.exit_code == 0, res.output
        # Has at least one expected bundled skill stem
        assert "installation" in res.output or "quick-start" in res.output

    def test_json(self, runner):
        res = runner.invoke(skills_group, ["list", "--json"])
        assert res.exit_code == 0, res.output
        payload = json.loads(res.output)
        assert isinstance(payload, list)
        assert payload, "expected non-empty skill list"
        assert "name" in payload[0]
        assert "path" in payload[0]


class TestSkillsGet:
    def test_get_existing_pretty(self, runner):
        # First bundled file's stem
        files = _list_skill_files(_skills_root())
        stem = files[0].stem
        res = runner.invoke(skills_group, ["get", stem])
        assert res.exit_code == 0, res.output
        assert res.output.strip()  # has content

    def test_get_existing_with_md_suffix(self, runner):
        files = _list_skill_files(_skills_root())
        stem = files[0].stem
        res = runner.invoke(skills_group, ["get", stem + ".md"])
        assert res.exit_code == 0, res.output

    def test_get_json(self, runner):
        files = _list_skill_files(_skills_root())
        stem = files[0].stem
        res = runner.invoke(skills_group, ["get", stem, "--json"])
        assert res.exit_code == 0
        payload = json.loads(res.output)
        assert payload["name"] == stem
        assert payload["content"]

    def test_get_missing_skill(self, runner):
        res = runner.invoke(skills_group, ["get", "nonexistent-skill-xyz"])
        assert res.exit_code != 0
        assert "not found" in res.output


class TestSkillsInstall:
    def test_dry_run_default(self, runner, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        res = runner.invoke(skills_group, ["install", "--dry-run"])
        assert res.exit_code == 0, res.output
        assert "would symlink" in res.output

    def test_dry_run_no_link(self, runner, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        res = runner.invoke(skills_group, ["install", "--dry-run", "--no-link"])
        assert res.exit_code == 0
        assert "would copy" in res.output

    def test_dry_run_claude_symlink(self, runner, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        res = runner.invoke(skills_group, ["install", "--dry-run", "--claude-symlink"])
        assert res.exit_code == 0
        assert ".claude" in res.output

    def test_install_symlink(self, runner, tmp_path):
        dest = tmp_path / "skills_dest"
        res = runner.invoke(skills_group, ["install", "--dest", str(dest)])
        assert res.exit_code == 0, res.output
        target = dest / "scitex-io"
        assert target.is_symlink()
        assert target.resolve() == _skills_root().resolve()
        assert "linked" in res.output

    def test_install_copy(self, runner, tmp_path):
        dest = tmp_path / "skills_dest"
        res = runner.invoke(skills_group, ["install", "--dest", str(dest), "--no-link"])
        assert res.exit_code == 0, res.output
        target = dest / "scitex-io"
        assert target.is_dir()
        assert not target.is_symlink()
        # At least one .md present
        assert any(target.rglob("*.md"))
        assert "copied" in res.output

    def test_install_replaces_existing_symlink(self, runner, tmp_path):
        dest = tmp_path / "skills_dest"
        # First install
        runner.invoke(skills_group, ["install", "--dest", str(dest)])
        # Re-run — should unlink + recreate
        res = runner.invoke(skills_group, ["install", "--dest", str(dest)])
        assert res.exit_code == 0, res.output
        assert (dest / "scitex-io").is_symlink()

    def test_install_replaces_existing_dir(self, runner, tmp_path):
        dest = tmp_path / "skills_dest"
        # Pre-create as plain directory
        (dest / "scitex-io").mkdir(parents=True)
        (dest / "scitex-io" / "stale.md").write_text("stale")
        res = runner.invoke(skills_group, ["install", "--dest", str(dest), "--no-link"])
        assert res.exit_code == 0, res.output
        # stale should be gone
        assert not (dest / "scitex-io" / "stale.md").exists()

    def test_install_replaces_existing_file(self, runner, tmp_path):
        dest = tmp_path / "skills_dest"
        dest.mkdir()
        target = dest / "scitex-io"
        target.write_text("not-a-dir")
        res = runner.invoke(skills_group, ["install", "--dest", str(dest)])
        assert res.exit_code == 0, res.output
        assert target.is_symlink()

    def test_install_claude_symlink_creates_link(self, runner, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        dest = tmp_path / "skills_dest"
        res = runner.invoke(
            skills_group,
            ["install", "--dest", str(dest), "--claude-symlink"],
        )
        assert res.exit_code == 0, res.output
        claude_link = tmp_path / ".claude" / "skills" / "scitex"
        assert claude_link.is_symlink()

    def test_install_claude_symlink_existing_nonlink_warns(
        self, runner, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("HOME", str(tmp_path))
        claude_link = tmp_path / ".claude" / "skills" / "scitex"
        claude_link.parent.mkdir(parents=True)
        claude_link.mkdir()  # pre-existing dir, not symlink
        dest = tmp_path / "skills_dest"
        res = runner.invoke(
            skills_group,
            ["install", "--dest", str(dest), "--claude-symlink"],
        )
        assert res.exit_code == 0
        assert "warning" in res.output.lower()
        assert not claude_link.is_symlink()
