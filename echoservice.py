def echo_service(frm, to, msg):
    print("echo_service", frm, to, msg)
    yield (to, frm, "echo:" + str(len(msg)) + "\n")
