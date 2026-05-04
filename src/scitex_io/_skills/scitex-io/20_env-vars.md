---
description: |
  [TOPIC] Environment variables
  [DETAILS] Env vars read by scitex-io at import/runtime. No user-tunable
  knobs; only optional-dependency presence flags (SCITEX_*_AVAILABLE).
tags: [scitex-io-env-vars, scitex-io, scitex-package]
---

# scitex-io — Environment Variables

scitex-io has **no user-tunable env vars**. The `SCITEX_*` strings found in the
source are optional-dependency probes (feature flags set implicitly by whether
a sibling package imports cleanly) and completion markers, not config knobs.

| Variable | Purpose | Default | Type |
|---|---|---|---|
| `SCITEX_ERRORS_AVAILABLE` | Presence flag: set when `scitex_errors` importable; gates rich error types. | unset | bool (presence) |
| `SCITEX_LOGGING_AVAILABLE` | Presence flag: set when `scitex_logging` importable; gates logger attach. | unset | bool (presence) |
| `SCITEX_IO_COMPLETE` | Internal sentinel for standalone-vs-umbrella detection. | unset | bool (presence) |
| `SCITEX_ONLY` | Cross-package sentinel used by downstream loaders; scitex-io only reads it. | unset | bool (presence) |

## Notes

- None of the above are intended to be set by end users.
- Add any future user-facing knobs under the `SCITEX_IO_*` prefix per ecosystem convention.

## Audit

```bash
grep -rhoE 'SCITEX_[A-Z0-9_]+' $HOME/proj/scitex-io/src/ | sort -u
```
