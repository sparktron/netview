# netview

## What this is
A slick TUI for viewing networking info on Linux. Wraps `ip`, `nmcli`, `iw`, `ss`, and
`/etc/resolv.conf` into a color-coded, column-aligned display with compact and verbose modes,
plus live refresh.

## Tech stack
- Language: Python 3.10+
- TUI/display: `rich` (tables, color, live refresh)
- Data sources: `ip`, `nmcli`, `iw`, `ss` (subprocess), `/etc/resolv.conf`, `/proc/net/`
- Packaging: `pyproject.toml` (no setup.py)
- Testing: `pytest` + `pytest-mock`
- No external network calls, no root required for basic operation (ss/iw may need elevated perms)

## Directory layout
```
netview/
├── netview/
│   ├── __init__.py
│   ├── main.py           # entry point (python -m netview)
│   ├── cli.py            # argparse, main()
│   ├── collectors/
│   │   ├── __init__.py   # collect_all() — orchestrates all collectors
│   │   ├── interfaces.py # ip addr / ip link
│   │   ├── routes.py     # ip route
│   │   ├── wireless.py   # iw dev
│   │   ├── dns.py        # /etc/resolv.conf, nmcli
│   │   └── connections.py# ss (listening + established)
│   ├── display/
│   │   ├── __init__.py   # color constants
│   │   ├── compact.py    # compact table view
│   │   └── verbose.py    # verbose panels view
│   └── models.py         # dataclasses for all collected data
├── tests/
│   ├── conftest.py
│   ├── test_interfaces.py
│   ├── test_collectors.py
│   └── test_display.py
├── pyproject.toml
├── README.md
└── CLAUDE.md
```

## Key commands
```bash
# Install (editable, with dev deps)
pip install -e ".[dev]"

# Run (compact mode, default)
netview

# Run verbose
netview -v

# Filter to one interface
netview -i eth0

# Live refresh (2s interval default)
netview -w
netview -w 5          # 5s interval

# Run tests (must use python3.10 — pytest-mock is installed there)
python3.10 -m pytest

# Type check
python3.10 -m mypy netview/
```

## Coding conventions
- All data collection in `collectors/` — no display logic there
- All display logic in `display/` — no subprocess calls there
- `models.py` owns all dataclasses; collectors return model instances
- Subprocess calls always use `capture_output=True, text=True, timeout=5`; never `shell=True`
- Colors defined as constants in `display/__init__.py`, not scattered inline
- `rich.table.Table` for compact, `rich.panel.Panel` + `rich.console.Group` for verbose
- Argparse flag style mirrors `ip`/`tcpdump`: `-v`, `-i <iface>`, `-w [interval]`
- Functions max 60 lines; collectors return empty/default models on failure, log to stderr
- Never require root; degrade gracefully if a data source is unavailable

## Guardrails
- Never commit secrets or credentials
- No new dependencies without asking first (rich is the only allowed TUI lib)
- Never use `shell=True` in subprocess calls
- Handle missing tools gracefully (iw not installed, nmcli not running, etc.)
- Don't silently swallow exceptions in collectors — log to stderr and return safe defaults
- Keep compact mode fast (<200ms); verbose can be slower

## Compact mode columns (in order)
TYPE | NAME | STATE | IPv4 | IPv6 | MAC | MTU | SSID (wireless only)

## Verbose mode sections (per interface)
- Header: name, type, state, flags
- Addresses: all IPv4 + IPv6 with prefix lengths and scope
- Link: MAC, MTU
- Wireless: SSID, signal dBm, TX rate, channel, frequency (if applicable)
- Routes: all routes for this interface
- Connections: listening ports + established connections on this interface's IPs
- DNS: configured nameservers and search domains (global section, not per-interface)
