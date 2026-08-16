# Roadmap

## Proven surface

- LAN adapter discovery and private caching
- compact controller, body, circuit, pump, and sensor status
- JSON and raw diagnostic output
- guarded cleaner on/off with delay handling and post-write readback
- guarded delay cancellation

## Next

- remove reliance on private `screenlogicpy` attributes for delay cancellation;
- add mocked CLI dispatch tests and stable JSON-schema notes;
- improve errors for discovery, timeout, and protocol-version failures;
- document supervised validation across more ScreenLogic controller families.

## Out of scope by default

- arbitrary circuit writes;
- unattended safety-critical automation;
- storing public site topology or credentials;
- claiming broad hardware compatibility without validation.
