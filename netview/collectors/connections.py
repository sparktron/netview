from __future__ import annotations

import re
import subprocess
import sys

from netview.models import Connection

# Matches: users:(("sshd",pid=1234,fd=3))
_PROCESS_RE = re.compile(r'users:\(\("([^"]+)"')


def _split_addr_port(addr_port: str) -> tuple[str, int]:
    """Split '192.168.1.1:22' or '[::1]:22' or '[::]:*' into (addr, port)."""
    if addr_port.startswith("["):
        # IPv6 bracket notation: [addr]:port or [addr]:*
        m = re.match(r"\[([^\]]+)\]:(\d+|\*)", addr_port)
        if m:
            raw_port = m.group(2)
            port = int(raw_port) if raw_port.isdigit() else 0
            return m.group(1), port
        return addr_port, 0
    if ":" in addr_port:
        last_colon = addr_port.rfind(":")
        host = addr_port[:last_colon]
        raw_port = addr_port[last_colon + 1 :]
        try:
            port = int(raw_port)
        except ValueError:
            port = 0
        return host, port
    return addr_port, 0


def _parse_ss_output(output: str, default_state: str) -> list[Connection]:
    connections: list[Connection] = []
    for line in output.splitlines():
        parts = line.split()
        # ss -H columns: State Recv-Q Send-Q Local Peer [Process]
        if len(parts) < 5:
            continue
        state = parts[0]
        local_raw = parts[3]
        peer_raw = parts[4]
        process_col = parts[5] if len(parts) > 5 else ""

        local_addr, local_port = _split_addr_port(local_raw)
        remote_addr, remote_port = _split_addr_port(peer_raw)

        pm = _PROCESS_RE.search(process_col)
        process = pm.group(1) if pm else ""

        connections.append(
            Connection(
                protocol="tcp",
                local_addr=local_addr,
                local_port=local_port,
                remote_addr=remote_addr if remote_addr not in ("*", "0.0.0.0", "::") else "",
                remote_port=remote_port,
                state=state if state != "UNCONN" else default_state,
                process=process,
            )
        )
    return connections


def _run_ss(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["ss"] + args,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout
    except FileNotFoundError:
        print("netview: 'ss' command not found", file=sys.stderr)
        return ""
    except subprocess.TimeoutExpired:
        print("netview: timeout running 'ss'", file=sys.stderr)
        return ""


def collect_connections() -> list[Connection]:
    listening = _parse_ss_output(_run_ss(["-tlnpH"]), "LISTEN")
    established = _parse_ss_output(_run_ss(["-tnpH"]), "ESTAB")
    return listening + established
