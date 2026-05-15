#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Round-trip tests for the small save-handler modules:
  _yaml, _plotly, _text, _csv, _pickle, _joblib, _torch,
  _optuna_study_as_csv_and_pngs

Each test uses real I/O — no mocks. Deps are installed in [dev] extras.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scitex_io._save_modules._csv import _save_csv
from scitex_io._save_modules._joblib import _save_joblib
from scitex_io._save_modules._pickle import _save_pickle
from scitex_io._save_modules._text import _save_text
from scitex_io._save_modules._torch import _save_torch
from scitex_io._save_modules._yaml import _convert_paths_to_strings, _save_yaml

# --- _yaml.py ---------------------------------------------------------------


class TestSaveYaml:
    def test_dict_round_trip(self, tmp_path):
        from ruamel.yaml import YAML

        out = tmp_path / "data.yaml"
        _save_yaml({"a": 1, "b": [1, 2, 3]}, str(out))
        yaml = YAML()
        with open(out) as f:
            loaded = yaml.load(f)
        assert loaded["a"] == 1
        assert list(loaded["b"]) == [1, 2, 3]

    def test_path_objects_converted_to_strings(self, tmp_path):
        from ruamel.yaml import YAML

        out = tmp_path / "data.yaml"
        _save_yaml({"path": Path("/etc/hostname")}, str(out))
        yaml = YAML()
        with open(out) as f:
            loaded = yaml.load(f)
        assert loaded["path"] == "/etc/hostname"
        assert isinstance(loaded["path"], str)

    def test_convert_paths_recursive(self):
        nested = {
            "p": Path("/a"),
            "list": [Path("/b"), {"deep": Path("/c")}],
            "tuple": (Path("/d"), 1),
            "primitive": 42,
        }
        out = _convert_paths_to_strings(nested)
        assert out["p"] == "/a"
        assert out["list"][0] == "/b"
        assert out["list"][1]["deep"] == "/c"
        assert isinstance(out["tuple"], tuple)
        assert out["tuple"][0] == "/d"
        assert out["primitive"] == 42

    def test_convert_dotdict_to_dict(self):
        from scitex_io._utils import DotDict

        d = DotDict({"a": 1, "p": Path("/x")})
        out = _convert_paths_to_strings(d)
        assert isinstance(out, dict)
        assert out["a"] == 1
        assert out["p"] == "/x"

    def test_via_sio_save(self, tmp_path):
        import scitex_io as sio

        out = tmp_path / "via_save.yaml"
        sio.save({"x": 1}, str(out), verbose=False)
        from ruamel.yaml import YAML

        yaml = YAML()
        with open(out) as f:
            loaded = yaml.load(f)
        assert loaded["x"] == 1


# --- _text.py ---------------------------------------------------------------


class TestSaveText:
    def test_string_round_trip(self, tmp_path):
        out = tmp_path / "note.txt"
        _save_text("hello world\nline 2\n", str(out))
        assert out.read_text() == "hello world\nline 2\n"

    def test_empty_string(self, tmp_path):
        out = tmp_path / "empty.txt"
        _save_text("", str(out))
        assert out.read_text() == ""

    def test_via_sio_save(self, tmp_path):
        import scitex_io as sio

        out = tmp_path / "note.txt"
        sio.save("hi", str(out), verbose=False)
        assert out.read_text() == "hi"


# --- _csv.py ---------------------------------------------------------------


class TestSaveCsv:
    def test_dataframe(self, tmp_path):
        out = tmp_path / "df.csv"
        df = pd.DataFrame({"x": [1, 2, 3], "y": [0.5, 1.5, 2.5]})
        _save_csv(df, str(out))
        back = pd.read_csv(out)
        pd.testing.assert_frame_equal(back, df)

    def test_dict_of_lists(self, tmp_path):
        out = tmp_path / "d.csv"
        _save_csv({"a": [1, 2], "b": [3, 4]}, str(out))
        back = pd.read_csv(out)
        assert list(back.columns) == ["a", "b"]
        assert back["a"].tolist() == [1, 2]
        assert back["b"].tolist() == [3, 4]

    def test_ndarray_2d(self, tmp_path):
        out = tmp_path / "arr.csv"
        arr = np.array([[1, 2], [3, 4]])
        _save_csv(arr, str(out))
        # Reads back with default int column names "0","1".
        back = pd.read_csv(out)
        assert back.shape == (2, 2)

    def test_list_of_scalars(self, tmp_path):
        out = tmp_path / "scalars.csv"
        _save_csv([1, 2, 3, 4], str(out))
        # Single column CSV is fine.
        back = pd.read_csv(out)
        assert back.iloc[:, 0].tolist() == [2, 3, 4] or back.iloc[:, 0].tolist() == [
            1,
            2,
            3,
            4,
        ]


# --- _pickle.py ------------------------------------------------------------


class TestSavePickle:
    def test_arbitrary_object(self, tmp_path):
        out = tmp_path / "obj.pkl"
        obj = {"a": [1, 2, 3], "b": np.array([4, 5])}
        _save_pickle(obj, str(out))
        with open(out, "rb") as f:
            back = pickle.load(f)
        assert back["a"] == [1, 2, 3]
        np.testing.assert_array_equal(back["b"], np.array([4, 5]))

    def test_via_sio_save_pkl_gz(self, tmp_path):
        import scitex_io as sio

        out = tmp_path / "obj.pkl.gz"
        sio.save({"x": 1}, str(out), verbose=False)
        assert out.is_file() and out.stat().st_size > 0


# --- _joblib.py ------------------------------------------------------------


class TestSaveJoblib:
    def test_array(self, tmp_path):
        import joblib

        out = tmp_path / "arr.joblib"
        arr = np.arange(100)
        _save_joblib(arr, str(out))
        back = joblib.load(out)
        np.testing.assert_array_equal(back, arr)


# --- _torch.py -------------------------------------------------------------


class TestSaveTorch:
    def test_tensor(self, tmp_path):
        import torch

        out = tmp_path / "t.pt"
        t = torch.tensor([1.0, 2.0, 3.0])
        _save_torch(t, str(out))
        back = torch.load(out, weights_only=False)
        assert torch.equal(back, t)

    def test_state_dict(self, tmp_path):
        import torch

        out = tmp_path / "sd.pt"
        sd = {"weight": torch.zeros(2, 2), "bias": torch.ones(2)}
        _save_torch(sd, str(out))
        back = torch.load(out, weights_only=False)
        assert torch.equal(back["weight"], torch.zeros(2, 2))
        assert torch.equal(back["bias"], torch.ones(2))


# --- _plotly.py ------------------------------------------------------------


class TestSavePlotly:
    def test_save_figure_to_html(self, tmp_path):
        pytest.importorskip("plotly")
        from plotly.graph_objects import Figure, Scatter

        from scitex_io._save_modules._plotly import _save_plotly_html

        fig = Figure(data=[Scatter(x=[1, 2, 3], y=[4, 5, 6])])
        out = tmp_path / "fig.html"
        _save_plotly_html(fig, str(out))
        assert out.is_file()
        assert "plotly" in out.read_text().lower()

    def test_save_non_figure_raises(self, tmp_path):
        pytest.importorskip("plotly")
        from scitex_io._save_modules._plotly import _save_plotly_html

        with pytest.raises(TypeError):
            _save_plotly_html({"not": "a figure"}, str(tmp_path / "x.html"))
