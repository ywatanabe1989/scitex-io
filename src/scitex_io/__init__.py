#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scitex-io: Universal scientific data I/O with plugin registry.

Supports 30+ formats out of the box. Register custom handlers via::

    from scitex_io import register_saver, register_loader

    @register_saver(".myformat")
    def save_myformat(obj, path, **kw): ...

    @register_loader(".myformat")
    def load_myformat(path, **kw): ...
"""

# Registry API (must be imported before _builtin_handlers)
from ._registry import (
    get_loader,
    get_saver,
    list_formats,
    register_loader,
    register_saver,
    unregister_loader,
    unregister_saver,
)

# Trigger built-in handler registration
from . import _builtin_handlers  # noqa: F401

# Core I/O
from ._save import save
from ._load import load
from ._load_configs import load_configs
from ._glob import glob, parse_glob
from ._reload import reload
from ._flush import flush
from ._cache import cache

# Explorers
from ._load_modules._H5Explorer import H5Explorer, explore_h5, has_h5_key
from ._load_modules._ZarrExplorer import ZarrExplorer, explore_zarr, has_zarr_key

# Cache control
from ._load_cache import (
    get_cache_info,
    configure_cache,
    clear_cache as clear_load_cache,
)

# Save utilities
from ._save_modules import (
    save_image,
    save_text,
    save_mp4,
    save_listed_dfs_as_csv,
    save_listed_scalars_as_csv,
    save_optuna_study_as_csv_and_pngs,
)

# Optional modules
try:
    from ._path import path
except ImportError:
    path = None

try:
    from ._mv_to_tmp import mv_to_tmp
except ImportError:
    mv_to_tmp = None

try:
    from ._json2md import json2md
except ImportError:
    json2md = None

try:
    from .utils import migrate_h5_to_zarr, migrate_h5_to_zarr_batch
except ImportError:
    migrate_h5_to_zarr = None
    migrate_h5_to_zarr_batch = None

__version__ = "0.2.0"

__all__ = [
    # Registry API
    "register_saver",
    "register_loader",
    "get_saver",
    "get_loader",
    "list_formats",
    "unregister_saver",
    "unregister_loader",
    # Core I/O
    "save",
    "load",
    "load_configs",
    "glob",
    "parse_glob",
    "reload",
    "flush",
    "cache",
    # Explorers
    "H5Explorer",
    "explore_h5",
    "has_h5_key",
    "ZarrExplorer",
    "explore_zarr",
    "has_zarr_key",
    # Cache control
    "get_cache_info",
    "configure_cache",
    "clear_load_cache",
    # Save utilities
    "save_image",
    "save_text",
    "save_mp4",
    "save_listed_dfs_as_csv",
    "save_listed_scalars_as_csv",
    "save_optuna_study_as_csv_and_pngs",
    # Optional
    "path",
    "mv_to_tmp",
    "json2md",
    "migrate_h5_to_zarr",
    "migrate_h5_to_zarr_batch",
]
