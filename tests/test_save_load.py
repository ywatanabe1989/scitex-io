#!/usr/bin/env python3
"""Round-trip save/load tests for common formats."""
import os
import numpy as np
import pandas as pd
import pytest
from scitex_io import save, load, list_formats


def _has_handler(ext):
    """Check if both save and load handlers are registered for ext."""
    fmt = list_formats()
    all_save = fmt["save"]["builtin"] + fmt["save"]["user"]
    all_load = fmt["load"]["builtin"] + fmt["load"]["user"]
    return ext in all_save and ext in all_load


class TestRoundTrip:
    def test_json(self, tmp_dir):
        data = {"a": 1, "b": [2, 3]}
        path = os.path.join(tmp_dir, "test.json")
        save(data, path, verbose=False)
        assert load(path, cache=False) == data

    def test_csv(self, tmp_dir):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        path = os.path.join(tmp_dir, "test.csv")
        save(df, path, verbose=False)
        loaded = load(path, cache=False)
        assert list(loaded.columns) == ["x", "y"]

    @pytest.mark.skipif(not _has_handler(".yaml"), reason="yaml handler not available")
    def test_yaml(self, tmp_dir):
        data = {"key": "value"}
        path = os.path.join(tmp_dir, "test.yaml")
        save(data, path, verbose=False)
        assert load(path, cache=False)["key"] == "value"

    def test_npy(self, tmp_dir):
        arr = np.array([1.0, 2.0, 3.0])
        path = os.path.join(tmp_dir, "test.npy")
        save(arr, path, verbose=False)
        assert np.array_equal(load(path, cache=False), arr)

    def test_pkl(self, tmp_dir):
        data = {"x": [1, 2, set([3, 4])]}
        path = os.path.join(tmp_dir, "test.pkl")
        save(data, path, verbose=False)
        assert load(path, cache=False) == data

    def test_custom_format(self, tmp_dir):
        from scitex_io import register_saver, register_loader, unregister_saver, unregister_loader
        @register_saver(".mytest")
        def save_mytest(obj, path, **kw):
            with open(path, "w") as f: f.write(f"MYTEST:{obj}")
        @register_loader(".mytest")
        def load_mytest(path, **kw):
            with open(path) as f: return f.read().replace("MYTEST:", "")
        path = os.path.join(tmp_dir, "test.mytest")
        save("hello", path, verbose=False)
        assert load(path, cache=False) == "hello"
        unregister_saver(".mytest")
        unregister_loader(".mytest")
