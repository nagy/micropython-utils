import asyncio


def make_pinger_service(_route_table, sleeptime=1):
    _func_local = {}

    async def timer():
        while True:
            print("pinger_timer", _func_local)
            if "frm" in _func_local and "to" in _func_local:
                await _route_table(_func_local["to"], _func_local["frm"], "pong\n")
            await asyncio.sleep(sleeptime)

    asyncio.create_task(timer())

    async def pinger_service(frm, to, msg):
        _func_local["frm"] = frm
        _func_local["to"] = to
        print("pinger_service", frm, to, msg)

    return pinger_service
