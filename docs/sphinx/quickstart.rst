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


Project Configuration
---------------------

Most research projects have hard-coded parameters scattered across scripts — sample rates,
thresholds, model hyperparameters, plot dimensions. ``load_configs`` centralizes them in
YAML files under a ``config/`` directory:

.. code-block:: text

   project/
     config/
       PATHS.yaml          # DATA_DIR: /data/experiment_01
       PREPROCESS.yaml     # SAMPLE_RATE: 1000, BANDPASS: [0.5, 40]
       MODEL.yaml          # HIDDEN_DIM: 256, DROPOUT: 0.3
       PLOT.yaml           # FIGSIZE: [180, 60], DPI: 300
       IS_DEBUG.yaml       # IS_DEBUG: true

.. code-block:: python

   from scitex_io import load_configs

   # One call loads all YAML files, namespaced by filename
   CONFIG = load_configs()                            # ./config/*.yaml
   CONFIG = load_configs(config_dir="./my_configs")   # custom path

   CONFIG.PATHS.DATA_DIR            # "/data/experiment_01"
   CONFIG.PREPROCESS.SAMPLE_RATE    # 1000
   CONFIG.MODEL.HIDDEN_DIM          # 256

   # Debug mode: keys prefixed with DEBUG_ override their counterparts
   # In MODEL.yaml:  HIDDEN_DIM: 256, DEBUG_HIDDEN_DIM: 32
   CONFIG = load_configs(IS_DEBUG=True)
   CONFIG.MODEL.HIDDEN_DIM          # 32 (debug value promoted)

Returns a ``DotDict`` — a nested dictionary with dot-notation access. Config keys should
use **UPPER_CASE** to signal that they are user-defined constants, not runtime variables.


DotDict
-------

``DotDict`` gives dot-notation access to nested dictionaries:

.. code-block:: python

   from scitex_io import DotDict

   d = DotDict({"MODEL": {"HIDDEN_DIM": 256, "LAYERS": 4}})
   d.MODEL.HIDDEN_DIM    # 256
   d.MODEL.LAYERS        # 4

   # Standard dict operations work too
   d["MODEL"]["HIDDEN_DIM"]    # 256
   d.MODEL.keys()              # dict_keys(["HIDDEN_DIM", "LAYERS"])
   d.MODEL.to_dict()           # {"HIDDEN_DIM": 256, "LAYERS": 4}


Metadata Embedding
------------------

A saved PNG has no record of the code, parameters, or session that produced it.
``embed_metadata`` solves this by writing provenance directly into the file:

.. code-block:: python

   from scitex_io import embed_metadata, read_metadata, has_metadata

   # Embed metadata into a figure
   embed_metadata("figure.png", {
       "experiment": "exp_042",
       "model": "resnet50",
       "accuracy": 0.94,
       "timestamp": "2026-03-11",
   })

   # Read it back — months later, from the file alone
   meta = read_metadata("figure.png")
   meta["experiment"]    # "exp_042"

   # Check if a file carries metadata
   has_metadata("figure.png")   # True

Supports PNG (tEXt chunks), JPEG (EXIF UserComment), SVG (XML metadata), and PDF
(Info Dictionary). The figure carries its own history — no external database needed.


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
