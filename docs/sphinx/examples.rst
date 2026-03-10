Examples
========

scitex-io ships with example scripts in the ``examples/`` directory.
Run them all at once:

.. code-block:: bash

   cd examples/
   ./00_run_all.sh

Example 1: Basic Save/Load
---------------------------

Save and load common scientific data formats.

.. code-block:: python

   from scitex_io import save, load
   import numpy as np

   # NumPy array
   arr = np.arange(12).reshape(3, 4)
   save(arr, "array.npy")
   loaded = load("array.npy")
   assert (loaded == arr).all()

   # Dictionary as JSON
   config = {"learning_rate": 0.001, "epochs": 100, "model": "resnet"}
   save(config, "config.json")
   assert load("config.json")["learning_rate"] == 0.001

   # Dictionary as YAML
   save(config, "config.yaml")

   # CSV via pandas
   import pandas as pd
   df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
   save(df, "data.csv")

Output saved to ``examples/01_basic_save_load_out/``:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - File
     - Content
   * - ``array.npy``
     - 3x4 NumPy array
   * - ``config.json``
     - Training configuration
   * - ``config.yaml``
     - Same config in YAML format
   * - ``data.csv``
     - Simple DataFrame


Example 2: Custom Format
-------------------------

Register and use a custom format handler.

.. code-block:: python

   from scitex_io import register_saver, register_loader, save, load

   @register_saver(".tsv3")
   def save_tsv3(obj, path, **kwargs):
       with open(path, "w") as f:
           for row in obj:
               f.write("   ".join(str(v) for v in row) + "\n")

   @register_loader(".tsv3")
   def load_tsv3(path, **kwargs):
       with open(path) as f:
           return [line.strip().split("   ") for line in f]

   data = [["Alice", "30"], ["Bob", "25"]]
   save(data, "custom.tsv3")
   assert load("custom.tsv3") == data

Output saved to ``examples/02_custom_format_out/custom.tsv3``.


Part of SciTeX
--------------

When used inside the `SciTeX framework <https://scitex.ai>`_, I/O is
automatically tracked for reproducibility:

.. code-block:: python

   import scitex

   @scitex.session
   def main(CONFIG=scitex.INJECTED):
       data = scitex.io.load("input.csv")     # auto-tracked by clew
       result = process(data)
       scitex.io.save(result, "output.csv")   # auto-tracked by clew
       return 0

``scitex.io`` delegates to ``scitex_io`` — they share the same API and registry.
