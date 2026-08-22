# Protocol notes

`poolctl` uses `screenlogicpy` for adapter discovery, connection, state refresh,
cleaner-circuit writes, heat-mode writes, and heat-setpoint writes. The adapter
is normally discovered by LAN broadcast and cached outside the repository.

Heat control uses the dependency's public `async_set_heat_mode` and
`async_set_heat_temp` methods. `poolctl` resolves an exact body, validates the
controller-provided temperature range, performs the write, refreshes state, and
returns both pre-write and post-write body data.

Delay cancellation is implemented in `poolctl/protocol.py` because the pinned
dependency does not expose that request as a public helper. The request opcode
is locked by a unit test. The implementation currently needs two private
`screenlogicpy` gateway attributes; dependency upgrades therefore require a
focused compatibility review and supervised hardware validation.

Equipment names, sensors, pumps, and body fields vary by controller and site
configuration. Human output is a curated summary; `status --raw` exists for
diagnosis and should not be treated as a stable public schema.
