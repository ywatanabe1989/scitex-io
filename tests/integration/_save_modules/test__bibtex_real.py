"""Real round-trip tests for scitex_io bibtex save+load."""


from __future__ import annotations
from scitex_io._load_modules._bibtex import (
    _load_bibtex,
    _parse_bibtex_content,
    _parse_bibtex_fields,
    _parse_bibtex_fields_basic,
    _unescape_bibtex,
    load_bibtex,
)
from scitex_io._save_modules._bibtex import (
    _entry_to_bibtex,
    _escape_bibtex,
    save_bibtex,
)


# -----------------------------
# _escape_bibtex / _unescape_bibtex
# -----------------------------
def test_escape_bibtex_special_chars():
    assert _escape_bibtex("a & b") == r"a \& b"
    assert _escape_bibtex("50%") == r"50\%"
    assert _escape_bibtex("$x$") == r"\$x\$"
    assert _escape_bibtex("a#b_c") == r"a\#b\_c"


def test_unescape_bibtex_round_trip_for_simple_chars():
    out = _unescape_bibtex(r"a \& b \% c \$ \# \_")
    assert "&" in out and "%" in out and "$" in out and "#" in out and "_" in out


# -----------------------------
# _entry_to_bibtex
# -----------------------------
def test_entry_to_bibtex_basic():
    entry = {
        "entry_type": "article",
        "key": "doe2020",
        "fields": {"title": "Hello", "year": "2020", "author": "Doe, J."},
    }
    out = _entry_to_bibtex(entry)
    assert out.startswith("@article{doe2020,")
    assert "title = {Hello}" in out
    assert out.rstrip().endswith("}")


def test_entry_to_bibtex_default_type_and_key():
    out = _entry_to_bibtex({"fields": {"a": "1"}})
    assert out.startswith("@misc{unknown,")


def test_entry_to_bibtex_escapes_special_chars():
    e = {
        "entry_type": "misc",
        "key": "k",
        "fields": {"title": "Lions & Tigers $50%"},
    }
    out = _entry_to_bibtex(e)
    assert r"\&" in out and r"\%" in out and r"\$" in out


# -----------------------------
# save_bibtex
# -----------------------------
def test_save_bibtex_single_entry_round_trip(tmp_path):
    p = str(tmp_path / "a.bib")
    entry = {
        "entry_type": "article",
        "key": "smith2021",
        "fields": {"title": "A Study", "year": "2021", "author": "Smith"},
    }
    save_bibtex(entry, p)
    entries = _load_bibtex(p)
    assert len(entries) == 1
    assert entries[0]["entry_type"] == "article"
    assert entries[0]["key"] == "smith2021"
    assert entries[0]["fields"]["title"] == "A Study"
    assert entries[0]["fields"]["year"] == "2021"


def test_save_bibtex_list_of_entries(tmp_path):
    p = str(tmp_path / "b.bib")
    entries_in = [
        {"entry_type": "article", "key": "a1", "fields": {"title": "T1"}},
        {"entry_type": "book", "key": "b1", "fields": {"title": "T2"}},
    ]
    save_bibtex(entries_in, p)
    entries_out = _load_bibtex(p)
    assert len(entries_out) == 2
    keys = [e["key"] for e in entries_out]
    assert "a1" in keys and "b1" in keys


def test_save_bibtex_no_header(tmp_path):
    p = str(tmp_path / "c.bib")
    save_bibtex(
        {"entry_type": "misc", "key": "k", "fields": {"title": "X"}},
        p,
        add_header=False,
    )
    with open(p) as f:
        text = f.read()
    assert not text.lstrip().startswith("%")


def test_save_bibtex_append_mode(tmp_path):
    p = str(tmp_path / "d.bib")
    save_bibtex({"entry_type": "misc", "key": "k1", "fields": {"t": "x"}}, p)
    save_bibtex(
        {"entry_type": "misc", "key": "k2", "fields": {"t": "y"}},
        p,
        append=True,
    )
    entries = _load_bibtex(p)
    keys = [e["key"] for e in entries]
    assert "k1" in keys and "k2" in keys


# -----------------------------
# _load_bibtex / parse helpers
# -----------------------------
def test_load_bibtex_basic_mode(tmp_path):
    p = tmp_path / "e.bib"
    p.write_text("@article{x1,\n  title = {Hello},\n  year = {2020}\n}\n")
    entries = _load_bibtex(str(p), parse_mode="basic")
    assert len(entries) == 1
    assert entries[0]["fields"]["title"] == "Hello"
    assert entries[0]["fields"]["year"] == "2020"


def test_load_bibtex_quoted_value():
    content = '@misc{k,\n  title = "Quoted Value",\n  year = "1999"\n}\n'
    entries = _parse_bibtex_content(content, "full")
    assert entries[0]["fields"]["title"] == "Quoted Value"


def test_load_bibtex_full_uppercase_type():
    content = "@ARTICLE{k,\n  title = {Up},\n  year = {2000}\n}\n"
    entries = _parse_bibtex_content(content, "full")
    assert entries[0]["entry_type"] == "article"


def test_load_bibtex_missing_file_raises(tmp_path):
    import pytest

    p = tmp_path / "missing.bib"
    with pytest.raises(ValueError):
        _load_bibtex(str(p))


def test_load_bibtex_convenience_alias(tmp_path):
    p = tmp_path / "f.bib"
    p.write_text("@misc{k,\n  title = {T}\n}\n")
    out = load_bibtex(str(p))
    assert out[0]["key"] == "k"


def test_parse_fields_basic_handles_quoted_and_braced():
    fields = _parse_bibtex_fields_basic('  title = {Hello},\n  year = "2020"\n')
    assert fields["title"] == "Hello"
    assert fields["year"] == "2020"


def test_parse_fields_full_unescapes_special_chars():
    body = "  title = {a \\& b}\n"
    fields = _parse_bibtex_fields(body)
    assert "&" in fields["title"]


# -----------------------------
# Paper / PaperCollection passthrough
# -----------------------------
class _FakePaper:
    """Mimic scitex.scholar.Paper enough to exercise the save passthrough."""

    def _to_bibtex(self, include_enriched=True):
        return "@article{x, title={T}}"


class _FakePaperCollection:
    def __init__(self):
        self._papers = [_FakePaper(), _FakePaper()]

    def _to_bibtex(self, include_enriched=True):
        return "@article{a, title={A}}\n@article{b, title={B}}\n"


def test_save_bibtex_paper_passthrough(tmp_path):
    p = _FakePaper()
    # Force class name match.
    p.__class__.__name__ = "Paper"
    out = tmp_path / "p.bib"
    save_bibtex(p, str(out))
    text = out.read_text()
    assert "@article" in text and "T" in text
    # Header should mention "BibTeX entry"
    assert "BibTeX entry" in text


def test_save_bibtex_paper_collection_passthrough(tmp_path):
    coll = _FakePaperCollection()
    coll.__class__.__name__ = "PaperCollection"
    out = tmp_path / "pc.bib"
    save_bibtex(coll, str(out))
    text = out.read_text()
    assert "@article{a" in text and "@article{b" in text
    # Header should mention "BibTeX bibliography"
    assert "BibTeX bibliography" in text
