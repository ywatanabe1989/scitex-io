#!/usr/bin/env python3
"""Tests for embed_metadata_jpeg + embed_metadata_pdf round-trip."""

import json

import pytest

PIL = pytest.importorskip("PIL")
piexif = pytest.importorskip("piexif")
pypdf = pytest.importorskip("pypdf")

from scitex_io._metadata_modules.embed_metadata_jpeg import embed_metadata_jpeg
from scitex_io._metadata_modules.embed_metadata_pdf import embed_metadata_pdf


def _make_jpeg(path, size=(10, 10), mode="RGB"):
    img = PIL.Image.new(mode, size, color=(128, 64, 32) if mode == "RGB" else 128)
    img.save(str(path), "JPEG", quality=95)
    return path


def test_embed_jpeg_round_trip(tmp_path):
    p = _make_jpeg(tmp_path / "a.jpg")
    payload = json.dumps({"k": "v", "n": 42})
    embed_metadata_jpeg(str(p), payload)
    exif = piexif.load(str(p))
    desc = exif["0th"][piexif.ImageIFD.ImageDescription].decode("utf-8")
    assert desc == payload


def test_embed_jpeg_rgba_converted(tmp_path):
    p = tmp_path / "rgba.jpg"
    img = PIL.Image.new("RGBA", (8, 8), (10, 20, 30, 200))
    img.save(str(p), "JPEG", quality=90)
    img2 = PIL.Image.new("RGBA", (8, 8), (10, 20, 30, 200))
    img2.save(str(p))  # actually save the rgba version
    embed_metadata_jpeg(str(p), json.dumps({"mode": "rgba"}))
    out = PIL.Image.open(str(p))
    assert out.mode == "RGB"


def test_embed_jpeg_palette_mode(tmp_path):
    p = tmp_path / "pal.jpg"
    img = PIL.Image.new("P", (8, 8), 5)
    img.save(str(p))
    embed_metadata_jpeg(str(p), json.dumps({"mode": "p"}))
    out = PIL.Image.open(str(p))
    assert out.mode == "RGB"


def test_embed_jpeg_la_mode(tmp_path):
    p = tmp_path / "la.jpg"
    img = PIL.Image.new("LA", (8, 8), (128, 200))
    img.save(str(p))
    embed_metadata_jpeg(str(p), json.dumps({"mode": "la"}))
    out = PIL.Image.open(str(p))
    assert out.mode == "RGB"


def test_embed_jpeg_preserves_other_exif(tmp_path):
    p = _make_jpeg(tmp_path / "b.jpg")
    # Pre-populate a non-ImageDescription EXIF field.
    exif_dict = {
        "0th": {},
        "Exif": {piexif.ExifIFD.UserComment: b"prior"},
        "GPS": {},
        "1st": {},
    }
    img = PIL.Image.open(str(p))
    img.save(str(p), "JPEG", quality=95, exif=piexif.dump(exif_dict))
    embed_metadata_jpeg(str(p), json.dumps({"k": "v"}))
    after = piexif.load(str(p))
    assert after["Exif"][piexif.ExifIFD.UserComment] == b"prior"


def test_embed_pdf_round_trip(tmp_path):
    # Build a 1-page PDF via pypdf
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    p = tmp_path / "a.pdf"
    with open(p, "wb") as f:
        writer.write(f)

    payload = json.dumps({"hello": "world"})
    embed_metadata_pdf(str(p), payload, metadata={"title": "T", "author": "A"})

    reader = pypdf.PdfReader(str(p))
    assert reader.metadata["/Title"] == "T"
    assert reader.metadata["/Author"] == "A"
    assert reader.metadata["/Subject"] == payload
    assert reader.metadata["/Creator"] == "SciTeX"


def test_embed_pdf_empty_metadata_keys(tmp_path):
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    p = tmp_path / "b.pdf"
    with open(p, "wb") as f:
        writer.write(f)
    embed_metadata_pdf(str(p), "{}", metadata={})
    reader = pypdf.PdfReader(str(p))
    assert reader.metadata["/Title"] == ""
    assert reader.metadata["/Author"] == ""
