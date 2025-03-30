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


def create_task(*, port: int, route):
    import socket
    import asyncio

    _udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # _udpsocket.setblocking(False)
    addr = None

    async def udpsender(frm: int, to: int, msg: bytes):
        # print("udpsender", frm, to, msg)
        if addr:
            # print("udpsender:addr", addr)
            _udpsocket.sendto(msg, addr)
        else:
            print("udpsender NOT SENDING")

    async def serve_udp():
        import select

        nonlocal addr

        _bufsize = 250
        _udpsocket.bind(socket.getaddrinfo("0.0.0.0", port)[0][-1])

        poller = select.poll()
        poller.register(_udpsocket, select.POLLIN)
        while True:
            try:
                # TODO look at https://docs.micropython.org/en/latest/library/select.html#select.poll.ipoll
                # aka allocation free polling
                if poller.poll(1):  # 1ms timeout
                    msg, addr = _udpsocket.recvfrom(_bufsize)
                    # print(f"{msg=}    {addr=}")
                    PI_OFFSET = 4
                    if len(msg) < PI_OFFSET + 20 + 8:
                        print("udpsender TOO SMALL")
                        continue
                    # remote_addr = int.from_bytes(addr[0:4], "big")  # THIS IS FALSE
                    # remote_port = int.from_bytes(addr[2:4], "big")
                    await route(
                        0,
                        parse_to(msg),
                        msg,
                    )
                await asyncio.sleep(0)  # yield
            except asyncio.core.CancelledError:
                _udpsocket.close()
                break

    asyncio.create_task(serve_udp())

    return udpsender
