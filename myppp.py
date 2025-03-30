import socket
import network
import machine
import os

listen_sock = None
ppp = None


def accept_handler(listen_sock):
    cl, remote_addr = listen_sock.accept()
    cl.setblocking(False)

    # for esp32
    if hasattr(os, "dupterm_notify"):
        cl.setsockopt(socket.SOL_SOCKET, 20, os.dupterm_notify)
    os.dupterm(cl)


def init():
    global listen_sock, ppp

    uart0 = machine.UART(0, 921600)
    ppp = network.PPP(uart0)
    ppp.active(1)
    ppp.connect()

    listen_sock = socket.socket()
    listen_sock.bind(("", 1234))
    listen_sock.listen(1)
    listen_sock.setsockopt(socket.SOL_SOCKET, 20, accept_handler)
