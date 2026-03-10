Quickstart
==========

Basic Usage
-----------

.. code-block:: python

    from scitex_io import save, load

    # Save/load with auto-detected format
    save({"key": "value"}, "data.json")
    data = load("data.json")

Custom Format Registration
--------------------------

.. code-block:: python

    from scitex_io import register_saver, register_loader

    @register_saver(".custom")
    def save_custom(obj, path, **kwargs):
        with open(path, "w") as f:
            f.write(str(obj))

    @register_loader(".custom")
    def load_custom(path, **kwargs):
        with open(path) as f:
            return f.read()

List Registered Formats
-----------------------

.. code-block:: python

    from scitex_io import list_formats
    formats = list_formats()
    print(f"Save: {len(formats['save']['builtin'])} built-in")
    print(f"Load: {len(formats['load']['builtin'])} built-in")
