#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python API introspection commands for scitex-io."""

import click


def _format_signature(func):
    """Format a function signature with colors."""
    import inspect

    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return ""

    params = []
    for name, param in sig.parameters.items():
        if param.annotation != inspect.Parameter.empty:
            ann = param.annotation
            type_str = ann.__name__ if hasattr(ann, "__name__") else str(ann)
            type_str = type_str.replace("typing.", "")
        else:
            type_str = None

        if param.default != inspect.Parameter.empty:
            def_str = repr(param.default)
            if len(def_str) > 20:
                def_str = "..."
            if type_str:
                p = f"{click.style(name, bold=True)}: {click.style(type_str, fg='cyan')} = {click.style(def_str, fg='yellow')}"
            else:
                p = f"{click.style(name, bold=True)} = {click.style(def_str, fg='yellow')}"
        else:
            if type_str:
                p = f"{click.style(name, bold=True)}: {click.style(type_str, fg='cyan')}"
            else:
                p = click.style(name, bold=True)
        params.append(p)

    return f"({', '.join(params)})"


def _get_apis(module, prefix="", max_depth=3, _depth=0, _visited=None):
    """Recursively collect public API items from a module."""
    import inspect
    import types

    if _visited is None:
        _visited = set()

    mid = id(module)
    if mid in _visited or _depth > max_depth:
        return []
    _visited.add(mid)

    results = []
    for name in sorted(dir(module)):
        if name.startswith("_"):
            continue
        try:
            obj = getattr(module, name)
        except Exception:
            continue

        full_name = f"{prefix}.{name}" if prefix else name

        if callable(obj) and not isinstance(obj, type):
            doc = (inspect.getdoc(obj) or "").split("\n")[0]
            sig = _format_signature(obj)
            results.append(("F", full_name, sig, doc))
        elif isinstance(obj, type):
            doc = (inspect.getdoc(obj) or "").split("\n")[0]
            results.append(("C", full_name, "", doc))
        elif isinstance(obj, types.ModuleType):
            pkg = getattr(obj, "__package__", "") or ""
            if "scitex_io" in pkg:
                results.append(("M", full_name, "", ""))
                results.extend(
                    _get_apis(obj, full_name, max_depth, _depth + 1, _visited)
                )

    return results


TYPE_COLORS = {"M": "blue", "C": "magenta", "F": "green", "V": "cyan"}


@click.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="-v names, -vv sigs, -vvv docs")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def list_python_apis(verbose, as_json):
    """List public Python APIs in scitex-io.

    \b
    Example:
      $ scitex-io list-python-apis
      $ scitex-io list-python-apis -vv
      $ scitex-io list-python-apis --json
    """
    import scitex_io

    apis = _get_apis(scitex_io, "scitex_io")

    if as_json:
        import json as _json

        payload = {
            "module": "scitex_io",
            "apis": [
                {"kind": kind, "name": name, "signature": sig, "doc": doc}
                for kind, name, sig, doc in apis
            ],
        }
        click.echo(_json.dumps(payload, indent=2))
        return

    if not apis:
        click.echo("No public APIs found.")
        return

    for kind, name, sig, doc in apis:
        color = TYPE_COLORS.get(kind, "white")
        kind_label = click.style(f"[{kind}]", fg=color)
        name_styled = click.style(name, fg=color, bold=True)

        if verbose == 0:
            click.echo(f"  {kind_label} {name_styled}")
        elif verbose == 1:
            line = f"  {kind_label} {name_styled}{sig}"
            click.echo(line)
        else:
            line = f"  {kind_label} {name_styled}{sig}"
            if doc:
                line += f"\n       {click.style(doc, dim=True)}"
            click.echo(line)
