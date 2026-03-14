#!/usr/bin/env python3
"""Example 5: Embed provenance metadata into figure files.

Demonstrates embed_metadata, read_metadata, and has_metadata for PNG files.
Supported formats: PNG (tEXt), JPEG (EXIF), SVG (XML), PDF (Info Dict).
"""

import os

from scitex_io import embed_metadata, has_metadata, read_metadata, save

SCRIPT_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(SCRIPT_DIR, "05_metadata_embedding_out")
os.makedirs(OUT_DIR, exist_ok=True)

FIGURE_PATH = os.path.join(OUT_DIR, "figure.png")

# --- Create a simple figure ---------------------------------------------------
try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6], marker="o")
    ax.set(xlabel="X", ylabel="Y", title="Demo Figure")
    fig.savefig(FIGURE_PATH, dpi=100)
    plt.close()
except ImportError:
    # Fallback: create a minimal 1x1 PNG without matplotlib
    import struct
    import zlib

    def _minimal_png(path):
        sig = b"\x89PNG\r\n\x1a\n"
        ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        ihdr_chunk = b"IHDR" + ihdr
        ihdr_crc = struct.pack(">I", zlib.crc32(ihdr_chunk) & 0xFFFFFFFF)
        raw = zlib.compress(b"\x00\x00\x00\x00")
        idat_chunk = b"IDAT" + raw
        idat_crc = struct.pack(">I", zlib.crc32(idat_chunk) & 0xFFFFFFFF)
        with open(path, "wb") as f:
            f.write(sig)
            f.write(struct.pack(">I", len(ihdr)) + ihdr_chunk + ihdr_crc)
            f.write(struct.pack(">I", len(raw)) + idat_chunk + idat_crc)
            f.write(
                struct.pack(">I", 0)
                + b"IEND"
                + struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
            )

    _minimal_png(FIGURE_PATH)

# --- Embed metadata -----------------------------------------------------------
METADATA = {
    "EXPERIMENT": "exp_042",
    "MODEL": "resnet50",
    "ACCURACY": 0.94,
    "TIMESTAMP": "2026-03-11",
    "NOTES": "Baseline run with default hyperparameters",
}

embed_metadata(FIGURE_PATH, METADATA)
print("Metadata embedded into figure.png")

# --- Read it back -------------------------------------------------------------
assert has_metadata(FIGURE_PATH), "Expected metadata in figure.png"

META = read_metadata(FIGURE_PATH)
print(f"EXPERIMENT : {META['EXPERIMENT']}")
print(f"MODEL      : {META['MODEL']}")
print(f"ACCURACY   : {META['ACCURACY']}")

# --- Save metadata as sidecar for archival ------------------------------------
save(META, os.path.join(OUT_DIR, "figure_metadata.json"))
print(f"Metadata also saved to {OUT_DIR}/figure_metadata.json")
