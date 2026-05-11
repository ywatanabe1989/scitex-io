"""Real round-trip tests for scitex_io._save_modules._hdf5.

Exercises the SWMR-enabled HDF5 save path with real h5py files in tmp_path.
"""

from __future__ import annotations

import os

import h5py
import numpy as np

from scitex_io._save_modules._hdf5 import SWMRFile, _save_dataset, _save_hdf5


# -----------------------------
# _save_hdf5: high-level round-trip
# -----------------------------
def test_save_hdf5_dict_of_arrays_round_trip(tmp_path):
    spath = str(tmp_path / "a.h5")
    obj = {
        "x": np.arange(100, dtype="float32"),
        "y": np.linspace(0, 1, 50),
    }
    _save_hdf5(obj, spath)
    assert os.path.exists(spath)
    with h5py.File(spath, "r") as f:
        np.testing.assert_array_equal(f["x"][:], obj["x"])
        np.testing.assert_allclose(f["y"][:], obj["y"])


def test_save_hdf5_non_dict_wrapped_under_data(tmp_path):
    spath = str(tmp_path / "b.h5")
    arr = np.arange(10, dtype="int32")
    _save_hdf5(arr, spath)
    with h5py.File(spath, "r") as f:
        np.testing.assert_array_equal(f["data"][:], arr)


def test_save_hdf5_with_key_creates_nested_group(tmp_path):
    spath = str(tmp_path / "c.h5")
    _save_hdf5({"arr": np.arange(5)}, spath, key="g1/g2/leaf")
    with h5py.File(spath, "r") as f:
        np.testing.assert_array_equal(f["g1/g2/leaf/arr"][:], np.arange(5))


def test_save_hdf5_key_exists_no_override_returns(tmp_path):
    spath = str(tmp_path / "d.h5")
    _save_hdf5({"arr": np.arange(5)}, spath, key="g1")
    # Without override=True the second call should be a no-op.
    _save_hdf5({"arr": np.arange(5, 10)}, spath, key="g1", override=False)
    with h5py.File(spath, "r") as f:
        np.testing.assert_array_equal(f["g1/arr"][:], np.arange(5))


def test_save_hdf5_key_override(tmp_path):
    spath = str(tmp_path / "e.h5")
    _save_hdf5({"arr": np.arange(5)}, spath, key="g1")
    _save_hdf5({"arr": np.arange(5, 10)}, spath, key="g1", override=True)
    with h5py.File(spath, "r") as f:
        np.testing.assert_array_equal(f["g1/arr"][:], np.arange(5, 10))


def test_save_hdf5_append_mode(tmp_path):
    """A second call with a different key appends to the existing file."""
    spath = str(tmp_path / "f.h5")
    _save_hdf5({"a": np.arange(3)}, spath, key="ka")
    _save_hdf5({"b": np.arange(4)}, spath, key="kb")
    with h5py.File(spath, "r") as f:
        np.testing.assert_array_equal(f["ka/a"][:], np.arange(3))
        np.testing.assert_array_equal(f["kb/b"][:], np.arange(4))


def test_save_hdf5_compression_option(tmp_path):
    spath = str(tmp_path / "g.h5")
    arr = np.zeros(2000, dtype="float64")
    _save_hdf5({"arr": arr}, spath, compression="gzip", compression_opts=1)
    with h5py.File(spath, "r") as f:
        assert f["arr"].compression == "gzip"


def test_save_hdf5_swmr_disabled(tmp_path):
    spath = str(tmp_path / "h.h5")
    _save_hdf5({"arr": np.arange(8)}, spath, swmr=False)
    with h5py.File(spath, "r") as f:
        np.testing.assert_array_equal(f["arr"][:], np.arange(8))


# -----------------------------
# _save_dataset: per-type branches
# -----------------------------
def test_save_dataset_string(tmp_path):
    spath = str(tmp_path / "i.h5")
    with h5py.File(spath, "w", libver="latest") as f:
        _save_dataset(f, "label", "hello", "gzip", 4)
    with h5py.File(spath, "r") as f:
        # h5py returns bytes by default for string datasets
        assert f["label"][()] in (b"hello", "hello")


def test_save_dataset_numpy_array_large_uses_chunks(tmp_path):
    spath = str(tmp_path / "j.h5")
    big = np.arange(2000, dtype="float32")
    with h5py.File(spath, "w", libver="latest") as f:
        _save_dataset(f, "arr", big, "gzip", 4)
    with h5py.File(spath, "r") as f:
        assert f["arr"].chunks is not None
        assert f["arr"].compression == "gzip"


def test_save_dataset_numpy_array_small_no_compression(tmp_path):
    spath = str(tmp_path / "k.h5")
    small = np.arange(10, dtype="int32")
    with h5py.File(spath, "w", libver="latest") as f:
        _save_dataset(f, "arr", small, "gzip", 4)
    with h5py.File(spath, "r") as f:
        np.testing.assert_array_equal(f["arr"][:], small)
        assert f["arr"].compression is None


def test_save_dataset_list_of_scalars(tmp_path):
    spath = str(tmp_path / "l.h5")
    with h5py.File(spath, "w", libver="latest") as f:
        _save_dataset(f, "lst", [1, 2, 3], "gzip", 4)
    with h5py.File(spath, "r") as f:
        np.testing.assert_array_equal(f["lst"][:], [1, 2, 3])


def test_save_dataset_list_of_dicts_pickled(tmp_path):
    """Object-dtype lists get pickled via np.void."""
    spath = str(tmp_path / "m.h5")
    with h5py.File(spath, "w", libver="latest") as f:
        _save_dataset(f, "obj", [{"a": 1}, {"b": 2}], "gzip", 4)
    # Simply verify it round-trips on disk and can be opened.
    with h5py.File(spath, "r") as f:
        assert "obj" in f


def test_save_dataset_scalar_int(tmp_path):
    spath = str(tmp_path / "n.h5")
    with h5py.File(spath, "w", libver="latest") as f:
        _save_dataset(f, "i", 42, "gzip", 4)
    with h5py.File(spath, "r") as f:
        assert int(f["i"][()]) == 42


def test_save_dataset_fallback_pickled_via_void(tmp_path):
    """Object that cannot be created as a dataset directly is pickled."""
    spath = str(tmp_path / "o.h5")
    # A tuple of mixed picklable objects exercises the fallback path.
    payload = (1, "two", [3, 4])
    with h5py.File(spath, "w", libver="latest") as f:
        _save_dataset(f, "weird", payload, "gzip", 4)
    with h5py.File(spath, "r") as f:
        assert "weird" in f


# -----------------------------
# SWMRFile context manager
# -----------------------------
def test_swmr_file_write_mode(tmp_path):
    p = str(tmp_path / "w.h5")
    with SWMRFile(p, mode="w") as f:
        f.create_dataset("x", data=np.arange(5))
    with h5py.File(p, "r") as f:
        np.testing.assert_array_equal(f["x"][:], np.arange(5))


def test_swmr_file_read_mode(tmp_path):
    p = str(tmp_path / "rd.h5")
    with h5py.File(p, "w", libver="latest") as f:
        f.create_dataset("x", data=np.arange(3))
    with SWMRFile(p, mode="r") as f:
        np.testing.assert_array_equal(f["x"][:], np.arange(3))


def test_swmr_file_append_creates_when_missing(tmp_path):
    """SWMRFile in 'a' mode creates the file if missing."""
    p = str(tmp_path / "anew.h5")
    with SWMRFile(p, mode="a", swmr=False) as f:
        f.create_dataset("y", data=np.arange(4))
    with h5py.File(p, "r") as f:
        np.testing.assert_array_equal(f["y"][:], np.arange(4))


def test_swmr_file_append_to_existing(tmp_path):
    p = str(tmp_path / "aex.h5")
    with h5py.File(p, "w", libver="latest") as f:
        f.create_dataset("a", data=np.arange(2))
    with SWMRFile(p, mode="a", swmr=False) as f:
        f.create_dataset("b", data=np.arange(3))
    with h5py.File(p, "r") as f:
        assert "a" in f and "b" in f


def test_swmr_file_append_swmr_enabled(tmp_path):
    """Append to a non-existing file with swmr=True (creates new SWMR file)."""
    p = str(tmp_path / "asw.h5")
    with SWMRFile(p, mode="a", swmr=True) as f:
        f.create_dataset("x", data=np.arange(3))
    with h5py.File(p, "r") as f:
        np.testing.assert_array_equal(f["x"][:], np.arange(3))


def test_save_hdf5_root_level_no_key(tmp_path):
    """key=None places everything at the root."""
    spath = str(tmp_path / "root.h5")
    _save_hdf5({"a": np.arange(3)}, spath)
    with h5py.File(spath, "r") as f:
        np.testing.assert_array_equal(f["a"][:], np.arange(3))
