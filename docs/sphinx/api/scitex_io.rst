scitex_io
=========

.. automodule:: scitex_io
   :members:
   :undoc-members:
   :show-inheritance:

Core I/O
--------

.. autofunction:: scitex_io.save
.. autofunction:: scitex_io.load
.. autofunction:: scitex_io.load_configs
.. autofunction:: scitex_io.glob
.. autofunction:: scitex_io.reload
.. autofunction:: scitex_io.flush
.. autofunction:: scitex_io.cache

Registry
--------

.. autofunction:: scitex_io.register_saver
.. autofunction:: scitex_io.register_loader
.. autofunction:: scitex_io.get_saver
.. autofunction:: scitex_io.get_loader
.. autofunction:: scitex_io.list_formats
.. autofunction:: scitex_io.unregister_saver
.. autofunction:: scitex_io.unregister_loader

Cache Control
-------------

.. autofunction:: scitex_io.get_cache_info
.. autofunction:: scitex_io.configure_cache
.. autofunction:: scitex_io.clear_load_cache

Dict Utilities
--------------

.. autoclass:: scitex_io.DotDict
   :members:

Metadata
--------

.. autofunction:: scitex_io.embed_metadata
.. autofunction:: scitex_io.read_metadata
.. autofunction:: scitex_io.has_metadata

Explorers
---------

.. autoclass:: scitex_io.H5Explorer
   :members:

.. autoclass:: scitex_io.ZarrExplorer
   :members:
