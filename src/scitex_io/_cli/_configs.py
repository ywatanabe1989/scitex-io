#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI command for loading YAML configurations."""

import json

import click


@click.command(
    "configs", hidden=True, context_settings={"ignore_unknown_options": True}
)
@click.pass_context
def configs_deprecated(ctx):
    """(deprecated) Renamed to `load-configs`."""
    click.echo(
        "error: `scitex-io configs` was renamed to `scitex-io load-configs`.\n"
        "Re-run with: scitex-io load-configs",
        err=True,
    )
    ctx.exit(2)


@click.command("load-configs")
@click.option("-d", "--config-dir", default="./config", help="Config directory path.")
@click.option("--debug/--no-debug", default=None, help="Force debug mode on/off.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.option("-v", "--verbose", is_flag=True, help="Show debug key promotions.")
def load_configs_cmd(config_dir, debug, as_json, verbose):
    """Load YAML configuration files from a directory.

    Reads all *.yaml files from CONFIG_DIR (default: ./config),
    namespaced by filename. Also loads from categories/ subdirectory.

    \b
    Example:
      $ scitex-io load-configs
      $ scitex-io load-configs -d ./my-config --json
      $ scitex-io load-configs --debug -v
    """
    from scitex_io import load_configs

    result = load_configs(
        IS_DEBUG=debug,
        config_dir=config_dir,
        verbose=verbose,
    )

    if as_json:
        click.echo(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        click.secho(f"Config dir: {config_dir}", fg="cyan")
        click.secho(f"Namespaces: {list(result.keys())}", fg="green")
        for ns in result.keys():
            click.echo(f"\n[{ns}]")
            val = result[ns]
            if hasattr(val, "to_dict"):
                val = val.to_dict()
            click.echo(json.dumps(val, indent=2, default=str))
