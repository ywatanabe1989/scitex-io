#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 14:52:34 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_save_modules/_save_image.py
# ----------------------------------------
import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import io as _io

try:
    import plotly
except ImportError:
    plotly = None

try:
    from PIL import Image
except ImportError:
    Image = None


def _sanitize_mpl_savefig_kwargs(kwargs: dict) -> dict:
    """Filter kwargs so they are safe to forward to `Figure.savefig(...)`.

    matplotlib accepts a narrow kwarg set; passing extras raises.
    Also: `metadata=` must be a flat `dict[str, str]` — matplotlib calls
    ``.encode()`` on each value when writing PNG chunk headers. scitex's
    auto-collected nested-dict metadata crashes with
    ``'dict' object has no attribute 'encode'``. Drop the key if nested.
    """
    allowed = {
        "dpi",
        "facecolor",
        "edgecolor",
        "orientation",
        "format",
        "transparent",
        "bbox_inches",
        "pad_inches",
        "metadata",
        "bbox_extra_artists",
        "backend",
        "pil_kwargs",
    }
    out = {k: v for k, v in kwargs.items() if k in allowed}
    md = out.get("metadata")
    if isinstance(md, dict) and any(
        not isinstance(v, (str, type(None))) for v in md.values()
    ):
        # Flatten one level or drop — matplotlib only accepts flat str values.
        out["metadata"] = {
            k: v for k, v in md.items() if isinstance(v, (str, type(None)))
        }
    return out


def save_image(obj, spath, **kwargs):
    mpl_kwargs = _sanitize_mpl_savefig_kwargs(kwargs)

    # png
    if spath.endswith(".png"):
        # plotly
        if isinstance(obj, plotly.graph_objs.Figure):
            obj.write_image(file=spath, format="png")
        # PIL image
        elif isinstance(obj, Image.Image):
            obj.save(spath)
        # matplotlib
        else:
            try:
                obj.savefig(spath, **mpl_kwargs)
            except AttributeError:
                obj.figure.savefig(spath, **mpl_kwargs)
        del obj

    # tiff
    elif spath.endswith(".tiff") or spath.endswith(".tif"):
        # PIL image
        if isinstance(obj, Image.Image):
            obj.save(spath)
        # matplotlib
        else:
            try:
                obj.savefig(spath, format="tiff", **{**{"dpi": 300}, **mpl_kwargs})
            except AttributeError:
                obj.figure.savefig(
                    spath, format="tiff", **{**{"dpi": 300}, **mpl_kwargs}
                )

        del obj

    # jpeg
    elif spath.endswith(".jpeg") or spath.endswith(".jpg"):
        buf = _io.BytesIO()

        # plotly
        if isinstance(obj, plotly.graph_objs.Figure):
            obj.write_image(buf, format="png")
            buf.seek(0)
            img = Image.open(buf)
            img.convert("RGB").save(spath, "JPEG")
            buf.close()

        # PIL image
        elif isinstance(obj, Image.Image):
            obj.save(spath)

        # matplotlib
        else:
            try:
                obj.savefig(buf, format="png")
            except:
                obj.figure.savefig(buf, format="png")

            buf.seek(0)
            img = Image.open(buf)
            img.convert("RGB").save(spath, "JPEG")
            buf.close()
        del obj

    # GIF
    elif spath.endswith(".gif"):
        # PIL image
        if isinstance(obj, Image.Image):
            obj.save(spath, save_all=True)
        # plotly - convert via PNG first
        elif isinstance(obj, plotly.graph_objs.Figure):
            buf = _io.BytesIO()
            obj.write_image(buf, format="png")
            buf.seek(0)
            img = Image.open(buf)
            img.save(spath, "GIF")
            buf.close()
        # matplotlib
        else:
            buf = _io.BytesIO()
            try:
                obj.savefig(buf, format="png")
            except:
                obj.figure.savefig(buf, format="png")
            buf.seek(0)
            img = Image.open(buf)
            img.save(spath, "GIF")
            buf.close()
        del obj

    # SVG
    elif spath.endswith(".svg"):
        # Plotly
        if isinstance(obj, plotly.graph_objs.Figure):
            obj.write_image(file=spath, format="svg")
        # Matplotlib
        else:
            try:
                obj.savefig(spath, format="svg", **mpl_kwargs)
            except AttributeError:
                obj.figure.savefig(spath, format="svg", **mpl_kwargs)
        del obj

    # PDF
    elif spath.endswith(".pdf"):
        # Plotly
        if isinstance(obj, plotly.graph_objs.Figure):
            obj.write_image(file=spath, format="pdf")
        # PIL Image - convert to PDF
        elif isinstance(obj, Image.Image):
            # Convert RGBA to RGB if needed
            if obj.mode == "RGBA":
                rgb_img = Image.new("RGB", obj.size, (255, 255, 255))
                rgb_img.paste(obj, mask=obj.split()[3])
                rgb_img.save(spath, "PDF")
            else:
                obj.save(spath, "PDF")
        # Matplotlib
        else:
            try:
                obj.savefig(spath, format="pdf", **mpl_kwargs)
            except AttributeError:
                obj.figure.savefig(spath, format="pdf", **mpl_kwargs)
        del obj


# EOF
