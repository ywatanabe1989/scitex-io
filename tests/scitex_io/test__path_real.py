"""Tests for scitex_io._path helpers."""


from __future__ import annotations
import os
from pathlib import Path

import pytest

from scitex_io._path import (
    find,
    find_latest,
    find_the_git_root_dir,
    split_fpath,
    touch,
)


# -----------------------------
# split_fpath
# -----------------------------
def test_split_fpath_basic():
    d, n, e = split_fpath("/a/b/c/file.txt")
    assert d == "/a/b/c/"
    assert n == "file"
    assert e == ".txt"


def test_split_fpath_no_extension():
    d, n, e = split_fpath("/a/file")
    assert d == "/a/"
    assert n == "file"
    assert e == ""


def test_split_fpath_relative():
    d, n, e = split_fpath("rel/dir/x.mat")
    assert d == "rel/dir/"
    assert n == "x"
    assert e == ".mat"


# -----------------------------
# touch
# -----------------------------
def test_touch_creates_file(tmp_path):
    p = tmp_path / "new.txt"
    assert not p.exists()
    touch(str(p))
    assert p.exists()


def test_touch_updates_mtime(tmp_path):
    p = tmp_path / "exist.txt"
    p.write_text("hi")
    old = p.stat().st_mtime
    # Force a different mtime by setting it backwards.
    os.utime(str(p), (old - 100, old - 100))
    touch(str(p))
    assert p.stat().st_mtime > old - 100


# -----------------------------
# find
# -----------------------------
def test_find_files_by_pattern(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "b.log").write_text("y")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.txt").write_text("z")
    out = find(str(tmp_path), type="f", exp="*.txt")
    names = sorted(os.path.basename(p) for p in out)
    assert names == ["a.txt", "c.txt"]


def test_find_directories(tmp_path):
    (tmp_path / "d1").mkdir()
    (tmp_path / "d2").mkdir()
    (tmp_path / "f.txt").write_text("x")
    out = find(str(tmp_path), type="d", exp="*")
    names = sorted(os.path.basename(p) for p in out)
    assert "d1" in names and "d2" in names
    # f.txt is a file, should not be in dirs output
    assert "f.txt" not in names


def test_find_all_types(tmp_path):
    (tmp_path / "f.txt").write_text("x")
    (tmp_path / "d").mkdir()
    out = find(str(tmp_path), type=None, exp="*")
    names = sorted(os.path.basename(p) for p in out)
    assert "f.txt" in names and "d" in names


def test_find_multiple_patterns(tmp_path):
    (tmp_path / "a.txt").write_text("1")
    (tmp_path / "b.md").write_text("2")
    (tmp_path / "c.py").write_text("3")
    out = find(str(tmp_path), type="f", exp=["*.txt", "*.md"])
    names = sorted(os.path.basename(p) for p in out)
    assert names == ["a.txt", "b.md"]


def test_find_no_matches(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    out = find(str(tmp_path), type="f", exp="*.xyz")
    assert out == []


# -----------------------------
# find_latest
# -----------------------------
def test_find_latest_picks_highest_version(tmp_path):
    for v in [1, 2, 5, 3]:
        (tmp_path / f"data_v{v}.txt").write_text("x")
    latest = find_latest(str(tmp_path), "data", ".txt")
    assert latest is not None
    assert latest.endswith("data_v5.txt")


def test_find_latest_returns_none_when_missing(tmp_path):
    assert find_latest(str(tmp_path), "absent", ".txt") is None


def test_find_latest_with_custom_prefix(tmp_path):
    (tmp_path / "file-r2.bin").write_text("x")
    (tmp_path / "file-r10.bin").write_text("y")
    latest = find_latest(str(tmp_path), "file", ".bin", version_prefix="-r")
    assert latest.endswith("file-r10.bin")


# -----------------------------
# find_the_git_root_dir
# -----------------------------
def _git_available():
    try:
        import git  # noqa: F401

        return True
    except ImportError:
        return False


def test_find_the_git_root_dir_returns_a_path(tmp_path, monkeypatch):
    """In this repo the call should succeed; assert a string path is returned."""
    if not _git_available():
        # Function imports `git` lazily — raises ModuleNotFoundError when missing.
        with pytest.raises(ModuleNotFoundError):
            find_the_git_root_dir()
        return
    monkeypatch.chdir(Path(__file__).parent)
    root = find_the_git_root_dir()
    assert root is not None
    assert os.path.isdir(root)


def test_find_the_git_root_dir_raises_outside_repo(tmp_path, monkeypatch):
    if not _git_available():
        # Same: import failure is the observable error.
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ModuleNotFoundError):
            find_the_git_root_dir()
        return
    import git

    monkeypatch.chdir(tmp_path)
    with pytest.raises(git.exc.InvalidGitRepositoryError):
        find_the_git_root_dir()
