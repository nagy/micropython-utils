import sys
import asyncio
import tcpserver
import udpserver
import echoservice
import pingservice
from router import route


for code in sys.argv[1:]:
    exec(code, locals(), globals())


loop = asyncio.get_event_loop()
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
