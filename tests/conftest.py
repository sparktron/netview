import json
import subprocess
from unittest.mock import MagicMock

import pytest


IP_ADDR_JSON = json.dumps([
    {
        "ifindex": 1,
        "ifname": "lo",
        "flags": ["LOOPBACK", "UP", "LOWER_UP"],
        "mtu": 65536,
        "operstate": "UNKNOWN",
        "link_type": "loopback",
        "address": "00:00:00:00:00:00",
        "addr_info": [
            {"family": "inet", "local": "127.0.0.1", "prefixlen": 8, "scope": "host"},
            {"family": "inet6", "local": "::1", "prefixlen": 128, "scope": "host"},
        ],
    },
    {
        "ifindex": 2,
        "ifname": "eth0",
        "flags": ["BROADCAST", "MULTICAST", "UP", "LOWER_UP"],
        "mtu": 1500,
        "operstate": "UP",
        "link_type": "ether",
        "address": "aa:bb:cc:dd:ee:ff",
        "addr_info": [
            {"family": "inet", "local": "192.168.1.10", "prefixlen": 24, "scope": "global"},
        ],
    },
    {
        "ifindex": 3,
        "ifname": "wlan0",
        "flags": ["BROADCAST", "MULTICAST", "UP", "LOWER_UP"],
        "mtu": 1500,
        "operstate": "UP",
        "link_type": "ether",
        "address": "11:22:33:44:55:66",
        "addr_info": [
            {"family": "inet", "local": "10.0.0.5", "prefixlen": 24, "scope": "global"},
        ],
    },
])

IP_ROUTE_JSON = json.dumps([
    {"dst": "default", "gateway": "192.168.1.1", "dev": "eth0", "metric": 100, "protocol": "dhcp"},
    {"dst": "192.168.1.0/24", "dev": "eth0", "metric": 0, "protocol": "kernel"},
])

SS_LISTEN_OUTPUT = (
    "LISTEN  0  128  0.0.0.0:22  0.0.0.0:*  users:((\"sshd\",pid=1234,fd=3))\n"
    "LISTEN  0  128  [::]:22  [::]:*  users:((\"sshd\",pid=1234,fd=4))\n"
)

SS_ESTAB_OUTPUT = (
    "ESTAB  0  0  192.168.1.10:22  10.0.0.99:54321  users:((\"sshd\",pid=5678,fd=5))\n"
)

RESOLV_CONF = "nameserver 8.8.8.8\nnameserver 8.8.4.4\nsearch example.com\n"


def _make_completed_process(stdout: str) -> MagicMock:
    m = MagicMock(spec=subprocess.CompletedProcess)
    m.stdout = stdout
    m.returncode = 0
    return m


@pytest.fixture
def mock_ip_addr(mocker):
    return mocker.patch(
        "subprocess.run",
        return_value=_make_completed_process(IP_ADDR_JSON),
    )
