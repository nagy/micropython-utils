import asyncio


async def _aexec(src, to, msg):
    return exec(msg, locals(), globals())


_route_table = {0: _aexec}


async def route(src, dst, msg):
    return await _route_table[dst](src, dst, msg)


# async def blink():
#     while 1:
#         await route(99, 0, "print('blink', 123)")
#         await asyncio.sleep(5)


# async def wait():
#     while 1:
#         await asyncio.sleep(5)


async def main(espn):
    async for _mac, msg in espn:
        src, dst, rest = (
            int.from_bytes(msg[0:1], "big"),
            int.from_bytes(msg[1:2], "big"),
            msg[2:],
        )
        await route(src, dst, rest)
