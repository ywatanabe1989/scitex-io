#!/bin/bash
# Run all scitex-io examples
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "=== Running scitex-io examples ==="
for script in "$SCRIPT_DIR"/[0-9]*.py; do
    [ -f "$script" ] || continue
    echo "--- Running $(basename "$script") ---"
    python3 "$script"
    echo
done
echo "=== All examples completed ==="
