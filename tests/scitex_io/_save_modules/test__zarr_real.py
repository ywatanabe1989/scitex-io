#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real-file round-trip tests for scitex_io._save_modules._zarr.

The existing test__zarr.py is a placeholder. This file exercises the
full save path: directory store, zip store, key paths, compressors,
mixed-type dicts (str / scalar / array / object).
"""

from __future__ import annotations

import numpy as np
import pytest
import zarr

from scitex_io._save_modules._zarr import _save_zarr


class TestSaveZarrDirectoryStore:
    def test_array_default_compressor(self, tmp_path):
        arr = np.arange(100, dtype=np.float32).reshape(10, 10)
        out = str(tmp_path / "data.zarr")
        _save_zarr(arr, out)
        root = zarr.open(out, mode="r")
        assert "data" in root
        np.testing.assert_array_equal(root["data"][:], arr)

    def test_dict_top_level(self, tmp_path):
        d = {
            "arr": np.array([1, 2, 3, 4]),
            "scalar": 42,
            "name": "experiment-01",
            "flag": True,
        }
        out = str(tmp_path / "data.zarr")
        _save_zarr(d, out)
        root = zarr.open(out, mode="r")
        np.testing.assert_array_equal(root["arr"][:], np.array([1, 2, 3, 4]))
        assert int(root["scalar"][()]) == 42
        # Strings get stored as numpy arrays — read back as bytes/str.
        s = root["name"][()]
        if isinstance(s, bytes):
            s = s.decode()
        assert s == "experiment-01"
        assert bool(root["flag"][()]) is True

    def test_key_creates_nested_group(self, tmp_path):
        out = str(tmp_path / "data.zarr")
        _save_zarr(
            {"signal": np.arange(8)},
            out,
            key="session1/run3",
        )
        root = zarr.open(out, mode="r")
        assert "session1" in root
        assert "run3" in root["session1"]
        np.testing.assert_array_equal(
            root["session1"]["run3"]["signal"][:], np.arange(8)
        )

    def test_key_overwrite(self, tmp_path):
        """Writing twice to the same key overrides cleanly."""
        out = str(tmp_path / "data.zarr")
        _save_zarr({"x": np.arange(4)}, out, key="group/a")
        _save_zarr({"x": np.arange(4, 8)}, out, key="group/a")
        root = zarr.open(out, mode="r")
        np.testing.assert_array_equal(root["group"]["a"]["x"][:], np.arange(4, 8))

    @pytest.mark.parametrize("comp", ["zstd", "lz4", "gzip"])
    def test_named_compressors(self, tmp_path, comp):
        arr = np.random.default_rng(0).normal(size=(50, 50)).astype(np.float32)
        out = str(tmp_path / f"data_{comp}.zarr")
        _save_zarr(arr, out, compressor=comp)
        root = zarr.open(out, mode="r")
        np.testing.assert_allclose(root["data"][:], arr)

    def test_unknown_compressor_falls_back_to_zstd(self, tmp_path):
        """Implementation maps unknown names to zstd default."""
        out = str(tmp_path / "data.zarr")
        _save_zarr(np.arange(10), out, compressor="not-a-real-codec")
        root = zarr.open(out, mode="r")
        np.testing.assert_array_equal(root["data"][:], np.arange(10))

    def test_object_array_pickled(self, tmp_path):
        """Object-dtype arrays are pickled and tagged via _type attr."""
        # Lists become object arrays after np.asarray; alternatively
        # provide a dict whose value is a non-array object.
        out = str(tmp_path / "data.zarr")
        obj = {"meta": np.array([{"a": 1}, {"b": 2}], dtype=object)}
        _save_zarr(obj, out, compressor="zstd")
        root = zarr.open(out, mode="r")
        # The pickled tag should be present.
        assert root["meta"].attrs.get("_type") == "pickled"

    def test_consolidate_metadata_directory_store(self, tmp_path, capsys):
        out = str(tmp_path / "data.zarr")
        _save_zarr({"x": np.arange(4)}, out, consolidate_metadata=True)
        # Either consolidated or fallback line should print.
        captured = capsys.readouterr()
        assert "Saved to Zarr" in captured.out


class TestSaveZarrZipStore:
    def test_zip_store_round_trip(self, tmp_path):
        out = str(tmp_path / "data.zarr.zip")
        _save_zarr({"x": np.arange(16, dtype=np.int64)}, out)
        # Open the zip store directly to verify.
        store = zarr.storage.ZipStore(out, mode="r")
        try:
            root = zarr.open(store, mode="r")
            np.testing.assert_array_equal(root["x"][:], np.arange(16))
        finally:
            store.close()

    def test_zip_store_extension_zip(self, tmp_path):
        """A bare .zip path also routes to the ZipStore code path."""
        out = str(tmp_path / "data.zip")
        _save_zarr({"y": np.arange(5)}, out)
        store = zarr.storage.ZipStore(out, mode="r")
        try:
            root = zarr.open(store, mode="r")
            np.testing.assert_array_equal(root["y"][:], np.arange(5))
        finally:
            store.close()


class TestSaveZarrEdgeCases:
    def test_overwrite_existing_file(self, tmp_path):
        """Path exists as a regular file → implementation removes
        it and creates a directory store in its place."""
        out = tmp_path / "data.zarr"
        out.write_bytes(b"stale content")
        _save_zarr({"x": np.arange(3)}, str(out))
        assert out.is_dir(), "should now be a directory store"
        root = zarr.open(str(out), mode="r")
        np.testing.assert_array_equal(root["x"][:], np.arange(3))

    def test_explicit_directory_store_type(self, tmp_path):
        out = str(tmp_path / "data.zarr")
        _save_zarr({"x": np.arange(3)}, out, store_type="directory")
        root = zarr.open(out, mode="r")
        np.testing.assert_array_equal(root["x"][:], np.arange(3))

    def test_explicit_zip_store_type(self, tmp_path):
        # When store_type=zip is forced, even non-.zip extensions
        # should route to ZipStore.
        out = str(tmp_path / "data.bin")
        _save_zarr({"x": np.arange(3)}, out, store_type="zip")
        store = zarr.storage.ZipStore(out, mode="r")
        try:
            root = zarr.open(store, mode="r")
            np.testing.assert_array_equal(root["x"][:], np.arange(3))
        finally:
            store.close()
