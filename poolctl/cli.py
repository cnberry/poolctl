from __future__ import annotations

import argparse
import asyncio
import json

from poolctl.control import cancel_delay, cleaner_status, delay_status, set_circuit_state
from poolctl.gateway import discover_adapter, fetch_status
from poolctl.render import render_bodies, render_circuits, render_pumps, render_status, summarize


async def async_main() -> None:
    parser = argparse.ArgumentParser(prog="poolctl")
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover_parser = subparsers.add_parser("discover")
    discover_parser.add_argument("--json", action="store_true")

    for command in ("status", "circuits", "bodies", "pumps"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--json", action="store_true")
        if command == "status":
            sub.add_argument("--raw", action="store_true")

    cleaner_parser = subparsers.add_parser("cleaner")
    cleaner_sub = cleaner_parser.add_subparsers(dest="cleaner_command", required=True)
    cleaner_status_parser = cleaner_sub.add_parser("status")
    cleaner_status_parser.add_argument("--json", action="store_true")
    for name in ("on", "off"):
        cmd = cleaner_sub.add_parser(name)
        cmd.add_argument("--yes", action="store_true", help="actually perform the hardware write")
        cmd.add_argument("--json", action="store_true")

    delay_parser = subparsers.add_parser("delay")
    delay_sub = delay_parser.add_subparsers(dest="delay_command", required=True)
    delay_status_parser = delay_sub.add_parser("status")
    delay_status_parser.add_argument("--json", action="store_true")
    delay_cancel_parser = delay_sub.add_parser("cancel")
    delay_cancel_parser.add_argument("--yes", action="store_true", help="actually perform the hardware write")
    delay_cancel_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "discover":
        adapter = await discover_adapter()
        if args.json:
            print(json.dumps(adapter, indent=2, sort_keys=True))
        else:
            print(f"{adapter['name']} @ {adapter['ip']}:{adapter['port']}")
        return

    if args.command == "cleaner":
        if args.cleaner_command == "status":
            status = await cleaner_status()
            if args.json:
                print(json.dumps(status, indent=2, sort_keys=True, default=str))
            else:
                circuit = status["circuit"]
                delay = status["delay"]
                print(f"Cleaner: {circuit['state']} (circuit {circuit['id']}: {circuit['name']})")
                print(f"Delays: cleaner={delay['cleaner']} pool={delay['pool']} spa={delay['spa']}")
            return

        enabled = args.cleaner_command == "on"
        if not args.yes:
            action = "on" if enabled else "off"
            raise SystemExit(f"Refusing to turn cleaner {action} without --yes. Run: poolctl cleaner {action} --yes")

        result = await set_circuit_state("Cleaner", enabled)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True, default=str))
        else:
            requested = result["requested"]
            current = result["current"]
            print(f"Requested cleaner {'on' if requested['enabled'] else 'off'}; current state is {current['state']}")
            print(f"Delay before: cleaner={result['delay_before']['cleaner']} pool={result['delay_before']['pool']} spa={result['delay_before']['spa']}")
            print(f"Delay after:  cleaner={result['delay_after']['cleaner']} pool={result['delay_after']['pool']} spa={result['delay_after']['spa']}")
        return

    if args.command == "delay":
        if args.delay_command == "status":
            status = await delay_status()
            if args.json:
                print(json.dumps(status, indent=2, sort_keys=True, default=str))
            else:
                print(f"Delays: cleaner={status['cleaner']} pool={status['pool']} spa={status['spa']}")
            return

        if not args.yes:
            raise SystemExit("Refusing to cancel delays without --yes. Run: poolctl delay cancel --yes")

        result = await cancel_delay()
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True, default=str))
        else:
            before = result['before']
            after = result['after']
            print(f"Delay before: cleaner={before['cleaner']} pool={before['pool']} spa={before['spa']}")
            print(f"Delay after:  cleaner={after['cleaner']} pool={after['pool']} spa={after['spa']}")
        return

    payload = await fetch_status()
    if args.command == "status" and args.raw:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
        return

    summary = summarize(payload)
    if args.json:
        if args.command == "status":
            print(json.dumps(summary, indent=2, sort_keys=True, default=str))
        elif args.command == "circuits":
            print(json.dumps(summary["circuits"], indent=2, sort_keys=True, default=str))
        elif args.command == "bodies":
            print(json.dumps(summary["bodies"], indent=2, sort_keys=True, default=str))
        elif args.command == "pumps":
            print(json.dumps(summary["pumps"], indent=2, sort_keys=True, default=str))
        return

    if args.command == "status":
        print(render_status(summary))
    elif args.command == "circuits":
        print(render_circuits(summary))
    elif args.command == "bodies":
        print(render_bodies(summary))
    elif args.command == "pumps":
        print(render_pumps(summary))


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
