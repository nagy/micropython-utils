def make_echo_service(*, route):
    async def echo_service(frm, to, msg):
        print("echo_service", frm, to, msg)
        await route(to, frm, msg)

    return echo_service
