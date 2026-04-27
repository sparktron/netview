from __future__ import annotations

from netview.collectors.connections import collect_connections
from netview.collectors.dns import collect_dns
from netview.collectors.interfaces import collect_interfaces
from netview.collectors.routes import collect_routes
from netview.collectors.wireless import collect_wireless_info, collect_wireless_interfaces
from netview.models import DNSConfig, Interface, InterfaceType


def collect_all(
    iface_filter: str | None = None,
) -> tuple[list[Interface], DNSConfig]:
    interfaces = collect_interfaces()
    routes = collect_routes()
    dns = collect_dns()
    connections = collect_connections()
    wireless_ifaces = collect_wireless_interfaces()

    # Enrich wireless interfaces
    for iface in interfaces:
        if iface.name in wireless_ifaces:
            iface.type = InterfaceType.WIRELESS
            iface.wireless = collect_wireless_info(iface.name)

    # Assign routes to interfaces
    for route in routes:
        for iface in interfaces:
            if iface.name == route.dev:
                iface.routes.append(route)
                break

    # Assign connections to interfaces by matching local address
    iface_addrs: dict[str, Interface] = {}
    for iface in interfaces:
        for addr in iface.ipv4 + iface.ipv6:
            iface_addrs[addr.address] = iface

    for conn in connections:
        target = iface_addrs.get(conn.local_addr)
        if target is None and conn.local_addr in ("0.0.0.0", "::", ""):
            # Wildcard listeners — attach to first non-loopback interface
            for iface in interfaces:
                if iface.type != InterfaceType.LOOPBACK:
                    target = iface
                    break
        if target is not None:
            target.connections.append(conn)

    if iface_filter:
        interfaces = [i for i in interfaces if i.name == iface_filter]

    return interfaces, dns
