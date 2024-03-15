def create_task(port, route):
    import asyncio

    async def tcp_handle_client(reader, writer):
        remote_port = int.from_bytes(reader.get_extra_info("peername")[2:4], "big")
        # register this client
        route[remote_port] = lambda frm, to, msg: writer.write(msg)
        firstline = await reader.readline()
        target = int(firstline)
        while msg := await reader.read(1024):
            try:
                route(remote_port, target, msg)
            except Exception as err:
                print(err)
                break
        del route[remote_port]

    asyncio.create_task(asyncio.start_server(tcp_handle_client, "0.0.0.0", port))
