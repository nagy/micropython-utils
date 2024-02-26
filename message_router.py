from machine import unique_id


async def _aexec(_to, msg):
    return exec(msg, locals(), globals())


_route_table = {
    int.from_bytes(unique_id(), "big"): _aexec
    # ...
}


async def route(to, msg):
    return await _route_table[to](to, msg)


async def main(espn):
    async for mac, msg in espn:
        to, rest = int.from_bytes(msg[0:6], "big"), msg[6:]
        await route(to, rest)
