#!/usr/bin/env python3
"""Test configuration for scitex-io."""
import tempfile
import pytest

@pytest.fixture
def tmp_dir():
    """Provide a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as td:
        yield td
