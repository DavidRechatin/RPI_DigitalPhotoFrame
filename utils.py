#!/usr/bin/python3

def get_ip_address() -> str:
    """Discover and return the local ip address"""
    import socket
    from errno import ENETUNREACH

    try:
        ip = ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [
            [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + [
                   "no IP found"])[0])
    except IOError as e:
        if e.errno == ENETUNREACH:
            ip = "127.0.0.1"
        else:
            raise
    return ip


def turn_off_cursor():
    """Hide the cursor at the screen
    Todo:
        * don't need sudo
    """
    import subprocess

    terminal = open("/dev/tty0", "wb")
    subprocess.run(["setterm", "-cursor", "off"], stdout=terminal, env={"TERM": "xterm-256color"})
