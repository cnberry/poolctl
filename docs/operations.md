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

## Live validation

Automated tests never contact pool hardware. Before a release that changes write
behavior, validate status, cleaner off/on/off, and delay reporting on supervised
equipment, recording only sanitized results.
