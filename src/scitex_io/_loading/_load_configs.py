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


def _normalize_to_upper(d, path="CONFIG"):
    """Normalize every key in a config tree to UPPER_CASE.

    Walks a (possibly nested) dict/DotDict in place and renames every
    string key to its ``str.upper()`` form so the loaded config is
    case-stable regardless of how filenames and YAML keys were written.

    If two siblings fold to the same UPPER key (e.g. ``MODEL`` +
    ``model``, or ``HIDDEN_DIM`` + ``hidden_dim``), keep the value
    associated with the already-UPPER variant and drop the lowercase
    one, emitting a ``UserWarning`` pointing at the conflict location.
    """
    if not isinstance(d, (dict, DotDict)):
        return d

    by_upper: dict[str, list[str]] = {}
    for k in list(d.keys()):
        if isinstance(k, str):
            by_upper.setdefault(k.upper(), []).append(k)

    for upper, variants in by_upper.items():
        if len(variants) > 1:
            keep = upper if upper in variants else variants[0]
            for v in variants:
                if v != keep:
                    warnings.warn(
                        f"load_configs: case conflict at {path}.* — "
                        f"{variants!r} fold to {upper!r}; keeping value "
                        f"from {keep!r}, dropping {v!r}.",
                        UserWarning,
                        stacklevel=3,
                    )
                    d.pop(v, None)
            # After de-duplication, rename keep → upper if needed.
            if keep != upper:
                d[upper] = d.pop(keep)
        else:
            (only,) = variants
            if only != upper:
                d[upper] = d.pop(only)

    for k, v in list(d.items()):
        if isinstance(v, (dict, DotDict)):
            _normalize_to_upper(v, path=f"{path}.{k}")
    return d


def load_configs(
    IS_DEBUG=None,
    show=False,
    verbose=False,
    config_dir: Optional[Union[str, Path]] = None,
):
    """Load and merge every YAML under ``config_dir`` into one ``DotDict``.

    Filename stems become top-level keys; YAML keys become nested
    attributes. Every key (filename stem and every nested key) is
    normalised to UPPER_CASE at load time so the in-memory tree is
    case-stable regardless of source casing — ``model.yaml`` with
    ``hidden_dim: 256`` lands at ``CONFIG.MODEL.HIDDEN_DIM``.

    If two siblings fold to the same UPPER key (e.g. ``MODEL.yaml``
    next to ``model.yaml``, or ``HIDDEN_DIM`` next to ``hidden_dim``),
    a ``UserWarning`` is emitted pointing at the conflict, the
    UPPER variant's value is kept, and the lowercase one is dropped.

    Debug mode promotes any ``DEBUG_<KEY>`` sibling over its non-debug
    counterpart, so a single ``IS_DEBUG.yaml`` flips the whole project
    between production and debug values. Equivalent triggers:
    ``IS_DEBUG.yaml`` with ``IS_DEBUG: true``, the ``IS_DEBUG=True``
    kwarg, or running under ``CI=True``.

    Parameters
    ----------
    IS_DEBUG : bool, optional
        Force debug mode. If ``None`` (default), inferred from
        ``IS_DEBUG.yaml`` inside ``config_dir`` or from the ``CI``
        env var.
    show : bool
        Echo the ``DEBUG_<KEY> -> <KEY>`` substitutions to stdout.
    verbose : bool
        Print detailed information.
    config_dir : Union[str, Path], optional
        Directory containing the YAML files. Defaults to ``"./config"``.

    Returns
    -------
    DotDict
        Merged configuration tree with UPPER_CASE keys throughout.

    Examples
    --------
    >>> CONFIG = load_configs()                       # ./config/*.yaml
    >>> CONFIG.MODEL.HIDDEN_DIM                       # 256
    >>> CONFIG = load_configs(IS_DEBUG=True)
    >>> CONFIG.MODEL.HIDDEN_DIM                       # 32 (DEBUG_ promoted)
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

        # Normalise every filename-level key (from YAML stem) and every
        # nested key to UPPER_CASE so the loaded config is case-stable
        # regardless of source casing. Conflicts (e.g. MODEL.yaml +
        # model.yaml, HIDDEN_DIM + hidden_dim) warn and drop the
        # lowercase variant in favour of the UPPER one.
        _normalize_to_upper(CONFIGS)

        return DotDict(CONFIGS)

    except Exception as e:
        print(f"Error loading configs: {e}")
        return DotDict({})


# EOF
