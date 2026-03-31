from __future__ import annotations

import asyncio
from typing import Any

from screenlogicpy import ScreenLogicGateway

from poolctl.gateway import discover_adapter, fetch_status
from poolctl.protocol import async_request_cancel_delay
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


def delay_active(delay: dict[str, int | None]) -> bool:
    return any((delay.get("cleaner"), delay.get("pool"), delay.get("spa")))


def extract_delay(data: dict[str, Any]) -> dict[str, int | None]:
    sensors = data.get("controller", {}).get("sensor", {})
    return {
        "cleaner": sensors.get("cleaner_delay", {}).get("value"),
        "pool": sensors.get("pool_delay", {}).get("value"),
        "spa": sensors.get("spa_delay", {}).get("value"),
    }


async def settle_circuit_state(
    gateway: ScreenLogicGateway,
    adapter: dict[str, Any],
    circuit_name: str,
    *,
    attempts: int = 5,
    delay_seconds: float = 1.0,
) -> dict[str, Any]:
    snapshots = []
    last = None
    for _ in range(attempts):
        await asyncio.sleep(delay_seconds)
        await gateway.async_update()
        current_data = gateway.get_data()
        updated = summarize({"adapter": adapter, "data": current_data})
        current = find_circuit(updated, circuit_name)
        delay = extract_delay(current_data)
        last = {"current": current, "delay": delay}
        snapshots.append(last)
    return {"last": last, "snapshots": snapshots}


async def set_circuit_state(circuit_name: str, enabled: bool) -> dict[str, Any]:
    payload = await fetch_status()
    summary = summarize(payload)
    circuit = find_circuit(summary, circuit_name)
    before_delay = extract_delay(payload["data"])

    adapter = await discover_adapter()
    gateway = ScreenLogicGateway()
    await gateway.async_connect(**adapter)
    try:
        canceled_delay = False

        await gateway.async_set_circuit(circuit["id"], 1 if enabled else 0)
        await gateway.async_update()

        current_data = gateway.get_data()
        updated = summarize({"adapter": adapter, "data": current_data})
        current = find_circuit(updated, circuit["name"])
        current_delay = extract_delay(current_data)

        if enabled and current["state"] != "on" and current_delay.get("cleaner"):
            await async_request_cancel_delay(gateway._protocol, gateway._max_retries)
            canceled_delay = True
            await gateway.async_update()

        settled = await settle_circuit_state(gateway, adapter, circuit["name"])
        final_state = settled["last"] or {
            "current": current,
            "delay": current_delay,
        }
        return {
            "requested": {"name": circuit["name"], "id": circuit["id"], "enabled": enabled},
            "canceled_delay": canceled_delay,
            "delay_before": before_delay,
            "delay_after": final_state["delay"],
            "current": final_state["current"],
            "snapshots": settled["snapshots"],
            "confirmed": final_state["current"]["state"] == ("on" if enabled else "off"),
        }
    finally:
        await gateway.async_disconnect()
