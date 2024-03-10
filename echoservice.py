def make_echo_service(_route_table, prefix="echo"):
    async def echo_service(frm, to, msg):
        print("echo_service", frm, to, msg)
        await _route_table(to, frm, prefix + ":" + str(len(msg)) + "\n")

    return echo_service
