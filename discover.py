import asyncio
import json

from screenlogicpy import discovery


async def main() -> None:
    hosts = await discovery.async_discover()
    print(json.dumps(hosts, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    asyncio.run(main())
