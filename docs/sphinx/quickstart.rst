Quickstart
==========

Save and Load
-------------

Format is auto-detected from the file extension:

.. code-block:: python

   from scitex_io import save, load

   # DataFrames
   import pandas as pd
   df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
   save(df, "data.csv")
   loaded = load("data.csv")

   # NumPy arrays
   import numpy as np
   save(np.array([1, 2, 3]), "data.npy")

   # Dictionaries
   save({"key": "value"}, "config.yaml")
   save({"nested": [1, 2]}, "data.json")

   # Any Python object
   save({"complex": object()}, "data.pkl")

One function for save, one for load — 30+ formats work the same way.


List Available Formats
----------------------

.. code-block:: python

   from scitex_io import list_formats

   formats = list_formats()
   print(f"Save: {len(formats['save']['builtin'])} built-in formats")
   print(f"Load: {len(formats['load']['builtin'])} built-in formats")

.. code-block:: text

   Save: 24 built-in formats
   Load: 29 built-in formats


Custom Format Registration
--------------------------

Register handlers for any file extension:

.. code-block:: python

   from scitex_io import register_saver, register_loader, save, load

   @register_saver(".tsv3")
   def save_tsv3(obj, path, **kwargs):
       """Save with 3-space-separated values."""
       with open(path, "w") as f:
           for row in obj:
               f.write("   ".join(str(v) for v in row) + "\n")

   @register_loader(".tsv3")
   def load_tsv3(path, **kwargs):
       """Load 3-space-separated values."""
       with open(path) as f:
           return [line.strip().split("   ") for line in f]

   # Now .tsv3 works like any built-in format
   save([[1, 2], [3, 4]], "data.tsv3")
   assert load("data.tsv3") == [["1", "2"], ["3", "4"]]

.. note::

   User-registered handlers take priority over built-in ones for the same
   extension. This lets you override default behavior without modifying
   the library.


Caching
-------

Repeated loads are cached automatically:

.. code-block:: python

   from scitex_io import load, get_cache_info, clear_load_cache

   data1 = load("large_file.hdf5")   # reads from disk
   data2 = load("large_file.hdf5")   # returns cached copy (instant)

   info = get_cache_info()
   print(f"Cache hits: {info['hits']}, misses: {info['misses']}")

   clear_load_cache()  # free memory
