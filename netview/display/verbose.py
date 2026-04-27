from __future__ import annotations

import rich.box
from rich.console import ConsoleRenderable, Group, RichCast
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from netview.display import (
    COL_DIM,
    COL_HEADER,
    LABEL,
    STATE_DOWN,
    STATE_UP,
    STATE_UNK,
    TYPE_COLORS,
)
from netview.models import DNSConfig, Interface, InterfaceState, InterfaceType


def _kv(label: str, value: str) -> Text:
    t = Text()
    t.append(f"{label}: ", style=LABEL)
    t.append(value)
    return t


def _state_str(state: InterfaceState) -> tuple[str, str]:
    if state == InterfaceState.UP:
        return "UP", "green bold"
    if state == InterfaceState.DOWN:
        return "DOWN", "red"
    return "UNKNOWN", "yellow"


def _iface_panel(iface: Interface) -> Panel:
    type_style = TYPE_COLORS.get(iface.type.value, TYPE_COLORS["other"])
    state_str, state_style = _state_str(iface.state)

    header = Text()
    header.append(iface.name, style="bold white")
    header.append("  ")
    header.append(iface.type.value, style=type_style)
    header.append("  ")
    header.append(state_str, style=state_style)
    if iface.flags:
        header.append(f"  [{' '.join(iface.flags)}]", style=COL_DIM)

    lines: list[ConsoleRenderable | RichCast | str] = [header, Text("")]

    # Addresses
    if iface.ipv4 or iface.ipv6:
        lines.append(Text("Addresses", style=COL_HEADER))
        for a in iface.ipv4:
            scope = f"  ({a.scope})" if a.scope else ""
            lines.append(Text(f"  {a.address}/{a.prefix_len}  ipv4{scope}"))
        for a in iface.ipv6:
            scope = f"  ({a.scope})" if a.scope else ""
            lines.append(Text(f"  {a.address}/{a.prefix_len}  ipv6{scope}", style=COL_DIM))
        lines.append(Text(""))

    # Link
    lines.append(Text("Link", style=COL_HEADER))
    lines.append(_kv("  MAC", iface.mac or "—"))
    lines.append(_kv("  MTU", str(iface.mtu) if iface.mtu else "—"))
    lines.append(Text(""))

    # Wireless
    if iface.wireless:
        w = iface.wireless
        lines.append(Text("Wireless", style=COL_HEADER))
        lines.append(_kv("  SSID", w.ssid or "—"))
        lines.append(_kv("  Signal", f"{w.signal_dbm} dBm" if w.signal_dbm is not None else "—"))
        lines.append(_kv("  TX rate", f"{w.tx_rate} MBit/s" if w.tx_rate is not None else "—"))
        lines.append(_kv("  Channel", str(w.channel) if w.channel is not None else "—"))
        lines.append(_kv("  Frequency", w.frequency or "—"))
        lines.append(Text(""))

    # Routes
    if iface.routes:
        lines.append(Text("Routes", style=COL_HEADER))
        rt = Table(box=None, show_header=True, header_style=COL_DIM, padding=(0, 1))
        rt.add_column("Destination")
        rt.add_column("Gateway")
        rt.add_column("Metric", justify="right")
        rt.add_column("Proto")
        for r in iface.routes:
            rt.add_row(
                r.destination,
                r.gateway or "—",
                str(r.metric),
                r.protocol,
            )
        lines.append(rt)
        lines.append(Text(""))

    # Connections
    if iface.connections:
        lines.append(Text("Connections", style=COL_HEADER))
        ct = Table(box=None, show_header=True, header_style=COL_DIM, padding=(0, 1))
        ct.add_column("State")
        ct.add_column("Local")
        ct.add_column("Remote")
        ct.add_column("Process")
        for c in iface.connections:
            local = f"{c.local_addr}:{c.local_port}"
            remote = f"{c.remote_addr}:{c.remote_port}" if c.remote_addr else "*"
            ct.add_row(c.state, local, remote, c.process)
        lines.append(ct)

    return Panel(Group(*lines), title=iface.name, expand=False)


def _dns_panel(dns: DNSConfig) -> Panel:
    lines: list[ConsoleRenderable | RichCast | str] = []
    if dns.nameservers:
        lines.append(Text("Nameservers", style=COL_HEADER))
        for ns in dns.nameservers:
            lines.append(Text(f"  {ns}"))
    if dns.search_domains:
        lines.append(Text(""))
        lines.append(Text("Search domains", style=COL_HEADER))
        lines.append(Text(f"  {' '.join(dns.search_domains)}"))
    if not lines:
        lines.append(Text("No DNS configuration found", style=COL_DIM))
    return Panel(Group(*lines), title="DNS", expand=False)


def render_verbose(interfaces: list[Interface], dns: DNSConfig) -> Group:
    panels: list[ConsoleRenderable | RichCast | str] = [_iface_panel(i) for i in interfaces]
    panels.append(_dns_panel(dns))
    return Group(*panels)
