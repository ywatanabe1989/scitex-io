Plugin Registry
===============

The plugin registry is the core mechanism behind scitex-io's extensibility.
Every file format is just a pair of save/load handlers registered against a
file extension.

Architecture
------------

.. code-block:: text

   ┌─────────────────────────────────────────────────┐
   │                  scitex-io                       │
   ├─────────────────────────────────────────────────┤
   │  Public API                                      │
   │    save(obj, path)    load(path)                 │
   │    list_formats()     register_saver/loader()    │
   ├─────────────────────────────────────────────────┤
   │  Registry (_registry.py)                         │
   │    ┌──────────────────┐ ┌──────────────────┐    │
   │    │   User handlers  │ │ Built-in handlers│    │
   │    │   (priority 1)   │ │ (priority 2)     │    │
   │    └──────────────────┘ └──────────────────┘    │
   ├─────────────────────────────────────────────────┤
   │  Format Modules                                  │
   │    _save_modules/    _load_modules/              │
   │    24 savers          29 loaders                 │
   ├─────────────────────────────────────────────────┤
   │  Interfaces                                      │
   │    CLI (Click)     │  MCP (FastMCP)              │
   │    scitex-io info  │  scitex-io mcp start        │
   │    6 commands      │  4 tools                    │
   └─────────────────────────────────────────────────┘

How Dispatch Works
------------------

When you call ``save(obj, "data.csv")``:

1. The extension ``.csv`` is extracted from the path
2. The registry checks **user handlers** first
3. If no user handler, checks **built-in handlers**
4. The matched handler is called with ``(obj, path, **kwargs)``
5. If no handler found, raises ``ValueError``

The same process applies to ``load(path)``.


Registering Handlers
--------------------

.. code-block:: python

   from scitex_io import register_saver, register_loader

   @register_saver(".parquet")
   def save_parquet(obj, path, **kwargs):
       obj.to_parquet(path, **kwargs)

   @register_loader(".parquet")
   def load_parquet(path, **kwargs):
       import pandas as pd
       return pd.read_parquet(path, **kwargs)

.. list-table:: **Table 4.** Registry API functions.
   :header-rows: 1
   :widths: 35 65

   * - Function
     - Description
   * - ``register_saver(ext)``
     - Decorator to register a save handler for the given extension
   * - ``register_loader(ext)``
     - Decorator to register a load handler for the given extension
   * - ``get_saver(ext)``
     - Retrieve the save handler for an extension
   * - ``get_loader(ext)``
     - Retrieve the load handler for an extension
   * - ``list_formats()``
     - List all registered extensions (built-in + user)
   * - ``unregister_saver(ext)``
     - Remove a user-registered save handler
   * - ``unregister_loader(ext)``
     - Remove a user-registered load handler


Handler Contract
----------------

Save handlers must accept:

.. code-block:: python

   def my_saver(obj: Any, path: str, **kwargs) -> None:
       """Write obj to path."""
       ...

Load handlers must accept:

.. code-block:: python

   def my_loader(path: str, **kwargs) -> Any:
       """Read and return data from path."""
       ...

The ``**kwargs`` are passed through from ``save()``/``load()`` calls,
allowing format-specific options.
