from __future__ import annotations

import argparse
import asyncio
import json

from poolctl.control import (
    HEAT_MODES,
    cancel_delay,
    cleaner_status,
    delay_status,
    heat_status,
    set_circuit_state,
    set_heat_mode,
    set_heat_temp,
)
from poolctl.gateway import discover_adapter, fetch_status
from poolctl.render import render_bodies, render_circuits, render_pumps, render_status, summarize


async def async_main() -> None:
    parser = argparse.ArgumentParser(prog="poolctl")
    parser.add_argument("--host", help="connect directly to a specific ScreenLogic adapter IP")
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
    delay_cancel_parser.add_argument(
        "--yes", action="store_true", help="actually perform the hardware write"
    )
    delay_cancel_parser.add_argument("--json", action="store_true")

    heat_parser = subparsers.add_parser("heat")
    heat_sub = heat_parser.add_subparsers(dest="heat_command", required=True)
    heat_status_parser = heat_sub.add_parser("status")
    heat_status_parser.add_argument("body", nargs="?", help="body name or numeric ID")
    heat_status_parser.add_argument("--json", action="store_true")
    heat_set_parser = heat_sub.add_parser("set")
    heat_set_parser.add_argument("body", help="body name or numeric ID")
    heat_set_parser.add_argument("mode", choices=tuple(HEAT_MODES))
    heat_set_parser.add_argument(
        "--yes", action="store_true", help="actually perform the hardware write"
    )
    heat_set_parser.add_argument("--json", action="store_true")
    heat_temp_parser = heat_sub.add_parser("temp")
    heat_temp_parser.add_argument("body", help="body name or numeric ID")
    heat_temp_parser.add_argument("temperature", type=int)
    heat_temp_parser.add_argument(
        "--yes", action="store_true", help="actually perform the hardware write"
    )
    heat_temp_parser.add_argument("--json", action="store_true")

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
            status = await cleaner_status(args.host)
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
            raise SystemExit(
                f"Refusing to turn cleaner {action} without --yes. Run: poolctl cleaner {action} --yes"
            )

        delay_before = await delay_status(args.host)
        cancelled_delay = None
        if enabled and delay_before.get("cleaner", 0):
            cancelled_delay = await cancel_delay(args.host)

        result = await set_circuit_state("Cleaner", enabled, args.host)
        status_after = await cleaner_status(args.host)
        payload = {
            "requested": "on" if enabled else "off",
            "delay_before": delay_before,
            "delay_cancelled": cancelled_delay,
            "result": result,
            "status_after": status_after,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, default=str))
        else:
            state = status_after["circuit"]["state"]
            delay = status_after["delay"]
            if cancelled_delay is not None:
                print("Delay cancelled before cleaner enable.")
            print(f"Cleaner: {state}")
            print(f"Delays: cleaner={delay['cleaner']} pool={delay['pool']} spa={delay['spa']}")
        return

    if args.command == "delay":
        if args.delay_command == "status":
            status = await delay_status(args.host)
            if args.json:
                print(json.dumps(status, indent=2, sort_keys=True, default=str))
            else:
                print(
                    f"Delays: cleaner={status['cleaner']} pool={status['pool']} spa={status['spa']}"
                )
            return

        if not args.yes:
            raise SystemExit(
                "Refusing to cancel delays without --yes. Run: poolctl delay cancel --yes"
            )

        result = await cancel_delay(args.host)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True, default=str))
        else:
            print(f"Delays: cleaner={result['cleaner']} pool={result['pool']} spa={result['spa']}")
        return

    if args.command == "heat":
        if args.heat_command == "status":
            status = await heat_status(args.body, args.host)
            if args.json:
                print(json.dumps(status, indent=2, sort_keys=True, default=str))
            elif args.body:
                print(
                    f"{status['name']}: {status['temp_f']}°F, heat_mode={status['heat_mode']}, "
                    f"setpoint={status['heat_setpoint_f']}°F, heat_state={status['heat_state']}"
                )
            else:
                print(render_bodies({"bodies": status}))
            return

        if not args.yes:
            if args.heat_command == "set":
                example = f"poolctl heat set {args.body} {args.mode} --yes"
            else:
                example = f"poolctl heat temp {args.body} {args.temperature} --yes"
            raise SystemExit(f"Refusing to change heat settings without --yes. Run: {example}")

        if args.heat_command == "set":
            result = await set_heat_mode(args.body, args.mode, args.host)
        else:
            result = await set_heat_temp(args.body, args.temperature, args.host)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True, default=str))
        else:
            status = result["status_after"]
            print(
                f"{status['name']}: {status['temp_f']}°F, heat_mode={status['heat_mode']}, "
                f"setpoint={status['heat_setpoint_f']}°F, heat_state={status['heat_state']}"
            )
        return

    payload = await fetch_status(args.host)
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
