from __future__ import annotations

import rich.box
from rich.table import Table
from rich.text import Text

from netview.display import COL_DIM, COL_HEADER, STATE_DOWN, STATE_UP, STATE_UNK, TYPE_COLORS
from netview.models import Address, Interface, InterfaceState, InterfaceType


def _state_text(state: InterfaceState) -> Text:
    if state == InterfaceState.UP:
        return Text("UP", style=STATE_UP)
    if state == InterfaceState.DOWN:
        return Text("DOWN", style=STATE_DOWN)
    return Text("?", style=STATE_UNK)


def _type_text(itype: InterfaceType) -> Text:
    style = TYPE_COLORS.get(itype.value, TYPE_COLORS["other"])
    labels = {
        InterfaceType.ETHERNET: "eth",
        InterfaceType.WIRELESS: "wifi",
        InterfaceType.LOOPBACK: "lo",
        InterfaceType.OTHER: "other",
    }
    return Text(labels[itype], style=style)


def _addr_cell(addrs: list[Address]) -> str:
    if not addrs:
        return ""
    return "\n".join(f"{a.address}/{a.prefix_len}" for a in addrs)


def render_compact(interfaces: list[Interface]) -> Table:
    table = Table(
        box=rich.box.SIMPLE_HEAD,
        show_header=True,
        header_style=COL_HEADER,
        padding=(0, 1),
    )

    table.add_column("TYPE", style=None, no_wrap=True)
    table.add_column("NAME", style="bold", no_wrap=True)
    table.add_column("STATE", no_wrap=True)
    table.add_column("IPv4", style=None)
    table.add_column("IPv6", style=COL_DIM)
    table.add_column("MAC", style=COL_DIM, no_wrap=True)
    table.add_column("MTU", style=COL_DIM, no_wrap=True, justify="right")
    table.add_column("SSID", style="bright_blue")

    for iface in interfaces:
        mtu_str = str(iface.mtu) if iface.mtu else ""
        ssid = iface.wireless.ssid if iface.wireless else ""

        table.add_row(
            _type_text(iface.type),
            iface.name,
            _state_text(iface.state),
            _addr_cell(iface.ipv4),
            _addr_cell(iface.ipv6),
            iface.mac,
            mtu_str,
            ssid,
        )

    return table
