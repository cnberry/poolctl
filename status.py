import asyncio
import json
from typing import Any

from screenlogicpy import ScreenLogicGateway, discovery


async def fetch() -> dict[str, Any]:
    hosts = await discovery.async_discover()
    if not hosts:
        raise RuntimeError("No ScreenLogic adapters discovered on local subnet")

    host = hosts[0]
    gateway = ScreenLogicGateway()
    await gateway.async_connect(**host)
    try:
        await gateway.async_update()
        data = gateway.get_data()
        return {
            "adapter": host,
            "data": data,
        }
    finally:
        await gateway.async_disconnect()


async def main() -> None:
    payload = await fetch()
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    asyncio.run(main())
