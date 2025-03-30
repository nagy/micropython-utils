class Route(dict):
    async def fallback(self, frm, trgt, msg):
        print("unrouted:", frm, trgt, msg)

    def __call__(self, frm, trgt, msg):
        if trgt in self:
            ret = self[trgt](frm, trgt, msg) or []
            for _2frm, _2trgt, _2msg in ret:
                self(_2frm, _2trgt, _2msg)
            return ret
        else:
            return self.fallback(frm, trgt, msg)


route = Route()
