from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class InterfaceType(str, Enum):
    ETHERNET = "ethernet"
    WIRELESS = "wireless"
    LOOPBACK = "loopback"
    OTHER = "other"


class InterfaceState(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    UNKNOWN = "UNKNOWN"


@dataclass
class Address:
    address: str
    prefix_len: int
    scope: str = ""


@dataclass
class WirelessInfo:
    ssid: str = ""
    signal_dbm: int | None = None
    tx_rate: float | None = None  # MBit/s
    channel: int | None = None
    frequency: str = ""


@dataclass
class RouteEntry:
    destination: str
    gateway: str
    dev: str
    metric: int = 0
    protocol: str = ""


@dataclass
class Connection:
    protocol: str  # tcp/udp
    local_addr: str
    local_port: int
    remote_addr: str = ""
    remote_port: int = 0
    state: str = ""
    process: str = ""


@dataclass
class DNSConfig:
    nameservers: list[str] = field(default_factory=list)
    search_domains: list[str] = field(default_factory=list)


@dataclass
class Interface:
    name: str
    type: InterfaceType
    state: InterfaceState
    ipv4: list[Address] = field(default_factory=list)
    ipv6: list[Address] = field(default_factory=list)
    mac: str = ""
    mtu: int = 0
    flags: list[str] = field(default_factory=list)
    wireless: WirelessInfo | None = None
    routes: list[RouteEntry] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)
