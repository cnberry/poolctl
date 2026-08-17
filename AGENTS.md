# Repository guidance

## Purpose

`poolctl` is a terminal-first Pentair ScreenLogic inspection and control tool.
Keep the reusable protocol/control layer separate from presentation, and keep
the installed CLI useful without requiring repository knowledge.

## Engineering principles

- Read state before adding or performing a write.
- Keep commands small, explicit, and scriptable.
- Treat live pool hardware as safety-sensitive.
- Require a deliberate guard for every mutating command.
- Report post-write state instead of equating request acceptance with success.
- Keep real adapter names, IPs, and site topology outside the public repository.
- Preserve compact human output and stable JSON output.
- Test pure selection, rendering, configuration, and protocol logic without
  requiring live hardware.
- Update `README.md`, `SKILL.md`, and relevant files under `docs/` when command
  behavior changes.
- Maintain `script/install` as the language-neutral deployment contract. A
  future Rust migration changes that script, not private bootstrap callers.

## Layout

- `poolctl/gateway.py` — discovery, cached adapter resolution, and status fetch
- `poolctl/config.py` — private local adapter configuration
- `poolctl/render.py` — summary shaping and human-readable output
- `poolctl/control.py` — guarded cleaner and delay helpers
- `poolctl/protocol.py` — protocol behavior missing from `screenlogicpy`
- `poolctl/cli.py` — command-line parser and dispatch
- `script/install` — stable installer entry point for deployment automation
- `tests/` — hardware-free unit tests
- `docs/` — operations, protocol, troubleshooting, and roadmap notes

## Development

Use the private home-ops bootstrap for installed use and `.venv` for development. Run the full
format, lint, secret-scan, and test sequence documented in `README.md` before
publishing. Never make a live hardware write as part of an automated test.
