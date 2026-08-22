# Operations and safety

## Read before write

Use `poolctl cleaner status` or `poolctl delay status` before a write when the
requested action or current state is unclear. All writes require `--yes`; this
flag is a deliberate automation guard, not evidence that the physical area is
safe.

## Cleaner enable sequence

`poolctl cleaner on --yes`:

1. reads the current delay state;
2. cancels an active cleaner delay;
3. resolves the single circuit named `Cleaner`;
4. writes the enabled state;
5. refreshes controller data; and
6. reports post-action cleaner and delay state.

Circuit selection refuses missing or ambiguous matches. The CLI does not expose
a general arbitrary-circuit write command.

## Delay cancellation

`poolctl delay cancel --yes` sends the pinned ScreenLogic cancel-delay request,
refreshes controller state, and reports cleaner, pool, and spa delay values.
Canceling a delay can cause scheduled equipment to resume; inspect the system
and physical area first.

## Pool and spa heat

Use `poolctl heat status` before a heat write. Mode changes accept only `off`,
`solar`, `solar-preferred`, or `heater`; temperature changes must fall within
the selected body's controller-reported minimum and maximum. Exact body names
and numeric IDs are accepted, and every write requires `--yes`.

Both heat write commands refresh the controller and return `status_before` and
`status_after`. Treat the returned state as authoritative; request acceptance
alone is not success.

## Live validation

Automated tests never contact pool hardware. Before a release that changes write
behavior, validate status and guarded write/readback behavior on supervised
equipment, recording only sanitized results. Do not change live heat settings
solely for an automated deployment check.
