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
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/io/_save_modules/_plotly.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-16 12:30:15 (ywatanabe)"
# # File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_plotly.py
#
# import plotly
#
#
# def _save_plotly_html(obj, spath):
#     """
#     Save a Plotly figure as an HTML file.
#
#     Parameters
#     ----------
#     obj : plotly.graph_objs.Figure
#         The Plotly figure to save.
#     spath : str
#         Path where the HTML file will be saved.
#
#     Returns
#     -------
#     None
#     """
#     if isinstance(obj, plotly.graph_objs.Figure):
#         obj.write_html(file=spath)
#     else:
#         raise TypeError("Object must be a plotly.graph_objs.Figure")

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/io/_save_modules/_plotly.py
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

