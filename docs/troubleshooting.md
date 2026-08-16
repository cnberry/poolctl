# Troubleshooting

## No adapter is discovered

- Run from the same local network as the ScreenLogic adapter.
- Check client isolation, VLAN, VPN, and broadcast-filtering settings.
- Try a one-off direct host: `poolctl --host 192.0.2.10 status`.
- Delete or replace the private adapter cache if its address changed.

## A cached adapter no longer responds

Without `--host`, `poolctl` falls back to discovery after a failed cached
connection and saves the newly discovered adapter. A direct host failure is
returned without silently choosing a different controller.

## Cleaner lookup fails

The guarded command requires one unambiguous circuit matching `Cleaner`. Inspect
`poolctl circuits` and verify the controller's circuit name. The CLI intentionally
does not guess among several partial matches.

## A write is refused

Mutating commands require `--yes`. Re-run only after verifying the intended
equipment and that the physical area is clear.
