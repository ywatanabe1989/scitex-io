#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Info command for scitex-io CLI."""

import click


@click.command()
@click.option("-v", "--verbose", count=True, help="Verbosity level (-v, -vv)")
def info(verbose):
    """Show registered I/O formats and registry status."""
    from .._registry import list_formats

    formats = list_formats()
    save_builtin = sorted(formats["save"]["builtin"])
    save_user = sorted(formats["save"]["user"])
    load_builtin = sorted(formats["load"]["builtin"])
    load_user = sorted(formats["load"]["user"])

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
