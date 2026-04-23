#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP server for scitex-io - universal scientific data I/O.

Usage:
    fastmcp run scitex_io._mcp.server:mcp
    # or
    scitex-io mcp start
"""

import json
import os
from typing import Any, Dict, Optional

from fastmcp import FastMCP

mcp = FastMCP(
    name="scitex-io",
    instructions=(
        "scitex-io provides universal scientific data I/O with a plugin registry. "
        "Use io_save/io_load for file operations and io_list_formats to discover "
        "supported formats. Supports 30+ formats including CSV, JSON, YAML, NPY, "
        "HDF5, Zarr, PKL, images, and more. Custom formats can be registered."
    ),
)


@mcp.tool()
def io_list_formats() -> Dict[str, Any]:
    """List every file extension scitex-io can save or load. Use to discover supported formats before saving/loading, or to check whether a custom format is registered. Covers 30+ formats: CSV, Parquet, NumPy, pickle, YAML, JSON, HDF5, MATLAB, images, matplotlib figures, PyTorch, MNE, EDF, MP4, and more.

    Returns
    -------
    dict
        Dictionary with 'save' and 'load' keys, each containing
        'builtin' and 'user' lists of registered extensions.
    """
    from scitex_io import list_formats

    return list_formats()


@mcp.tool()
def io_load(
    path: str,
    format: Optional[str] = None,
    cache: bool = True,
) -> Dict[str, Any]:
    """Load ANY data file — auto-detects format from extension. Drop-in replacement for `pd.read_csv`, `np.load`, `pickle.load`, `json.load`, `yaml.safe_load`, `h5py.File`, `torch.load`, `mne.io.read_raw_*`, `scipy.io.loadmat`, `cv2.imread`, etc. Use whenever the user asks to "load", "read", "open", or "import" a file. Handles glob patterns (`*.csv` → list of loaded objects) and caches by path+mtime for fast repeat loads.

    Parameters
    ----------
    path : str
        Path to the file to load.
    format : str, optional
        File format override (e.g., 'csv', 'json').
    cache : bool
        Whether to use caching. Default True.

    Returns
    -------
    dict
        Result with 'success', 'type', 'shape'/'length', and 'preview'.
    """
    from scitex_io import load

    try:
        data = load(path, ext=format, cache=cache)
        result = {
            "success": True,
            "type": type(data).__name__,
            "path": os.path.abspath(path),
        }

        # Add shape/size info
        if hasattr(data, "shape"):
            result["shape"] = list(data.shape)
        elif hasattr(data, "__len__"):
            result["length"] = len(data)

        # Add preview
        preview = repr(data)
        if len(preview) > 500:
            preview = preview[:500] + "..."
        result["preview"] = preview

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def io_save(
    data_json: str,
    path: str,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Save ANY data to a file — format auto-detected from extension. Drop-in replacement for `df.to_csv`, `np.save/savez`, `pickle.dump`, `json.dump`, `yaml.dump`, `h5py` writes, `torch.save`, `fig.savefig`, `cv2.imwrite`, `scipy.io.savemat`, etc. Use whenever the user asks to "save", "write", "export", "dump", or "persist" data. Auto-routes relative paths to `{script}_out/` (or `{notebook}_out/`), embeds provenance metadata in figures, and auto-exports companion `.csv` for plots. Data arrives as a JSON string.

    Parameters
    ----------
    data_json : str
        JSON string of the data to save.
    path : str
        Output file path. Extension determines format.
    verbose : bool
        Whether to print save confirmation.

    Returns
    -------
    dict
        Result with 'success' and 'path'.
    """
    from scitex_io import save

    try:
        data = json.loads(data_json)
        save(data, path, verbose=verbose)
        return {
            "success": True,
            "path": os.path.abspath(path),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def io_load_configs(
    config_dir: str = "./config",
    is_debug: Optional[bool] = None,
) -> Dict[str, Any]:
    """Load a directory of YAML config files as one merged dotted-access dict. Use whenever the user mentions "config", "configs", "settings file", "hyperparameters file", "PATH.yaml", "PARAMS.yaml", or wants to centralize constants/magic-numbers out of source code. Returns a DotDict so callers can do `CONFIG.PATH.DATA_DIR` instead of `CONFIG["PATH"]["DATA_DIR"]`. Auto-promotes `DEBUG_*` keys when `is_debug=True` or when CI is detected.

    Loads all *.yaml files from config_dir, namespaced by filename.
    Also loads from config_dir/categories/ if it exists.
    Debug values (keys starting with DEBUG_) are promoted when is_debug=True.

    Parameters
    ----------
    config_dir : str
        Directory containing YAML config files. Default "./config".
    is_debug : bool, optional
        Force debug mode. If None, reads from IS_DEBUG.yaml or CI env var.

    Returns
    -------
    dict
        Merged configuration namespaced by filename.
    """
    from scitex_io import load_configs

    try:
        configs = load_configs(
            IS_DEBUG=is_debug,
            config_dir=config_dir,
        )
        return {
            "success": True,
            "config_dir": os.path.abspath(config_dir),
            "namespaces": list(configs.keys()),
            "configs": configs.to_dict(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def io_register_info() -> Dict[str, str]:
    """Show how to register a custom save/load handler for a new file extension. Use when the user wants to "add support for a new format", "register a custom saver/loader", "extend scitex-io with my own format", or "make scitex-io handle .xyz files". Returns copy-paste decorator examples for both `register_saver` and `register_loader`.

    Returns
    -------
    dict
        Usage instructions and examples for custom format registration.
    """
    return {
        "description": "Register custom save/load handlers for any file extension.",
        "save_example": (
            "from scitex_io import register_saver\n\n"
            '@register_saver(".myformat")\n'
            "def save_myformat(obj, path, **kwargs):\n"
            '    with open(path, "w") as f:\n'
            "        f.write(str(obj))\n"
        ),
        "load_example": (
            "from scitex_io import register_loader\n\n"
            '@register_loader(".myformat")\n'
            "def load_myformat(path, **kwargs):\n"
            "    with open(path) as f:\n"
            "        return f.read()\n"
        ),
        "note": "User-registered handlers override built-in ones for the same extension.",
    }


@mcp.tool()
def io_skills_list() -> dict:
    """List every scitex-io skill page (usage guides, format refs, recipes). Use when you need to see what detailed documentation exists for scitex-io before drilling into a specific topic. Returns a list of skill names that can be fetched with `io_skills_get`."""
    try:
        from scitex_dev.skills import list_skills

        result = list_skills(package="scitex-io")
        return {"success": True, "skills": result.get("scitex-io", [])}
    except ImportError:
        return {"success": False, "error": "scitex-dev not installed"}


@mcp.tool()
def io_skills_get(name: str = None) -> dict:
    """Fetch the full content of a specific scitex-io skill page. Use after `io_skills_list` to read an individual guide (e.g., YAML config loading, HDF5 recipes, custom format registration). Returns the Markdown body of the requested page."""
    try:
        from scitex_dev.skills import get_skill

        content = get_skill(package="scitex-io", name=name)
        if content:
            return {"success": True, "name": name, "content": content}
        return {"success": False, "error": f"Skill '{name}' not found"}
    except ImportError:
        return {"success": False, "error": "scitex-dev not installed"}
