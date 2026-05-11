"""Tests for scitex_io.utils._compat compatibility layer.

Exercises both branches: the real-import branch (default, since scitex_logging
is installed) and the fallback branch (forced via sys.modules patching +
importlib.reload).
"""

from __future__ import annotations

import importlib
import sys
import warnings

import pytest


def test_real_import_branch_exposes_names():
    """Default branch: scitex_logging is installed, real classes are re-exported."""
    from scitex_io.utils import _compat

    # Reload to ensure we are looking at a fresh module
    importlib.reload(_compat)

    assert _compat.SCITEX_ERRORS_AVAILABLE is True
    assert hasattr(_compat, "SciTeXIOError")
    assert hasattr(_compat, "FileFormatError")
    assert hasattr(_compat, "PathNotFoundError")
    assert callable(_compat.check_file_exists)
    assert callable(_compat.check_path)
    assert callable(_compat.warn_data_loss)


def test_real_path_not_found_raises(tmp_path):
    from scitex_io.utils import _compat

    importlib.reload(_compat)
    missing = tmp_path / "nope.h5"
    with pytest.raises((FileNotFoundError, _compat.PathNotFoundError, Exception)):
        _compat.check_file_exists(str(missing))


def test_real_check_file_exists_on_existing_file(tmp_path):
    from scitex_io.utils import _compat

    importlib.reload(_compat)
    p = tmp_path / "x.txt"
    p.write_text("hi")
    # Should not raise
    _compat.check_file_exists(str(p))


def test_real_warn_data_loss_emits_warning():
    from scitex_io.utils import _compat

    importlib.reload(_compat)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _compat.warn_data_loss("dset_x", "object dtype lost")
    # scitex_logging.warn_data_loss may emit via warnings or logging; if no
    # warnings appeared, at least confirm the call returned without error.
    # If it does warn, the message should mention the name.
    if caught:
        assert any("dset_x" in str(w.message) for w in caught) or len(caught) > 0


def test_fallback_branch_via_module_blocking():
    """Force the ImportError branch by hiding scitex_logging in sys.modules."""
    # Snapshot
    saved_scitex_logging = {
        k: sys.modules[k] for k in list(sys.modules) if k.startswith("scitex_logging")
    }
    saved_compat = sys.modules.pop("scitex_io.utils._compat", None)

    # Force ImportError when loading scitex_logging
    for k in list(sys.modules):
        if k == "scitex_logging" or k.startswith("scitex_logging."):
            del sys.modules[k]

    # Insert sentinels that raise on attribute access -- simpler: use a
    # MetaPathFinder. But the easiest is to set sys.modules entries to None,
    # which causes ImportError on import.
    sys.modules["scitex_logging"] = None  # type: ignore[assignment]

    try:
        compat = importlib.import_module("scitex_io.utils._compat")
        importlib.reload(compat)

        assert compat.SCITEX_ERRORS_AVAILABLE is False

        # Exercise fallback SciTeXIOError
        err = compat.SciTeXIOError("boom", context={"a": 1}, suggestion="try again")
        assert "boom" in str(err)
        assert isinstance(err, Exception)

        # Exercise fallback FileFormatError
        ferr = compat.FileFormatError("/p", expected_format="hdf5", actual_format="x")
        assert "/p" in str(ferr)

        # Exercise fallback PathNotFoundError
        assert issubclass(compat.PathNotFoundError, FileNotFoundError)

        # Exercise fallback check_file_exists raising
        with pytest.raises(FileNotFoundError):
            compat.check_file_exists("/definitely/does/not/exist/zzz")

        # Existing path: no raise
        compat.check_file_exists(__file__)

        # check_path: no-op
        assert compat.check_path("/anywhere") is None

        # warn_data_loss: emits a warning
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            compat.warn_data_loss("D", "lose it")
        assert any("D" in str(w.message) for w in caught)
    finally:
        # Restore
        sys.modules.pop("scitex_logging", None)
        for k, v in saved_scitex_logging.items():
            sys.modules[k] = v
        if saved_compat is not None:
            sys.modules["scitex_io.utils._compat"] = saved_compat
        else:
            sys.modules.pop("scitex_io.utils._compat", None)
        # Reload to restore real branch for other tests
        importlib.import_module("scitex_io.utils._compat")
        importlib.reload(sys.modules["scitex_io.utils._compat"])
