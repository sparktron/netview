# netview

A color-coded TUI for Linux networking info — wraps `ip`, `iw`, `ss`, and `/etc/resolv.conf`
into a compact table or detailed panel view with optional live refresh.

## Install

```bash
pip install -e ".[dev]"
```

Requires Python 3.10+ and the `rich` library (installed automatically).

## Usage

```bash
# Compact table (default)
netview

# Verbose panels
netview -v

# Filter to one interface
netview -i wlan0

# Live refresh every 2 seconds
netview -w

# Live refresh every 5 seconds
netview -w 5
```

## Compact columns

```
TYPE  NAME       STATE  IPv4             IPv6          MAC                 MTU   SSID
────────────────────────────────────────────────────────────────────────────────────
lo    lo         UP     127.0.0.1/8      ::1/128       00:00:00:00:00:00  65536
eth   eth0       UP     192.168.1.10/24  fe80::1/64    aa:bb:cc:dd:ee:ff   1500
wifi  wlan0      UP     10.0.0.5/24      ...           11:22:33:44:55:66   1500  MyNet
```

## Data sources

| Data | Tool |
|------|------|
| Interfaces & addresses | `ip -j addr show` |
| Routes | `ip -j route show` |
| Wireless info | `iw dev <iface> link/info` |
| DNS | `/etc/resolv.conf`, fallback `nmcli` |
| Connections | `ss -tlnpH` / `ss -tnpH` |

Missing tools degrade gracefully — `iw` and `nmcli` are optional.

## Development

```bash
# Tests
python3.10 -m pytest -v

# Type check
python3.10 -m mypy netview/
```
