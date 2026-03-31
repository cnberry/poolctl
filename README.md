# poolctl 🌊🤖🔱

A terminal-first Pentair ScreenLogic exploration and control tool for taming a mildly cursed pool box over the LAN.

## Goals

- Discover Pentair ScreenLogic adapters on the local network
- Inspect pool configuration and current state
- Provide a clean CLI for common control actions
- Evolve into a reusable library + CLI split

## Status

Early reconnaissance project, now split into a small package + CLI with basic unit tests.

## Visual identity

```text
      .-.
   .-(   )-.        poolctl
  (___.__)__)       🌊🤖🔱
     /___\\
    /_____\\
```

## Commands

- `poolctl discover`
- `poolctl --host 192.168.4.33 status`
- `poolctl status`
- `poolctl circuits`
- `poolctl bodies`
- `poolctl pumps`
- `poolctl cleaner status`
- `poolctl cleaner on --yes`
- `poolctl cleaner off --yes`
- `poolctl delay status`
- `poolctl delay cancel --yes`

JSON output is available with `--json`, and raw status payloads can be dumped with:

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

## Notes for agents and future-us

See `AGENTS.md` for project principles, current shape, and the near-term roadmap.
