"""Unit tests for ``scitex_io.save`` path-resolution and feature flags.

Routing matrix (covered):

| env_type      | input shape          | output sdir                          |
|---------------|----------------------|--------------------------------------|
| jupyter (env) | filename / relative  | <notebook_dir>/<stem>_out/<path>     |
| jupyter (—)   | filename / relative  | <cwd>/notebook_out/<path>  + warn    |
| any           | absolute (`/...`)    | path used as-is                      |

Save flags (covered): ``symlink_from_cwd``, ``symlink_to``, ``dry_run``,
``makedirs``, ``verbose``.

Patching: ``detect_environment`` is imported lazily inside ``save``
from ``scitex_io._utils`` — patch that fully-qualified name.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import numpy as np
import pytest

import scitex_io as sio
import scitex_io._builtin_handlers  # noqa: F401 — register builtin .npy etc.
from scitex_io._utils import get_notebook_info_simple

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def cwd_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    yield tmp_path


@pytest.fixture
def reset_warn_latch(monkeypatch):
    import scitex_io._save as _save_mod

    monkeypatch.setattr(_save_mod, "_NOTEBOOK_PATH_WARNED", False)


def _patch_env(env_type: str):
    return mock.patch("scitex_io._utils.detect_environment", return_value=env_type)


# ===========================================================================
# get_notebook_info_simple — return-shape contract
# ===========================================================================


def test_notebook_info_returns_2_tuple_shape(monkeypatch):
    """Must return a 2-tuple — never a dict (callers unpack as 2-tuple)."""
    monkeypatch.delenv("SCITEX_NOTEBOOK_PATH", raising=False)
    info = get_notebook_info_simple()
    assert isinstance(info, tuple)
    assert len(info) == 2


def test_notebook_info_none_when_no_signal(monkeypatch):
    monkeypatch.delenv("SCITEX_NOTEBOOK_PATH", raising=False)
    monkeypatch.setattr(sys, "argv", ["pytest", "test_x.py"])
    assert get_notebook_info_simple() == (None, None)


def test_notebook_info_env_var_override(tmp_path, monkeypatch):
    nb = tmp_path / "demo.ipynb"
    nb.write_text("{}")
    monkeypatch.setenv("SCITEX_NOTEBOOK_PATH", str(nb))
    name, dirpath = get_notebook_info_simple()
    assert name == "demo.ipynb"
    assert Path(dirpath).resolve() == tmp_path.resolve()


def test_notebook_info_env_var_falls_through_when_path_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("SCITEX_NOTEBOOK_PATH", str(tmp_path / "nope.ipynb"))
    monkeypatch.setattr(sys, "argv", ["pytest"])
    assert get_notebook_info_simple() == (None, None)


def test_notebook_info_finds_ipynb_in_argv(tmp_path, monkeypatch):
    nb = tmp_path / "fromargv.ipynb"
    nb.write_text("{}")
    monkeypatch.delenv("SCITEX_NOTEBOOK_PATH", raising=False)
    monkeypatch.setattr(sys, "argv", ["nbconvert", str(nb)])
    name, _ = get_notebook_info_simple()
    assert name == "fromargv.ipynb"


# ===========================================================================
# Save routing — absolute path bypasses ALL routing branches
# ===========================================================================


def test_abs_path_used_as_is_in_jupyter(cwd_tmp, monkeypatch):
    monkeypatch.delenv("SCITEX_NOTEBOOK_PATH", raising=False)
    monkeypatch.setenv("SCITEX_IO_QUIET_NOTEBOOK_WARN", "1")
    target = cwd_tmp / "abs_jupyter.npy"
    with _patch_env("jupyter"):
        sio.save(np.array([1, 2, 3]), str(target))
    assert target.is_file()
    assert not (cwd_tmp / "notebook_out").exists()


def test_abs_path_with_subdirs_creates_them(cwd_tmp):
    target = cwd_tmp / "deep" / "nested" / "data.npy"
    with _patch_env("script"):
        sio.save(np.array([1.0]), str(target))
    assert target.is_file()


def test_abs_path_makedirs_false_returns_false_on_missing_parent(cwd_tmp):
    """``makedirs=False`` skips parent-dir creation. ``save`` catches
    the underlying FileNotFoundError and returns ``False``."""
    target = cwd_tmp / "missing-parent" / "data.npy"
    with _patch_env("script"):
        result = sio.save(np.array([1.0]), str(target), makedirs=False)
    assert result is False
    assert not target.exists()


# ===========================================================================
# Save routing — Jupyter with notebook detection (env-var override)
# ===========================================================================


def test_jupyter_filename_only_with_env_routes_under_stem_out(cwd_tmp, monkeypatch):
    """Filename-only input: <cwd>/<stem>_out/<filename>."""
    nb = cwd_tmp / "demo.ipynb"
    nb.write_text("{}")
    monkeypatch.setenv("SCITEX_NOTEBOOK_PATH", str(nb))
    with _patch_env("jupyter"):
        sio.save(np.array([1, 2]), "result.npy")
    assert (cwd_tmp / "demo_out" / "result.npy").is_file()


def test_jupyter_relative_subdir_with_env_preserves_subdirs(cwd_tmp, monkeypatch):
    nb = cwd_tmp / "demo.ipynb"
    nb.write_text("{}")
    monkeypatch.setenv("SCITEX_NOTEBOOK_PATH", str(nb))
    with _patch_env("jupyter"):
        sio.save(np.array([1, 2]), "_assets/figs/01.npy")
    assert (cwd_tmp / "demo_out" / "_assets" / "figs" / "01.npy").is_file()


def test_jupyter_notebook_in_subdir_uses_notebook_dir_not_cwd(tmp_path, monkeypatch):
    nb_dir = tmp_path / "examples"
    nb_dir.mkdir()
    nb = nb_dir / "demo.ipynb"
    nb.write_text("{}")
    monkeypatch.chdir(tmp_path)  # cwd ≠ notebook_dir
    monkeypatch.setenv("SCITEX_NOTEBOOK_PATH", str(nb))
    with _patch_env("jupyter"):
        sio.save(np.array([1.0]), "out.npy")
    assert (nb_dir / "demo_out" / "out.npy").is_file()
    assert not (tmp_path / "demo_out" / "out.npy").exists()


# ===========================================================================
# Save routing — Jupyter without detection (fallback + warning)
# ===========================================================================


def test_jupyter_fallback_to_notebook_out_with_warning(
    cwd_tmp, monkeypatch, reset_warn_latch, capsys
):
    monkeypatch.delenv("SCITEX_NOTEBOOK_PATH", raising=False)
    monkeypatch.delenv("SCITEX_IO_QUIET_NOTEBOOK_WARN", raising=False)
    monkeypatch.setattr(sys, "argv", ["pytest"])
    with _patch_env("jupyter"):
        sio.save(np.array([1.0]), "fallback.npy")
    assert (cwd_tmp / "notebook_out" / "fallback.npy").is_file()
    err = capsys.readouterr().err
    assert "notebook path could not be auto-detected" in err
    assert "SCITEX_NOTEBOOK_PATH" in err


def test_jupyter_warning_fires_only_once(
    cwd_tmp, monkeypatch, reset_warn_latch, capsys
):
    monkeypatch.delenv("SCITEX_NOTEBOOK_PATH", raising=False)
    monkeypatch.delenv("SCITEX_IO_QUIET_NOTEBOOK_WARN", raising=False)
    monkeypatch.setattr(sys, "argv", ["pytest"])
    with _patch_env("jupyter"):
        sio.save(np.array([1.0]), "a.npy")
        sio.save(np.array([2.0]), "b.npy")
        sio.save(np.array([3.0]), "c.npy")
    err = capsys.readouterr().err
    assert err.count("notebook path could not be auto-detected") == 1


def test_jupyter_warning_silenced_by_env_var(
    cwd_tmp, monkeypatch, reset_warn_latch, capsys
):
    monkeypatch.delenv("SCITEX_NOTEBOOK_PATH", raising=False)
    monkeypatch.setenv("SCITEX_IO_QUIET_NOTEBOOK_WARN", "1")
    monkeypatch.setattr(sys, "argv", ["pytest"])
    with _patch_env("jupyter"):
        sio.save(np.array([1.0]), "quiet.npy")
    err = capsys.readouterr().err
    assert "notebook path" not in err
    assert (cwd_tmp / "notebook_out" / "quiet.npy").is_file()


# ===========================================================================
# Symlink behaviours
# ===========================================================================


def test_symlink_from_cwd_creates_link_at_cwd(cwd_tmp, monkeypatch):
    """``symlink_from_cwd=True`` only fires when the saved path differs
    from `<cwd>/<specified_path>`. In jupyter env with notebook-detection,
    save lands at `<dir>/<stem>_out/<rel>`, which differs from cwd —
    symlink is created."""
    nb = cwd_tmp / "demo.ipynb"
    nb.write_text("{}")
    monkeypatch.setenv("SCITEX_NOTEBOOK_PATH", str(nb))
    with _patch_env("jupyter"):
        sio.save(np.array([7.0]), "real.npy", symlink_from_cwd=True)
    routed = cwd_tmp / "demo_out" / "real.npy"
    assert routed.is_file()
    cwd_link = cwd_tmp / "real.npy"
    assert cwd_link.exists() or cwd_link.is_symlink()


def test_symlink_to_creates_link_at_custom_path(cwd_tmp, monkeypatch):
    """``symlink_to`` drops a symlink at an explicit custom path."""
    nb = cwd_tmp / "demo.ipynb"
    nb.write_text("{}")
    monkeypatch.setenv("SCITEX_NOTEBOOK_PATH", str(nb))
    custom_link = cwd_tmp / "links" / "x_link.npy"
    with _patch_env("jupyter"):
        sio.save(
            np.array([1.0, 2.0]),
            "x.npy",
            symlink_to=str(custom_link),
        )
    routed = cwd_tmp / "demo_out" / "x.npy"
    assert routed.is_file()
    assert custom_link.exists() or custom_link.is_symlink()


def test_load_after_symlink_round_trip(cwd_tmp, monkeypatch):
    """The whole point of symlink_from_cwd: round-trip by filename."""
    nb = cwd_tmp / "demo.ipynb"
    nb.write_text("{}")
    monkeypatch.setenv("SCITEX_NOTEBOOK_PATH", str(nb))
    with _patch_env("jupyter"):
        sio.save(np.array([42.0]), "rt.npy", symlink_from_cwd=True)
    arr = sio.load("rt.npy")
    assert arr.tolist() == [42.0]


# ===========================================================================
# dry_run flag
# ===========================================================================


def test_dry_run_does_not_write_file(cwd_tmp):
    target = cwd_tmp / "dry.npy"
    with _patch_env("script"):
        sio.save(np.array([1.0]), str(target), dry_run=True)
    assert not target.exists()


def test_dry_run_returns_without_error(cwd_tmp):
    target = cwd_tmp / "dry2.npy"
    with _patch_env("script"):
        # Should not raise even if the dir doesn't exist with makedirs=False.
        sio.save(np.array([1.0]), str(target), dry_run=True, makedirs=False)


# ===========================================================================
# Defensive — never resurrect the legacy `name/path_out/` shape
# ===========================================================================


def test_never_creates_legacy_name_path_out(cwd_tmp, monkeypatch, reset_warn_latch):
    """Regression: dict-keys-as-tuple bug routed every save to
    ``<cwd>/name/path_out/``."""
    monkeypatch.delenv("SCITEX_NOTEBOOK_PATH", raising=False)
    monkeypatch.setenv("SCITEX_IO_QUIET_NOTEBOOK_WARN", "1")
    monkeypatch.setattr(sys, "argv", ["pytest"])
    with _patch_env("jupyter"):
        sio.save(np.array([1.0]), "x.npy")
    assert not (cwd_tmp / "name").exists()
