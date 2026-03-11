"""Linter plugin for scitex-io: IO-specific rules (IO001-IO007).

Registered via entry point 'scitex_linter.plugins' so scitex-linter
discovers these rules automatically when scitex-io is installed.
"""


def get_plugin():
    """Return scitex-io linter rules and call mappings."""
    from scitex_linter._rules._base import Rule

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

    return {
        "rules": [IO001, IO002, IO003, IO004, IO005, IO006, IO007],
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
        },
        "axes_hints": {},
        "checkers": [],
    }
