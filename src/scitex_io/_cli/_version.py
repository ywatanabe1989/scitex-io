#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Version command for scitex-io CLI."""

import click


@click.command()
def version():
    """Show scitex-io version."""
    from .. import __version__

    click.echo(f"scitex-io {__version__}")
