#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Info command for scitex-io CLI."""

import click


@click.command("info", hidden=True, context_settings={"ignore_unknown_options": True})
@click.pass_context
def info_deprecated(ctx):
    """(deprecated) Renamed to `show-info`."""
    click.echo(
        "error: `scitex-io info` was renamed to `scitex-io show-info`.\n"
        "Re-run with: scitex-io show-info",
        err=True,
    )
    ctx.exit(2)


@click.command("show-info")
@click.option("-v", "--verbose", count=True, help="Verbosity level (-v, -vv)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def show_info(verbose, as_json):
    """Show registered I/O formats and registry status.

    \b
    Example:
      $ scitex-io show-info
      $ scitex-io show-info -v
      $ scitex-io show-info --json
    """
    from .._registry import list_formats

    formats = list_formats()
    save_builtin = sorted(formats["save"]["builtin"])
    save_user = sorted(formats["save"]["user"])
    load_builtin = sorted(formats["load"]["builtin"])
    load_user = sorted(formats["load"]["user"])

    if as_json:
        import json as _json

        click.echo(
            _json.dumps(
                {
                    "save": {"builtin": save_builtin, "user": save_user},
                    "load": {"builtin": load_builtin, "user": load_user},
                },
                indent=2,
            )
        )
        return

    click.secho("scitex-io Format Registry", fg="cyan", bold=True)
    click.echo()

    click.secho(
        f"Save: {len(save_builtin)} built-in, {len(save_user)} user-registered",
        fg="green",
    )
    if verbose >= 1:
        click.echo(f"  Built-in: {', '.join(save_builtin)}")
        if save_user:
            click.echo(f"  User: {', '.join(save_user)}")

    click.echo()
    click.secho(
        f"Load: {len(load_builtin)} built-in, {len(load_user)} user-registered",
        fg="green",
    )
    if verbose >= 1:
        click.echo(f"  Built-in: {', '.join(load_builtin)}")
        if load_user:
            click.echo(f"  User: {', '.join(load_user)}")
