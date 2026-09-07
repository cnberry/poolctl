from __future__ import annotations

from typing import Any

from screenlogicpy import ScreenLogicGateway

from poolctl.gateway import fetch_status, resolve_adapter
from poolctl.protocol import async_request_cancel_delay
from poolctl.render import summarize

HEAT_MODES = {
    "off": 0,
    "solar": 1,
    "solar-preferred": 2,
    "heater": 3,
}


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


def find_body(summary: dict[str, Any], query: str) -> dict[str, Any]:
    q = normalize_name(query)
    matches = [
        body
        for body in summary["bodies"].values()
        if q in {normalize_name(str(body.get("name", ""))), str(body.get("id"))}
    ]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ValueError(f"No body matched {query!r}")
    names = ", ".join(str(body.get("name") or body.get("id")) for body in matches)
    raise ValueError(f"Ambiguous body {query!r}: {names}")


def extract_delay(data: dict[str, Any]) -> dict[str, int | None]:
    sensors = data.get("controller", {}).get("sensor", {})
    return {
        "cleaner": sensors.get("cleaner_delay", {}).get("value"),
        "pool": sensors.get("pool_delay", {}).get("value"),
        "spa": sensors.get("spa_delay", {}).get("value"),
    }


async def cleaner_status(host: str | None = None) -> dict[str, Any]:
    payload = await fetch_status(host)
    summary = summarize(payload)
    circuit = find_circuit(summary, "cleaner")
    return {
        "circuit": circuit,
        "delay": extract_delay(payload["data"]),
    }


async def delay_status(host: str | None = None) -> dict[str, int | None]:
    payload = await fetch_status(host)
    return extract_delay(payload["data"])


async def heat_status(body_name: str | None = None, host: str | None = None) -> dict[str, Any]:
    summary = summarize(await fetch_status(host))
    if body_name is None:
        return summary["bodies"]
    return find_body(summary, body_name)


async def set_heat_mode(body_name: str, mode: str, host: str | None = None) -> dict[str, Any]:
    if mode not in HEAT_MODES:
        choices = ", ".join(HEAT_MODES)
        raise ValueError(f"Invalid heat mode {mode!r}; choose from: {choices}")

    adapter = await resolve_adapter(host)
    gateway = ScreenLogicGateway()
    await gateway.async_connect(**adapter)
    try:
        await gateway.async_update()
        before = find_body(summarize({"adapter": adapter, "data": gateway.get_data()}), body_name)
        await gateway.async_set_heat_mode(int(before["id"]), HEAT_MODES[mode])
        await gateway.async_update()
        after = find_body(summarize({"adapter": adapter, "data": gateway.get_data()}), body_name)
        return {
            "requested": {"body": body_name, "mode": mode},
            "status_before": before,
            "status_after": after,
        }
    finally:
        await gateway.async_disconnect()


async def set_heat_temp(
    body_name: str, temperature: int, host: str | None = None
) -> dict[str, Any]:
    adapter = await resolve_adapter(host)
    gateway = ScreenLogicGateway()
    await gateway.async_connect(**adapter)
    try:
        await gateway.async_update()
        before = find_body(summarize({"adapter": adapter, "data": gateway.get_data()}), body_name)
        minimum = before.get("min_setpoint_f")
        maximum = before.get("max_setpoint_f")
        if isinstance(minimum, (int, float)) and isinstance(maximum, (int, float)):
            if not minimum <= temperature <= maximum:
                raise ValueError(
                    f"Temperature for {before['name']} must be between {minimum} and {maximum}°F"
                )
        await gateway.async_set_heat_temp(int(before["id"]), temperature)
        await gateway.async_update()
        after = find_body(summarize({"adapter": adapter, "data": gateway.get_data()}), body_name)
        return {
            "requested": {"body": body_name, "temperature_f": temperature},
            "status_before": before,
            "status_after": after,
        }
    finally:
        await gateway.async_disconnect()


async def set_circuit_state(
    circuit_name: str, enabled: bool, host: str | None = None
) -> dict[str, Any]:
    payload = await fetch_status(host)
    summary = summarize(payload)
    circuit = find_circuit(summary, circuit_name)

    adapter = await resolve_adapter(host)
    gateway = ScreenLogicGateway()
    await gateway.async_connect(**adapter)
    try:
        await gateway.async_set_circuit(circuit["id"], 1 if enabled else 0)
        await gateway.async_update()
        current_data = gateway.get_data()
        updated = summarize({"adapter": adapter, "data": current_data})
        return find_circuit(updated, circuit["name"])
    finally:
        await gateway.async_disconnect()


async def cancel_delay(host: str | None = None) -> dict[str, int | None]:
    adapter = await resolve_adapter(host)
    gateway = ScreenLogicGateway()
    await gateway.async_connect(**adapter)
    try:
        await async_request_cancel_delay(gateway._protocol, gateway._max_retries)
        await gateway.async_update()
        return extract_delay(gateway.get_data())
    finally:
        await gateway.async_disconnect()


def find_pool_circuit(summary: dict[str, Any]) -> dict[str, Any]:
    matches = [c for c in summary["circuits"] if normalize_name(c["name"]) == "pool"]
    if len(matches) != 1:
        raise ValueError("Expected exactly one circuit named Pool")
    return matches[0]


async def pump_status(host: str | None = None) -> dict[str, Any]:
    payload = await fetch_status(host)
    summary = summarize(payload)
    return {
        "circuit": find_pool_circuit(summary),
        "pumps": summary["pumps"],
        "delay": extract_delay(payload["data"]),
    }


async def set_pool_pump(enabled: bool, host: str | None = None) -> dict[str, Any]:
    """Control Pool circulation; controller interlocks and delays remain in force."""
    adapter = await resolve_adapter(host)
    gateway = ScreenLogicGateway()
    await gateway.async_connect(**adapter)
    try:
        await gateway.async_update()
        before = find_pool_circuit(summarize({"adapter": adapter, "data": gateway.get_data()}))
        await gateway.async_set_circuit(before["id"], 1 if enabled else 0)
        await gateway.async_update()
        data = gateway.get_data()
        summary = summarize({"adapter": adapter, "data": data})
        after = find_pool_circuit(summary)
        expected = "on" if enabled else "off"
        if after["id"] != before["id"] or after["state"] != expected:
            raise ValueError(
                "Pool circulation state was not confirmed; read status before retrying"
            )
        return {
            "requested": expected,
            "circuit": after,
            "pumps": summary["pumps"],
            "delay": extract_delay(data),
        }
    finally:
        await gateway.async_disconnect()
