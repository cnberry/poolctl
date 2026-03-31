# poolctl 🌊🤖🔱

A terminal-first Pentair ScreenLogic exploration and control tool for taming a mildly cursed pool box over the LAN.

## Goals

- Discover Pentair ScreenLogic adapters on the local network
- Inspect pool configuration and current state
- Provide a clean CLI for common control actions
- Evolve into a reusable library + CLI split

## Status

Early reconnaissance project, now split into a small package + CLI with basic unit tests.
The interface is intentionally being simplified toward small, explicit commands rather than clever orchestration.

## Visual identity

```text
      .-.
   .-(   )-.        poolctl
  (___.__)__)       🌊🤖🔱
     /___\\
    /_____\\
```

## Commands

Core inspection:
- `poolctl discover`
- `poolctl status`
- `poolctl circuits`
- `poolctl bodies`
- `poolctl pumps`

Cleaner control:
- `poolctl cleaner status`
- `poolctl cleaner on --yes`
- `poolctl cleaner off --yes`

Delay control:
- `poolctl delay status`
- `poolctl delay cancel --yes`

Debugging / direct host override:
- `poolctl --host 192.168.4.33 status`

Default output is compact and human-readable. Use `--json` for structured output.
Raw status payloads can be dumped with:
- `poolctl status --raw`

## Development

Classic direct shell flow:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install pytest
PYTHONPATH=. pytest -q
python poolctl.py status
```

Or, if you have `just` installed:

```bash
just setup
just test
just status
just circuits
```

The adapter discovered on first successful discovery/connect is cached in:

- `~/.config/poolctl/config.json`

Subsequent commands use the configured adapter first, with discovery available as a fallback or explicit command.

## Maintenance rule

When a behavior or interface change feels like a keeper, update the docs immediately:
- `README.md` for user-facing changes
- `AGENTS.md` for project principles, workflow, and engineering intent

Clean code. Good code. Updated docs.

## Notes for agents and future-us

See `AGENTS.md` for project principles, current shape, and the near-term roadmap.
