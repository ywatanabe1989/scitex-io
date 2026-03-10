MCP Server
==========

scitex-io provides a `Model Context Protocol <https://modelcontextprotocol.io/>`_ (MCP)
server, enabling AI agents to save, load, and discover file formats autonomously.

Installation
------------

.. code-block:: bash

   pip install scitex-io[mcp]

Starting the Server
-------------------

.. code-block:: bash

   scitex-io mcp start

MCP Client Configuration
-------------------------

Add to your MCP client configuration (e.g., Claude Desktop, Cursor):

.. code-block:: json

   {
     "mcpServers": {
       "scitex-io": {
         "command": "scitex-io",
         "args": ["mcp", "start"]
       }
     }
   }

Available Tools
---------------

.. list-table:: **Table 3.** Four MCP tools for AI-assisted file I/O. All tools accept JSON parameters and return JSON results.
   :header-rows: 1
   :widths: 25 75

   * - Tool
     - Description
   * - ``io_list_formats``
     - List all registered save/load format extensions
   * - ``io_load``
     - Load data from any supported file format. Returns type, shape, and preview.
   * - ``io_save``
     - Save data (as JSON string) to any supported format
   * - ``io_register_info``
     - Show how to register custom format handlers with examples

Tool Details
------------

**io_load**

.. code-block:: json

   {
     "path": "/data/experiment.csv",
     "format": null,
     "cache": true
   }

Returns shape/length, type name, and a truncated preview of the loaded data.

**io_save**

.. code-block:: json

   {
     "data_json": "{\"x\": [1, 2, 3], \"y\": [4, 5, 6]}",
     "path": "/data/output.json",
     "verbose": false
   }

Diagnostics
-----------

.. code-block:: bash

   scitex-io mcp doctor          # Check MCP dependencies
   scitex-io mcp list-tools      # List available tools
   scitex-io mcp list-tools -vv  # With full parameter descriptions
