---
name: poolctl
description: Control Chris's Pentair ScreenLogic pool setup from the local `poolctl` CLI. Use when asked to turn the pool cleaner on or off, check cleaner or delay status, cancel pool delays, inspect pool status/circuits/bodies/pumps, or otherwise operate the local pool system from this repo.
---

# poolctl

Use the local `poolctl` CLI from this repository.

## Rules

- Prefer the `poolctl` CLI over ad-hoc Python or direct protocol poking when the command already exists.
- Use the configured adapter by default.
- Keep responses short and action-oriented.
- For mutating commands, report the final compact CLI output, not internal debug details.
- If a requested behavior is not implemented in `poolctl`, say so plainly and then improve the CLI if appropriate.

## Run from repo root

```bash
cd REPO_ROOT/poolctl
. .venv/bin/activate
```

## Command map

### Cleaner

```bash
poolctl cleaner status
poolctl cleaner on --yes
poolctl cleaner off --yes
```

Use for requests like:
- "turn on my pool cleaner"
- "turn off the cleaner"
- "is the pool cleaner on?"

### Delays

```bash
poolctl delay status
poolctl delay cancel --yes
```

Use for requests like:
- "cancel pool delays"
- "clear system delay"
- "is there a cleaner delay?"

### General inspection

```bash
poolctl status
poolctl circuits
poolctl bodies
poolctl pumps
poolctl discover
```

### Direct host override

Only use when debugging or explicitly requested:

```bash
poolctl --host 192.168.1.50 status
```

## Chat-level workflow

When Chris says "turn on my pool cleaner", prefer this sequence:
1. `poolctl cleaner on --yes`
2. `poolctl cleaner status`
3. if cleaner is still off and cleaner delay is active, run `poolctl delay cancel --yes`
4. `poolctl cleaner status` again
5. report the final concise result

## Response style

Examples:
- "Done. Cleaner: on"
- "Done. Delays: cleaner=0 pool=0 spa=0"
- "Cleaner: off"

If a command fails, quote the relevant error briefly and say what you’ll do next.
