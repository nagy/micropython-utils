import sys
import asyncio
import tcpserver
import udpserver
import echoservice
import printservice
import pingservice
from router import _route_table


for code in sys.argv[1:]:
    exec(code, locals(), globals())


loop = asyncio.get_event_loop()
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
