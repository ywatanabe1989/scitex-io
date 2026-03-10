#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:05:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/src/scitex/io/_save_modules/__init__.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/io/_save_modules/__init__.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Save modules for scitex.io.save functionality

This package contains format-specific save handlers for various file types.
Each module provides a save_<format> function that handles saving objects
to that specific format.
"""

# Core deps always available
from ._csv import _save_csv as save_csv
from ._numpy import _save_npy as save_npy, _save_npz as save_npz
from ._pickle import _save_pickle as save_pickle, _save_pickle_gz as save_pickle_compressed
from ._json import _save_json as save_json
from ._text import _save_text as save_text
from ._tex import _save_tex as save_tex
from ._html import save_html

# Optional: openpyxl / xlrd
try:
    from ._excel import save_excel
except ImportError:
    save_excel = None

# Optional: joblib
try:
    from ._joblib import _save_joblib as save_joblib
except ImportError:
    save_joblib = None

# Optional: torch
try:
    from ._torch import _save_torch as save_torch
except ImportError:
    save_torch = None

# Optional: PyYAML
try:
    from ._yaml import _save_yaml as save_yaml
except ImportError:
    save_yaml = None

# Optional: h5py
try:
    from ._hdf5 import _save_hdf5 as save_hdf5
except ImportError:
    save_hdf5 = None

# Optional: scipy
try:
    from ._matlab import _save_matlab as save_matlab
except ImportError:
    save_matlab = None

# Optional: catboost
try:
    from ._catboost import _save_catboost as save_catboost
except ImportError:
    save_catboost = None

# Optional: matplotlib / PIL
try:
    from ._image import save_image
except ImportError:
    save_image = None

# Optional: matplotlib / imageio
try:
    from ._mp4 import _mk_mp4 as save_mp4
except ImportError:
    save_mp4 = None

# Optional: zarr
try:
    from ._zarr import _save_zarr as save_zarr
except ImportError:
    save_zarr = None

# Optional: bibtexparser
try:
    from ._bibtex import save_bibtex
except ImportError:
    save_bibtex = None

# Optional: pandas (listed df utilities)
try:
    from ._listed_dfs_as_csv import _save_listed_dfs_as_csv as save_listed_dfs_as_csv
except ImportError:
    save_listed_dfs_as_csv = None

try:
    from ._listed_scalars_as_csv import _save_listed_scalars_as_csv as save_listed_scalars_as_csv
except ImportError:
    save_listed_scalars_as_csv = None

# Optional: optuna
try:
    from ._optuna_study_as_csv_and_pngs import save_optuna_study_as_csv_and_pngs
except ImportError:
    save_optuna_study_as_csv_and_pngs = None

# Define what gets imported with "from scitex.io._save_modules import *"
__all__ = [
    "save_csv",
    "save_excel",
    "save_npy",
    "save_npz",
    "save_pickle",
    "save_pickle_compressed",
    "save_joblib",
    "save_torch",
    "save_json",
    "save_yaml",
    "save_hdf5",
    "save_matlab",
    "save_catboost",
    "save_text",
    "save_tex",
    "save_html",
    "save_image",
    "save_mp4",
    "save_zarr",
    "save_bibtex",
    "save_listed_dfs_as_csv",
    "save_listed_scalars_as_csv",
    "save_optuna_study_as_csv_and_pngs",
]

# EOF
