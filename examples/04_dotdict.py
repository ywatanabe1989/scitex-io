#!/usr/bin/env python3
"""DotDict — nested dictionary with dot-notation access.

DotDict is used by load_configs() to return config values that can be
accessed with attribute syntax: CONFIG.MODEL.HIDDEN_DIM instead of
CONFIG["MODEL"]["HIDDEN_DIM"].

Usage:
    python 04_dotdict.py
"""

from scitex_io import DotDict


def main():
    # Create from nested dict
    PARAMS = DotDict(
        {
            "MODEL": {
                "HIDDEN_DIM": 256,
                "N_LAYERS": 4,
                "DROPOUT": 0.3,
            },
            "TRAINING": {
                "LEARNING_RATE": 0.001,
                "BATCH_SIZE": 64,
                "EPOCHS": 100,
            },
        }
    )

    # Dot-notation access
    print(f"PARAMS.MODEL.HIDDEN_DIM   = {PARAMS.MODEL.HIDDEN_DIM}")
    print(f"PARAMS.TRAINING.EPOCHS    = {PARAMS.TRAINING.EPOCHS}")

    # Standard dict operations
    print(f"Namespaces: {list(PARAMS.keys())}")
    print(f"Model keys: {list(PARAMS.MODEL.keys())}")
    print(f"'MODEL' in PARAMS: {'MODEL' in PARAMS}")

    # Mutation
    PARAMS.MODEL.HIDDEN_DIM = 512
    print(f"\nAfter update: PARAMS.MODEL.HIDDEN_DIM = {PARAMS.MODEL.HIDDEN_DIM}")

    # Convert back to plain dict (e.g., for JSON serialization)
    plain = PARAMS.to_dict()
    print(f"Type after to_dict(): {type(plain).__name__}")
    print(f"plain['MODEL']['HIDDEN_DIM'] = {plain['MODEL']['HIDDEN_DIM']}")
    return 0


if __name__ == "__main__":
    main()
