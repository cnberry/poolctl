from __future__ import annotations

import argparse
import asyncio
import json

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

    args = parser.parse_args()

    if args.command == "discover":
        adapter = await discover_adapter()
        if args.json:
            print(json.dumps(adapter, indent=2, sort_keys=True))
        else:
            print(f"{adapter['name']} @ {adapter['ip']}:{adapter['port']}")
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
