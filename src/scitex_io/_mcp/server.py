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
    """List all registered save/load formats.

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
    """Load data from a file.

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
    """Save data to a file. Data is passed as JSON string.

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
def io_register_info() -> Dict[str, str]:
    """Show how to register custom format handlers.

    Returns
    -------
    dict
        Usage instructions and examples for custom format registration.
    """
    return {
        "description": "Register custom save/load handlers for any file extension.",
        "save_example": (
            'from scitex_io import register_saver\n\n'
            '@register_saver(".myformat")\n'
            'def save_myformat(obj, path, **kwargs):\n'
            '    with open(path, "w") as f:\n'
            '        f.write(str(obj))\n'
        ),
        "load_example": (
            'from scitex_io import register_loader\n\n'
            '@register_loader(".myformat")\n'
            'def load_myformat(path, **kwargs):\n'
            '    with open(path) as f:\n'
            '        return f.read()\n'
        ),
        "note": "User-registered handlers override built-in ones for the same extension.",
    }
