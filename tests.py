import pytest
import asyncio

# import tcpserver
# import udpserver
# import echoservice
# import printservice
# import pingservice
from router import _route_table


async def _mymsg(_frm, to, msg):
    return f"hello from {to} " + msg


async def _mybytes(_frm, _to, _msg):
    return b"hello bytes"


@pytest.mark.asyncio
async def test_route():
    _route_table[1] = _mybytes
    _route_table[2] = _mybytes
    res = await _route_table(10, 1, "foo")
    assert res == b"hello bytes"


@pytest.mark.asyncio
async def test_route_strings():
    _route_table["first"] = _mymsg
    _route_table["second"] = _mymsg
    res = await _route_table("pytest", "first", "foo")
    assert res == "hello from first foo"
    res = await _route_table("pytest", "second", "foo")
    assert res == "hello from second foo"


def test_route_strings_sync():
    _route_table["first"] = lambda _frm, _to, _msg: "hello"
    _route_table["second"] = lambda _frm, _to, _msg: "second"
    res = _route_table("pytest", "first", "foo")
    assert res == "hello"
    res = _route_table("pytest", "second", "foo")
    assert res == "second"
    # the fallback is still a coroutine
    fallbacked = _route_table("nonexistent", None, None)
    assert "__await__" in dir(fallbacked)
    assert None == asyncio.run(fallbacked)  # to skip warning
