---
name: formats
description: All 30+ supported file formats with extensions and notes.
---

# Supported Formats

## Tabular Data

| Extension | Load | Save | Notes |
|-----------|------|------|-------|
| `.csv` | DataFrame | DataFrame, dict, list | Auto-detects separator |
| `.tsv` | DataFrame | DataFrame | Tab-separated |
| `.xlsx` | DataFrame | DataFrame | Requires openpyxl |
| `.xls` | DataFrame | — | Legacy Excel |
| `.parquet` | DataFrame | DataFrame | Fast binary columnar |
| `.feather` | DataFrame | DataFrame | Fast IPC format |

## Array Data

| Extension | Load | Save | Notes |
|-----------|------|------|-------|
| `.npy` | ndarray | ndarray | Single NumPy array |
| `.npz` | dict of ndarray | dict of ndarray | Multiple arrays |
| `.mat` | dict | dict | MATLAB format (scipy) |

## Hierarchical Data

| Extension | Load | Save | Notes |
|-----------|------|------|-------|
| `.h5` / `.hdf5` | ndarray/dict | ndarray/dict | HDF5 (requires h5py) |
| `.zarr` | ndarray/dict | ndarray/dict | Zarr store (requires zarr) |

## Configuration

| Extension | Load | Save | Notes |
|-----------|------|------|-------|
| `.yaml` / `.yml` | dict | dict | YAML format |
| `.json` | dict | dict | JSON format |
| `.toml` | dict | dict | TOML format |

## Serialization

| Extension | Load | Save | Notes |
|-----------|------|------|-------|
| `.pkl` / `.pickle` | any | any | Python pickle |
| `.joblib` | any | any | Joblib serialization |

## Image

| Extension | Load | Save | Notes |
|-----------|------|------|-------|
| `.png` | ndarray | ndarray/Figure | PNG image |
| `.jpg` / `.jpeg` | ndarray | ndarray/Figure | JPEG image |
| `.tif` / `.tiff` | ndarray | ndarray | TIFF image |
| `.svg` | — | Figure | Vector format |
| `.eps` | — | Figure | PostScript vector |
| `.pdf` | — | Figure | PDF (figures) |

## Text

| Extension | Load | Save | Notes |
|-----------|------|------|-------|
| `.txt` | str | str | Plain text |
| `.md` | str | str | Markdown |
| `.log` | str | str | Log files |

## Video/Audio

| Extension | Load | Save | Notes |
|-----------|------|------|-------|
| `.mp4` | — | frames | Video from frame sequence |
| `.gif` | — | frames | Animated GIF |

## Special

| Extension | Load | Save | Notes |
|-----------|------|------|-------|
| `.pth` / `.pt` | state_dict | state_dict | PyTorch model weights |
| `.onnx` | — | model | ONNX model export |
