#!/usr/bin/env python3
"""Basic save/load demonstration for scitex-io."""
import os
import numpy as np
import pandas as pd
from scitex_io import save, load

OUT_DIR = os.path.join(os.path.dirname(__file__), "01_basic_save_load_out")
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    save({"experiment": "demo", "values": [1, 2, 3]}, os.path.join(OUT_DIR, "config.json"), verbose=False)
    print(f"JSON: {load(os.path.join(OUT_DIR, 'config.json'), cache=False)}")

    df = pd.DataFrame({"x": np.linspace(0, 1, 5), "y": np.random.randn(5)})
    save(df, os.path.join(OUT_DIR, "data.csv"), verbose=False)
    print(f"CSV: {load(os.path.join(OUT_DIR, 'data.csv'), cache=False).shape}")

    arr = np.random.randn(10, 3)
    save(arr, os.path.join(OUT_DIR, "array.npy"), verbose=False)
    print(f"NPY: shape={load(os.path.join(OUT_DIR, 'array.npy'), cache=False).shape}")

    save({"lr": 0.001, "epochs": 100}, os.path.join(OUT_DIR, "config.yaml"), verbose=False)
    print(f"YAML: {load(os.path.join(OUT_DIR, 'config.yaml'), cache=False)}")

    print(f"\nAll saved to: {OUT_DIR}")

if __name__ == "__main__":
    main()
