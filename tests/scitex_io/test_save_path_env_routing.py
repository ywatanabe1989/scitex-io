"""Tests for ``stx.io.save`` output-path routing across env_type values.

Operator directive 2026-06-13: the previous ``detect_environment()``
returned only ``"jupyter"`` or ``"python"`` — never ``"script"``,
``"ipython"``, or ``"interactive"``. The ``elif env_type == "script":``
branch in ``_save.py`` was dead code; every ``.py`` script save fell
to a silent ``else: sdir = cwd + "/output"`` and produced ``./output/``
instead of the canonical ``<script>_out/`` layout.

This release:
- Rewrites ``detect_environment`` to return one of the documented four
  strings (``jupyter`` / ``ipython`` / ``script`` / ``interactive``).
- Removes the silent else; an unrecognised env_type raises
  ``ValueError`` per operator's fail-fast directive.
- Defaults ``use_caller_path=True`` so a save under ``@stx.session`` (or
  any scitex wrapper) walks past scitex frames to the real user script.

These tests pin the contract end-to-end via real subprocess + tmp_path
(no mocks, per operator). Each test writes a tiny Python file to disk,
runs it as a real subprocess, and asserts the resulting file landed
where the documented routing says it should.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


def _run_script(tmp_path: Path, script_body: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Write ``script_body`` to ``tmp_path/script.py`` and run it as a subprocess.

    Returns the CompletedProcess so callers can inspect stdout / stderr /
    returncode. The subprocess cwd is ``tmp_path`` (so any accidental
    ``cwd/output/`` regression is sandboxed to tmp_path).
    """
    script = tmp_path / "tmp_save_routing.py"
    script.write_text(textwrap.dedent(script_body))
    proc_env = dict(os.environ)
    if env:
        proc_env.update(env)
    return subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
        env=proc_env,
    )


# ---------------------------------------------------------------------- #
# detect_environment — return-value contract                              #
# ---------------------------------------------------------------------- #


class TestDetectEnvironmentReturnsScriptInScriptContext:
    """``detect_environment()`` must return ``"script"`` when called from a real .py."""

    def test_returns_script_when_run_as_a_dot_py_subprocess(self, tmp_path):
        # Arrange
        script_body = """
            from scitex_io._utils import detect_environment
            print(detect_environment())
        """
        # Act
        result = _run_script(tmp_path, script_body)
        # Assert — single combined check on (exit, output).
        emitted = (result.returncode, result.stdout.strip())
        assert emitted == (0, "script"), (
            f"detect_environment() in a .py subprocess must return 'script'; "
            f"got {emitted}; stderr={result.stderr!r}"
        )

    def test_returns_interactive_when_run_via_python_c_one_liner(self):
        # Arrange — bare `python -c "..."` has no __main__.__file__.
        # Act
        result = subprocess.run(
            [sys.executable, "-c", "from scitex_io._utils import detect_environment; print(detect_environment())"],
            capture_output=True,
            text=True,
        )
        # Assert
        emitted = (result.returncode, result.stdout.strip())
        assert emitted == (0, "interactive"), (
            f"detect_environment() under `python -c` must return 'interactive'; "
            f"got {emitted}; stderr={result.stderr!r}"
        )


# ---------------------------------------------------------------------- #
# save() routing — script path goes to <script>_out/                      #
# ---------------------------------------------------------------------- #


class TestSaveRoutesScriptEnvToScriptOutDirectory:
    """A real .py subprocess calling ``stx.io.save`` lands in ``<script>_out/``."""

    def test_save_in_script_context_writes_under_script_out_directory(self, tmp_path):
        # Arrange — script that saves a tiny csv and prints the resolved path.
        script_body = """
            import scitex_io
            scitex_io.save("hello", "./test_save_output.txt")
        """
        # Act
        result = _run_script(tmp_path, script_body)
        # Assert — the canonical layout is <script_stem>_out/<relpath>.
        # script stem = "tmp_save_routing" → tmp_save_routing_out/test_save_output.txt
        expected = tmp_path / "tmp_save_routing_out" / "test_save_output.txt"
        emitted = (result.returncode, expected.is_file())
        assert emitted == (0, True), (
            f"script-context save must land in <script>_out/; "
            f"got returncode={result.returncode}, file-exists={expected.is_file()}; "
            f"expected={expected}; "
            f"stdout={result.stdout!r}; stderr={result.stderr!r}"
        )

    def test_save_must_not_land_in_legacy_cwd_output_directory(self, tmp_path):
        # Arrange — the previous bug routed every script save to
        # `<cwd>/output/` via the silent else branch. The fix removes
        # that fallback; this test pins that the legacy bad path is now
        # GONE — a script-context save MUST NOT create ./output/.
        script_body = """
            import scitex_io
            scitex_io.save("hello", "./test_save_output.txt")
        """
        # Act
        _run_script(tmp_path, script_body)
        # Assert — the legacy ./output/ directory MUST NOT exist.
        legacy = tmp_path / "output"
        assert not legacy.exists(), (
            f"script-context save must NOT regress to legacy ./output/; "
            f"found {legacy}/ with contents: {list(legacy.iterdir()) if legacy.exists() else '-'}"
        )


# ---------------------------------------------------------------------- #
# save() routing — interactive env goes to $SCITEX_DIR cache              #
# ---------------------------------------------------------------------- #


class TestSaveRoutesInteractiveEnvToScitexDirCache:
    """A bare-REPL save lands in ``$SCITEX_DIR/io/runtime/cache/``."""

    def test_python_c_save_writes_to_scitex_dir_cache(self, tmp_path):
        # Arrange — fake SCITEX_DIR so we can locate the result.
        scitex_dir = tmp_path / "fake_scitex_dir"
        env = {"SCITEX_DIR": str(scitex_dir)}
        oneliner = (
            "import scitex_io; "
            "scitex_io.save('hello', 'interactive_save.txt')"
        )
        # Act
        result = subprocess.run(
            [sys.executable, "-c", oneliner],
            capture_output=True,
            text=True,
            env={**os.environ, **env},
            cwd=str(tmp_path),
        )
        # Assert — the file MUST be inside $SCITEX_DIR/io/runtime/cache/.
        expected = scitex_dir / "io" / "runtime" / "cache" / "interactive_save.txt"
        emitted = (result.returncode, expected.is_file())
        assert emitted == (0, True), (
            f"interactive-context save must land in $SCITEX_DIR/io/runtime/cache/; "
            f"got returncode={result.returncode}, file-exists={expected.is_file()}; "
            f"expected={expected}; "
            f"stdout={result.stdout!r}; stderr={result.stderr!r}"
        )


# ---------------------------------------------------------------------- #
# save() fail-loud on unknown env_type                                    #
# ---------------------------------------------------------------------- #


class TestSaveFailsLoudOnUnknownEnvType:
    """An ``env_detector`` returning anything outside the vocabulary raises."""

    def test_unknown_env_type_raises_valueerror_with_diagnostic(self, tmp_path):
        # Arrange — pass an env_detector that returns garbage.
        script_body = """
            import sys
            import scitex_io
            try:
                scitex_io.save(
                    "hello",
                    "./should_not_create.txt",
                    env_detector=lambda: "totally_bogus_env",
                )
            except ValueError as e:
                print("RAISED:", str(e)[:120])
                sys.exit(0)
            else:
                print("DID NOT RAISE")
                sys.exit(2)
        """
        # Act
        result = _run_script(tmp_path, script_body)
        # Assert — ValueError raised with the documented vocabulary mentioned.
        emitted = (
            result.returncode,
            "RAISED:" in result.stdout,
            "totally_bogus_env" in result.stdout,
            "Expected one of" in result.stdout
            or "jupyter" in result.stdout,
        )
        assert emitted == (0, True, True, True), (
            f"unknown env_type must raise ValueError with documented vocabulary; "
            f"got {emitted}; stdout={result.stdout!r}; stderr={result.stderr!r}"
        )

    def test_unknown_env_type_does_not_create_silent_cwd_output_fallback(self, tmp_path):
        # Arrange — same as above but check NO file lands anywhere.
        script_body = """
            import scitex_io
            try:
                scitex_io.save(
                    "hello",
                    "./should_not_create.txt",
                    env_detector=lambda: "totally_bogus_env",
                )
            except ValueError:
                pass
        """
        # Act
        _run_script(tmp_path, script_body)
        # Assert — neither the legacy cwd/output/ nor the script_out/
        # nor any other location got a file.
        bad_paths = [
            tmp_path / "output" / "should_not_create.txt",
            tmp_path / "tmp_save_routing_out" / "should_not_create.txt",
            tmp_path / "should_not_create.txt",
        ]
        existing = [p for p in bad_paths if p.exists()]
        assert existing == [], (
            f"fail-loud raise must NOT silently write anywhere; "
            f"found writes at: {existing}"
        )
