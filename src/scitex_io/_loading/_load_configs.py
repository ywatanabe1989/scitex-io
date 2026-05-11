#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 23:54:07 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_configs.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = "./src/scitex/io/_load_configs.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import warnings
from pathlib import Path
from typing import Optional, Union

from .._glob import glob
from .._utils import DotDict
from ._load import load


def _resolve_case_conflicts(d, path="CONFIG"):
    """Drop case-conflicting siblings, preferring the UPPER_CASE variant.

    Walks a (possibly nested) dict/DotDict in place. For any pair of
    sibling keys that collide once upper-cased (e.g. ``hidden_dim`` +
    ``HIDDEN_DIM``), keep the upper variant, drop the other, and emit
    a ``UserWarning`` pointing at the conflict location.

    UPPER_CASE is the project convention for config constants — see
    ``load_configs`` docstring and the scitex-io README §3.
    """
    if not isinstance(d, (dict, DotDict)):
        return d
    by_upper: dict[str, list[str]] = {}
    for k in list(d.keys()):
        if isinstance(k, str):
            by_upper.setdefault(k.upper(), []).append(k)
    for upper, variants in by_upper.items():
        if len(variants) <= 1:
            continue
        upper_present = upper in variants
        keep = upper if upper_present else max(variants, key=str.isupper)
        for v in variants:
            if v != keep:
                warnings.warn(
                    f"load_configs: case conflict at {path}.* — "
                    f"{variants!r} fold to {upper!r}; keeping {keep!r}, "
                    f"dropping {v!r}. Use UPPER_CASE for config constants.",
                    UserWarning,
                    stacklevel=3,
                )
                d.pop(v, None)
    for k, v in list(d.items()):
        if isinstance(v, (dict, DotDict)):
            _resolve_case_conflicts(v, path=f"{path}.{k}")
    return d


def load_configs(
    IS_DEBUG=None,
    show=False,
    verbose=False,
    config_dir: Optional[Union[str, Path]] = None,
):
    """Load YAML configuration files from specified directory.

    Parameters
    ----------
    IS_DEBUG : bool, optional
        Debug mode flag. If None, reads from IS_DEBUG.yaml
    show : bool
        Show configuration changes
    verbose : bool
        Print detailed information
    config_dir : Union[str, Path], optional
        Directory containing configuration files. Can be a string or pathlib.Path object.
        Defaults to "./config" if None

    Returns
    -------
    DotDict
        Merged configuration dictionary
    """

    def apply_debug_values(config, IS_DEBUG):
        """Apply debug values if IS_DEBUG is True."""
        if not IS_DEBUG or not isinstance(config, (dict, DotDict)):
            return config

        for key, value in list(config.items()):
            if key.startswith(("DEBUG_", "debug_")):
                dk_wo_debug_prefix = key.split("_", 1)[1]
                config[dk_wo_debug_prefix] = value
                if show or verbose:
                    print(f"{key} -> {dk_wo_debug_prefix}")
            elif isinstance(value, (dict, DotDict)):
                config[key] = apply_debug_values(value, IS_DEBUG)
        return config

    try:
        # Handle config directory parameter
        if config_dir is None:
            config_dir = "./config"
        elif isinstance(config_dir, Path):
            config_dir = str(config_dir)

        # Set debug mode
        debug_config_path = f"{config_dir}/IS_DEBUG.yaml"
        IS_DEBUG = (
            IS_DEBUG
            or os.getenv("CI") == "True"
            or (
                os.path.exists(debug_config_path)
                and load(debug_config_path).get("IS_DEBUG")
            )
        )

        # Load and merge configs (namespaced by filename)
        CONFIGS = {}

        # Load from main config directory
        config_pattern = f"{config_dir}/*.yaml"
        for lpath in glob(config_pattern):
            if config := load(lpath):
                filename = Path(lpath).stem
                CONFIGS[filename] = apply_debug_values(config, IS_DEBUG)

        # Load from categories subdirectory if it exists
        categories_dir = f"{config_dir}/categories"
        if os.path.exists(categories_dir):
            categories_pattern = f"{categories_dir}/*.yaml"
            for lpath in glob(categories_pattern):
                if config := load(lpath):
                    filename = Path(lpath).stem
                    CONFIGS[filename] = apply_debug_values(config, IS_DEBUG)

        # UPPER_CASE convention: warn + drop case-conflicting siblings,
        # preferring the UPPER variant. Applies to filename-level keys
        # (e.g. MODEL.yaml + model.yaml) and recursively to keys inside
        # each YAML.
        _resolve_case_conflicts(CONFIGS)

        return DotDict(CONFIGS)

    except Exception as e:
        print(f"Error loading configs: {e}")
        return DotDict({})


# EOF
