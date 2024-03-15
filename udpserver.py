import asyncio
import select
import socket


def create_task(port, _route_table):
    _udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _addr_info = socket.getaddrinfo("0.0.0.0", port)[0]

    global make_udp_sender

    def make_udp_sender(port, host="127.0.0.1"):
        _addr_info = socket.getaddrinfo(host, port)[0]

        def sender(frm, to, msg):
            print("udpsender", frm, to, msg)
            _udpsocket.sendto(f"{frm} {to} ".encode() + msg, _addr_info[-1])

        return sender

    async def serve_udp():
        polltimeout = 1  # 1 ms
        max_packet = 1024
        _udpsocket.setblocking(False)
        _udpsocket.bind(_addr_info[-1])

        poller = select.poll()
        poller.register(_udpsocket, select.POLLIN)
        while True:
            try:
                if poller.poll(polltimeout):
                    buf, _addr = _udpsocket.recvfrom(max_packet)
                    # remote_port = int.from_bytes(addr[2:4], "big")
                    frm, trgt, msg = buf.split(b" ", 2)
                    _route_table(int(frm), int(trgt), msg)
                await asyncio.sleep(0)
            except asyncio.core.CancelledError:
                _udpsocket.close()
                break

    asyncio.create_task(serve_udp())
