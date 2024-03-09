def create_task(port, _route_table):
    import asyncio

    _fixed_tcp_port = 4

    async def tcp_handle_client(reader, writer):
        remote_port = int.from_bytes(reader.get_extra_info("peername")[2:4], "big")
        # register this client
        _route_table[_fixed_tcp_port] = lambda frm, to, msg: writer.awrite(msg)
        print(_route_table.keys())
        while l := await reader.read(1024):
            target, msg = l.split(b" ", 1)
            target = int(target)
            try:
                await _route_table[target](_fixed_tcp_port, target, msg)
            except Error as err:
                print(err)
                break
        del _route_table[_fixed_tcp_port]
        print(_route_table.keys())

    asyncio.create_task(asyncio.start_server(tcp_handle_client, "0.0.0.0", port))
