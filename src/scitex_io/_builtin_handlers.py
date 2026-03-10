#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto-register all built-in format handlers at import time.

This module is imported by __init__.py to populate the registry
with all supported formats. User registrations override these.
"""

from ._registry import register_loader, register_saver

# === SAVE HANDLERS ===

from ._save_modules import (
    save_catboost,
    save_csv,
    save_excel,
    save_hdf5,
    save_html,
    save_image,
    save_joblib,
    save_json,
    save_matlab,
    save_mp4,
    save_npy,
    save_npz,
    save_pickle,
    save_pickle_compressed,
    save_tex,
    save_text,
    save_torch,
    save_yaml,
    save_zarr,
)
from ._save_modules._bibtex import save_bibtex

_SAVER_MAP = {
    # Spreadsheet
    ".csv": save_csv,
    ".xlsx": save_excel,
    ".xls": save_excel,
    # NumPy
    ".npy": save_npy,
    ".npz": save_npz,
    # Pickle
    ".pkl": save_pickle,
    ".pickle": save_pickle,
    ".pkl.gz": save_pickle_compressed,
    # Binary
    ".joblib": save_joblib,
    ".pth": save_torch,
    ".pt": save_torch,
    ".mat": save_matlab,
    ".cbm": save_catboost,
    # Text
    ".json": save_json,
    ".yaml": save_yaml,
    ".yml": save_yaml,
    ".txt": save_text,
    ".md": save_text,
    ".py": save_text,
    ".css": save_text,
    ".js": save_text,
    ".tex": save_tex,
    # Bibliography
    ".bib": save_bibtex,
    # Data
    ".html": save_html,
    ".hdf5": save_hdf5,
    ".h5": save_hdf5,
    ".zarr": save_zarr,
    # Media
    ".mp4": save_mp4,
    # Images (handled via _handle_image_with_csv in _save.py)
    ".png": save_image,
    ".jpg": save_image,
    ".jpeg": save_image,
    ".gif": save_image,
    ".tiff": save_image,
    ".tif": save_image,
    ".svg": save_image,
    ".pdf": save_image,
}

for ext, fn in _SAVER_MAP.items():
    register_saver(ext, fn, builtin=True)


# === LOAD HANDLERS ===

from ._load_modules._bibtex import _load_bibtex
from ._load_modules._con import _load_con
from ._load_modules._docx import _load_docx
from ._load_modules._eeg import _load_eeg_data
from ._load_modules._hdf5 import _load_hdf5
from ._load_modules._image import _load_image
from ._load_modules._joblib import _load_joblib
from ._load_modules._json import _load_json
from ._load_modules._markdown import _load_markdown
from ._load_modules._matlab import _load_matlab
from ._load_modules._numpy import _load_npy
from ._load_modules._pandas import _load_csv, _load_excel, _load_tsv
from ._load_modules._pdf import _load_pdf
from ._load_modules._pickle import _load_pickle
from ._load_modules._sqlite3 import _load_db_sqlite3
from ._load_modules._torch import _load_torch
from ._load_modules._txt import _load_txt
from ._load_modules._xml import _load_xml
from ._load_modules._yaml import _load_yaml
from ._load_modules._zarr import _load_zarr

_LOADER_MAP = {
    # Default
    "": _load_txt,
    # Config
    ".yaml": _load_yaml,
    ".yml": _load_yaml,
    ".json": _load_json,
    ".xml": _load_xml,
    # Bibliography
    ".bib": _load_bibtex,
    # ML/DL
    ".pth": _load_torch,
    ".pt": _load_torch,
    ".joblib": _load_joblib,
    ".pkl": _load_pickle,
    ".pickle": _load_pickle,
    ".gz": _load_pickle,
    # Tabular
    ".csv": _load_csv,
    ".tsv": _load_tsv,
    ".xls": _load_excel,
    ".xlsx": _load_excel,
    ".xlsm": _load_excel,
    ".xlsb": _load_excel,
    ".db": _load_db_sqlite3,
    # Scientific
    ".npy": _load_npy,
    ".npz": _load_npy,
    ".mat": _load_matlab,
    ".hdf5": _load_hdf5,
    ".h5": _load_hdf5,
    ".zarr": _load_zarr,
    ".con": _load_con,
    # Documents
    ".txt": _load_txt,
    ".tex": _load_txt,
    ".log": _load_txt,
    ".event": _load_txt,
    ".py": _load_txt,
    ".sh": _load_txt,
    ".md": _load_markdown,
    ".docx": _load_docx,
    ".pdf": _load_pdf,
    # Images
    ".jpg": _load_image,
    ".png": _load_image,
    ".tiff": _load_image,
    ".tif": _load_image,
    # EEG
    ".vhdr": _load_eeg_data,
    ".vmrk": _load_eeg_data,
    ".edf": _load_eeg_data,
    ".bdf": _load_eeg_data,
    ".gdf": _load_eeg_data,
    ".cnt": _load_eeg_data,
    ".egi": _load_eeg_data,
    ".eeg": _load_eeg_data,
    ".set": _load_eeg_data,
}

for ext, fn in _LOADER_MAP.items():
    register_loader(ext, fn, builtin=True)
