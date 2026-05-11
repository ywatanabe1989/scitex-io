#!/usr/bin/env python3
"""Tests for embed_metadata_pdf."""

import json

import pytest

pypdf = pytest.importorskip("pypdf")

from scitex_io._metadata_modules.embed_metadata_pdf import embed_metadata_pdf


def test_embed_pdf_round_trip(tmp_path):
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
