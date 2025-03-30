espn = None


def parse_to(msg: bytes):
    import struct

    # these are the 4 bytes "packet information" that are added by the
    # linuxtunnel. you can turn this off in socat with the`iff-no-pi`
    # option for example.
    PI_OFFSET = 4

    src_addr, dst_addr = struct.unpack(">LL", msg[12 + PI_OFFSET : 12 + PI_OFFSET + 8])
    # print(f"src_addr={hex(src_addr)}   dst_addr={hex(dst_addr)}")
    # here we transport raw ip, so we cannot look into protocol specific data...
    return dst_addr


def make_espn_handler(*, peer):
    espn.add_peer(peer)

    async def espn_handler(frm: int, to: int, msg: bytes):
        # print("espn_handler", frm, to, msg)
        # await espn.asend(peer, msg, sync=False)
        espn.send(peer, msg, False)

    return espn_handler


def create_task(*, route):
    import asyncio
    from aioespnow import AIOESPNow

    global espn

    espn = AIOESPNow()
    espn.config(rxbuf=526 * 10)
    espn.active(True)

    async def serve_espn():
        async for _mac, msg in espn:
            await route(
                0,
                parse_to(msg),
                msg,
            )

    asyncio.create_task(serve_espn())
