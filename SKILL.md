---
name: poolctl
description: Inspect and control a local Pentair ScreenLogic pool system with the poolctl CLI. Use for pool status, circuits, bodies, pumps, cleaner state, heat mode and setpoint, cleaner control, and delay inspection or cancellation.
---

# poolctl

Use the installed `poolctl` CLI instead of ad-hoc protocol calls when a command
already exists.

## Safety rules

- Read state before a write when the request or current state is ambiguous.
- Treat adapter IPs, names, and raw payloads as private deployment data.
- Use `--yes` only after the requested equipment and action are clear.
- Report final state from the command, not merely that a write was submitted.
- Never invent support for an arbitrary circuit; the public write surface is
  intentionally limited to cleaner, delay, and pool/spa heat commands.

## Commands

```bash
poolctl discover
poolctl status
poolctl circuits
poolctl bodies
poolctl pumps
poolctl cleaner status
poolctl cleaner on --yes
poolctl cleaner off --yes
poolctl delay status
poolctl delay cancel --yes
poolctl heat status
poolctl heat set pool solar-preferred --yes
poolctl heat temp pool 88 --yes
```

Use `--json` for structured results. Put a one-off direct host before the
subcommand, for example `poolctl --host 192.0.2.10 status`.

Cleaner enable already checks and cancels cleaner delay when necessary, then
reports the post-action cleaner and delay state. If a command fails, quote the
short error and do not claim the hardware reached the requested state.

Heat writes require an exact body name or ID and `--yes`. Read the current heat
status first when the requested mode or setpoint is ambiguous, and report the
returned `status_after` rather than assuming the request succeeded.
