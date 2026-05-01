#!/usr/bin/env python3
"""Project configuration management with load_configs.

Demonstrates how to centralize hard-coded parameters (magic numbers)
in YAML files under a config/ directory, loaded as a single DotDict
with dot-notation access.

Convention: use UPPER_CASE for config keys to signal user-defined constants.

Usage:
    python 03_load_configs.py
"""

import os
import shutil

from scitex_io import load_configs, save

SCRIPT_DIR = os.path.dirname(__file__)
CONFIG_DIR = os.path.join(SCRIPT_DIR, "03_load_configs_config")
OUT_DIR = os.path.join(SCRIPT_DIR, "03_load_configs_out")


def setup_example_configs():
    """Create example config files."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    save(
        {
            "DATA_DIR": "/data/experiment_01",
            "OUTPUT_DIR": "./results",
            "RAW_SUBDIR": "raw",
        },
        os.path.join(CONFIG_DIR, "PATHS.yaml"),
        verbose=False,
    )

    save(
        {
            "SAMPLE_RATE": 1000,
            "BANDPASS": [0.5, 40],
            "NOTCH_FREQ": 50,
            "N_CHANNELS": 64,
            "DEBUG_SAMPLE_RATE": 100,
            "DEBUG_N_CHANNELS": 4,
        },
        os.path.join(CONFIG_DIR, "PREPROCESS.yaml"),
        verbose=False,
    )

    save(
        {
            "HIDDEN_DIM": 256,
            "N_LAYERS": 4,
            "DROPOUT": 0.3,
            "LEARNING_RATE": 0.001,
            "BATCH_SIZE": 64,
            "DEBUG_HIDDEN_DIM": 32,
            "DEBUG_BATCH_SIZE": 4,
        },
        os.path.join(CONFIG_DIR, "MODEL.yaml"),
        verbose=False,
    )

    save(
        {"IS_DEBUG": False},
        os.path.join(CONFIG_DIR, "IS_DEBUG.yaml"),
        verbose=False,
    )


def main():
    setup_example_configs()

    # Load all configs at once — namespaced by filename
    CONFIG = load_configs(config_dir=CONFIG_DIR)

    print("=== Production Config ===")
    print(f"CONFIG.PATHS.DATA_DIR        = {CONFIG.PATHS.DATA_DIR}")
    print(f"CONFIG.PREPROCESS.SAMPLE_RATE = {CONFIG.PREPROCESS.SAMPLE_RATE}")
    print(f"CONFIG.PREPROCESS.BANDPASS    = {CONFIG.PREPROCESS.BANDPASS}")
    print(f"CONFIG.MODEL.HIDDEN_DIM      = {CONFIG.MODEL.HIDDEN_DIM}")
    print(f"CONFIG.MODEL.BATCH_SIZE      = {CONFIG.MODEL.BATCH_SIZE}")

    # Debug mode — DEBUG_ prefixed values override their counterparts
    CONFIG_DBG = load_configs(config_dir=CONFIG_DIR, IS_DEBUG=True)

    print("\n=== Debug Config (IS_DEBUG=True) ===")
    print(f"CONFIG.PREPROCESS.SAMPLE_RATE = {CONFIG_DBG.PREPROCESS.SAMPLE_RATE}")
    print(f"CONFIG.PREPROCESS.N_CHANNELS  = {CONFIG_DBG.PREPROCESS.N_CHANNELS}")
    print(f"CONFIG.MODEL.HIDDEN_DIM      = {CONFIG_DBG.MODEL.HIDDEN_DIM}")
    print(f"CONFIG.MODEL.BATCH_SIZE      = {CONFIG_DBG.MODEL.BATCH_SIZE}")

    # DotDict is also a regular dict
    print(f"\nNamespaces: {list(CONFIG.keys())}")
    print(f"Model keys: {list(CONFIG.MODEL.keys())}")

    # Export merged config as JSON for reproducibility
    save(CONFIG.to_dict(), os.path.join(OUT_DIR, "merged_config.json"), verbose=False)
    print(f"\nMerged config saved to: {OUT_DIR}/merged_config.json")

    # Cleanup
    shutil.rmtree(CONFIG_DIR)
    return 0


if __name__ == "__main__":
    main()
