from __future__ import annotations

from typing import Any

from screenlogicpy import ScreenLogicGateway

from poolctl.gateway import discover_adapter, fetch_status
from poolctl.render import summarize


def normalize_name(value: str) -> str:
    return " ".join(value.strip().lower().split())


def find_circuit(summary: dict[str, Any], query: str) -> dict[str, Any]:
    q = normalize_name(query)
    exact = [c for c in summary["circuits"] if normalize_name(c["name"]) == q]
    if len(exact) == 1:
        return exact[0]
    partial = [c for c in summary["circuits"] if q in normalize_name(c["name"])]
    if len(partial) == 1:
        return partial[0]
    if not partial:
        raise ValueError(f"No circuit matched {query!r}")
    names = ", ".join(c["name"] for c in partial)
    raise ValueError(f"Ambiguous circuit name {query!r}: {names}")


async def cleaner_status() -> dict[str, Any]:
    payload = await fetch_status()
    summary = summarize(payload)
    sensors = payload["data"].get("controller", {}).get("sensor", {})
    circuit = find_circuit(summary, "cleaner")
    return {
        "circuit": circuit,
        "delay": {
            "cleaner": sensors.get("cleaner_delay", {}).get("value"),
            "pool": sensors.get("pool_delay", {}).get("value"),
            "spa": sensors.get("spa_delay", {}).get("value"),
        },
    }


async def set_circuit_state(circuit_name: str, enabled: bool) -> dict[str, Any]:
    payload = await fetch_status()
    summary = summarize(payload)
    circuit = find_circuit(summary, circuit_name)

    adapter = await discover_adapter()
    gateway = ScreenLogicGateway()
    await gateway.async_connect(**adapter)
    try:
        await gateway.async_set_circuit(circuit["id"], 1 if enabled else 0)
        await gateway.async_update()
        updated = summarize({"adapter": adapter, "data": gateway.get_data()})
        return {
            "requested": {"name": circuit["name"], "id": circuit["id"], "enabled": enabled},
            "current": find_circuit(updated, circuit["name"]),
        }
    finally:
        await gateway.async_disconnect()
