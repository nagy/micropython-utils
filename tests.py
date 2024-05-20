from router import Route
from layer4stream import StreamManager, parse_message, StreamTupleElem


def test_route():
    str = ""
    bytes = b""

    def mymsg(frm, to, msg):
        assert frm, to
        nonlocal str
        str += msg

    def mybytes(frm, to, msg):
        assert frm, to
        nonlocal bytes
        bytes += msg

    route = Route({1: mymsg, 2: mybytes})
    route(100, 1, "foo")
    route(100, 2, b"foobytes")
    assert str == "foo"
    assert bytes == b"foobytes"


def test_make_parse_stream_msg():
    data: bytes = bytes(StreamTupleElem(1, 1, 2, b"hello"))
    assert data == b"\x00\x01\x00\x02hello"
    seq, ack, msg = parse_message(data)
    assert seq == 1
    assert ack == 2
    assert msg == b"hello"


def test_stream():
    outecho = []
    route = Route()

    def printstorage_service(frm, to, msg):
        nonlocal outecho
        print("echo_service", frm, to, msg)
        outecho.append((frm, to, msg))

    def echo_service(frm, to, msg):
        return msg

    route[1] = StreamManager(2, route, printstorage_service)
    route[2] = StreamManager(1, route, echo_service)
    route(9999, 1, b"hello")
    assert outecho == [(2, 1, b"hello")]


def test_fallback():
    str = ""

    class TestRoute(Route):
        def fallback(self, frm, trgt, msg):
            nonlocal str
            assert frm, trgt
            str = msg

    empty_route = TestRoute()
    empty_route(100, 101, "hello")
    assert str == "hello"


def test_route_spotty():
    spot = ""
    counter = 0

    def onesenderreceiver(frm, to, msg):
        assert frm
        yield (to, 2, msg)

    def twoforwarder_spotty(frm, to, msg):
        nonlocal counter
        assert frm
        counter += 1
        if counter % 2 == 1:
            yield (to, 3, msg)

    def threereceiver(frm, to, msg):
        nonlocal spot
        assert frm, to
        spot += msg

    spotty_route = Route(
        {
            1: onesenderreceiver,
            2: twoforwarder_spotty,
            3: threereceiver,
        }
    )
    for _ in range(10):
        spotty_route(10, 1, "forwardmsg")
    assert spot == "forwardmsg" * 5
