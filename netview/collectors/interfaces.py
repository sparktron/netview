from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from netview.models import Address, Interface, InterfaceState, InterfaceType


def _run_ip_addr() -> list[dict[str, Any]]:
    try:
        result = subprocess.run(
            ["ip", "-j", "addr", "show"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return json.loads(result.stdout) if result.stdout.strip() else []
    except FileNotFoundError:
        print("netview: 'ip' command not found", file=sys.stderr)
        return []
    except (json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(f"netview: error reading interfaces: {exc}", file=sys.stderr)
        return []


def _iface_type(name: str, link_type: str) -> InterfaceType:
    if link_type == "loopback":
        return InterfaceType.LOOPBACK
    if name.startswith(("wl", "wlan", "wlp", "wlx")):
        return InterfaceType.WIRELESS
    if link_type == "ether":
        return InterfaceType.ETHERNET
    return InterfaceType.OTHER


def _iface_state(operstate: str, flags: list[str]) -> InterfaceState:
    # flags (e.g. ["UP", "LOOPBACK"]) are more reliable than operstate for loopback
    upper_flags = [f.upper() for f in flags]
    if "UP" in upper_flags:
        return InterfaceState.UP
    if "DOWN" in upper_flags or operstate.upper() == "DOWN":
        return InterfaceState.DOWN
    if operstate.upper() == "UP":
        return InterfaceState.UP
    return InterfaceState.UNKNOWN


def collect_interfaces() -> list[Interface]:
    entries = _run_ip_addr()
    interfaces: list[Interface] = []

    for entry in entries:
        name: str = entry.get("ifname", "")
        link_type: str = entry.get("link_type", "ether")
        operstate: str = entry.get("operstate", "UNKNOWN")
        mac: str = entry.get("address", "")
        mtu: int = entry.get("mtu", 0)
        flags: list[str] = entry.get("flags", [])

        ipv4: list[Address] = []
        ipv6: list[Address] = []
        for ai in entry.get("addr_info", []):
            family = ai.get("family", "")
            local = ai.get("local", "")
            prefixlen = ai.get("prefixlen", 0)
            scope = ai.get("scope", "")
            addr = Address(address=local, prefix_len=prefixlen, scope=scope)
            if family == "inet":
                ipv4.append(addr)
            elif family == "inet6":
                ipv6.append(addr)

        interfaces.append(
            Interface(
                name=name,
                type=_iface_type(name, link_type),
                state=_iface_state(operstate, flags),
                ipv4=ipv4,
                ipv6=ipv6,
                mac=mac,
                mtu=mtu,
                flags=flags,
            )
        )

    return interfaces
