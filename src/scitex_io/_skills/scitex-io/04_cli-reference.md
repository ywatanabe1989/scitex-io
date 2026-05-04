---
description: |
  [TOPIC] scitex-io CLI reference
  [DETAILS] Every subcommand with concrete examples — show-info, load-configs, list-python-apis, mcp, skills, version, shell-completion. Plus --help-recursive for the full tree.
tags: [scitex-io-cli-reference]
---

# CLI Reference

Run `scitex-io --help` for the live command list, or
`scitex-io --help-recursive` to dump help for every subcommand at
once.

## Top-level options

```bash
scitex-io --version            # print version
scitex-io -V
scitex-io --help               # categorized command list
scitex-io --help-recursive     # all commands and subcommands
scitex-io --json show-info     # propagate JSON output to subcommands
```

## Core I/O

```bash
scitex-io show-info                       # registered formats + version + paths
scitex-io load-configs                    # load ./config/*.yaml and pretty-print
scitex-io load-configs -d ./my_configs    # custom config directory
scitex-io load-configs --json             # JSON output
```

## Integration

```bash
scitex-io list-python-apis -vv            # public API with signatures
scitex-io mcp start                       # start the MCP server (needs [mcp] extra)
scitex-io mcp doctor                      # MCP health check
scitex-io mcp list-tools -vv              # MCP tools with parameters
```

## Skills (agent-facing docs)

```bash
scitex-io skills list                     # list bundled skill pages
scitex-io skills list --json
scitex-io skills get 02_quick-start       # print one skill page
scitex-io skills get 10_save-and-load --json

# Install (symlink _skills/scitex-io/ → ~/.scitex/dev/skills/scitex-io/)
scitex-io skills install
scitex-io skills install --claude-symlink # also expose to ~/.claude/skills/scitex/
scitex-io skills install --no-link        # copy instead of symlink
scitex-io skills install --dry-run        # preview without writing
```

## Utility

```bash
scitex-io version                         # version with build metadata
scitex-io shell-completion bash           # emit a completion script
scitex-io shell-completion zsh >> ~/.zshrc
scitex-io shell-completion fish > ~/.config/fish/completions/scitex-io.fish
```

## See also

- [03_python-api.md](03_python-api.md) — same surface in Python
- [20_env-vars.md](20_env-vars.md) — `SCITEX_IO_*` variables
- Full RTD: <https://scitex-io.readthedocs.io/en/latest/cli.html>
