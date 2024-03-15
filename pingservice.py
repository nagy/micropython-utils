import asyncio


def make_pinger_service(_route_table, sleeptime=1):
    frm = None
    to = None

    async def timer():
        nonlocal frm, to
        while True:
            print("pinger_timer", frm, to)
            if frm and to:
                _route_table(to, frm, "pong\n")
            await asyncio.sleep(sleeptime)

    asyncio.create_task(timer())

    def pinger_service(frm_, to_, msg):
        nonlocal frm, to
        frm = frm_
        to = to_
        print("pinger_service", frm, to, msg)

    return pinger_service
