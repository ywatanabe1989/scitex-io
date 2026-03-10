# scitex-io Migration Notes

## Origin
Extracted from: `~/proj/scitex-code/src/scitex/io/`
Date: 2025-11-10

## Changes Made

### 1. Inlined Dependencies
To make scitex-io standalone, we inlined utilities from parent package:

```python
# Created src/scitex_io/_utils.py with:
- DotDict (from scitex.dict)
- clean_path (from scitex.str)
- color_text (from scitex.str)
- readable_bytes (from scitex.str)
- preserve_doc (from scitex.decorators)
- split, this_path (from scitex.path)
- parse (from scitex.str)
- detect_environment, get_notebook_info_simple (from scitex.gen)
- SQLite3 wrapper (from scitex.db)
```

### 2. Import Updates

Changed all parent imports:
```python
# Before:
from scitex import logging
from scitex.dict import DotDict
from ..str._clean_path import clean_path

# After:
import logging  # Standard library
from ._utils import DotDict, clean_path
```

### 3. Files Modified

- `_save.py` - Inlined utilities
- `_load.py` - Added preserve_doc
- `_glob.py` - Updated parse import
- `_load_configs.py` - Updated DotDict import
- `_path.py` - Updated path utilities
- `_load_modules/_pdf.py` - Added DotDict inline
- `_load_modules/_sqlite3.py` - Added SQLite3 wrapper

### 4. Package Structure

```
scitex-io/
├── src/scitex_io/
│   ├── __init__.py
│   ├── _utils.py           # NEW: Inlined utilities
│   ├── _load.py
│   ├── _save.py
│   ├── _load_modules/      # 25+ format loaders
│   ├── _save_modules/      # 20+ format savers
│   └── utils/
├── pyproject.toml
├── README.md
└── MIGRATION-NOTES.md      # This file
```

## Dependencies

### Required:
- numpy, scipy, pandas
- h5py, zarr, numcodecs
- PyYAML, joblib, Pillow, matplotlib

### Optional (for full functionality):
- xarray, openpyxl, xlrd
- PyPDF2, pdfplumber, PyMuPDF
- python-docx, bibtexparser
- catboost, optuna, plotly, torch

## Testing

```bash
# Install
pip install -e ~/proj/scitex-io

# Test
python -c "from scitex_io import save, load; print('✓ Works')"
```

## Differences from Original

1. **No scitex dependency**: Fully standalone
2. **Simpler logging**: Uses standard library logging
3. **Inlined utilities**: Small code duplication for independence
4. **SQLite3**: Simple 8-line wrapper instead of full db module

## Future Improvements

- [ ] Add comprehensive tests
- [ ] Add type hints throughout
- [ ] Documentation with examples for each format
- [ ] Performance benchmarks
- [ ] Consider adding to scitex-core if other packages need utilities
