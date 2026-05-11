"""Tests for scitex_io.utils package __init__ re-exports."""

import scitex_io.utils as utils


def test_public_names_importable():
    assert hasattr(utils, "migrate_h5_to_zarr")
    assert hasattr(utils, "migrate_h5_to_zarr_batch")
    assert callable(utils.migrate_h5_to_zarr)
    assert callable(utils.migrate_h5_to_zarr_batch)


def test___all__():
    assert "migrate_h5_to_zarr" in utils.__all__
    assert "migrate_h5_to_zarr_batch" in utils.__all__
