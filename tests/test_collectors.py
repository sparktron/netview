import json
import subprocess
from unittest.mock import MagicMock, mock_open, patch

import pytest

from netview.collectors.connections import collect_connections, _split_addr_port
from netview.collectors.dns import collect_dns
from netview.collectors.routes import collect_routes
from tests.conftest import (
    IP_ROUTE_JSON,
    RESOLV_CONF,
    SS_ESTAB_OUTPUT,
    SS_LISTEN_OUTPUT,
)


def _mock_run(mocker, stdout: str):
    m = MagicMock(spec=subprocess.CompletedProcess)
    m.stdout = stdout
    m.returncode = 0
    return mocker.patch("subprocess.run", return_value=m)


# --- routes ---

def test_routes_parses_entries(mocker):
    _mock_run(mocker, IP_ROUTE_JSON)
    routes = collect_routes()
    assert len(routes) == 2
    default = next(r for r in routes if r.destination == "default")
    assert default.gateway == "192.168.1.1"
    assert default.dev == "eth0"
    assert default.metric == 100


def test_routes_empty_output(mocker):
    m = MagicMock()
    m.stdout = ""
    mocker.patch("subprocess.run", return_value=m)
    assert collect_routes() == []


def test_routes_missing_gateway(mocker):
    data = json.dumps([{"dst": "192.168.1.0/24", "dev": "eth0", "metric": 0, "protocol": "kernel"}])
    _mock_run(mocker, data)
    routes = collect_routes()
    assert routes[0].gateway == ""


def test_routes_graceful_no_ip(mocker, capsys):
    mocker.patch("subprocess.run", side_effect=FileNotFoundError)
    assert collect_routes() == []


# --- dns ---

def test_dns_resolv_conf(mocker):
    mocker.patch("builtins.open", mock_open(read_data=RESOLV_CONF))
    dns = collect_dns()
    assert "8.8.8.8" in dns.nameservers
    assert "8.8.4.4" in dns.nameservers
    assert "example.com" in dns.search_domains


def test_dns_fallback_nmcli_when_empty(mocker):
    mocker.patch("builtins.open", mock_open(read_data=""))
    nmcli_out = "IP4.DNS[1]:1.1.1.1\nIP4.DNS[2]:1.0.0.1\n"
    m = MagicMock(spec=subprocess.CompletedProcess)
    m.stdout = nmcli_out
    mocker.patch("subprocess.run", return_value=m)
    dns = collect_dns()
    assert "1.1.1.1" in dns.nameservers


def test_dns_missing_resolv_conf(mocker):
    mocker.patch("builtins.open", side_effect=OSError)
    m = MagicMock(spec=subprocess.CompletedProcess)
    m.stdout = ""
    mocker.patch("subprocess.run", return_value=m)
    dns = collect_dns()
    assert dns.nameservers == []


# --- connections ---

def test_split_addr_port_ipv4():
    assert _split_addr_port("192.168.1.1:22") == ("192.168.1.1", 22)


def test_split_addr_port_ipv6_bracket():
    assert _split_addr_port("[::1]:631") == ("::1", 631)


def test_split_addr_port_ipv6_wildcard():
    addr, port = _split_addr_port("[::]:*")
    assert addr == "::"
    assert port == 0


def test_split_addr_port_wildcard():
    addr, port = _split_addr_port("0.0.0.0:*")
    assert port == 0


def test_connections_listen_parse(mocker):
    call_count = 0

    def side_effect(cmd, **kwargs):
        nonlocal call_count
        m = MagicMock(spec=subprocess.CompletedProcess)
        if "-tlnpH" in cmd:
            m.stdout = SS_LISTEN_OUTPUT
        else:
            m.stdout = ""
        call_count += 1
        return m

    mocker.patch("subprocess.run", side_effect=side_effect)
    conns = collect_connections()
    listen_conns = [c for c in conns if c.state == "LISTEN"]
    assert len(listen_conns) == 2
    ports = {c.local_port for c in listen_conns}
    assert 22 in ports


def test_connections_estab_parse(mocker):
    def side_effect(cmd, **kwargs):
        m = MagicMock(spec=subprocess.CompletedProcess)
        if "-tnpH" in cmd:
            m.stdout = SS_ESTAB_OUTPUT
        else:
            m.stdout = ""
        return m

    mocker.patch("subprocess.run", side_effect=side_effect)
    conns = collect_connections()
    estab = [c for c in conns if c.state == "ESTAB"]
    assert len(estab) == 1
    assert estab[0].local_addr == "192.168.1.10"
    assert estab[0].local_port == 22
    assert estab[0].process == "sshd"


def test_connections_no_ss(mocker, capsys):
    mocker.patch("subprocess.run", side_effect=FileNotFoundError)
    conns = collect_connections()
    assert conns == []
    assert "ss" in capsys.readouterr().err
