#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-29 07:21:17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-io/src/scitex_io/_save.py
# ----------------------------------------
from __future__ import annotations
import os

__FILE__ = "./src/scitex_io/_save.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__


"""
1. Functionality:
   - Provides utilities for saving various data types to different file formats.
2. Input:
   - Objects to be saved (e.g., NumPy arrays, PyTorch tensors, Pandas DataFrames, etc.)
   - File path or name where the object should be saved
3. Output:
   - Saved files in various formats (e.g., CSV, NPY, PKL, JOBLIB, PNG, HTML, TIFF, MP4, YAML, JSON, HDF5, PTH, MAT, CBM)
4. Prerequisites:
   - Python 3.x
   - Required libraries: numpy, pandas, torch, matplotlib, plotly, h5py, joblib, PIL, ruamel.yaml
"""

"""Imports"""
import inspect
import os as _os
import logging
import subprocess
from pathlib import Path
from typing import Any, Union

from ._utils import clean, getsize, clean_path, color_text, readable_bytes
from ._registry import get_saver  # noqa: F401
from ._image_csv_handler import handle_image_with_csv  # noqa: F401

logger = logging.getLogger()


def sh(command, *args, **kwargs):
    """Simple shell execution."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.returncode == 0


def save(
    obj: Any,
    specified_path: Union[str, Path],
    makedirs: bool = True,
    verbose: bool = True,
    symlink_from_cwd: bool = False,
    symlink_to: Union[str, Path] = None,
    dry_run: bool = False,
    no_csv: bool = False,
    use_caller_path: bool = False,
    **kwargs,
) -> None:
    """
    Save an object to a file with the specified format.

    Parameters
    ----------
    obj : Any
        The object to be saved.
    specified_path : Union[str, Path]
        The file name or path where the object should be saved.
    makedirs : bool, optional
        If True, create the directory path if it does not exist. Default is True.
    verbose : bool, optional
        If True, print a message upon successful saving. Default is True.
    symlink_from_cwd : bool, optional
        If True, create a symlink from the current working directory. Default is False.
    symlink_to : Union[str, Path], optional
        If specified, create a symlink at this path pointing to the saved file.
    dry_run : bool, optional
        If True, simulate the saving process without writing files. Default is False.
    no_csv : bool, optional
        If True, skip CSV export for image saves. Default is False.
    use_caller_path : bool, optional
        If True, skip internal library frames for path detection. Default is False.
    **kwargs
        Additional keyword arguments to pass to the underlying save function.

    Returns
    -------
    Path or None
        Path to saved file on success, False on error.
    """
    try:
        if isinstance(specified_path, Path):
            specified_path = str(specified_path)

        ########################################
        # DO NOT MODIFY THIS SECTION
        ########################################
        spath, sfname = None, None

        # f-expression handling - safely parse f-strings
        if specified_path.startswith('f"') or specified_path.startswith("f'"):
            path_content = specified_path[2:-1]
            frame = inspect.currentframe().f_back
            try:
                import re

                variables = re.findall(r"\{([^}]+)\}", path_content)
                format_dict = {}
                for var in variables:
                    if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", var):
                        if var in frame.f_locals:
                            format_dict[var] = frame.f_locals[var]
                        elif var in frame.f_globals:
                            format_dict[var] = frame.f_globals[var]
                    else:
                        raise ValueError(f"Invalid variable name in f-string: {var}")
                specified_path = path_content.format(**format_dict)
            finally:
                del frame

        if specified_path.startswith("/"):
            spath = specified_path
        else:
            from ._utils import detect_environment, get_notebook_info_simple

            env_type = detect_environment()

            if env_type == "jupyter":
                notebook_name, notebook_dir = get_notebook_info_simple()
                if notebook_name:
                    notebook_base = _os.path.splitext(notebook_name)[0]
                    sdir = _os.path.join(
                        notebook_dir or _os.getcwd(), f"{notebook_base}_out"
                    )
                else:
                    sdir = _os.path.join(_os.getcwd(), "notebook_out")
                spath = _os.path.join(sdir, specified_path)

            elif env_type == "script":
                if use_caller_path:
                    script_path = None
                    scitex_src_path = _os.path.join(
                        _os.path.dirname(__file__), "..", ".."
                    )
                    scitex_src_path = _os.path.abspath(scitex_src_path)
                    for frame_info in inspect.stack()[1:]:
                        frame_path = _os.path.abspath(frame_info.filename)
                        if not frame_path.startswith(scitex_src_path):
                            script_path = frame_path
                            break
                    if script_path is None:
                        script_path = inspect.stack()[1].filename
                else:
                    script_path = inspect.stack()[1].filename

                sdir = clean_path(_os.path.splitext(script_path)[0] + "_out")
                spath = _os.path.join(sdir, specified_path)

            else:
                script_path = inspect.stack()[1].filename
                if (
                    ("ipython" in script_path)
                    or ("<stdin>" in script_path)
                    or env_type in ["ipython", "interactive"]
                ):
                    script_path = f"/tmp/{_os.getenv('USER')}"
                    sdir = script_path
                else:
                    sdir = _os.path.join(_os.getcwd(), "output")
                spath = _os.path.join(sdir, specified_path)

        spath_final = clean(spath)
        ########################################

        spath_cwd = _os.getcwd() + "/" + specified_path
        spath_cwd = clean(spath_cwd)

        should_skip_deletion = spath_final.endswith(".csv") or (
            (spath_final.endswith(".hdf5") or spath_final.endswith(".h5"))
            and "key" in kwargs
        )

        if not should_skip_deletion:
            for path in [spath_final, spath_cwd]:
                sh(["rm", "-f", f"{path}"], verbose=False)

        if dry_run:
            try:
                rel_path = _os.path.relpath(spath, _os.getcwd())
            except ValueError:
                rel_path = spath
            if verbose:
                print()
                logger.success(
                    color_text(f"(dry run) Saved to: ./{rel_path}", c="yellow")
                )
            return

        if makedirs:
            _os.makedirs(_os.path.dirname(spath_final), exist_ok=True)

        _save(
            obj,
            spath_final,
            verbose=verbose,
            symlink_from_cwd=symlink_from_cwd,
            symlink_to=symlink_to,
            dry_run=dry_run,
            no_csv=no_csv,
            **kwargs,
        )

        _symlink(spath, spath_cwd, symlink_from_cwd, verbose)
        _symlink_to(spath_final, symlink_to, verbose)
        return Path(spath)

    except Exception as e:
        logger.error(
            f"Error occurred while saving: {str(e)}\n"
            f"Debug: Initial script_path = {inspect.stack()[1].filename}\n"
            f"Debug: Final spath = {spath}\n"
            f"Debug: specified_path type = {type(specified_path)}\n"
            f"Debug: specified_path = {specified_path}"
        )
        return False


def _symlink(spath, spath_cwd, symlink_from_cwd, verbose):
    """Create a symbolic link from the current working directory."""
    if symlink_from_cwd and (spath != spath_cwd):
        _os.makedirs(_os.path.dirname(spath_cwd), exist_ok=True)
        sh(["rm", "-f", f"{spath_cwd}"], verbose=False)
        sh(["ln", "-sfr", f"{spath}", f"{spath_cwd}"], verbose=False)
        if verbose:
            logger.success(color_text(f"(Symlinked to: {spath_cwd})"))


def _symlink_to(spath_final, symlink_to, verbose):
    """Create a symbolic link at the specified path pointing to the saved file."""
    if symlink_to:
        if isinstance(symlink_to, Path):
            symlink_to = str(symlink_to)
        symlink_to = clean(symlink_to)
        _os.makedirs(_os.path.dirname(symlink_to), exist_ok=True)
        sh(["rm", "-f", f"{symlink_to}"], verbose=False)
        sh(["ln", "-sfr", f"{spath_final}", f"{symlink_to}"], verbose=False)
        if verbose:
            print(color_text(f"\n(Symlinked to: {symlink_to})", "yellow"))


_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".tiff", ".tif", ".svg", ".pdf"}


def _save(
    obj,
    spath,
    verbose=True,
    symlink_from_cwd=False,
    dry_run=False,
    no_csv=False,
    symlink_to=None,
    **kwargs,
):
    """Dispatch save to the appropriate handler based on file extension."""
    ext = _os.path.splitext(spath)[1].lower()

    # Special case: compound extension .pkl.gz
    if spath.endswith(".pkl.gz"):
        ext = ".pkl.gz"

    if ext in _IMAGE_EXTS:
        handle_image_with_csv(
            obj,
            spath,
            no_csv=no_csv,
            symlink_from_cwd=symlink_from_cwd,
            symlink_to=symlink_to,
            dry_run=dry_run,
            _save_fn=_save,
            _symlink_fn=_symlink,
            _symlink_to_fn=_symlink_to,
            **kwargs,
        )
    else:
        handler = get_saver(ext)
        if handler is None:
            raise ValueError(
                f"No save handler registered for '{ext}'. "
                f"Use register_saver('{ext}', your_fn) to add one."
            )
        handler(obj, spath, **kwargs)

    if verbose:
        if _os.path.exists(spath):
            file_size = readable_bytes(getsize(spath))
            try:
                rel_path = _os.path.relpath(spath, _os.getcwd())
            except ValueError:
                rel_path = spath
            print()
            logger.success(f"Saved to: ./{rel_path} ({file_size})")


# EOF
