#!/bin/bash
# Run all scitex-io examples
set -e

usage() {
    echo "Usage: $(basename "$0") [-h|--help]"
    echo ""
    echo "Run all scitex-io examples in order."
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message and exit"
}

case "${1:-}" in
-h | --help)
    usage
    exit 0
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "=== Running scitex-io examples ==="
for script in "$SCRIPT_DIR"/[0-9]*.py; do
    [ -f "$script" ] || continue
    echo "--- Running $(basename "$script") ---"
    python3 "$script"
    echo
done
echo "=== All examples completed ==="
