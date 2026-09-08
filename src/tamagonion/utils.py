import ipaddress
import socket

import psutil


def is_host_local(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = socket.getaddrinfo(host, None)[-1][-1][0]

    for interfaces in psutil.net_if_addrs().values():
        if ip in {addr.address for addr in interfaces}:
            return True

    return False
