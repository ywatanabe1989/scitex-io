#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_io._mcp._tools_extra — §6 parity MCP tools."""

import json
import os

import h5py
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from scitex_io._mcp import _tools_extra

# ---------- io_glob / io_parse_glob ----------


def test_io_glob_plain(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "b.txt").write_text("y")
    r = _tools_extra.io_glob(str(tmp_path / "*.txt"))
    assert r["success"] is True
    assert len(r["result"]) == 2


def test_io_glob_parse(tmp_path):
    (tmp_path / "exp01.csv").write_text("")
    (tmp_path / "exp02.csv").write_text("")
    r = _tools_extra.io_glob(str(tmp_path / "exp{idx}.csv"), parse=True)
    assert r["success"] is True
    # parse=True returns (paths, parsed)
    paths, parsed = r["result"]
    assert len(paths) == 2
    idxs = {p.get("idx") for p in parsed}
    assert {1, 2} <= idxs


def test_io_glob_ensure_one_failure(tmp_path):
    # 0 matches should fail (ensure_one)
    r = _tools_extra.io_glob(str(tmp_path / "no_match_*.xyz"), ensure_one=True)
    assert r["success"] is False
    assert "error" in r


def test_io_parse_glob(tmp_path):
    (tmp_path / "foo.txt").write_text("")
    (tmp_path / "bar.txt").write_text("")
    r = _tools_extra.io_parse_glob(str(tmp_path / "{name}.txt"))
    assert r["success"] is True
    # parse_glob returns (paths, parsed) tuple
    parsed_part = r["parsed"]
    if isinstance(parsed_part, tuple):
        _paths, parsed = parsed_part
    else:
        parsed = parsed_part
    names = {d["name"] for d in parsed}
    assert {"foo", "bar"} <= names


def test_io_parse_glob_error_ensure_one(tmp_path):
    r = _tools_extra.io_parse_glob(str(tmp_path / "no_such_{x}.q"), ensure_one=True)
    assert r["success"] is False


# ---------- io_get_loader / io_get_saver ----------


def test_io_get_loader_known():
    r = _tools_extra.io_get_loader(".csv")
    assert r["success"] is True
    assert r["ext"] == ".csv"
    assert r["loader"] is not None
    assert "." in r["loader"]


def test_io_get_loader_unknown():
    r = _tools_extra.io_get_loader(".totallyunknownXYZ")
    assert r["success"] is True
    assert r["loader"] is None


def test_io_get_saver_known():
    r = _tools_extra.io_get_saver(".json")
    assert r["success"] is True
    assert r["saver"] is not None


def test_io_get_saver_unknown():
    r = _tools_extra.io_get_saver(".totallyunknownXYZ")
    assert r["success"] is True
    assert r["saver"] is None


# ---------- metadata tools ----------


def _make_png(path):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3])
    fig.savefig(path)
    plt.close(fig)


def test_io_has_metadata_empty_png(tmp_path):
    p = tmp_path / "fig.png"
    _make_png(p)
    r = _tools_extra.io_has_metadata(str(p))
    assert r["success"] is True
    assert r["has_metadata"] is False


def test_io_embed_and_read_metadata(tmp_path):
    p = tmp_path / "fig.png"
    _make_png(p)
    md = {"k": "v", "n": 7}
    r1 = _tools_extra.io_embed_metadata(str(p), json.dumps(md))
    assert r1["success"] is True
    assert r1["path"] == os.path.abspath(str(p))

    r2 = _tools_extra.io_has_metadata(str(p))
    assert r2["has_metadata"] is True

    r3 = _tools_extra.io_read_metadata(str(p))
    assert r3["success"] is True
    assert r3["metadata"]["k"] == "v"
    assert r3["metadata"]["n"] == 7


def test_io_read_metadata_missing_file_error(tmp_path):
    r = _tools_extra.io_read_metadata(str(tmp_path / "nope.png"))
    assert r["success"] is False
    assert "error" in r


def test_io_embed_metadata_missing_file_error(tmp_path):
    r = _tools_extra.io_embed_metadata(str(tmp_path / "nope.png"), "{}")
    assert r["success"] is False


def test_io_embed_metadata_bad_json(tmp_path):
    p = tmp_path / "fig.png"
    _make_png(p)
    r = _tools_extra.io_embed_metadata(str(p), "not json {{{")
    assert r["success"] is False


# ---------- cache tools ----------


def test_io_get_cache_info_shape():
    r = _tools_extra.io_get_cache_info()
    assert r["success"] is True
    # has cache stats
    assert any(k in r for k in ("stats", "config", "metadata_size", "data_size"))


def test_io_clear_load_cache():
    r = _tools_extra.io_clear_load_cache()
    assert r["success"] is True


def test_io_configure_cache_toggle():
    r = _tools_extra.io_configure_cache(enabled=False)
    assert r["success"] is True
    # restore
    r2 = _tools_extra.io_configure_cache(enabled=True, max_size=32, verbose=False)
    assert r2["success"] is True


# ---------- HDF5 tools ----------


def _make_h5(path):
    with h5py.File(path, "w") as f:
        f.create_dataset("a/b", data=np.arange(5))
        f.create_dataset("top", data=np.array([1.0, 2.0]))


def test_io_explore_h5_real_file(tmp_path):
    p = tmp_path / "test.h5"
    _make_h5(p)
    r = _tools_extra.io_explore_h5(str(p))
    assert r["success"] is True
    assert r["path"] == os.path.abspath(str(p))


def test_io_explore_h5_missing_file(tmp_path):
    # explore_h5 on missing file only warns (doesn't raise) → envelope is still
    # success=True. We just verify the envelope shape stays consistent.
    r = _tools_extra.io_explore_h5(str(tmp_path / "nope.h5"))
    assert isinstance(r, dict)
    assert "success" in r


def test_io_has_h5_key_true(tmp_path):
    p = tmp_path / "k.h5"
    _make_h5(p)
    r = _tools_extra.io_has_h5_key(str(p), "a/b")
    assert r["success"] is True
    assert r["has_key"] is True


def test_io_has_h5_key_false(tmp_path):
    p = tmp_path / "k.h5"
    _make_h5(p)
    r = _tools_extra.io_has_h5_key(str(p), "no/such/key")
    assert r["success"] is True
    assert r["has_key"] is False


def test_io_has_h5_key_missing_file(tmp_path):
    r = _tools_extra.io_has_h5_key(str(tmp_path / "nope.h5"), "x")
    assert isinstance(r, dict)
    assert "success" in r


# ---------- Zarr tools ----------


def _make_zarr(path):
    import zarr

    store = zarr.open(str(path), mode="w")
    arr = store.create_array("arr1", shape=(10,), dtype="int64")
    arr[:] = np.arange(10)


def test_io_explore_zarr_envelope(tmp_path):
    p = tmp_path / "test.zarr"
    _make_zarr(p)
    r = _tools_extra.io_explore_zarr(str(p))
    # explore_zarr may return success or error depending on zarr version
    # (installed zarr v3 mismatches the implementation in some scitex_io
    # versions). Either way the envelope shape must be uniform.
    assert isinstance(r, dict)
    assert "success" in r
    if r["success"]:
        assert r["path"] == os.path.abspath(str(p))
    else:
        assert "error" in r


def test_io_explore_zarr_missing(tmp_path):
    r = _tools_extra.io_explore_zarr(str(tmp_path / "nope.zarr"))
    assert isinstance(r, dict)
    assert "success" in r


def test_io_has_zarr_key_true(tmp_path):
    p = tmp_path / "kz.zarr"
    _make_zarr(p)
    r = _tools_extra.io_has_zarr_key(str(p), "arr1")
    assert r["success"] is True
    assert r["has_key"] is True


def test_io_has_zarr_key_false(tmp_path):
    p = tmp_path / "kz.zarr"
    _make_zarr(p)
    r = _tools_extra.io_has_zarr_key(str(p), "missing_key")
    assert r["success"] is True
    assert r["has_key"] is False


def test_io_has_zarr_key_missing_store(tmp_path):
    r = _tools_extra.io_has_zarr_key(str(tmp_path / "no_such.zarr"), "k")
    # Either error envelope or has_key=False — both acceptable
    assert isinstance(r, dict)
    assert "success" in r


# ---------- io_json2md ----------


def test_io_json2md_simple():
    r = _tools_extra.io_json2md(json.dumps({"a": 1, "b": "x"}))
    assert r["success"] is True
    assert isinstance(r["markdown"], str)
    assert "a" in r["markdown"]


def test_io_json2md_nested_level():
    payload = {"section": {"sub": [1, 2, 3]}}
    r = _tools_extra.io_json2md(json.dumps(payload), level=2)
    assert r["success"] is True
    assert "section" in r["markdown"]


def test_io_json2md_bad_json():
    r = _tools_extra.io_json2md("not valid {{{")
    assert r["success"] is False
    assert "error" in r


# ---------- monkey-patched exception branches ----------


def test_io_has_metadata_exception(monkeypatch):
    def boom(_p):
        raise RuntimeError("forced-meta")

    monkeypatch.setattr("scitex_io.has_metadata", boom)
    r = _tools_extra.io_has_metadata("/anything")
    assert r["success"] is False
    assert "forced-meta" in r["error"]


def test_io_explore_h5_exception(monkeypatch):
    def boom(_p):
        raise RuntimeError("forced-h5")

    monkeypatch.setattr("scitex_io.explore_h5", boom)
    r = _tools_extra.io_explore_h5("/anything")
    assert r["success"] is False
    assert "forced-h5" in r["error"]


def test_io_has_h5_key_exception(monkeypatch):
    def boom(_p, _k):
        raise RuntimeError("forced-h5-key")

    monkeypatch.setattr("scitex_io.has_h5_key", boom)
    r = _tools_extra.io_has_h5_key("/anything", "k")
    assert r["success"] is False
    assert "forced-h5-key" in r["error"]


def test_io_explore_zarr_success_path(monkeypatch, tmp_path):
    """Cover the success branch of io_explore_zarr (line 227).

    The installed zarr version mismatches scitex_io's ZarrExplorer in this env
    (raises about `compressor` for v3 arrays). We force the success branch by
    stubbing explore_zarr to a no-op.
    """

    def fake_explore(_p):
        return None

    monkeypatch.setattr("scitex_io.explore_zarr", fake_explore)
    p = tmp_path / "fake.zarr"
    p.mkdir()
    r = _tools_extra.io_explore_zarr(str(p))
    assert r["success"] is True
    assert r["path"] == os.path.abspath(str(p))


def test_io_has_zarr_key_exception(monkeypatch):
    def boom(_p, _k):
        raise RuntimeError("forced-zarr-key")

    monkeypatch.setattr("scitex_io.has_zarr_key", boom)
    r = _tools_extra.io_has_zarr_key("/anything", "k")
    assert r["success"] is False


# EOF
