"""Test scitex_io._cli package init."""

import scitex_io._cli as cli_pkg


def test_exports_main():
    assert hasattr(cli_pkg, "main")
    assert "main" in cli_pkg.__all__


def test_help_has_version_prefix():
    # __init__.py injects "scitex-io (vX.Y.Z) — ..." into main.help
    assert cli_pkg.main.help
    assert "scitex-io" in cli_pkg.main.help
