#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CLI entry point for scitex-io."""


import click

from .. import __version__
from ._apis import list_python_apis
from ._configs import configs_deprecated, load_configs_cmd
from ._info import info_deprecated, show_info
from ._mcp import mcp
from ._version import version as version_cmd

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

COMMAND_CATEGORIES = [
    ("Core I/O", ["show-info", "load-configs"]),
    ("Integration", ["mcp", "list-python-apis"]),
    ("Utility", ["version", "shell-completion"]),
]


class CategorizedGroup(click.Group):
    """Custom Click group that displays commands organized by category."""

    def format_commands(self, ctx, formatter):
        commands = {}
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is not None and not cmd.hidden:
                commands[subcommand] = cmd

        if not commands:
            return

        displayed = set()
        for category_name, category_commands in COMMAND_CATEGORIES:
            category_items = []
            for name in category_commands:
                if name in commands and name not in displayed:
                    cmd = commands[name]
                    help_text = cmd.get_short_help_str(limit=formatter.width)
                    category_items.append((name, help_text))
                    displayed.add(name)
            if category_items:
                with formatter.section(category_name):
                    formatter.write_dl(category_items)

        uncategorized = [
            (name, commands[name].get_short_help_str(limit=formatter.width))
            for name in sorted(commands.keys())
            if name not in displayed
        ]
        if uncategorized:
            with formatter.section("Other"):
                formatter.write_dl(uncategorized)


def _print_help_recursive(ctx):
    """Print help for all commands recursively."""
    click.secho("━━━ scitex-io ━━━", fg="cyan", bold=True)
    click.echo(main.get_help(ctx))

    for name in sorted(main.list_commands(ctx) or []):
        cmd = main.get_command(ctx, name)
        if cmd is None:
            continue
        click.echo()
        click.secho(f"━━━ scitex-io {name} ━━━", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))
            if isinstance(cmd, click.Group):
                for sub_name in sorted(cmd.list_commands(sub_ctx) or []):
                    sub_cmd = cmd.get_command(sub_ctx, sub_name)
                    if sub_cmd is None:
                        continue
                    click.echo()
                    click.secho(
                        f"━━━ scitex-io {name} {sub_name} ━━━",
                        fg="cyan",
                        bold=True,
                    )
                    with click.Context(
                        sub_cmd, info_name=sub_name, parent=sub_ctx
                    ) as sub2_ctx:
                        click.echo(sub_cmd.get_help(sub2_ctx))


@click.group(
    cls=CategorizedGroup, context_settings=CONTEXT_SETTINGS, invoke_without_command=True
)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Emit structured JSON output (propagates to subcommands that honour it).",
)
@click.version_option(__version__, "--version", "-V")
@click.pass_context
def main(ctx, help_recursive, as_json):
    """scitex-io: Universal scientific data I/O with plugin registry.

    \b
    Config is loaded with the SciTeX precedence chain:
      config.yaml -> $SCITEX_IO_CONFIG -> ~/.scitex/io/config.yaml -> defaults
    """
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    if help_recursive:
        _print_help_recursive(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command(
    "shell-completion",
    hidden=True,
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.pass_context
def shell_completion_deprecated(ctx):
    """(deprecated) Renamed — use `install-shell-completion` or `print-shell-completion`."""
    click.echo(
        "error: `scitex-io shell-completion` was split into:\n"
        "  scitex-io install-shell-completion --shell <bash|zsh|fish>\n"
        "  scitex-io print-shell-completion   --shell <bash|zsh|fish>",
        err=True,
    )
    ctx.exit(2)


# §1a: install-shell-completion + print-shell-completion (canonical leaves)
try:
    from scitex_dev._cli._completion import attach_shell_completion

    attach_shell_completion(main, prog_name="scitex-io")
except ImportError:
    pass


main.add_command(load_configs_cmd, "load-configs")
main.add_command(configs_deprecated, "configs")  # hidden redirect
main.add_command(show_info, "show-info")
main.add_command(info_deprecated, "info")  # hidden redirect
main.add_command(list_python_apis, "list-python-apis")
main.add_command(mcp)
main.add_command(version_cmd, "version")

try:
    from scitex_dev.cli import docs_click_group

    main.add_command(docs_click_group(package="scitex-io"))
except ImportError:
    pass

from ._skills import skills_group

main.add_command(skills_group)
