#!/bin/bash
# Run all scitex-io examples; tee output to 00_run_all.sh.log with PASS/FAIL summary.
set -u

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
LOG_FILE="$SCRIPT_DIR/00_run_all.sh.log"

GREEN=$'\033[0;32m'
RED=$'\033[0;31m'
RESET=$'\033[0m'

run_all() {
    echo "=== Running scitex-io examples ==="
    declare -a PASSED=()
    declare -a FAILED=()

    for script in "$SCRIPT_DIR"/[0-9]*.py; do
        [ -f "$script" ] || continue
        name=$(basename "$script")
        echo "--- Running $name ---"
        if python3 "$script"; then
            PASSED+=("$name")
        else
            FAILED+=("$name")
        fi
        echo
    done

    echo "=== Summary ==="
    for n in "${PASSED[@]}"; do
        echo "${GREEN}PASS${RESET} $n"
    done
    for n in "${FAILED[@]}"; do
        echo "${RED}FAIL${RESET} $n"
    done
    echo "Passed: ${#PASSED[@]}  Failed: ${#FAILED[@]}"
    echo "=== All examples completed ==="

    if [ "${#FAILED[@]}" -gt 0 ]; then
        return 1
    fi
}

run_all 2>&1 | tee "$LOG_FILE"
exit "${PIPESTATUS[0]}"
