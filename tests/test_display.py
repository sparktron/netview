import pytest
from rich.table import Table

from netview.display.compact import render_compact
from netview.display.verbose import render_verbose
from netview.models import (
    Address,
    Connection,
    DNSConfig,
    Interface,
    InterfaceState,
    InterfaceType,
    RouteEntry,
    WirelessInfo,
)


def _make_eth(name: str = "eth0") -> Interface:
    return Interface(
        name=name,
        type=InterfaceType.ETHERNET,
        state=InterfaceState.UP,
        ipv4=[Address("192.168.1.10", 24, "global")],
        ipv6=[Address("fe80::1", 64, "link")],
        mac="aa:bb:cc:dd:ee:ff",
        mtu=1500,
        flags=["UP", "LOWER_UP"],
    )


def _make_wifi() -> Interface:
    iface = Interface(
        name="wlan0",
        type=InterfaceType.WIRELESS,
        state=InterfaceState.UP,
        ipv4=[Address("10.0.0.5", 24)],
        mac="11:22:33:44:55:66",
        mtu=1500,
    )
    iface.wireless = WirelessInfo(ssid="MyNet", signal_dbm=-65, tx_rate=300.0, channel=36, frequency="5180 MHz")
    return iface


def _make_dns() -> DNSConfig:
    return DNSConfig(nameservers=["8.8.8.8", "8.8.4.4"], search_domains=["example.com"])


# --- compact ---

def test_compact_returns_table():
    table = render_compact([_make_eth()])
    assert isinstance(table, Table)


def test_compact_empty_list():
    table = render_compact([])
    assert isinstance(table, Table)
    assert table.row_count == 0


def test_compact_wireless_shows_ssid():
    table = render_compact([_make_wifi()])
    # SSID column is index 7; check that cell value contains the SSID
    cell = table.columns[7]._cells[0]
    assert "MyNet" in str(cell)


def test_compact_no_ssid_for_ethernet():
    table = render_compact([_make_eth()])
    cell = table.columns[7]._cells[0]
    assert str(cell).strip() == ""


def test_compact_multiple_interfaces():
    table = render_compact([_make_eth(), _make_wifi()])
    assert table.row_count == 2


# --- verbose ---

def test_verbose_returns_group():
    from rich.console import Group
    result = render_verbose([_make_eth()], _make_dns())
    assert isinstance(result, Group)


def test_verbose_empty_interfaces():
    from rich.console import Group
    result = render_verbose([], _make_dns())
    assert isinstance(result, Group)


def test_verbose_with_wireless():
    from rich.console import Group
    result = render_verbose([_make_wifi()], _make_dns())
    assert isinstance(result, Group)


def test_verbose_with_routes_and_connections():
    from rich.console import Group
    iface = _make_eth()
    iface.routes = [RouteEntry("default", "192.168.1.1", "eth0", 100, "dhcp")]
    iface.connections = [Connection("tcp", "192.168.1.10", 22, "10.0.0.99", 54321, "ESTAB", "sshd")]
    result = render_verbose([iface], _make_dns())
    assert isinstance(result, Group)


def test_verbose_dns_panel_renders(capsys):
    from rich.console import Console, Group
    result = render_verbose([], _make_dns())
    console = Console(width=120)
    with console.capture() as cap:
        console.print(result)
    output = cap.get()
    assert "8.8.8.8" in output
    assert "example.com" in output
