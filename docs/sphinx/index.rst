SciTeX IO
=========

.. image:: _static/scitex-logo.png
   :alt: SciTeX
   :align: center
   :width: 400px

.. raw:: html

   <p align="center"><b>Universal scientific data I/O with plugin registry</b></p>
   <br>

**scitex-io** provides a single ``save()``/``load()`` interface for **30+ scientific
formats** with automatic format detection from file extensions. A two-tier plugin
registry lets you register custom formats that work seamlessly with the same API.

.. code-block:: python

   from scitex_io import save, load

   save(df, "data.csv")          # Pandas DataFrame
   save(arr, "data.npy")         # NumPy array
   save(config, "config.yaml")   # Dictionary
   loaded = load("data.csv")     # Auto-detected format


.. list-table:: **Three interfaces, one API**
   :header-rows: 1
   :widths: 20 40 40

   * - Interface
     - Access
     - Use Case
   * - **Python API**
     - ``from scitex_io import save, load``
     - Scripts, notebooks, pipelines
   * - **CLI**
     - ``scitex-io info``
     - Terminal, shell scripts
   * - **MCP Server**
     - ``scitex-io mcp start``
     - AI agents (Claude, Cursor, etc.)


.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   formats
   cli
   mcp

.. toctree::
   :maxdepth: 2
   :caption: Advanced

   registry
   explorers
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/scitex_io


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
