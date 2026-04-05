# poolctl 🌊🤖🔱

A terminal-first Pentair ScreenLogic control tool for interrogating and nudging a mildly cursed pool box over the LAN.

`poolctl` is part of the same small-tool family as `lightctl` and `hottubctl`: sharp commands, readable output, no app-shaped nonsense.

## What it does

- discovers ScreenLogic adapters on the local network
- shows current pool/spa status in a compact CLI format
- inspects circuits, bodies, and pumps
- checks and controls the cleaner
- checks and cancels system delay state

## Install

```bash
git clone git@github.com:your-user/poolctl.git
cd poolctl
just install
```

That installs `poolctl` with `pipx` so it behaves like a normal command, not a repo you have to babysit.

Useful `just` targets:

```bash
just status
just circuits
just bodies
just pumps
just raw
```

## Local config

`poolctl` stores discovered adapter config here:
- `~/.config/poolctl/config.json`

That file is local machine state, not repo content.

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
- `poolctl --host 192.168.1.50 status`

Default output is compact and human-readable. Use `--json` for structured output.
Use `poolctl status --raw` when you want the raw payload.

## Development

For early development or protocol poking:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install pytest
PYTHONPATH=. pytest -q
python poolctl.py status
```

Once the CLI is useful, prefer the installed command shape via `just install` / `just reinstall`.

## Why this repo exists

The goal is not to build a giant pool platform. The goal is to make the useful 90% easy:
- inspect the system quickly
- script common actions
- avoid phone-app friction
- keep the interface boring enough to trust

## Notes for future cleanup

See `AGENTS.md` for project principles and engineering intent.
`SKILL.md` exists so the repo can be driven directly from an agent/chat workflow.
