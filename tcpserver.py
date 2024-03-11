def create_task(port, _route_table):
    import asyncio

    async def tcp_handle_client(reader, writer):
        remote_port = int.from_bytes(reader.get_extra_info("peername")[2:4], "big")
        # register this client
        _route_table[remote_port] = lambda frm, to, msg: writer.awrite(msg)
        print(_route_table.keys())
        firstline = await reader.readline()
        target = int(firstline)
        while msg := await reader.read(1024):
            try:
                await _route_table(remote_port, target, msg)
            except Exception as err:
                print(err)
                break
        del _route_table[remote_port]
        print(_route_table.keys())

    asyncio.create_task(asyncio.start_server(tcp_handle_client, "0.0.0.0", port))
