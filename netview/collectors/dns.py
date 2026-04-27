from __future__ import annotations

import subprocess
import sys

from netview.models import DNSConfig

_RESOLV_CONF = "/etc/resolv.conf"


def _parse_resolv_conf() -> DNSConfig:
    nameservers: list[str] = []
    search_domains: list[str] = []
    try:
        with open(_RESOLV_CONF) as f:
            for line in f:
                line = line.strip()
                if line.startswith("nameserver"):
                    parts = line.split()
                    if len(parts) >= 2:
                        nameservers.append(parts[1])
                elif line.startswith("search") or line.startswith("domain"):
                    parts = line.split()
                    search_domains.extend(parts[1:])
    except OSError:
        pass
    return DNSConfig(nameservers=nameservers, search_domains=search_domains)


def _parse_nmcli_dns() -> DNSConfig:
    nameservers: list[str] = []
    try:
        result = subprocess.run(
            ["nmcli", "--terse", "--fields", "IP4.DNS", "dev", "show"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for line in result.stdout.splitlines():
            # format: IP4.DNS[1]:8.8.8.8
            if "DNS" in line and ":" in line:
                ip = line.split(":", 1)[1].strip()
                if ip and ip not in nameservers:
                    nameservers.append(ip)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return DNSConfig(nameservers=nameservers)


def collect_dns() -> DNSConfig:
    config = _parse_resolv_conf()
    if not config.nameservers:
        fallback = _parse_nmcli_dns()
        config.nameservers = fallback.nameservers
    return config
