"""Linter plugin for scitex-io: IO-specific rules (IO001-IO007).

Registered via entry point 'scitex_linter.plugins' so scitex-linter
discovers these rules automatically when scitex-io is installed.
"""


def get_plugin():
    """Return scitex-io linter rules and call mappings."""
    from scitex_dev.linter._rules._base import Rule

    IO001 = Rule(
        id="STX-IO001",
        severity="warning",
        category="io",
        message="`np.save()` detected — use `stx.io.save()` for provenance tracking",
        suggestion="Replace `np.save(path, arr)` with `stx.io.save(arr, path)`.",
        requires="scitex",
    )

    IO002 = Rule(
        id="STX-IO002",
        severity="warning",
        category="io",
        message="`np.load()` detected — use `stx.io.load()` for provenance tracking",
        suggestion="Replace `np.load(path)` with `stx.io.load(path)`.",
        requires="scitex",
    )

    IO003 = Rule(
        id="STX-IO003",
        severity="warning",
        category="io",
        message="`pd.read_csv()` detected — use `stx.io.load()` for provenance tracking",
        suggestion="Replace `pd.read_csv(path)` with `stx.io.load(path)`.",
        requires="scitex",
    )

    IO004 = Rule(
        id="STX-IO004",
        severity="warning",
        category="io",
        message="`.to_csv()` detected — use `stx.io.save()` for provenance tracking",
        suggestion="Replace `df.to_csv(path)` with `stx.io.save(df, path)`.",
        requires="scitex",
    )

    IO005 = Rule(
        id="STX-IO005",
        severity="warning",
        category="io",
        message="`pickle.dump()` detected — use `stx.io.save()` for provenance tracking",
        suggestion="Replace `pickle.dump(obj, f)` with `stx.io.save(obj, 'file.pkl')`.",
        requires="scitex",
    )

    IO006 = Rule(
        id="STX-IO006",
        severity="warning",
        category="io",
        message="`json.dump()` detected — use `stx.io.save()` for provenance tracking",
        suggestion="Replace `json.dump(obj, f)` with `stx.io.save(obj, 'file.json')`.",
        requires="scitex",
    )

    IO007 = Rule(
        id="STX-IO007",
        severity="warning",
        category="io",
        message="`.savefig()` detected — use `stx.io.save(fig, path)` for metadata embedding",
        suggestion="Replace `fig.savefig(path)` with `stx.io.save(fig, path)`.",
        requires="scitex",
    )

    # ------------------------------------------------------------------
    # Path-handling rules (PA001-PA005) — every PA rule talks about how
    # `stx.io.save()` resolves paths and stx.io lives in scitex-io.
    # Migrated out of the engine in the per-package-rules cutover.
    # ------------------------------------------------------------------
    PA001 = Rule(
        id="STX-PA001",
        severity="warning",
        category="path",
        message="Absolute path in `stx.io` call — use relative paths for reproducibility",
        suggestion="Use `stx.io.save(obj, './relative/path.ext')` — paths resolve to script_out/.",
        requires="scitex",
    )

    PA002 = Rule(
        id="STX-PA002",
        severity="warning",
        category="path",
        message="`open()` detected — use `stx.io.save()`/`stx.io.load()` which includes auto-logging",
        suggestion=(
            "Replace `open(path)` with `stx.io.load(path)` or `stx.io.save(obj, path)`.\n"
            "  stx.io automatically logs all I/O operations for provenance tracking."
        ),
        requires="scitex",
    )

    PA003 = Rule(
        id="STX-PA003",
        severity="info",
        category="path",
        message="`os.makedirs()`/`mkdir()` detected — `stx.io.save()` creates directories automatically",
        suggestion=(
            "Remove manual directory creation.\n"
            "  `stx.io.save(obj, './subdir/file.ext')` auto-creates `subdir/` inside script_out/."
        ),
        requires="scitex",
    )

    PA004 = Rule(
        id="STX-PA004",
        severity="warning",
        category="path",
        message="`os.chdir()` detected — scripts should be run from project root",
        suggestion="Remove `os.chdir()` and run scripts from the project root directory.",
    )

    PA005 = Rule(
        id="STX-PA005",
        severity="info",
        category="path",
        message="Path without `./` prefix in `stx.io` call — use `./` for explicit relative intent",
        suggestion="Use `./filename.ext` instead of `filename.ext` to clarify relative path intent.",
        requires="scitex",
    )

    return {
        "rules": [
            IO001,
            IO002,
            IO003,
            IO004,
            IO005,
            IO006,
            IO007,
            PA001,
            PA002,
            PA003,
            PA004,
            PA005,
        ],
        "call_rules": {
            ("np", "save"): IO001,
            ("numpy", "save"): IO001,
            ("np", "load"): IO002,
            ("numpy", "load"): IO002,
            ("pd", "read_csv"): IO003,
            ("pandas", "read_csv"): IO003,
            (None, "to_csv"): IO004,
            ("pickle", "dump"): IO005,
            ("pickle", "dumps"): IO005,
            ("json", "dump"): IO006,
            (None, "savefig"): IO007,
            ("os", "makedirs"): PA003,
            ("os", "mkdir"): PA003,
            ("os", "chdir"): PA004,
        },
        "axes_hints": {},
        "checkers": [],
    }
