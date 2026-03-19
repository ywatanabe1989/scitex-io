---
name: scitex-io
description: Universal file I/O supporting 30+ formats (CSV, NumPy, pickle, YAML, JSON, HDF5, images, figures, etc.). Use when loading or saving data files in scientific workflows.
allowed-tools: mcp__scitex__io_*
---

# Universal File I/O with scitex-io

## Quick Start

```python
import scitex_io as sio

# Save anything
sio.save(df, "data.csv")
sio.save(arr, "data.npy")
sio.save(fig, "plot.png")       # Figure + auto CSV export
sio.save(obj, "data.pkl")
sio.save(config, "config.yaml")

# Load anything
data = sio.load("data.csv")     # → DataFrame
arr = sio.load("data.npy")      # → ndarray
config = sio.load("config.yaml") # → dict

# Load all config files from directory
CONFIG = sio.load_configs("./config/")  # → DotDict
```

## Common Workflows

### "Save/load a DataFrame"

```python
sio.save(df, "results.csv")
sio.save(df, "results.xlsx")
sio.save(df, "results.parquet")  # Fast binary
df = sio.load("results.csv")
```

### "Save/load NumPy arrays"

```python
sio.save(arr, "data.npy")       # Single array
sio.save({"x": x, "y": y}, "data.npz")  # Multiple arrays
arr = sio.load("data.npy")
```

### "Work with configs"

```python
# Load all YAML/JSON files in config/ as nested DotDict
CONFIG = sio.load_configs("./config/")
print(CONFIG.model.learning_rate)  # Dot-access
print(CONFIG.data.batch_size)
```

### "Save figures with data"

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot(x, y)
sio.save(fig, "plot.png")  # Saves plot.png + plot.csv
```

### "Explore HDF5/Zarr files"

```python
sio.explore_h5("data.h5")       # Print structure
sio.has_h5_key("data.h5", "/grp/dataset")
data = sio.load("data.h5", key="/grp/dataset")
```

### "Embed/read metadata"

```python
sio.embed_metadata("figure.png", {"experiment": "exp01", "date": "2026-03-20"})
meta = sio.read_metadata("figure.png")
```

### "Register custom format"

```python
sio.register_saver(".mat", my_mat_saver)
sio.register_loader(".mat", my_mat_loader)
```

## CLI Commands

```bash
# File info
scitex-io info data.csv          # Show format, shape, dtypes
scitex-io info data.h5           # Show HDF5 structure

# Config management
scitex-io configs show ./config/ # Display merged configs

# MCP server
scitex-io mcp start

# Skills
scitex-io skills list
scitex-io skills get SKILL
scitex-io skills get formats
```

## MCP Tools (for AI agents)

| Tool | Purpose |
|------|---------|
| `io_save` | Save data to file (auto-detect format) |
| `io_load` | Load data from file (auto-detect format) |
| `io_load_configs` | Load config directory as merged dict |
| `io_list_formats` | List all registered save/load formats |
| `io_register_info` | Show registration info for a format |

## Specific Topics

* **Supported formats** [references/formats.md](references/formats.md)
