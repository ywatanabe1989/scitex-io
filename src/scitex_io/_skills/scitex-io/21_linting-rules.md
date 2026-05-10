---
description: |
  [TOPIC] Linting rules
  [DETAILS] STX-IO001–014 + STX-PA001–005 lint rules detected by
  scitex-linter when scitex-io is installed (np.save → stx.io.save, etc.).
tags: [scitex-io-linting-rules, scitex-io, scitex-package]
---

# Linting Rules

Detected by [scitex-linter](https://github.com/ywatanabe1989/scitex-linter) via entry point `scitex_dev.linter.plugins`.

## I/O rules (STX-IO0xx)

| Rule | Detects | Suggestion |
|------|---------|------------|
| STX-IO001 | `np.save/savez/savez_compressed/savetxt` | → `stx.io.save(arr, path)` |
| STX-IO002 | `np.load/loadtxt/genfromtxt` | → `stx.io.load(path)` |
| STX-IO003 | `pd.read_csv/parquet/excel/hdf/pickle/json/feather/table/orc` | → `stx.io.load(path)` |
| STX-IO004 | `df.to_csv/parquet/excel/hdf/pickle/json/feather/html/orc` | → `stx.io.save(df, path)` |
| STX-IO005 | `pickle.dump/dumps/load/loads` (and `cPickle`) | → `stx.io.save(obj, "file.pkl")` / `stx.io.load(...)` |
| STX-IO006 | `json.dump/dumps/load/loads` | → `stx.io.save(obj, "file.json")` / `stx.io.load(...)` |
| STX-IO007 | `.savefig()` | → `stx.io.save(fig, path)` for metadata embedding |
| STX-IO008 | `torch.save/load` | → `stx.io.save(obj, "file.pt")` / `stx.io.load(...)` |
| STX-IO009 | `joblib.dump/load` | → `stx.io.save(obj, "file.joblib")` / `stx.io.load(...)` |
| STX-IO010 | `yaml.dump/safe_dump/dump_all/load/safe_load/full_load` | → `stx.io.save(obj, "file.yaml")` / `stx.io.load(...)` |
| STX-IO011 | `scipy.io.savemat/loadmat` (`sio.savemat`/`sio.loadmat`) | → `stx.io.save(d, "file.mat")` / `stx.io.load(...)` |
| STX-IO012 | `cv2.imwrite/imread`, `Image.open`, `plt.imsave/imread`, `imageio.imwrite/imread` | → `stx.io.save(img, "file.png")` / `stx.io.load(...)` |
| STX-IO013 | `h5py.File()` | → `stx.io.save(obj, "file.h5")` / `stx.io.load(...)` |
| STX-IO014 | `stx.io.save/load(obj, "./x.<unknown>")` — extension has no registered handler | → `register_saver('.ext')` / `register_loader('.ext')`, or use a built-in extension |

## Path rules (STX-PA0xx)

| Rule | Detects | Suggestion |
|------|---------|------------|
| STX-PA001 | Absolute path in `stx.io.save/load(...)` | Use `./relative/path.ext` — paths resolve to `script_out/` |
| STX-PA002 | `open(path)` inside a `@stx.session` script | → `stx.io.save/load(...)` for auto-logging |
| STX-PA003 | `os.makedirs/mkdir`, `Path(...).mkdir` | Remove — `stx.io.save` auto-creates dirs (info-level) |
| STX-PA004 | `os.chdir()` | Remove — run scripts from project root |
| STX-PA005 | `stx.io.save(obj, "file.ext")` (no `./` prefix) | Use `./file.ext` for explicit relative intent (info-level) |

All IO rules: severity `warning`, category `io`. All PA rules: category `path`; PA003/PA005 are `info`, the rest `warning`.

## Recognized package aliases

The linter accepts these three forms interchangeably for save/load detection and PA rule application:

```python
stx.io.save(arr, "./a.npy")        # canonical short alias
scitex.io.save(arr, "./a.npy")     # canonical full alias
scitex_io.save(arr, "./a.npy")     # bare top-level (also: scitex_io.io.save(...))
```

## Custom format hint

Every IO rule's suggestion now includes a register-handler reminder:

```python
from scitex_io import register_saver, register_loader

@register_saver(".myext")
def save_myext(obj, path, **kw): ...

@register_loader(".myext")
def load_myext(path, **kw): ...
```

`STX-IO014` specifically fires when `stx.io.save/load` is called with an extension scitex-io has no registered handler for — pointing the user at `register_saver` / `register_loader` for that exact extension.

## Why

`stx.io.save/load` provides provenance tracking, auto-CSV export for figures, metadata embedding, centralized format dispatch, and (for `save`) script-relative output routing. Direct library calls bypass these.
