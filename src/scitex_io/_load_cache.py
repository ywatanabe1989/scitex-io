"""Top-level shim — re-exports from `_loading._load_cache`.

The umbrella `scitex.io._load` historically imported
``cache_data``, ``get_cached_data``, ``load_npy_cached`` from
``scitex_io._load_cache``. After standalonization the implementation
moved to ``scitex_io._loading._load_cache`` but the published umbrella
still uses the old top-level path. This shim preserves the public
import surface so umbrella consumers don't break.
"""

from scitex_io._loading._load_cache import (
    cache_data,
    get_cached_data,
    load_npy_cached,
)

__all__ = ["cache_data", "get_cached_data", "load_npy_cached"]
