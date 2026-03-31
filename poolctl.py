import argparse
import asyncio
import json
from typing import Any

from screenlogicpy import ScreenLogicGateway, discovery


async def discover_adapter() -> dict[str, Any]:
    hosts = await discovery.async_discover()
    if not hosts:
        raise RuntimeError("No ScreenLogic adapters discovered on local subnet")
    return hosts[0]


async def fetch_status() -> dict[str, Any]:
    adapter = await discover_adapter()
    gateway = ScreenLogicGateway()
    await gateway.async_connect(**adapter)
    try:
        await gateway.async_update()
        data = gateway.get_data()
        return {"adapter": adapter, "data": data}
    finally:
        await gateway.async_disconnect()


def summarize(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload["data"]
    controller = data.get("controller", {})
    sensors = controller.get("sensor", {})
    bodies = data.get("body", {})
    circuits = data.get("circuit", {})
    pumps = data.get("pump", {})

    def onoff(value: int) -> str:
        return "on" if value else "off"

    body_summary = {}
    for body_id, body in bodies.items():
        body_summary[body_id] = {
            "name": body.get("name"),
            "temp_f": body.get("last_temperature", {}).get("value"),
            "heat_mode": body.get("heat_mode", {}).get("enum_options", [])[body.get("heat_mode", {}).get("value", 0)] if body.get("heat_mode") else None,
            "heat_setpoint_f": body.get("heat_setpoint", {}).get("value"),
            "heat_state": body.get("heat_state", {}).get("enum_options", [])[body.get("heat_state", {}).get("value", 0)] if body.get("heat_state") else None,
        }

    circuit_summary = []
    for _, circuit in sorted(circuits.items(), key=lambda item: int(item[0])):
        circuit_summary.append(
            {
                "id": circuit.get("circuit_id"),
                "name": circuit.get("name"),
                "state": onoff(circuit.get("value", 0)),
                "function": circuit.get("function"),
                "interface": circuit.get("interface"),
            }
        )

    pump_summary = {}
    for pump_id, pump in pumps.items():
        if pump.get("data", 0) == 0:
            continue
        pump_summary[pump_id] = {
            "state": onoff(pump.get("state", {}).get("value", 0)),
            "rpm": pump.get("rpm_now", {}).get("value"),
            "watts": pump.get("watts_now", {}).get("value"),
            "gpm": pump.get("gpm_now", {}).get("value"),
        }

    return {
        "adapter": payload["adapter"],
        "model": controller.get("model", {}).get("value"),
        "air_temp_f": sensors.get("air_temperature", {}).get("value"),
        "salt_ppm": sensors.get("salt_ppm", {}).get("value"),
        "bodies": body_summary,
        "circuits": circuit_summary,
        "pumps": pump_summary,
    }


async def main() -> None:
    parser = argparse.ArgumentParser(prog="poolctl")
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover_parser = subparsers.add_parser("discover")
    discover_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--json", action="store_true")
    status_parser.add_argument("--raw", action="store_true")

    args = parser.parse_args()

    if args.command == "discover":
        adapter = await discover_adapter()
        if args.json:
            print(json.dumps(adapter, indent=2, sort_keys=True))
        else:
            print(f"{adapter['name']} @ {adapter['ip']}:{adapter['port']}")
        return

    if args.command == "status":
        payload = await fetch_status()
        if args.raw:
            print(json.dumps(payload, indent=2, sort_keys=True, default=str))
            return
        summary = summarize(payload)
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True, default=str))
            return

        print(f"Adapter: {summary['adapter']['name']} @ {summary['adapter']['ip']}:{summary['adapter']['port']}")
        print(f"Model:   {summary['model']}")
        print(f"Air:     {summary['air_temp_f']}°F")
        print(f"Salt:    {summary['salt_ppm']} ppm")
        print()
        print("Bodies:")
        for body in summary["bodies"].values():
            print(
                f"  - {body['name']}: temp={body['temp_f']}°F heat_mode={body['heat_mode']} setpoint={body['heat_setpoint_f']}°F heat_state={body['heat_state']}"
            )
        print()
        print("Pumps:")
        for pump_id, pump in summary["pumps"].items():
            print(f"  - pump {pump_id}: {pump['state']} rpm={pump['rpm']} watts={pump['watts']} gpm={pump['gpm']}")
        print()
        print("Circuits:")
        for circuit in summary["circuits"]:
            print(f"  - {circuit['id']}: {circuit['name']} [{circuit['state']}]")


if __name__ == "__main__":
    asyncio.run(main())
