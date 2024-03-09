import sys
import asyncio
import tcpserver
import udpserver


async def echo_service(frm, to, msg):
    print("echo_service", frm, to, msg)
    await _route_table[frm](to, frm, "echo:" + str(len(msg)) + "\n")

async def print_service(frm, to, msg):
    print("print_service", frm, to, msg)

_route_table = {
    # 7: echo_service,
}

for code in sys.argv[1:]:
    exec(code, locals(), globals())

print("_route_table.keys() =", _route_table.keys())

loop = asyncio.get_event_loop()
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
