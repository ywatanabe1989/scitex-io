from __future__ import annotations
# Smoke test (TODO: real coverage).
def test_placeholder():
    assert True

# Add your tests here

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/io/_save_modules/_yaml.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-16 12:26:16 (ywatanabe)"
# # File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_yaml.py
#
# from pathlib import Path
# from ruamel.yaml import YAML
#
#
# def _convert_paths_to_strings(obj):
#     """
#     Recursively convert pathlib.Path objects to strings and DotDict objects to regular dicts in a data structure.
#
#     Parameters
#     ----------
#     obj : any
#         The object to process. Can be dict, list, tuple, DotDict, Path, or any other type.
#
#     Returns
#     -------
#     any
#         Copy of the object with all Path objects converted to strings and DotDict objects converted to regular dicts.
#     """
#     if isinstance(obj, Path):
#         return str(obj)
#     elif hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
#         # Handle DotDict or similar objects with to_dict() method
#         dict_obj = obj.to_dict()
#         return _convert_paths_to_strings(dict_obj)
#     elif isinstance(obj, dict):
#         return {key: _convert_paths_to_strings(value) for key, value in obj.items()}
#     elif isinstance(obj, (list, tuple)):
#         converted_list = [_convert_paths_to_strings(item) for item in obj]
#         return tuple(converted_list) if isinstance(obj, tuple) else converted_list
#     else:
#         return obj
#
#
# def _save_yaml(obj, spath):
#     """
#     Save a Python object as a YAML file.
#
#     Automatically converts any pathlib.Path objects and DotDict objects within
#     the data structure before serialization, as YAML cannot directly serialize
#     these complex objects.
#
#     Parameters
#     ----------
#     obj : dict or DotDict
#         The object to serialize to YAML. Can contain pathlib.Path objects and
#         DotDict objects, which will be automatically converted to strings and
#         regular dicts respectively.
#     spath : str
#         Path where the YAML file will be saved.
#
#     Returns
#     -------
#     None
#     """
#     # Convert any Path objects to strings before YAML serialization
#     obj_with_strings = _convert_paths_to_strings(obj)
#
#     yaml = YAML()
#     yaml.preserve_quotes = True
#     yaml.indent(mapping=4, sequence=4, offset=2)
#
#     with open(spath, "w") as f:
#         yaml.dump(obj_with_strings, f)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/io/_save_modules/_yaml.py
# --------------------------------------------------------------------------------


# === merged from test__small_handlers.py ===
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Round-trip tests for the small save-handler modules:
  _yaml, _plotly, _text, _csv, _pickle, _joblib, _torch,
  _optuna_study_as_csv_and_pngs

Each test uses real I/O — no mocks. Deps are installed in [dev] extras.
"""


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


