CLI Reference
=============

scitex-io provides a command-line interface via the ``scitex-io`` command.

.. code-block:: bash

   scitex-io --help-recursive    # Show all commands and subcommands

Commands
--------

.. list-table:: **Table 2.** CLI commands organized by category.
   :header-rows: 1
   :widths: 15 30 55

   * - Category
     - Command
     - Description
   * - **Core I/O**
     - ``scitex-io info``
     - Show all registered save/load formats
   * - **Integration**
     - ``scitex-io mcp``
     - MCP server management (start, doctor, list-tools)
   * - **Integration**
     - ``scitex-io list-python-apis``
     - List all Python API functions with signatures
   * - **Utility**
     - ``scitex-io version``
     - Show version information
   * - **Utility**
     - ``scitex-io shell-completion``
     - Generate shell completion scripts

Format Inspection
-----------------

.. code-block:: bash

   # Show all registered formats
   scitex-io info

   # Example output:
   #   Save formats (24 built-in):
   #     .csv, .json, .npy, .npz, .pkl, .yaml, ...
   #   Load formats (29 built-in):
   #     .csv, .json, .npy, .npz, .pkl, .yaml, ...

API Introspection
-----------------

.. code-block:: bash

   scitex-io list-python-apis         # List all public functions
   scitex-io list-python-apis -v      # With signatures
   scitex-io list-python-apis -vv     # With descriptions
   scitex-io list-python-apis -vvv    # Full details

Shell Completion
----------------

Generate tab-completion scripts for your shell:

.. code-block:: bash

   # Bash
   eval "$(scitex-io shell-completion bash)"

   # Zsh
   eval "$(scitex-io shell-completion zsh)"

   # Fish
   scitex-io shell-completion fish | source

To make it permanent, add to your shell profile (e.g., ``~/.bashrc``).
