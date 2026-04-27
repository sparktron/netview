from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from netview.models import RouteEntry


def _run_ip_route() -> list[dict[str, Any]]:
    try:
        result = subprocess.run(
            ["ip", "-j", "route", "show"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return json.loads(result.stdout) if result.stdout.strip() else []
    except FileNotFoundError:
        print("netview: 'ip' command not found", file=sys.stderr)
        return []
    except (json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(f"netview: error reading routes: {exc}", file=sys.stderr)
        return []


def collect_routes() -> list[RouteEntry]:
    entries = _run_ip_route()
    routes: list[RouteEntry] = []

    for entry in entries:
        dst: str = entry.get("dst", "")
        gateway: str = entry.get("gateway", "")
        dev: str = entry.get("dev", "")
        metric: int = entry.get("metric", 0)
        protocol: str = entry.get("protocol", "")
        routes.append(
            RouteEntry(
                destination=dst,
                gateway=gateway,
                dev=dev,
                metric=metric,
                protocol=protocol,
            )
        )

    return routes
