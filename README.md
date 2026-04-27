# netview

A blazing-fast, color-coded TUI for viewing Linux networking information at a glance. Displays interfaces, IP addresses, routes, DNS configuration, and active connections in a responsive, easy-to-read format.

**Features:**
- 📊 Compact table view showing all interfaces at once
- 🔍 Detailed verbose mode with per-interface panels
- 🔄 Live refresh mode for monitoring changes
- 🎨 Beautiful color-coded output with status indicators
- 🚀 Instant startup (<200ms in compact mode)
- 🛡️ Graceful degradation — works without root, handles missing tools elegantly
- 📱 Responsive design — adapts to terminal width

## Quick Start

### Installation

```bash
pip install -e .
```

Then run:

```bash
netview
```

### Requirements

- Python 3.10+
- `rich` library (installed automatically)
- Linux with `ip`, `ss` commands (standard on all modern Linux systems)
- Optional: `iw` for wireless info, `nmcli` for DNS fallback

## Usage

### Compact Mode (Default)

Shows all interfaces in a single table:

```bash
netview
```

```
  TYPE    NAME          STATE   IPv4   IPv6   MAC                   MTU   SSID  
 ────────────────────────────────────────────────────────────────────────────── 
  lo      lo            UP      127…   ::1…   00:00:00:00:00:00   65536         
  eth     enp114s0      UP                    c4:c6:e6:db:dd:38    1500         
  wifi    wlp0s20f3     UP      192…   fdb…   dc:97:ba:e5:8d:64    1500   MySSID
  other   tailscale0    UP             fe8…                        1280         
  eth     docker0       UP      172…   fe8…   1a:63:c2:99:41:87    1500         
```

**Columns:**
- **TYPE**: Interface type (eth, wifi, lo, other) with color coding
- **NAME**: Interface name
- **STATE**: Operational state (UP/DOWN)
- **IPv4**: First IPv4 address with prefix length
- **IPv6**: First IPv6 address with prefix length
- **MAC**: Hardware address
- **MTU**: Maximum transmission unit
- **SSID**: Network name (wireless only)

### Verbose Mode

Show detailed information for each interface:

```bash
netview -v
```

Displays per-interface panels with:
- All configured addresses (IPv4 & IPv6) with scope
- MAC address and MTU
- Wireless details (SSID, signal strength, TX rate, channel, frequency)
- Routing table entries
- Active connections (listening + established)
- Global DNS configuration

**Skip connections section** if there are too many:

```bash
netview -v --no-connections
```

This displays all information except the connections table, useful when you have many listening/established connections.

```
╭──────────────────────────── lo ─────────────────────────────╮
│ lo  loopback  UP  [LOOPBACK UP LOWER_UP]                    │
│                                                             │
│ Addresses                                                   │
│   127.0.0.1/8  ipv4  (host)                                 │
│   ::1/128  ipv6  (host)                                     │
│                                                             │
│ Link                                                        │
│   MAC: 00:00:00:00:00:00                                    │
│   MTU: 65536                                                │
│                                                             │
│ Connections                                                 │
│  State   Local            Remote           Process          │
│  LISTEN  127.0.0.1:631    *                                 │
│  LISTEN  127.0.0.1:7001   *                nxnode.bin       │
│  ESTAB   127.0.0.1:44382  127.0.0.1:44421  mviz             │
│                                                             │
├────────────────────────────────────────────────────────────┤
│ DNS                                                         │
│   Nameservers: 8.8.8.8, 8.8.4.4                             │
│   Search domains: example.com                               │
╰────────────────────────────────────────────────────────────╯
```

### Filter to Single Interface

```bash
netview -i eth0
```

Only shows the specified interface in compact or verbose mode.

### Live Refresh

Monitor network changes in real-time:

```bash
netview -w          # refresh every 2 seconds (default)
netview -w 5        # refresh every 5 seconds
```

Automatically updates the display when network configuration changes. Press `Ctrl-C` to exit.

### Command Help

```bash
netview -h
```

```
usage: netview [-h] [-v] [-i IFACE] [-w [INTERVAL]] [--no-connections]

TUI for Linux networking info

options:
  -h, --help            show this help message and exit
  -v, --verbose         verbose mode
  -i IFACE, --interface IFACE
                        filter to one interface
  -w [INTERVAL], --watch [INTERVAL]
                        live refresh (default 2s)
  --no-connections      skip connections section in verbose mode
```

## Data Sources

netview collects data from standard Linux utilities:

| Data | Tool | Required |
|------|------|----------|
| Interfaces & addresses | `ip -j addr show` | ✅ Yes |
| Routes | `ip -j route show` | ✅ Yes |
| Wireless info | `iw dev <iface> link/info` | ❌ Optional |
| DNS configuration | `/etc/resolv.conf` | ✅ Yes |
| Connections | `ss -tlnpH` / `ss -tnpH` | ✅ Yes |

**Fallbacks & Graceful Degradation:**
- If `iw` is not installed, wireless information is skipped
- If `/etc/resolv.conf` is empty, netview tries `nmcli` for DNS info
- If `nmcli` is unavailable, DNS section is left empty
- If any tool fails, it's logged to stderr and netview continues

## Installation from Source

### Clone and Install

```bash
git clone https://github.com/sparktron/netview.git
cd netview
pip install -e ".[dev]"
```

### Development Setup

Install dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
python3.10 -m pytest -v
```

Type check:

```bash
python3.10 -m mypy netview/
```

**Note:** Tests require `pytest-mock` which is installed in the Python 3.10 environment. Use `python3.10 -m pytest` rather than just `pytest`.

## Architecture

```
netview/
├── collectors/          # Data collection layer
│   ├── interfaces.py   # Interface details
│   ├── routes.py       # Routing table
│   ├── wireless.py     # Wireless info
│   ├── dns.py          # DNS configuration
│   ├── connections.py  # Active connections
│   └── __init__.py     # Orchestrates collection
├── display/            # Display layer
│   ├── compact.py      # Compact table view
│   ├── verbose.py      # Detailed panel view
│   └── __init__.py     # Color constants
├── models.py           # Data models (dataclasses)
├── cli.py              # Argument parsing & main loop
└── main.py             # Entry point
```

**Design Principles:**
- All data collection in `collectors/` — no display logic
- All rendering in `display/` — no subprocess calls
- Dataclasses in `models.py` — single source of truth
- Subprocess calls always use `capture_output=True, text=True, timeout=5`
- Never `shell=True`
- Errors logged to stderr, graceful defaults returned

## Performance

- **Compact mode:** <200ms startup
- **Verbose mode:** <500ms startup
- **Live refresh:** Minimal CPU usage, <10MB memory

## Troubleshooting

### "ip command not found"

netview requires the `ip` command from the `iproute2` package. Install it:

**Debian/Ubuntu:**
```bash
sudo apt install iproute2
```

**RedHat/CentOS:**
```bash
sudo yum install iproute
```

**Arch:**
```bash
sudo pacman -S iproute2
```

### Incomplete wireless information

If wireless details (SSID, signal) are missing, install `iw`:

**Debian/Ubuntu:**
```bash
sudo apt install iw
```

**RedHat/CentOS:**
```bash
sudo yum install wireless-tools
```

**Arch:**
```bash
sudo pacman -S wireless_tools
```

### Incomplete DNS information

If DNS servers aren't showing, ensure `/etc/resolv.conf` is readable or install `NetworkManager`:

```bash
sudo apt install network-manager  # Debian/Ubuntu
sudo yum install NetworkManager   # RedHat/CentOS
```

### Port numbers show as *

This means the port couldn't be parsed from `ss` output, likely due to a format change. Please file an issue on GitHub with your Linux distribution and kernel version.

## Testing

Run the full test suite:

```bash
python3.10 -m pytest -v
```

Test coverage:
- **test_interfaces.py:** Interface parsing, type detection, state resolution
- **test_collectors.py:** Routes, DNS, connections parsing with mocked subprocess
- **test_display.py:** Table and panel rendering without crashing

All tests use `pytest-mock` to mock subprocess calls, so they run offline without requiring actual network tools.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and test: `python3.10 -m pytest -v && python3.10 -m mypy netview/`
4. Commit with clear messages
5. Push and open a pull request

## License

MIT License — see LICENSE file for details.

## FAQ

**Q: Do I need to run netview as root?**

A: No. Most functionality works as a regular user. Some tools (`ss`, `iw`) may require elevated privileges to show detailed process information for other users' connections, but netview will degrade gracefully.

**Q: Can I use netview remotely over SSH?**

A: Yes. netview uses `rich` which works over SSH with TERM=xterm-256color or similar. Colors may not work over slow connections.

**Q: Why does my interface show "?" for state?**

A: This happens when the interface's operational state can't be determined from the kernel. It's usually safe to ignore — check the flags field in verbose mode for actual state.

**Q: How often should I refresh (-w)?**

A: The default 2 seconds is reasonable for most use cases. Use 5+ seconds if you're monitoring over a slow connection.

**Q: Can I customize colors or output format?**

A: Not yet, but this is planned for a future release. Open an issue on GitHub if you have specific requests.
