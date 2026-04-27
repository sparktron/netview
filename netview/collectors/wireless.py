from __future__ import annotations

import re
import subprocess
import sys

from netview.models import WirelessInfo


def collect_wireless_interfaces() -> set[str]:
    try:
        result = subprocess.run(
            ["iw", "dev"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        ifaces: set[str] = set()
        for line in result.stdout.splitlines():
            m = re.match(r"\s+Interface\s+(\S+)", line)
            if m:
                ifaces.add(m.group(1))
        return ifaces
    except FileNotFoundError:
        return set()
    except subprocess.TimeoutExpired:
        print("netview: timeout running 'iw dev'", file=sys.stderr)
        return set()


def _parse_iw_link(output: str) -> WirelessInfo:
    info = WirelessInfo()
    for line in output.splitlines():
        line = line.strip()
        m = re.match(r"SSID:\s+(.+)", line)
        if m:
            info.ssid = m.group(1)
            continue
        m = re.match(r"signal:\s+(-?\d+)\s+dBm", line)
        if m:
            info.signal_dbm = int(m.group(1))
            continue
        # prefer tx bitrate
        m = re.match(r"tx bitrate:\s+([\d.]+)\s+MBit/s", line)
        if m:
            info.tx_rate = float(m.group(1))
    return info


def _parse_iw_info(output: str, info: WirelessInfo) -> WirelessInfo:
    for line in output.splitlines():
        line = line.strip()
        m = re.match(r"channel\s+(\d+)\s+\(([\d.]+)\s+MHz\)", line)
        if m:
            info.channel = int(m.group(1))
            info.frequency = m.group(2) + " MHz"
    return info


def collect_wireless_info(iface: str) -> WirelessInfo:
    info = WirelessInfo()
    try:
        link = subprocess.run(
            ["iw", "dev", iface, "link"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        info = _parse_iw_link(link.stdout)

        iw_info = subprocess.run(
            ["iw", "dev", iface, "info"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        info = _parse_iw_info(iw_info.stdout, info)
    except FileNotFoundError:
        pass
    except subprocess.TimeoutExpired:
        print(f"netview: timeout reading wireless info for {iface}", file=sys.stderr)
    return info
