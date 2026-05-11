#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real-PDF tests for ``_pdf_text_extractors``.

from __future__ import annotations
We don't mock pypdf. We build real PDFs and verify the extractor output.
"""


from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pypdf import PdfReader, PdfWriter

from scitex_io._load_modules import _pdf_text_extractors as tx
from scitex_io._load_modules._pdf_text_extractors import (
    _extract_pages,
    _extract_text,
    _extract_text_fitz,
    _extract_text_pdfplumber,
    _extract_text_pypdf2,
)


# ---------------------------------------------------------------------------
def _mk_text_pdf(path: Path, pages_text):
    from matplotlib.backends.backend_pdf import PdfPages

    with PdfPages(str(path)) as pdf:
        for txt in pages_text:
            fig, ax = plt.subplots()
            ax.set_axis_off()
            ax.text(0.05, 0.5, txt, fontsize=10, family="monospace")
            pdf.savefig(fig)
            plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def pdf_simple(tmp_path):
    p = tmp_path / "s.pdf"
    _mk_text_pdf(p, ["Hello PDF World"])
    return str(p)


@pytest.fixture
def pdf_multi(tmp_path):
    p = tmp_path / "m.pdf"
    _mk_text_pdf(p, ["Alpha page one", "Beta page two", "Gamma page three"])
    return str(p)


@pytest.fixture
def pdf_blank_pages(tmp_path):
    """Mix of blank and text pages — tests the ``if text.strip()`` branch."""
    p = tmp_path / "blanks.pdf"
    w = PdfWriter()
    w.add_blank_page(width=200, height=200)
    with open(p, "wb") as f:
        w.write(f)
    return str(p)


@pytest.fixture
def pdf_encrypted(tmp_path, pdf_simple):
    src = PdfReader(pdf_simple)
    w = PdfWriter()
    for pg in src.pages:
        w.add_page(pg)
    w.encrypt("pw")
    out = tmp_path / "enc.pdf"
    with open(out, "wb") as f:
        w.write(f)
    return str(out)


# ---------------------------------------------------------------------------
# _extract_text_pypdf2
# ---------------------------------------------------------------------------
class TestExtractTextPypdf2:
    def test_extract_with_clean(self, pdf_simple):
        out = _extract_text_pypdf2(pdf_simple, clean=True)
        assert isinstance(out, str)
        assert "Hello" in out and "PDF" in out

    def test_extract_no_clean(self, pdf_simple):
        out = _extract_text_pypdf2(pdf_simple, clean=False)
        assert "Hello" in out

    def test_multi_page_joined(self, pdf_multi):
        out = _extract_text_pypdf2(pdf_multi, clean=True)
        assert "Alpha" in out and "Beta" in out and "Gamma" in out

    def test_blank_pdf_returns_empty(self, pdf_blank_pages):
        out = _extract_text_pypdf2(pdf_blank_pages, clean=True)
        assert out == ""

    def test_encrypted_raises(self, pdf_encrypted):
        with pytest.raises(Exception):
            _extract_text_pypdf2(pdf_encrypted, clean=False)

    def test_unavailable_raises(self, pdf_simple, monkeypatch):
        # Force the availability flag to False to hit the early ImportError.
        monkeypatch.setattr(tx, "PYPDF2_AVAILABLE", False)
        with pytest.raises(ImportError, match="PyPDF2 not available"):
            _extract_text_pypdf2(pdf_simple, clean=False)


# ---------------------------------------------------------------------------
# _extract_text_fitz — PyMuPDF backend (real)
# ---------------------------------------------------------------------------
class TestExtractTextFitz:
    def test_fitz_real_extraction(self, pdf_simple):
        assert tx.FITZ_AVAILABLE and tx.fitz is not None
        out = _extract_text_fitz(pdf_simple, clean=True)
        assert "Hello" in out

    def test_fitz_no_clean(self, pdf_multi):
        out = _extract_text_fitz(pdf_multi, clean=False)
        for piece in ("Alpha", "Beta", "Gamma"):
            assert piece in out

    def test_fitz_unavailable_raises(self, pdf_simple, monkeypatch):
        # Force the availability flag to False (and clear ``fitz``) to hit
        # the explicit ImportError branch.
        monkeypatch.setattr(tx, "FITZ_AVAILABLE", False)
        monkeypatch.setattr(tx, "fitz", None)
        with pytest.raises(ImportError, match="PyMuPDF"):
            _extract_text_fitz(pdf_simple, clean=False)

    def test_fitz_error_path(self, tmp_path):
        # Garbage file → fitz.open raises → caught and re-raised by us.
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"not a pdf at all")
        with pytest.raises(Exception):
            _extract_text_fitz(str(bad), clean=False)


# ---------------------------------------------------------------------------
# _extract_text_pdfplumber — pdfplumber backend (real)
# ---------------------------------------------------------------------------
class TestExtractTextPdfplumber:
    def test_pdfplumber_real_extraction(self, pdf_simple):
        assert tx.PDFPLUMBER_AVAILABLE
        out = _extract_text_pdfplumber(pdf_simple, clean=True)
        assert "Hello" in out

    def test_pdfplumber_no_clean(self, pdf_multi):
        out = _extract_text_pdfplumber(pdf_multi, clean=False)
        for piece in ("Alpha", "Beta", "Gamma"):
            assert piece in out

    def test_pdfplumber_unavailable_raises(self, pdf_simple, monkeypatch):
        monkeypatch.setattr(tx, "PDFPLUMBER_AVAILABLE", False)
        with pytest.raises(ImportError, match="pdfplumber"):
            _extract_text_pdfplumber(pdf_simple, clean=False)

    def test_pdfplumber_error_path(self, tmp_path):
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"not a pdf at all")
        with pytest.raises(Exception):
            _extract_text_pdfplumber(str(bad), clean=False)


# ---------------------------------------------------------------------------
# Unified dispatcher
# ---------------------------------------------------------------------------
class TestExtractText:
    def test_dispatch_pypdf2(self, pdf_simple):
        out = _extract_text(pdf_simple, "pypdf2", clean=True)
        assert "Hello" in out

    def test_dispatch_unknown_falls_back_to_pypdf2(self, pdf_simple):
        # Source: anything other than 'fitz'/'pdfplumber' uses pypdf2.
        out = _extract_text(pdf_simple, "anything_else", clean=True)
        assert "Hello" in out

    def test_dispatch_fitz(self, pdf_simple):
        out = _extract_text(pdf_simple, "fitz", clean=True)
        assert "Hello" in out

    def test_dispatch_pdfplumber(self, pdf_simple):
        out = _extract_text(pdf_simple, "pdfplumber", clean=True)
        assert "Hello" in out


# ---------------------------------------------------------------------------
# _extract_pages
# ---------------------------------------------------------------------------
class TestExtractPages:
    def test_pypdf2_multi_page(self, pdf_multi):
        pages = _extract_pages(pdf_multi, "pypdf2", clean=True)
        assert len(pages) == 3
        assert pages[0]["page_number"] == 1
        assert pages[1]["page_number"] == 2
        assert pages[2]["page_number"] == 3
        for p in pages:
            assert isinstance(p["text"], str)
            assert p["char_count"] == len(p["text"])
            assert p["word_count"] == len(p["text"].split())

    def test_pypdf2_no_clean(self, pdf_simple):
        pages = _extract_pages(pdf_simple, "pypdf2", clean=False)
        assert len(pages) == 1
        assert "Hello" in pages[0]["text"]

    def test_unknown_backend_returns_empty(self, pdf_simple):
        # Source: only fitz/pdfplumber/pypdf2 branches populate the list.
        # Anything else (or backends whose lib is missing) returns [].
        pages = _extract_pages(pdf_simple, "no_such_backend", clean=False)
        assert pages == []

    def test_fitz_backend_pages(self, pdf_multi):
        pages = _extract_pages(pdf_multi, "fitz", clean=True)
        assert len(pages) == 3
        for i, p in enumerate(pages):
            assert p["page_number"] == i + 1
            assert isinstance(p["text"], str)

    def test_fitz_backend_pages_no_clean(self, pdf_simple):
        pages = _extract_pages(pdf_simple, "fitz", clean=False)
        assert len(pages) == 1
        assert "Hello" in pages[0]["text"]

    def test_pdfplumber_backend_pages(self, pdf_multi):
        pages = _extract_pages(pdf_multi, "pdfplumber", clean=True)
        assert len(pages) == 3
        for i, p in enumerate(pages):
            assert p["page_number"] == i + 1

    def test_pdfplumber_backend_pages_no_clean(self, pdf_simple):
        pages = _extract_pages(pdf_simple, "pdfplumber", clean=False)
        assert len(pages) == 1

    def test_fitz_backend_skipped_when_unavailable(self, pdf_simple, monkeypatch):
        monkeypatch.setattr(tx, "FITZ_AVAILABLE", False)
        assert _extract_pages(pdf_simple, "fitz", clean=False) == []

    def test_pdfplumber_backend_skipped_when_unavailable(self, pdf_simple, monkeypatch):
        monkeypatch.setattr(tx, "PDFPLUMBER_AVAILABLE", False)
        assert _extract_pages(pdf_simple, "pdfplumber", clean=False) == []


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])
