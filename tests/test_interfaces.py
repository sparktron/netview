import json
import subprocess
from unittest.mock import MagicMock

import pytest

from netview.collectors.interfaces import collect_interfaces
from netview.models import InterfaceState, InterfaceType
from tests.conftest import IP_ADDR_JSON


def _mock_run(mocker, stdout: str):
    m = MagicMock(spec=subprocess.CompletedProcess)
    m.stdout = stdout
    m.returncode = 0
    return mocker.patch("subprocess.run", return_value=m)


def test_collect_interfaces_basic(mocker):
    _mock_run(mocker, IP_ADDR_JSON)
    ifaces = collect_interfaces()
    assert len(ifaces) == 3
    names = [i.name for i in ifaces]
    assert "lo" in names
    assert "eth0" in names
    assert "wlan0" in names


def test_loopback_type_and_state(mocker):
    _mock_run(mocker, IP_ADDR_JSON)
    ifaces = collect_interfaces()
    lo = next(i for i in ifaces if i.name == "lo")
    assert lo.type == InterfaceType.LOOPBACK
    # UP flag in flags list → state must be UP despite operstate UNKNOWN
    assert lo.state == InterfaceState.UP


def test_ethernet_type(mocker):
    _mock_run(mocker, IP_ADDR_JSON)
    ifaces = collect_interfaces()
    eth0 = next(i for i in ifaces if i.name == "eth0")
    assert eth0.type == InterfaceType.ETHERNET
    assert eth0.state == InterfaceState.UP
    assert eth0.mac == "aa:bb:cc:dd:ee:ff"
    assert eth0.mtu == 1500


def test_wireless_type_by_name(mocker):
    _mock_run(mocker, IP_ADDR_JSON)
    ifaces = collect_interfaces()
    wlan0 = next(i for i in ifaces if i.name == "wlan0")
    # wlan* prefix → WIRELESS
    assert wlan0.type == InterfaceType.WIRELESS


def test_ipv4_parsed(mocker):
    _mock_run(mocker, IP_ADDR_JSON)
    ifaces = collect_interfaces()
    eth0 = next(i for i in ifaces if i.name == "eth0")
    assert len(eth0.ipv4) == 1
    assert eth0.ipv4[0].address == "192.168.1.10"
    assert eth0.ipv4[0].prefix_len == 24


def test_ipv6_parsed(mocker):
    _mock_run(mocker, IP_ADDR_JSON)
    ifaces = collect_interfaces()
    lo = next(i for i in ifaces if i.name == "lo")
    assert len(lo.ipv6) == 1
    assert lo.ipv6[0].address == "::1"


def test_graceful_failure_no_ip_command(mocker, capsys):
    mocker.patch("subprocess.run", side_effect=FileNotFoundError)
    ifaces = collect_interfaces()
    assert ifaces == []
    captured = capsys.readouterr()
    assert "ip" in captured.err


def test_graceful_failure_bad_json(mocker, capsys):
    m = MagicMock()
    m.stdout = "not json"
    mocker.patch("subprocess.run", return_value=m)
    ifaces = collect_interfaces()
    assert ifaces == []


def test_empty_output(mocker):
    m = MagicMock()
    m.stdout = ""
    mocker.patch("subprocess.run", return_value=m)
    assert collect_interfaces() == []
