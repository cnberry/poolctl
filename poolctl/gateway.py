from __future__ import annotations

from typing import Any

from screenlogicpy import ScreenLogicGateway, discovery

from poolctl.config import get_adapter_config, set_adapter_config


async def discover_adapters() -> list[dict[str, Any]]:
    return await discovery.async_discover()


async def discover_adapter() -> dict[str, Any]:
    hosts = await discover_adapters()
    if not hosts:
        raise RuntimeError("No ScreenLogic adapters discovered on local subnet")
    adapter = hosts[0]
    set_adapter_config(adapter)
    return adapter


async def resolve_adapter(host: str | None = None) -> dict[str, Any]:
    if host:
        return {"ip": host, "port": 80}

    configured = get_adapter_config()
    if configured and configured.get("ip"):
        return configured

    return await discover_adapter()


async def fetch_status(host: str | None = None) -> dict[str, Any]:
    adapter = await resolve_adapter(host)
    gateway = ScreenLogicGateway()
    try:
        await gateway.async_connect(**adapter)
    except Exception:
        if host:
            raise
        adapter = await discover_adapter()
        await gateway.async_connect(**adapter)
    try:
        await gateway.async_update()
        data = gateway.get_data()
        return {"adapter": adapter, "data": data}
    finally:
        await gateway.async_disconnect()
