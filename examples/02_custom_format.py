#!/usr/bin/env python3
"""Custom format registration demonstration for scitex-io."""
import os
from scitex_io import register_saver, register_loader, save, load, list_formats

OUT_DIR = os.path.join(os.path.dirname(__file__), "02_custom_format_out")
os.makedirs(OUT_DIR, exist_ok=True)

@register_saver(".tsv3")
def save_tsv3(obj, path, **kwargs):
    with open(path, "w") as f:
        for row in obj:
            f.write("\t".join(str(x) for x in row[:3]) + "\n")

@register_loader(".tsv3")
def load_tsv3(path, **kwargs):
    rows = []
    with open(path) as f:
        for line in f:
            rows.append(line.strip().split("\t"))
    return rows

def main():
    fmts = list_formats()
    print(f"Formats: {len(fmts['save']['builtin'])} save, {len(fmts['load']['builtin'])} load")
    data = [[1, 2, 3], [4, 5, 6]]
    save(data, os.path.join(OUT_DIR, "custom.tsv3"), verbose=False)
    print(f"Custom .tsv3: {load(os.path.join(OUT_DIR, 'custom.tsv3'), cache=False)}")

if __name__ == "__main__":
    main()
