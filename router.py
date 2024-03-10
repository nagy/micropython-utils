import asyncio


class Route(dict):
    # fallback = lambda frm, trgt, msg: asyncio.sleep(0)

    async def fallback(self, frm, trgt, msg):
        print("fallback", frm, trgt, msg)
        await asyncio.sleep(0)

    # this is a coroutine
    def __call__(self, frm, trgt, msg):
        if trgt in self:
            return self[trgt](frm, trgt, msg)
        else:
            return self.fallback(frm, trgt, msg)


_route_table = Route()

print("_route_table.keys() =", _route_table.keys())
