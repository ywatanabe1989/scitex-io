"""Regression test for scitex-io#21 — headerless CSV .str guard."""

from __future__ import annotations

import scitex_io


class TestHeaderlessCSV:
    def test_load_with_header_none(self, tmp_path):
        """#21: previously crashed with `AttributeError: Can only use .str...`
        because `.str.contains("^Unnamed")` was applied to an integer RangeIndex.
        """
        p = tmp_path / "headerless.csv"
        p.write_text("1.0\n2.0\n3.0\n")
        df = scitex_io.load(str(p), header=None)
        assert df.shape == (3, 1)
        assert list(df.columns) == [0]
        assert df.values.flatten().tolist() == [1.0, 2.0, 3.0]

    def test_load_with_header_0_still_works(self, tmp_path):
        """Default string-header path must still strip `Unnamed:` columns."""
        p = tmp_path / "with_header.csv"
        p.write_text("a,b,Unnamed: 2\n1,2,3\n4,5,6\n")
        df = scitex_io.load(str(p))
        # Unnamed: 2 should be stripped
        assert "Unnamed: 2" not in df.columns
        assert list(df.columns) == ["a", "b"]


# EOF
