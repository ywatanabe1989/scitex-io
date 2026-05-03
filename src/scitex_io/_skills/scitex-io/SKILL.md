---
name: scitex-io
description: |
  [WHAT] Universal one-call file I/O for 30+ scientific formats — CSV,
  Parquet, NumPy .npy/.npz, pickle, YAML, JSON, HDF5, MATLAB .mat,
  images, matplotlib figures, PyTorch .pt, MNE .fif, EDF, video. Also
  YAML config loading, figure metadata embedding, load-time caching.
  [WHEN] reading or writing any data file — as a drop-in replacement
  for pd.read_csv, np.load, pickle.load, json.load, fig.savefig,
  torch.save. Trigger phrases: "load", "save", "read", "write", "open
  a file", "save this figure", "cache this result", "load my config",
  "glob these files", "FileNotFoundError after stx.io.save",
  "symlink_from_cwd", "script_out directory".
  [HOW] stx.io.save(obj, path) / stx.io.load(path) auto-dispatch by
  extension. save() auto-routes to {script}_out/ from caller context;
  load() resolves the path against cwd. Pass symlink_from_cwd=True
  for round-trip, or use absolute paths on both sides.
tags: [scitex-io]
allowed-tools: mcp__scitex__io_*
primary_interface: python
interfaces:
  python: 3
  cli: 1
  mcp: 2
  skills: 3
  http: 0
---

# scitex-io

> **Interfaces:** Python ⭐⭐⭐ · CLI ⭐ · MCP ⭐⭐ · Skills ⭐⭐⭐ · Hook — · HTTP —

Universal scientific data I/O with plugin registry. One `save()`/`load()` for 30+ formats.

## Installation & import (two equivalent paths)

The same module is reachable via two install paths; use whichever
matches your dependency story. Verified 2026-04-23 in a clean
container.

```python
# Standalone — pip install scitex-io
import scitex_io as sio
sio.save(df, "results.csv")

# Umbrella — pip install scitex
import scitex.io as sio
sio.save(df, "results.csv")
```

`pip install scitex-io` alone **does not** expose the `scitex`
namespace; `import scitex.io` raises `ModuleNotFoundError`. If you
want the `scitex.io` form, install both (`pip install scitex
scitex-io`) or install the umbrella which pulls scitex-io in
as an extra.

See [../../general/02_interface-python-api.md] for the ecosystem-wide
rule and the empirical verification table.

## Sub-skills

### Core
* [01_save-and-load](01_save-and-load.md) — Core save/load API, registry, custom formats
* [02_centralized-config](02_centralized-config.md) — `load_configs()` and DotDict
* [03_metadata-embedding](03_metadata-embedding.md) — Provenance in PNG/JPEG/SVG/PDF
* [04_cache](04_cache.md) — Load caching, reload, flush
* [05_glob](05_glob.md) — Pattern matching with natural sort
* [06_supported-formats](06_supported-formats.md) — All 30+ format tables
* [07_path-resolution](07_path-resolution.md) — Auto save-path, scitex.path utilities

### Standards
* [20_linting-rules](20_linting-rules.md) — STX-IO001–007 lint rules

## MCP Tools

| Tool | Purpose |
|------|---------|
| `io_save` | Save data to file (auto-detect format) |
| `io_load` | Load data from file (auto-detect format) |
| `io_load_configs` | Load config directory as merged dict |
| `io_list_formats` | List all registered save/load formats |
| `io_register_info` | Show registration info for a format |

## CLI

```bash
scitex-io info data.csv           # Format, shape, dtypes
scitex-io configs show ./config/  # Display merged configs
scitex-io mcp start               # Start MCP server
scitex-io skills list              # List skill pages
```


## Environment

- [08_env-vars.md](08_env-vars.md) — SCITEX_* env vars read by scitex-io at runtime
