from __future__ import annotations

import struct

from screenlogicpy.const.msg import CODE
from screenlogicpy.requests.request import async_make_request


async def async_request_cancel_delay(protocol, max_retries: int):
    response = await async_make_request(
        protocol,
        CODE.CANCEL_DELAY_QUERY,
        struct.pack("<I", 0),
        max_retries,
    )
    if response != b"":
        raise RuntimeError(f"Cancel delay failed. Unexpected response: {response!r}")
