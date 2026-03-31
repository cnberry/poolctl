from __future__ import annotations

import struct

from screenlogicpy.requests.request import async_make_request


CANCEL_DELAY_QUERY = 12580


async def async_request_cancel_delay(protocol, max_retries: int):
    response = await async_make_request(
        protocol,
        CANCEL_DELAY_QUERY,
        struct.pack("<I", 0),
        max_retries,
    )
    if response != b"":
        raise RuntimeError(f"Cancel delay failed. Unexpected response: {response!r}")
