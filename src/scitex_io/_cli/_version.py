#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Version command for scitex-io CLI."""

import click


@click.command(
    "version", hidden=True, context_settings={"ignore_unknown_options": True}
)
@click.pass_context
def version(ctx):
    """(deprecated) Use `scitex-io --version` instead."""
    click.echo(
        "error: `scitex-io version` was replaced by `scitex-io --version`.\n"
        "Re-run with: scitex-io --version",
        err=True,
    )
    ctx.exit(2)
