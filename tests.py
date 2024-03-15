from router import Route


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


def test_fallback():
    str = ""

    class TestRoute(Route):
        def fallback(self, frm, trgt, msg):
            nonlocal str
            assert frm, trgt
            str = msg

    empty_route = TestRoute()
    assert empty_route(100, 101, "hello") is None
    empty_route(100, 101, "hello")
    assert str == "hello"


def test_route_strings():
    str = ""

    def mymsg(frm, to, msg):
        nonlocal str
        assert frm, to
        str += msg

    route = Route({"first": mymsg, "second": mymsg})
    route("pytest", "first", "foo")
    route("pytest", "second", "foo")
    assert str == "foofoo"


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
