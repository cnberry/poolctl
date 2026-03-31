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
- `poolctl status`
- `poolctl circuits`
- `poolctl bodies`
- `poolctl pumps`
- `poolctl cleaner status`
- `poolctl cleaner on --yes`  _(tries enable first, then cancels cleaner delay if needed)_
- `poolctl cleaner off --yes`

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

## Notes for agents and future-us

See `AGENTS.md` for project principles, current shape, and the near-term roadmap.
