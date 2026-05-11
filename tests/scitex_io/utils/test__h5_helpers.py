"""Tests for scitex_io.utils._h5_helpers.

Exercises real h5py + zarr code paths against real files in tmp_path.
"""

from __future__ import annotations

import warnings

import h5py
import numpy as np
import pytest
import zarr

from scitex_io.utils._h5_helpers import (
    copy_h5_attributes,
    get_zarr_compressor,
    infer_chunks,
    migrate_dataset,
    migrate_group,
    validate_migration,
)


# -----------------------------
# get_zarr_compressor
# -----------------------------
def test_get_zarr_compressor_none():
    assert get_zarr_compressor(None) is None


def test_get_zarr_compressor_passthrough_non_string():
    from numcodecs import Zstd

    z = Zstd(level=1)
    assert get_zarr_compressor(z) is z


@pytest.mark.parametrize("name", ["zstd", "lz4", "gzip", "blosc"])
def test_get_zarr_compressor_named(name):
    c = get_zarr_compressor(name)
    assert c is not None
    # All numcodecs codecs have an `encode` callable
    assert hasattr(c, "encode")


def test_get_zarr_compressor_unknown_defaults_to_zstd():
    from numcodecs import Zstd

    c = get_zarr_compressor("not-a-real-codec")
    assert isinstance(c, Zstd)


# -----------------------------
# infer_chunks
# -----------------------------
def test_infer_chunks_scalar_returns_none():
    assert infer_chunks((), np.dtype("float64")) is None


def test_infer_chunks_small_1d_fits_in_one_chunk():
    chunks = infer_chunks((100,), np.dtype("float64"), target_chunk_mb=10.0)
    assert chunks == (100,)


def test_infer_chunks_large_1d_split():
    # 10 MB target with float64 (8 bytes) = ~1.3M elements per chunk
    chunks = infer_chunks((10_000_000,), np.dtype("float64"), target_chunk_mb=10.0)
    assert chunks is not None
    assert len(chunks) == 1
    assert 0 < chunks[0] <= 10_000_000


def test_infer_chunks_multi_dim_remaining_elements_drops_to_one():
    # Force the branch where remaining_elements <= 1
    chunks = infer_chunks(
        (1000, 1000, 1000), np.dtype("float64"), target_chunk_mb=0.001
    )
    assert chunks is not None
    assert len(chunks) == 3
    # Later dims should fall to 1 once the budget is exhausted
    assert chunks[-1] == 1


# -----------------------------
# copy_h5_attributes
# -----------------------------
def test_copy_h5_attributes_various_types(tmp_path):
    h5p = tmp_path / "a.h5"
    zp = tmp_path / "a.zarr"
    with h5py.File(h5p, "w") as f:
        ds = f.create_dataset("d", data=np.arange(4))
        ds.attrs["str"] = "hello"
        ds.attrs["bytes"] = b"binary"
        ds.attrs["int"] = np.int64(42)
        ds.attrs["float"] = np.float32(1.5)
        ds.attrs["arr_s"] = np.array([b"a", b"bb"])
        ds.attrs["np_arr"] = np.array([1, 2, 3])

    z_store = zarr.open(str(zp), mode="w")
    z_arr = z_store.create_dataset("d", shape=(4,), dtype="int64")

    with h5py.File(h5p, "r") as f:
        copy_h5_attributes(f["d"], z_arr)

    assert z_arr.attrs["str"] == "hello"
    assert z_arr.attrs["bytes"] == "binary"
    assert z_arr.attrs["int"] == 42
    assert abs(z_arr.attrs["float"] - 1.5) < 1e-6
    assert list(z_arr.attrs["arr_s"]) == ["a", "bb"]
    assert list(z_arr.attrs["np_arr"]) == [1, 2, 3]


def test_copy_h5_attributes_handles_failure(tmp_path):
    """Force the except branch by passing a zarr_obj whose attrs assignment raises."""
    h5p = tmp_path / "b.h5"
    with h5py.File(h5p, "w") as f:
        f.attrs["k"] = "v"
        h5_grp = f["/"]

        class BadAttrs:
            def __setitem__(self, k, v):
                raise RuntimeError("nope")

        class FakeZarr:
            attrs = BadAttrs()

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            copy_h5_attributes(h5_grp, FakeZarr())
        assert any("Could not copy attribute" in str(w.message) for w in caught)


# -----------------------------
# migrate_dataset
# -----------------------------
def _make_h5(tmp_path, builder):
    p = tmp_path / "src.h5"
    with h5py.File(p, "w") as f:
        builder(f)
    return p


def test_migrate_dataset_numeric(tmp_path):
    p = _make_h5(
        tmp_path, lambda f: f.create_dataset("d", data=np.arange(20, dtype="float32"))
    )
    z_store = zarr.open(str(tmp_path / "dst.zarr"), mode="w")
    with h5py.File(p, "r") as f:
        out = migrate_dataset(f["d"], z_store, "d", compressor=None, chunks=True)
    assert out is not None
    np.testing.assert_array_equal(out[:], np.arange(20, dtype="float32"))
    assert out.dtype == np.float32


def test_migrate_dataset_chunks_false(tmp_path):
    p = _make_h5(tmp_path, lambda f: f.create_dataset("d", data=np.zeros((4, 4))))
    z_store = zarr.open(str(tmp_path / "dst.zarr"), mode="w")
    with h5py.File(p, "r") as f:
        out = migrate_dataset(f["d"], z_store, "d", compressor=None, chunks=False)
    assert out is not None
    assert out.shape == (4, 4)


def test_migrate_dataset_chunks_tuple(tmp_path):
    p = _make_h5(tmp_path, lambda f: f.create_dataset("d", data=np.zeros((10, 10))))
    z_store = zarr.open(str(tmp_path / "dst.zarr"), mode="w")
    with h5py.File(p, "r") as f:
        out = migrate_dataset(f["d"], z_store, "d", compressor=None, chunks=(2, 2))
    assert out.chunks == (2, 2)


def test_migrate_dataset_scalar(tmp_path):
    p = _make_h5(tmp_path, lambda f: f.create_dataset("s", data=np.float64(3.14)))
    z_store = zarr.open(str(tmp_path / "dst.zarr"), mode="w")
    with h5py.File(p, "r") as f:
        out = migrate_dataset(f["s"], z_store, "s", compressor=None, chunks=True)
    assert out is not None
    assert float(out[()]) == pytest.approx(3.14)


def test_migrate_dataset_object_string_scalar(tmp_path):
    def build(f):
        ds = f.create_dataset("s", shape=(), dtype=h5py.string_dtype(encoding="utf-8"))
        ds[()] = "hello world"

    p = _make_h5(tmp_path, build)
    z_store = zarr.open(str(tmp_path / "dst.zarr"), mode="w")
    with h5py.File(p, "r") as f:
        out = migrate_dataset(f["s"], z_store, "s", compressor=None)
    assert out is not None


def test_migrate_dataset_object_string_array(tmp_path):
    def build(f):
        data = np.array(["a", "bb", "ccc"], dtype=object)
        f.create_dataset(
            "arr",
            data=data,
            dtype=h5py.string_dtype(encoding="utf-8"),
        )

    p = _make_h5(tmp_path, build)
    z_store = zarr.open(str(tmp_path / "dst.zarr"), mode="w")
    with h5py.File(p, "r") as f:
        out = migrate_dataset(f["arr"], z_store, "arr", compressor=None)
    assert out is not None
    vals = list(out[:])
    assert vals == ["a", "bb", "ccc"]


def test_migrate_dataset_empty_zero_size(tmp_path):
    def build(f):
        f.create_dataset("e", shape=(0,), dtype="float64")

    p = _make_h5(tmp_path, build)
    z_store = zarr.open(str(tmp_path / "dst.zarr"), mode="w")
    with h5py.File(p, "r") as f:
        out = migrate_dataset(f["e"], z_store, "e", compressor=None)
    assert out is not None
    assert out.shape == (0,)


# -----------------------------
# migrate_group
# -----------------------------
def test_migrate_group_with_nested(tmp_path):
    p = tmp_path / "nested.h5"
    with h5py.File(p, "w") as f:
        f.attrs["root_attr"] = "root"
        f.create_dataset("a", data=np.arange(5))
        g = f.create_group("g")
        g.attrs["ga"] = 7
        g.create_dataset("inner", data=np.ones((3, 3)))
        h = g.create_group("h")
        h.create_dataset("deep", data=np.array([[1.0, 2.0]]))

    z_path = tmp_path / "nested.zarr"
    z_store = zarr.open(str(z_path), mode="w")
    with h5py.File(p, "r") as f:
        migrate_group(f, z_store, compressor=None, chunks=True, show_progress=True)

    assert z_store.attrs["root_attr"] == "root"
    np.testing.assert_array_equal(z_store["a"][:], np.arange(5))
    assert z_store["g"].attrs["ga"] == 7
    np.testing.assert_array_equal(z_store["g/inner"][:], np.ones((3, 3)))
    np.testing.assert_array_equal(z_store["g/h/deep"][:], np.array([[1.0, 2.0]]))


# -----------------------------
# validate_migration
# -----------------------------
def test_validate_migration_passes(tmp_path):
    p = tmp_path / "v.h5"
    with h5py.File(p, "w") as f:
        f.create_dataset("a", data=np.arange(10))
        g = f.create_group("g")
        g.create_dataset("b", data=np.zeros((2, 2)))

    z_path = tmp_path / "v.zarr"
    z_store = zarr.open(str(z_path), mode="w")
    with h5py.File(p, "r") as f:
        migrate_group(f, z_store, compressor=None, chunks=True)
        validate_migration(f, z_store, show_progress=True)


def test_validate_migration_shape_mismatch_raises(tmp_path):
    from scitex_io.utils._compat import SciTeXIOError

    p = tmp_path / "v2.h5"
    with h5py.File(p, "w") as f:
        f.create_dataset("a", data=np.arange(10))

    z_path = tmp_path / "v2.zarr"
    z_store = zarr.open(str(z_path), mode="w")
    z_store.create_dataset("a", shape=(5,), dtype="int64")

    with h5py.File(p, "r") as f:
        with pytest.raises(SciTeXIOError):
            validate_migration(f, z_store)


def test_validate_migration_key_mismatch_raises(tmp_path):
    from scitex_io.utils._compat import SciTeXIOError

    p = tmp_path / "v3.h5"
    with h5py.File(p, "w") as f:
        f.create_dataset("a", data=np.arange(3))
        f.create_dataset("b", data=np.arange(3))

    z_path = tmp_path / "v3.zarr"
    z_store = zarr.open(str(z_path), mode="w")
    z_store.create_dataset("a", shape=(3,), dtype="int64")

    with h5py.File(p, "r") as f:
        with pytest.raises(SciTeXIOError):
            validate_migration(f, z_store)


def test_validate_migration_dtype_warning(tmp_path):
    p = tmp_path / "v4.h5"
    with h5py.File(p, "w") as f:
        f.create_dataset("a", data=np.arange(4, dtype="int32"))

    z_path = tmp_path / "v4.zarr"
    z_store = zarr.open(str(z_path), mode="w")
    z_store.create_dataset("a", shape=(4,), dtype="float64")

    with h5py.File(p, "r") as f, warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        validate_migration(f, z_store)
    assert any("Dtype mismatch" in str(w.message) for w in caught)
