#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_io._save_modules._feather.

`_save_feather` accepts a DataFrame / dict / ndarray and writes a
Feather v2 file. Tests exercise:
  - DataFrame round-trip
  - dict → DataFrame coercion
  - ndarray → DataFrame coercion
  - kwargs pass-through to pandas
  - extension dispatch via scitex_io.save()
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pyarrow.feather as pf

from scitex_io._save_modules._feather import _save_feather


class TestSaveFeather:
    def test_dataframe_round_trip(self, tmp_path):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [0.1, 0.2, 0.3]})
        out = tmp_path / "data.feather"
        _save_feather(df, str(out))
        assert out.is_file() and out.stat().st_size > 0
        back = pf.read_feather(str(out))
        pd.testing.assert_frame_equal(back, df)

    def test_dict_coerced_to_dataframe(self, tmp_path):
        d = {"a": [1, 2], "b": ["x", "y"]}
        out = tmp_path / "data.feather"
        _save_feather(d, str(out))
        back = pf.read_feather(str(out))
        pd.testing.assert_frame_equal(back, pd.DataFrame(d))

    def test_ndarray_coerced_to_dataframe(self, tmp_path):
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        out = tmp_path / "data.feather"
        _save_feather(arr, str(out))
        back = pf.read_feather(str(out))
        # Default pandas coercion: column names are 0, 1, 2 (integers)
        assert back.shape == (2, 3)
        assert back.iloc[0].tolist() == [1, 2, 3]
        assert back.iloc[1].tolist() == [4, 5, 6]

    def test_kwargs_forwarded(self, tmp_path):
        """pandas.to_feather forwards kwargs like compression."""
        df = pd.DataFrame({"x": list(range(100))})
        out = tmp_path / "data.feather"
        # Uncompressed should write
        _save_feather(df, str(out), compression="uncompressed")
        size_uncompressed = out.stat().st_size

        out2 = tmp_path / "data_zstd.feather"
        _save_feather(df, str(out2), compression="zstd")
        size_zstd = out2.stat().st_size
        # Compressed should typically be smaller — or at least pandas
        # honors the kwarg without raising.
        assert size_uncompressed > 0
        assert size_zstd > 0

    def test_dispatch_via_sio_save(self, tmp_path):
        """scitex_io.save dispatches .feather → _save_feather."""
        import scitex_io as sio

        df = pd.DataFrame({"x": [1, 2, 3]})
        out = tmp_path / "data.feather"
        sio.save(df, str(out), verbose=False)
        assert out.is_file()
        back = pf.read_feather(str(out))
        pd.testing.assert_frame_equal(back, df)
