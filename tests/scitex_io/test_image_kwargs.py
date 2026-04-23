"""Regression tests for scitex-io#20 — savefig kwargs forwarding + metadata sanitization."""

from __future__ import annotations

import matplotlib
import pytest

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

import scitex_io  # noqa: E402

try:
    from PIL import Image
except ImportError:
    Image = None


@pytest.fixture
def fig(tmp_path):
    f, ax = plt.subplots()
    ax.plot([1, 2, 3])
    yield f
    plt.close(f)


class TestSavefigKwargForwarding:
    """Issue #20 part 1: facecolor/dpi/bbox_inches forwarded to matplotlib savefig."""

    @pytest.mark.skipif(Image is None, reason="PIL not available")
    def test_facecolor_applied(self, fig, tmp_path):
        out = tmp_path / "red.png"
        scitex_io.save(fig, str(out), facecolor="red", symlink_from_cwd=False)
        assert out.exists()
        img = Image.open(out).convert("RGB")
        # Corner should be red after facecolor override
        assert img.getpixel((0, 0)) == (255, 0, 0), (
            f"expected red corner, got {img.getpixel((0, 0))}"
        )

    def test_dpi_applied(self, fig, tmp_path):
        out_lo = tmp_path / "lo.png"
        out_hi = tmp_path / "hi.png"
        scitex_io.save(fig, str(out_lo), dpi=50, symlink_from_cwd=False)
        scitex_io.save(fig, str(out_hi), dpi=300, symlink_from_cwd=False)
        assert out_hi.stat().st_size > out_lo.stat().st_size


class TestMetadataSanitization:
    """Issue #20 part 2: nested-dict metadata must not crash matplotlib savefig."""

    def test_nested_metadata_does_not_crash(self, fig, tmp_path):
        out = tmp_path / "nested.png"
        # Before the fix, the nested-dict value would raise
        # 'dict' object has no attribute 'encode' inside matplotlib.
        scitex_io.save(
            fig,
            str(out),
            metadata={"Title": "ok", "bad": {"nested": "dict"}},
            symlink_from_cwd=False,
        )
        assert out.exists()


# EOF
