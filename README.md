# scitex-io

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Universal scientific data I/O with plugin registry</b></p>

<p align="center">
  <a href="https://badge.fury.io/py/scitex-io"><img src="https://badge.fury.io/py/scitex-io.svg" alt="PyPI version"></a>
  <a href="https://scitex-io.readthedocs.io/"><img src="https://readthedocs.org/projects/scitex-io/badge/?version=latest" alt="Documentation"></a>
  <a href="https://github.com/ywatanabe1989/scitex-io/actions/workflows/ci.yml"><img src="https://github.com/ywatanabe1989/scitex-io/actions/workflows/ci.yml/badge.svg" alt="Tests"></a>
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="License: AGPL-3.0"></a>
</p>

<p align="center">
  <a href="https://scitex-io.readthedocs.io/">Full Documentation</a> · <code>pip install scitex-io</code>
</p>

---

## Problem

Operating systems already solve this: double-click a `.csv` and it opens in a spreadsheet, double-click a `.pdf` and it opens in a reader — the OS dispatches to the right application based on the file extension. Yet in Python, there is no equivalent. Loading a CSV requires `pandas.read_csv()`, an HDF5 file requires `h5py.File()`, a NumPy array requires `numpy.load()`, and so on — each format demands its own library, its own API, and its own boilerplate. Adding a new format means touching save and load logic scattered throughout your codebase.

## Solution

scitex-io provides a single `save()`/`load()` interface for 30+ scientific formats with automatic format detection from file extensions. A two-tier plugin registry lets you register custom formats that work seamlessly with the same API — user handlers override built-ins, so you can extend or replace any format without modifying the library.

<details>
<summary><b>Supported Formats (30+)</b></summary>

<br>

| Category | Extensions |
|----------|-----------|
| Spreadsheet | `.csv`, `.tsv`, `.xlsx`, `.xls` |
| Scientific | `.npy`, `.npz`, `.mat`, `.hdf5`, `.h5`, `.zarr` |
| Serialization | `.pkl`, `.pickle`, `.pkl.gz`, `.joblib` |
| ML/DL | `.pth`, `.pt`, `.cbm` |
| Config | `.json`, `.yaml`, `.yml` |
| Documents | `.txt`, `.md`, `.pdf`, `.docx`, `.tex` |
| Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.tiff`, `.tif`, `.svg` |
| Media | `.mp4` |
| Web | `.html` |
| Bibliography | `.bib` |

</details>

## Installation

Requires Python >= 3.9.

```bash
pip install scitex-io
```

For MCP server support:

```bash
pip install scitex-io[mcp]
```

> **SciTeX users**: `pip install scitex` already includes scitex-io.

## Quickstart

```python
from scitex_io import save, load

# Universal save/load — format auto-detected from extension
import pandas as pd
df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
save(df, "data.csv")
loaded = load("data.csv")

# 30+ formats work the same way
import numpy as np
save(np.array([1, 2, 3]), "data.npy")
save({"key": "value"}, "config.yaml")
save({"nested": [1, 2]}, "data.json")
```

<details>
<summary><b>Custom Format Registration</b></summary>

<br>

```python
from scitex_io import register_saver, register_loader, save, load

@register_saver(".custom")
def save_custom(obj, path, **kwargs):
    with open(path, "w") as f:
        f.write(str(obj))

@register_loader(".custom")
def load_custom(path, **kwargs):
    with open(path) as f:
        return f.read()

save("hello", "data.custom")
assert load("data.custom") == "hello"
```

</details>

## Three Interfaces

<details>
<summary><strong>Python API</strong></summary>

<br>

```python
from scitex_io import save, load, list_formats, register_saver, register_loader

save(obj, "path.ext")        # Save any object
data = load("path.ext")      # Load any file
fmts = list_formats()        # Show all registered formats
```

> **[Full API reference](https://scitex-io.readthedocs.io/)**

</details>

<details>
<summary><strong>CLI Commands</strong></summary>

<br>

```bash
scitex-io --help-recursive          # Show all commands
scitex-io info                      # Show registered formats
scitex-io list-python-apis -vv      # List Python APIs with signatures
scitex-io version                   # Show version
scitex-io mcp start                 # Start MCP server
scitex-io mcp doctor                # Check MCP health
scitex-io mcp list-tools -vv        # List MCP tools with parameters
```

> **[Full CLI reference](https://scitex-io.readthedocs.io/)**

</details>

<details>
<summary><strong>MCP Server — for AI Agents</strong></summary>

<br>

AI agents can save, load, and discover formats autonomously.

| Tool | Description |
|------|-------------|
| `io_list_formats` | List all registered save/load formats |
| `io_load` | Load data from any supported format |
| `io_save` | Save data to any supported format |
| `io_register_info` | Show how to register custom formats |

```bash
scitex-io mcp start
```

> **[Full MCP specification](https://scitex-io.readthedocs.io/)**

</details>

## Part of SciTeX

scitex-io is part of [**SciTeX**](https://scitex.ai). When used inside the SciTeX framework, I/O is seamless:

```python
import scitex

@scitex.session
def main(CONFIG=scitex.INJECTED):
    data = scitex.io.load("input.csv")     # auto-tracked by clew
    result = process(data)
    scitex.io.save(result, "output.csv")   # auto-tracked by clew
    return 0
```

`scitex.io` delegates to `scitex_io` — they share the same API and registry.

The SciTeX ecosystem follows the Four Freedoms for researchers:

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because research infrastructure deserves the same freedoms as the software it runs on.

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>

<!-- EOF -->
