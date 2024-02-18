from asyncio import create_task, start_server
from aioespnow import AIOESPNow

_tcpwriter = None
_server = None


async def tcp_to_espnow_server(espn, tsk, reader, writer):
    global _tcpwriter
    global _server

    _tcpwriter = writer
    while True:
        try:
            peer = await reader.readexactly(6)
            length = int.from_bytes(await reader.readexactly(1), "little")
            data = await reader.readexactly(length)
        except EOFError:
            tsk.cancel()
            _server.close()
            _tcpwriter = None
            break
        try:
            await espn.asend(peer, data)
        except OSError as err:
            if len(err.args) > 1 and err.args[1] == "ESP_ERR_ESPNOW_NOT_FOUND":
                espn.add_peer(peer)
                await espn.asend(peer, data)  # retry
                continue
            else:
                _tcpwriter = None
                break
        except Exception:
            _tcpwriter = None
            break


async def espnow_to_tcp_server(espn):
    global _tcpwriter

    async for mac, msg in espn:
        if not _tcpwriter:
            continue
        _tcpwriter.write(mac)
        _tcpwriter.write(bytes([len(msg)]))
        _tcpwriter.write(msg)
        await _tcpwriter.drain()


async def main(addr="0.0.0.0", port=8888, espn=AIOESPNow()):
    global _server

    espn.active(True)

    tsk = create_task(espnow_to_tcp_server(espn))
    server = await start_server(
        lambda rd, wr: tcp_to_espnow_server(espn, tsk, rd, wr), addr, port, backlog=0
    )
    _server = server
    async with server:
        await server.wait_closed()
