# poolctl

A terminal-first Pentair ScreenLogic exploration and control tool.

## Goals

- Discover Pentair ScreenLogic adapters on the local network
- Inspect pool configuration and current state
- Provide a clean CLI for common control actions
- Evolve into a reusable library + CLI split

## Status

Early reconnaissance project, now split into a small package + CLI with basic unit tests.

## Commands

- `poolctl discover`
- `poolctl status`
- `poolctl circuits`
- `poolctl bodies`
- `poolctl pumps`

JSON output is available with `--json`, and raw status payloads can be dumped with:

- `poolctl status --raw`

## Development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install pytest
PYTHONPATH=. pytest -q
python poolctl.py status
```
