class MessageRouter(dict):
    @staticmethod
    async def fallback(to, msg):
        pass

    async def call(self, to, msg):
        target = self.get(to, self.fallback)
        if type(target) == int:
            return await self.call(target, msg)
        return await self.get(to, self.fallback)(to, msg)


MR = MessageRouter()
# MR[123] = lambda to, msg: print("xxx> ", to, msg)
# MR[int.from_bytes(machine.unique_id(),"little")] = lambda _to, msg: exec(msg, locals(), globals())
