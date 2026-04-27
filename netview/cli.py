from __future__ import annotations

import argparse
import time
from typing import Callable

from rich.console import Console, ConsoleRenderable, RichCast
from rich.live import Live

_RenderResult = ConsoleRenderable | RichCast | str


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="netview",
        description="TUI for Linux networking info",
    )
    p.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    p.add_argument("-i", "--interface", metavar="IFACE", help="filter to one interface")
    p.add_argument(
        "-w",
        "--watch",
        nargs="?",
        const=2,
        type=int,
        metavar="INTERVAL",
        help="live refresh (default 2s)",
    )
    p.add_argument(
        "--no-connections",
        "--nc",
        action="store_true",
        dest="no_connections",
        help="skip connections section in verbose mode",
    )
    return p


def _make_render(
    verbose: bool, iface_filter: str | None, no_connections: bool = False
) -> "Callable[[], _RenderResult]":
    def render() -> _RenderResult:
        from netview.collectors import collect_all
        from netview.display.compact import render_compact
        from netview.display.verbose import render_verbose

        ifaces, dns = collect_all(iface_filter)
        if verbose:
            return render_verbose(ifaces, dns, show_connections=not no_connections)
        return render_compact(ifaces)

    return render


def main() -> None:
    args = _build_parser().parse_args()
    console = Console()
    render = _make_render(args.verbose, args.interface, args.no_connections)

    if args.watch is not None:
        interval = max(1, args.watch)
        with Live(render(), console=console, refresh_per_second=1) as live:
            while True:
                time.sleep(interval)
                live.update(render())
    else:
        console.print(render())
