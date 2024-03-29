def create_task(route):
    import asyncio
    from aioespnow import AIOESPNow

    espn = AIOESPNow()
    espn.active(True)

    global make_espn_handler

    def make_espn_handler(peer):
        espn.add_peer(peer)

        def espn_handler(frm, to, msg):
            print("espn_handler", frm, to, msg)
            espn.send(peer, f"{frm} {to} ".encode() + msg)

        return espn_handler

    async def serve_espn():
        async for _mac, msg in espn:
            frm, trgt, msg = msg.split(b" ", 2)
            frm = int(frm)
            trgt = int(trgt)
            await route[trgt](frm, trgt, msg)

    asyncio.create_task(serve_espn())
