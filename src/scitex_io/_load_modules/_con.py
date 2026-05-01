#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:51:45 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_con.py

from typing import Any

try:
    import mne

    MNE_AVAILABLE = True
except ImportError:
    mne = None  # type: ignore[assignment]
    MNE_AVAILABLE = False


def _load_con(lpath: str, **kwargs) -> Any:
    if not MNE_AVAILABLE:
        raise ImportError(
            "Loading .con files requires the 'mne' package. "
            "Install with: pip install mne"
        )
    if not lpath.endswith(".con"):
        raise ValueError("File must have .con extension")
    raw = mne.io.read_raw_fif(lpath, preload=True, **kwargs)
    samp_rate = raw.info["sfreq"]
    obj = raw.to_data_frame()
    obj["samp_rate"] = samp_rate
    return obj


# EOF
