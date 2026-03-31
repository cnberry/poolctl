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

- **Hide vendor friction only when explicitly desired.**
  Prefer small sharp commands over over-smart orchestration. Keep cleaner control and delay cancellation as separate explicit commands unless the user wants otherwise.

## Current shape

- `poolctl/gateway.py` — adapter discovery + live status fetch
- `poolctl/render.py` — summary shaping and human-readable output
- `poolctl/control.py` — small control helpers for cleaner and delay actions
- `poolctl/protocol.py` — protocol gaps not covered by screenlogicpy
- `poolctl/cli.py` — command-line entrypoint
- `tests/` — unit tests for pure logic/rendering

## Near-term roadmap

1. Robust circuit lookup by name/id
2. Dead-simple cleaner and delay commands
3. Better structured JSON output
4. Config file / adapter selection overrides
5. Optional Rust port later if the Python shape proves right

## Style

- Keep code boring and readable.
- Avoid needless framework energy.
- Prefer explicit names over magic.
- Don’t let the repo turn into app-store cosplay.

## Vibe

This project is a small terminal trident for poking a cursed pool box over the LAN.

🌊🤖🔱
