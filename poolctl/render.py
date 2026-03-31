from __future__ import annotations

from typing import Any


def enum_value(field: dict[str, Any] | None) -> Any:
    if not field:
        return None
    options = field.get("enum_options") or []
    value = field.get("value")
    if isinstance(value, int) and 0 <= value < len(options):
        return options[value]
    return value


def onoff(value: int) -> str:
    return "on" if value else "off"


def summarize(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload["data"]
    controller = data.get("controller", {})
    sensors = controller.get("sensor", {})
    bodies = data.get("body", {})
    circuits = data.get("circuit", {})
    pumps = data.get("pump", {})

    body_summary = {}
    for body_id, body in bodies.items():
        body_summary[body_id] = {
            "name": body.get("name"),
            "temp_f": body.get("last_temperature", {}).get("value"),
            "heat_mode": enum_value(body.get("heat_mode")),
            "heat_setpoint_f": body.get("heat_setpoint", {}).get("value"),
            "heat_state": enum_value(body.get("heat_state")),
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


def render_status(summary: dict[str, Any]) -> str:
    lines = [
        f"Adapter: {summary['adapter']['name']} @ {summary['adapter']['ip']}:{summary['adapter']['port']}",
        f"Model:   {summary['model']}",
        f"Air:     {summary['air_temp_f']}°F",
        f"Salt:    {summary['salt_ppm']} ppm",
        "",
        "Bodies:",
    ]
    for body in summary["bodies"].values():
        lines.append(
            f"  - {body['name']}: temp={body['temp_f']}°F heat_mode={body['heat_mode']} setpoint={body['heat_setpoint_f']}°F heat_state={body['heat_state']}"
        )

    lines.extend(["", "Pumps:"])
    for pump_id, pump in summary["pumps"].items():
        lines.append(
            f"  - pump {pump_id}: {pump['state']} rpm={pump['rpm']} watts={pump['watts']} gpm={pump['gpm']}"
        )

    lines.extend(["", "Circuits:"])
    for circuit in summary["circuits"]:
        lines.append(f"  - {circuit['id']}: {circuit['name']} [{circuit['state']}]")

    return "\n".join(lines)


def render_circuits(summary: dict[str, Any]) -> str:
    return "\n".join(
        f"{circuit['id']:>3}  {circuit['state']:<3}  {circuit['name']}"
        for circuit in summary["circuits"]
    )


def render_bodies(summary: dict[str, Any]) -> str:
    return "\n".join(
        f"{body['name']}: {body['temp_f']}°F, heat_mode={body['heat_mode']}, setpoint={body['heat_setpoint_f']}°F, heat_state={body['heat_state']}"
        for body in summary["bodies"].values()
    )


def render_pumps(summary: dict[str, Any]) -> str:
    return "\n".join(
        f"pump {pump_id}: {pump['state']} rpm={pump['rpm']} watts={pump['watts']} gpm={pump['gpm']}"
        for pump_id, pump in summary["pumps"].items()
    )
