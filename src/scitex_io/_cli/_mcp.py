#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP server commands for scitex-io."""

import click


@click.group(invoke_without_command=True)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.pass_context
def mcp(ctx, help_recursive):
    """MCP (Model Context Protocol) server commands."""
    if help_recursive:
        _print_help_recursive(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _print_help_recursive(ctx):
    """Print help for mcp and all its subcommands."""
    fake_parent = click.Context(click.Group(), info_name="scitex-io")
    parent_ctx = click.Context(mcp, info_name="mcp", parent=fake_parent)

    click.secho("━━━ scitex-io mcp ━━━", fg="cyan", bold=True)
    click.echo(mcp.get_help(parent_ctx))

    for name in sorted(mcp.list_commands(ctx) or []):
        cmd = mcp.get_command(ctx, name)
        if cmd is None:
            continue
        click.echo()
        click.secho(f"━━━ scitex-io mcp {name} ━━━", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=parent_ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))


@mcp.command("start")
@click.option("--host", default="127.0.0.1", help="Host to bind to.")
@click.option("--port", default=8100, type=int, help="Port to bind to.")
@click.option("--dry-run", is_flag=True, help="Print launch plan without starting.")
@click.option(
    "-y", "--yes", is_flag=True, help="Suppress interactive confirmation (assume yes)."
)
def start_server(host, port, dry_run, yes):
    """Start the scitex-io MCP server.

    \b
    Example:
      $ scitex-io mcp start
      $ scitex-io mcp start --host 0.0.0.0 --port 9100
      $ scitex-io mcp start --dry-run
    """
    if dry_run:
        click.echo(f"DRY RUN — would start scitex-io MCP server on {host}:{port}")
        return
    try:
        from .._mcp.server import mcp as mcp_server
    except ImportError as e:
        raise click.ClickException(
            f"MCP not available. Install: pip install scitex-io[mcp]\n{e}"
        ) from e

    click.echo(f"Starting scitex-io MCP server on {host}:{port}")
    mcp_server.run()


@mcp.command("doctor")
def doctor():
    """Check MCP server health and dependencies.

    \b
    Example:
      $ scitex-io mcp doctor
    """
    checks = []

    # Check fastmcp
    try:
        import fastmcp

        checks.append(("fastmcp", True, f"v{fastmcp.__version__}"))
    except ImportError:
        checks.append(("fastmcp", False, "not installed (pip install scitex-io[mcp])"))

    # Check MCP server
    try:
        checks.append(("MCP server", True, "importable"))
    except Exception as e:
        checks.append(("MCP server", False, str(e)))

    # Check scitex_io core
    try:
        from .. import __version__, list_formats

        fmts = list_formats()
        n_save = len(fmts["save"]["builtin"])
        n_load = len(fmts["load"]["builtin"])
        checks.append(
            (
                "scitex-io",
                True,
                f"v{__version__} ({n_save} save, {n_load} load formats)",
            )
        )
    except Exception as e:
        checks.append(("scitex-io", False, str(e)))

    click.secho("scitex-io MCP Doctor", fg="cyan", bold=True)
    click.echo()
    all_ok = True
    for name, ok, detail in checks:
        status = click.style("OK", fg="green") if ok else click.style("FAIL", fg="red")
        all_ok = all_ok and ok
        click.echo(f"  [{status}] {name}: {detail}")

    click.echo()
    if all_ok:
        click.secho("All checks passed.", fg="green")
    else:
        click.secho("Some checks failed. See above.", fg="red")


@mcp.command(
    "installation", hidden=True, context_settings={"ignore_unknown_options": True}
)
@click.pass_context
def installation_deprecated(ctx):
    """(deprecated) Renamed to `install`."""
    click.echo(
        "error: `scitex-io mcp installation` was renamed to "
        "`scitex-io mcp install`.\n"
        "Re-run with: scitex-io mcp install",
        err=True,
    )
    ctx.exit(2)


@mcp.command(
    "show-installation", hidden=True, context_settings={"ignore_unknown_options": True}
)
@click.pass_context
def show_installation_deprecated(ctx):
    """(deprecated) Renamed to `install`."""
    click.echo(
        "error: `scitex-io mcp show-installation` was renamed to "
        "`scitex-io mcp install`.\n"
        "Re-run with: scitex-io mcp install",
        err=True,
    )
    ctx.exit(2)


@mcp.command("install")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.option("--dry-run", is_flag=True, help="Accepted for §2; this verb is informational, never mutates state.")
@click.option("--yes", "-y", is_flag=True, help="Accepted for §2; this verb is informational, never mutates state.")
def install(as_json, dry_run, yes):
    """Show MCP installation and configuration instructions.

    \b
    Example:
      $ scitex-io mcp install
      $ scitex-io mcp install --json
    """
    del dry_run, yes  # audit §2 — no-op flags
    config = {
        "mcpServers": {
            "scitex-io": {
                "command": "fastmcp",
                "args": ["run", "scitex_io._mcp.server:mcp"],
            }
        }
    }
    if as_json:
        import json as _json

        click.echo(
            _json.dumps(
                {
                    "install_command": "pip install scitex-io[mcp]",
                    "config": config,
                    "verify_commands": ["scitex-io mcp doctor"],
                    "renamed_from": "show-installation",
                },
                indent=2,
            )
        )
        return

    click.secho("scitex-io MCP Installation", fg="cyan", bold=True)
    click.echo()
    click.echo("Install scitex-io with MCP support:")
    click.echo()
    click.secho("  pip install scitex-io[mcp]", fg="green")
    click.echo()
    click.echo("Add to your MCP client config (e.g., claude_desktop_config.json):")
    click.echo()
    import json as _json

    for line in _json.dumps(config, indent=2).split("\n"):
        click.secho(f"  {line}", dim=True)
    click.echo()
    click.echo("Or start the server manually:")
    click.echo()
    click.secho("  scitex-io mcp start", fg="green")
    click.echo()
    click.echo("Verify with:")
    click.echo()
    click.secho("  scitex-io mcp doctor", fg="green")


@mcp.command("list-tools")
@click.option("-v", "--verbose", count=True, help="-v names, -vv params, -vvv docs")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def list_tools(verbose, as_json):
    """List available MCP tools.

    \b
    Example:
      $ scitex-io mcp list-tools
      $ scitex-io mcp list-tools -vv
      $ scitex-io mcp list-tools --json
    """
    try:
        from .._mcp.server import mcp as mcp_server
    except ImportError as e:
        raise click.ClickException(
            f"MCP not available. Install: pip install scitex-io[mcp]\n{e}"
        ) from e

    import asyncio

    tools = asyncio.run(mcp_server.list_tools())

    if as_json:
        import json as _json

        payload = {
            "total": len(tools),
            "tools": [
                {
                    "name": getattr(t, "name", str(t)),
                    "description": getattr(t, "description", "") or "",
                    "parameters": getattr(t, "parameters", {}) or {},
                }
                for t in tools
            ],
        }
        click.echo(_json.dumps(payload, indent=2))
        return

    if not tools:
        click.echo("No MCP tools registered.")
        return

    click.secho(f"MCP Tools ({len(tools)})", fg="cyan", bold=True)
    click.echo()

    for tool in tools:
        name = getattr(tool, "name", str(tool))
        desc = getattr(tool, "description", "") or ""
        first_line = desc.split("\n")[0] if desc else ""
        params = getattr(tool, "parameters", {}) or {}
        props = params.get("properties", {})

        if verbose == 0:
            click.echo(f"  {click.style(name, fg='green', bold=True)}")
        elif verbose == 1:
            click.echo(f"  {click.style(name, fg='green', bold=True)}")
            if first_line:
                click.echo(f"    {click.style(first_line, dim=True)}")
        else:
            click.echo(f"  {click.style(name, fg='green', bold=True)}")
            if desc:
                for line in desc.split("\n")[:5]:
                    click.echo(f"    {click.style(line, dim=True)}")
            if props:
                click.echo(f"    {click.style('Parameters:', fg='yellow')}")
                for pname, pinfo in props.items():
                    ptype = pinfo.get("type", "any")
                    pdesc = pinfo.get("description", "")
                    click.echo(
                        f"      {click.style(pname, bold=True)}: "
                        f"{click.style(ptype, fg='cyan')}"
                        f"{f' - {pdesc}' if pdesc else ''}"
                    )
        click.echo()
