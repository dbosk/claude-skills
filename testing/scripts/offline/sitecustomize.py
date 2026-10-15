"""Refuse network connections to anything but loopback, in this process.

offline_run.py puts this directory first on PYTHONPATH, so every Python
process it starts, and every Python subprocess of those, imports this
module at startup.  Then the sitecustomize it shadows (e.g. the
distribution's) is run as usual.
"""

import importlib.util
import ipaddress
import socket
import sys
from importlib.machinery import PathFinder
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _loopback(address) -> bool:
    host = address[0] if isinstance(address, tuple) else address
    if not isinstance(host, str):
        return False
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host.split("%")[0]).is_loopback
    except ValueError:  # a host name: resolving it is already a lookup
        return False


class NetworkBlocked(RuntimeError):
    """Not an OSError: HTTP clients retry those with backoff, for hours."""


def _guard(original):
    def connect(self, address):
        if self.family in (socket.AF_INET, socket.AF_INET6) and not _loopback(address):
            raise NetworkBlocked(f"blocked by offline_run: {address!r} is not loopback")
        return original(self, address)
    return connect


socket.socket.connect = _guard(socket.socket.connect)
socket.socket.connect_ex = _guard(socket.socket.connect_ex)

# Run the sitecustomize this one shadows.
_others = [p for p in sys.path if Path(p or ".").resolve() != _HERE]
_spec = PathFinder.find_spec("sitecustomize", _others)
if _spec and _spec.loader:
    _spec.loader.exec_module(importlib.util.module_from_spec(_spec))
