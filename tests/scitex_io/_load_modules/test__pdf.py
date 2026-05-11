#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real-PDF tests for the PDF load pipeline.

from __future__ import annotations
We use real PDFs (built with matplotlib + pypdf) and avoid mocks so that
the actual source code paths in ``_pdf``, ``_pdf_text_extractors`` and
``_pdf_content_extractors`` are exercised end-to-end.

Note: fitz (PyMuPDF) and pdfplumber are intentionally not installed in
this venv. The pypdf-backed paths are the ones meant to be reachable
here. We do NOT use ``pytest.importorskip`` to dodge code paths.
"""


import os
from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pypdf import PdfReader, PdfWriter

from scitex_io._load_modules._pdf import _load_pdf, load_pdf


# ---------------------------------------------------------------------------
# Helpers: real PDF builders
# ---------------------------------------------------------------------------
def _mk_text_pdf(path: Path, pages_text):
    """Render ``pages_text`` (list of str) into a multi-page PDF using mpl."""
    from matplotlib.backends.backend_pdf import PdfPages

    with PdfPages(str(path)) as pdf:
        for txt in pages_text:
            fig, ax = plt.subplots()
            ax.set_axis_off()
            ax.text(0.05, 0.5, txt, fontsize=10, family="monospace")
            pdf.savefig(fig)
            plt.close(fig)
    return path


def _mk_encrypted_pdf(path: Path, body_path: Path):
    r = PdfReader(str(body_path))
    w = PdfWriter()
    for p in r.pages:
        w.add_page(p)
    w.encrypt("password123")
    with open(path, "wb") as f:
        w.write(f)
    return path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def single_page_pdf(tmp_path):
    p = tmp_path / "single.pdf"
    _mk_text_pdf(p, ["Hello World"])
    return p


@pytest.fixture
def scientific_pdf(tmp_path):
    """Multi-page PDF whose lines include IMRaD-style section headers."""
    p = tmp_path / "paper.pdf"
    pages = [
        "Frontpage content title\nauthors\n",
        "abstract\nThis is the abstract body.\n",
        "introduction\nIntro body sentence.\n",
        "methods\nMethod description here.\n",
        "results\nWe observed results.\nreferences\nSmith 2020.",
    ]
    _mk_text_pdf(p, pages)
    return p


@pytest.fixture
def empty_pdf(tmp_path):
    p = tmp_path / "empty.pdf"
    w = PdfWriter()
    w.add_blank_page(width=72, height=72)
    with open(p, "wb") as f:
        w.write(f)
    return p


@pytest.fixture
def encrypted_pdf(tmp_path, single_page_pdf):
    p = tmp_path / "enc.pdf"
    _mk_encrypted_pdf(p, single_page_pdf)
    return p


@pytest.fixture
def malformed_pdf(tmp_path):
    p = tmp_path / "broken.pdf"
    p.write_bytes(b"%PDF-1.4\nthis is not a real pdf body\n%%EOF\n")
    return p


# ---------------------------------------------------------------------------
# load_pdf alias / public entry
# ---------------------------------------------------------------------------
class TestLoadPdfAlias:
    def test_alias_dispatches_to_load_pdf(self, single_page_pdf):
        out = load_pdf(str(single_page_pdf), mode="text", backend="pypdf2")
        assert isinstance(out, str)
        assert "Hello" in out


# ---------------------------------------------------------------------------
# _load_pdf: dispatch + validation
# ---------------------------------------------------------------------------
class TestLoadPdfDispatch:
    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            _load_pdf(str(tmp_path / "missing.pdf"))

    def test_invalid_mode_raises(self, single_page_pdf):
        with pytest.raises(ValueError, match="Unknown extraction mode"):
            _load_pdf(str(single_page_pdf), mode="bogus", backend="pypdf2")

    def test_mode_text(self, single_page_pdf):
        out = _load_pdf(str(single_page_pdf), mode="text", backend="pypdf2")
        assert isinstance(out, str) and "Hello" in out

    def test_mode_sections(self, scientific_pdf):
        out = _load_pdf(str(scientific_pdf), mode="sections", backend="pypdf2")
        assert isinstance(out, dict)
        # At least frontpage must always exist; if section headers were on
        # their own line at extraction-time, we should also see them.
        assert "frontpage" in out

    def test_mode_metadata(self, single_page_pdf):
        out = _load_pdf(str(single_page_pdf), mode="metadata", backend="pypdf2")
        assert isinstance(out, dict)
        assert out["file_name"] == "single.pdf"
        assert out["pages"] == 1
        assert "md5_hash" in out and len(out["md5_hash"]) == 32
        assert out["backend"] == "pypdf2"

    def test_mode_pages(self, scientific_pdf):
        out = _load_pdf(str(scientific_pdf), mode="pages", backend="pypdf2")
        assert isinstance(out, list)
        assert len(out) == 5
        for i, p in enumerate(out):
            assert p["page_number"] == i + 1
            assert "text" in p and "char_count" in p and "word_count" in p

    def test_mode_full_pypdf2(self, scientific_pdf):
        out = _load_pdf(str(scientific_pdf), mode="full", backend="pypdf2")
        # DotDict allows dict-style access
        assert out["filename"] == "paper.pdf"
        assert out["backend"] == "pypdf2"
        assert "full_text" in out
        assert "pages" in out and len(out["pages"]) == 5
        assert "stats" in out
        stats = out["stats"]
        assert stats["total_pages"] == 5
        assert stats["avg_words_per_page"] >= 0

    def test_mode_scientific(self, scientific_pdf):
        out = _load_pdf(str(scientific_pdf), mode="scientific", backend="pypdf2")
        assert out["extraction_mode"] == "scientific"
        assert "text" in out and "sections" in out and "metadata" in out
        # Tables/images branches must populate empty results since
        # pdfplumber & fitz are not installed.
        assert out["tables"] == {}
        assert out["images"] == []
        assert "stats" in out

    def test_mode_tables(self, single_page_pdf):
        out = _load_pdf(str(single_page_pdf), mode="tables")
        assert isinstance(out, dict)

    def test_mode_images(self, single_page_pdf, tmp_path):
        out = _load_pdf(
            str(single_page_pdf),
            mode="images",
            output_dir=str(tmp_path / "imgs"),
        )
        assert isinstance(out, list)

    def test_mode_tables_no_pdfplumber_raises(self, single_page_pdf, monkeypatch):
        from scitex_io._load_modules import _pdf_content_extractors as ce

        monkeypatch.setattr(ce, "PDFPLUMBER_AVAILABLE", False)
        with pytest.raises(ImportError, match="pdfplumber"):
            _load_pdf(str(single_page_pdf), mode="tables")

    def test_mode_images_no_fitz_raises(self, single_page_pdf, monkeypatch):
        from scitex_io._load_modules import _pdf_content_extractors as ce

        monkeypatch.setattr(ce, "FITZ_AVAILABLE", False)
        with pytest.raises(ImportError, match="PyMuPDF"):
            _load_pdf(str(single_page_pdf), mode="images")

    def test_mode_full_with_fitz_extract_images(self, scientific_pdf, tmp_path):
        out = _load_pdf(
            str(scientific_pdf),
            mode="full",
            backend="fitz",
            extract_images=True,
            output_dir=str(tmp_path / "fimg"),
        )
        assert "full_text" in out
        assert "images" in out

    def test_full_extract_images_error_branch(
        self, scientific_pdf, tmp_path, monkeypatch
    ):
        # Make _extract_images raise to exercise the inner except-clause.
        from scitex_io._load_modules import _pdf as pmod

        def boom(*a, **k):
            raise RuntimeError("forced")

        monkeypatch.setattr(pmod, "_extract_images", boom)
        out = _load_pdf(
            str(scientific_pdf),
            mode="full",
            backend="fitz",
            extract_images=True,
            output_dir=str(tmp_path / "fimg2"),
        )
        # The inner except in _extract_full assigns result["images"] = []
        assert out.get("images") == []

    def test_full_tables_error_branch(self, scientific_pdf, monkeypatch):
        from scitex_io._load_modules import _pdf as pmod

        def boom(*a, **k):
            raise RuntimeError("forced")

        monkeypatch.setattr(pmod, "_extract_tables", boom)
        out = _load_pdf(str(scientific_pdf), mode="full", backend="fitz")
        assert out.get("tables") == {}

    def test_scientific_tables_error_branch(self, scientific_pdf, monkeypatch):
        from scitex_io._load_modules import _pdf as pmod

        def boom(*a, **k):
            raise RuntimeError("forced")

        monkeypatch.setattr(pmod, "_extract_tables", boom)
        out = _load_pdf(str(scientific_pdf), mode="scientific")
        assert out["tables"] == {}

    def test_scientific_images_error_branch(self, scientific_pdf, monkeypatch):
        from scitex_io._load_modules import _pdf as pmod

        def boom(*a, **k):
            raise RuntimeError("forced")

        monkeypatch.setattr(pmod, "_extract_images", boom)
        out = _load_pdf(str(scientific_pdf), mode="scientific")
        assert out["images"] == []

    def test_scientific_tables_unavailable_branch(self, scientific_pdf, monkeypatch):
        from scitex_io._load_modules import _pdf as pmod

        monkeypatch.setattr(pmod, "PDFPLUMBER_AVAILABLE", False)
        out = _load_pdf(str(scientific_pdf), mode="scientific")
        assert out["tables"] == {}

    def test_scientific_images_unavailable_branch(self, scientific_pdf, monkeypatch):
        from scitex_io._load_modules import _pdf as pmod

        monkeypatch.setattr(pmod, "FITZ_AVAILABLE", False)
        out = _load_pdf(str(scientific_pdf), mode="scientific")
        assert out["images"] == []

    def test_kwargs_mode_override(self, single_page_pdf):
        """Passing mode as a kwarg also works."""
        out = _load_pdf(str(single_page_pdf), backend="pypdf2", mode="text")
        assert isinstance(out, str)

    def test_output_dir_autocreated_for_full(self, scientific_pdf):
        out = _load_pdf(str(scientific_pdf), mode="full", backend="pypdf2")
        # No explicit error and we have results
        assert "full_text" in out

    def test_explicit_output_dir(self, scientific_pdf, tmp_path):
        odir = tmp_path / "imgs"
        out = _load_pdf(
            str(scientific_pdf),
            mode="full",
            backend="pypdf2",
            output_dir=str(odir),
        )
        assert "full_text" in out


# ---------------------------------------------------------------------------
# Encrypted / malformed PDFs propagate errors out of _load_pdf via the
# extractor exception handling.
# ---------------------------------------------------------------------------
class TestErrorPaths:
    def test_encrypted_pdf_text_extraction_raises(self, encrypted_pdf):
        from pypdf.errors import FileNotDecryptedError

        with pytest.raises(FileNotDecryptedError):
            _load_pdf(str(encrypted_pdf), mode="text", backend="pypdf2")

    def test_malformed_pdf_text_extraction_raises(self, malformed_pdf):
        with pytest.raises(Exception):
            _load_pdf(str(malformed_pdf), mode="text", backend="pypdf2")

    def test_scientific_catches_error_branch(self, malformed_pdf):
        # Scientific mode swallows the inner error and writes it to result["error"].
        out = _load_pdf(str(malformed_pdf), mode="scientific", backend="pypdf2")
        assert "error" in out

    def test_full_catches_error_branch(self, malformed_pdf):
        out = _load_pdf(str(malformed_pdf), mode="full", backend="pypdf2")
        assert "error" in out


# ---------------------------------------------------------------------------
# Docstring / signature sanity (cheap)
# ---------------------------------------------------------------------------
class TestSignature:
    def test_has_docstring(self):
        assert _load_pdf.__doc__ and "PDF" in _load_pdf.__doc__

    def test_signature_params(self):
        import inspect

        sig = inspect.signature(_load_pdf)
        assert "lpath" in sig.parameters
        assert sig.parameters["mode"].default == "full"


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
