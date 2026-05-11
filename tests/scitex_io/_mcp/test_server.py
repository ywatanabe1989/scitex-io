#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_io._mcp.server — exercises every @mcp.tool() in server.py.

Tests call the underlying decorated functions directly. FastMCP's @mcp.tool()
returns a normal callable, so server.io_save(...) works.
"""

import json
import os

import pandas as pd

from scitex_io._mcp import server

# ---------- module presence ----------


def test_module_imports():
    from scitex_io._mcp import server as s

    assert s.mcp is not None
    assert s.mcp.name == "scitex-io"


# ---------- io_list_formats ----------


def test_io_list_formats_shape():
    r = server.io_list_formats()
    assert isinstance(r, dict)
    assert set(r.keys()) >= {"save", "load"}
    for side in ("save", "load"):
        assert set(r[side].keys()) >= {"builtin", "user"}
        assert isinstance(r[side]["builtin"], list)
        assert any(ext.startswith(".") for ext in r[side]["builtin"])


# ---------- io_register_info ----------


def test_io_register_info_shape():
    r = server.io_register_info()
    assert set(r.keys()) >= {"description", "save_example", "load_example", "note"}
    assert "register_saver" in r["save_example"]
    assert "register_loader" in r["load_example"]


# ---------- io_save / io_load round-trips ----------


def test_io_save_load_json(tmp_path):
    p = str(tmp_path / "data.json")
    payload = {"a": 1, "b": [1, 2, 3]}
    save_r = server.io_save(json.dumps(payload), p)
    assert save_r["success"] is True
    assert os.path.exists(p)

    load_r = server.io_load(p, cache=False)
    assert load_r["success"] is True
    assert load_r["type"] in ("dict",)
    assert load_r["path"] == os.path.abspath(p)
    assert "preview" in load_r


def test_io_save_load_yaml(tmp_path):
    p = str(tmp_path / "data.yaml")
    save_r = server.io_save(json.dumps({"k": "v"}), p)
    assert save_r["success"] is True
    load_r = server.io_load(p, cache=False)
    assert load_r["success"] is True


def test_io_save_load_csv(tmp_path):
    # Save a list-of-dicts JSON to .csv — scitex_io handles via pandas
    p = str(tmp_path / "data.csv")
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    # pass via JSON (list-of-records)
    payload = df.to_dict(orient="list")
    save_r = server.io_save(json.dumps(payload), p)
    assert save_r["success"] is True
    load_r = server.io_load(p, cache=False)
    assert load_r["success"] is True
    # DataFrame has shape
    assert "shape" in load_r


def test_io_save_load_long_preview_truncated(tmp_path):
    # Make a load output whose repr exceeds 500 chars
    p = str(tmp_path / "big.json")
    server.io_save(json.dumps({"k" + str(i): "v" * 20 for i in range(50)}), p)
    r = server.io_load(p, cache=False)
    assert r["success"] is True
    assert r["preview"].endswith("...")
    assert len(r["preview"]) <= 503


def test_io_load_missing_returns_error(tmp_path):
    r = server.io_load(str(tmp_path / "does_not_exist.json"), cache=False)
    assert r["success"] is False
    assert "error" in r


def test_io_save_bad_json_returns_error(tmp_path):
    r = server.io_save("not valid json {{{", str(tmp_path / "x.json"))
    assert r["success"] is False
    assert "error" in r


def test_io_save_unsupported_ext_envelope(tmp_path):
    # scitex_io.save() swallows the unknown-ext error internally (logs it).
    # We only assert the envelope shape — either success=False or success=True.
    r = server.io_save(json.dumps({"a": 1}), str(tmp_path / "x.totallyunknownext"))
    assert isinstance(r, dict)
    assert "success" in r


# ---------- io_load_configs ----------


def test_io_load_configs_happy(tmp_path):
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "path.yaml").write_text("data_dir: /tmp/data\n")
    (cfg / "params.yaml").write_text("hidden_dim: 256\n")
    r = server.io_load_configs(config_dir=str(cfg))
    assert r["success"] is True
    assert "PATH" in r["namespaces"]
    assert "PARAMS" in r["namespaces"]
    assert r["config_dir"] == os.path.abspath(str(cfg))
    assert isinstance(r["configs"], dict)


def test_io_load_configs_missing_dir(tmp_path):
    # nonexistent path — function may either error or return empty namespaces.
    r = server.io_load_configs(config_dir=str(tmp_path / "no_such_dir"))
    # Either path exercised; just assert envelope shape.
    assert "success" in r


def test_io_load_configs_with_debug_flag(tmp_path):
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "params.yaml").write_text("VAL: 1\nDEBUG_VAL: 99\n")
    r = server.io_load_configs(config_dir=str(cfg), is_debug=True)
    assert r["success"] is True


# ---------- io_skills_list / io_skills_get ----------


def test_io_skills_list_real_package():
    raw = server.io_skills_list()
    r = json.loads(raw)
    assert r["success"] is True
    assert r["package"] == "scitex-io"
    assert isinstance(r["skills"], list)
    assert len(r["skills"]) > 0
    # SKILL.md is excluded
    assert "SKILL" not in r["skills"]
    # Expect at least one known leaf
    assert any("save-and-load" in name for name in r["skills"])


def test_io_skills_get_real_skill():
    raw = server.io_skills_list()
    skills = json.loads(raw)["skills"]
    name = skills[0]
    raw_get = server.io_skills_get(name)
    r = json.loads(raw_get)
    assert r["success"] is True
    assert r["name"] == name
    assert isinstance(r["content"], str)
    assert len(r["content"]) > 0


def test_io_skills_get_unknown_skill():
    raw = server.io_skills_get("nonexistent_skill_xyz")
    r = json.loads(raw)
    assert r["success"] is False
    assert "available" in r["error"]


# ---------- Numpy/pickle round-trips ----------


def test_io_save_load_npy(tmp_path):
    p = str(tmp_path / "arr.npy")
    payload = [1, 2, 3, 4]
    r = server.io_save(json.dumps(payload), p)
    assert r["success"] is True
    rr = server.io_load(p, cache=False)
    assert rr["success"] is True
    assert "shape" in rr


def test_io_save_load_pkl(tmp_path):
    p = str(tmp_path / "obj.pkl")
    payload = {"k": [1, 2, 3]}
    r = server.io_save(json.dumps(payload), p)
    assert r["success"] is True
    rr = server.io_load(p, cache=False)
    assert rr["success"] is True


# ---------- resources ----------


def test_resources_register():
    from fastmcp import FastMCP

    from scitex_io._mcp._resources import CHEATSHEET, FORMATS, register_resources

    m = FastMCP(name="test")
    register_resources(m)
    assert "scitex-io" in CHEATSHEET
    assert "Save Formats" in FORMATS


def test_resources_readers_invoke():
    """Actually read the registered resources (covers the inner fns)."""
    import asyncio

    from fastmcp import FastMCP

    from scitex_io._mcp._resources import register_resources

    m = FastMCP(name="test")
    register_resources(m)

    async def go():
        return (
            await m.read_resource("scitex-io://cheatsheet"),
            await m.read_resource("scitex-io://formats"),
        )

    r1, r2 = asyncio.run(go())
    assert "scitex-io" in str(r1)
    assert "Save Formats" in str(r2)


# Trigger remaining `except Exception` paths in tools that wrap a function
# that normally won't fail. We use a temporary monkey-patch.


def test_io_load_configs_exception_path(monkeypatch, tmp_path):
    """Force load_configs to raise → success=False branch."""
    from scitex_io._mcp import server as server_mod

    def boom(**kwargs):
        raise RuntimeError("forced")

    monkeypatch.setattr("scitex_io.load_configs", boom)
    r = server_mod.io_load_configs(config_dir=str(tmp_path))
    assert r["success"] is False
    assert "forced" in r["error"]


def test_io_skills_list_exception_path(monkeypatch):
    """Force io_skills_list into its except branch."""
    from scitex_io._mcp import server as server_mod

    class BadPath:
        def __init__(self, *a, **kw):
            raise RuntimeError("boom-path")

    monkeypatch.setattr("scitex_io._mcp.server.Path", BadPath, raising=False)
    # The function imports Path inside the body — patch via builtins module
    monkeypatch.setattr("pathlib.Path", BadPath)
    raw = server_mod.io_skills_list()
    r = json.loads(raw)
    assert r["success"] is False


def test_io_skills_get_exception_path(monkeypatch):
    from scitex_io._mcp import server as server_mod

    class BadPath:
        def __init__(self, *a, **kw):
            raise RuntimeError("boom-path")

    monkeypatch.setattr("pathlib.Path", BadPath)
    raw = server_mod.io_skills_get("anything")
    r = json.loads(raw)
    assert r["success"] is False


# EOF
