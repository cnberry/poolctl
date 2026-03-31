# AGENTS.md

## What this repo is

`poolctl` is a terminal-first Pentair ScreenLogic exploration and control project.

The goal is not to build a bloated smart-home platform on day one. The goal is to build:
- a clean library layer
- a sharp CLI
- small, understandable commands
- enough protocol understanding to control real hardware safely

Think: UNIX tool, not enterprise sludge.

## Project principles

- **Library first, CLI immediately useful.**
  The protocol/control logic should be reusable, while the CLI stays pleasant for direct human use.

- **Read before write.**
  Prefer adding discovery, inventory, and state inspection before mutating commands.

- **Small commands, low surprise.**
  Commands should do one thing well and print useful output.

- **Test the rendering and logic layers.**
  Unit tests should cover summary/formatting/helpers even when live hardware tests are limited.

- **Treat live pool hardware with respect.**
  Avoid risky or surprising writes. Add guardrails around mutating commands.

- **Hide vendor friction when we understand it.**
  If the Pentair workflow requires nonsense like canceling delay before enabling the cleaner, `poolctl` should absorb that complexity.

## Current shape

- `poolctl/gateway.py` — adapter discovery + live status fetch
- `poolctl/render.py` — summary shaping and human-readable output
- `poolctl/cli.py` — command-line entrypoint
- `tests/` — unit tests for pure logic/rendering

## Near-term roadmap

1. Cleaner-focused smart control, especially clearing system delay before enabling the cleaner
2. Robust circuit lookup by name/id
3. Safe circuit on/off commands
4. Better structured JSON output
5. Config file / adapter selection overrides
6. Optional Rust port later if the Python shape proves right

## Style

- Keep code boring and readable.
- Avoid needless framework energy.
- Prefer explicit names over magic.
- Don’t let the repo turn into app-store cosplay.

## Vibe

This project is a small terminal trident for poking a cursed pool box over the LAN.

🌊🤖🔱
