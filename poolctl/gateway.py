from __future__ import annotations

from typing import Any

from screenlogicpy import ScreenLogicGateway, discovery


async def discover_adapters() -> list[dict[str, Any]]:
    return await discovery.async_discover()


async def discover_adapter() -> dict[str, Any]:
    hosts = await discover_adapters()
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
