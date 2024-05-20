import asyncio
from router import Route


class StreamTupleElem:
    def __init__(self, frm: int, seq: int, ack: int, msg: bytes):
        self.frm = frm
        self.seq = seq
        self._ack = ack
        self.msg = msg
        self.acked = False
        self.ttl = 10

    def ack(self):
        "Acknowledge this packet"
        self.acked = True

    def tick(self):
        self.ttl -= 1

    def __bool__(self):
        "Is this packet considered alive?"
        return (not self.acked) and bool(self.ttl > 0)

    def __bytes__(self):
        "The serialized message"
        return (
            int.to_bytes(self.seq, 2, "big")
            + int.to_bytes(self._ack, 2, "big")
            + self.msg
        )


def parse_message(msg: bytes):
    seq, ack, msg = (
        int.from_bytes(msg[0:2], "big"),
        int.from_bytes(msg[2:4], "big"),
        msg[4:],
    )
    return seq, ack, msg


class State:
    def __init__(self):
        self.seq = 0
        self.ack = 0


# seq and ack numbers are numbers for packets instead of bytes, like
# in tcp. the reason for this is that we do not expect that datagram
# packets are being reshaped.
class StreamManager:
    def __init__(self, target: int, route: Route, forward_fn, create_task=False):
        self.forward_fn = forward_fn
        self.target = target
        self.route = route
        self.outstanding_msgs: list[StreamTupleElem] = []
        self.states: dict[int, State] = {}
        if create_task:
            asyncio.create_task(self._tick())

    def __call__(self, frm: int, trgt: int, msg: bytes):
        if __debug__:
            print(f"{self!r}: received", frm, trgt, msg)
        if frm == self.target:
            # comes from other StreamManager endpoint
            seq, ack, smsg = parse_message(msg)
            self.update_state(frm, seq, ack)
            # pass message on
            # raise Exception(f"testing {seq} {smsg}")
            backmsg = self.forward_fn(frm, trgt, smsg)
            if backmsg:
                self.route(trgt, frm, bytes(StreamTupleElem(trgt, seq, ack, backmsg)))
        else:
            self.route(trgt, self.target, bytes(StreamTupleElem(trgt, 0, 0, msg)))
        if __debug__:
            print(f"{msg = !r}")

    def update_state(self, frm, seq, ack):
        if frm in self.states:
            elem = self.states[frm]
        else:
            pass

    async def _tick(self):
        while True:
            await asyncio.sleep(1)
            self._tick_sync()

    def _tick_sync(self):
        if self.outstanding_msgs and all(self.outstanding_msgs):
            self.outstanding_msgs = []
        for msg in self.outstanding_msgs:
            if not msg and not msg.acked:
                pass  # resend msg

    def __repr__(self):
        return f"<StreamManager to:{self.target} {self.route}>"
